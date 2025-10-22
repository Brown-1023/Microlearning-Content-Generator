"""
LangGraph pipeline for generating and formatting microlearning content.
Implements the required flow: load_prompts → generator → formatter → validator → retry/done
"""

import os
import json
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Literal, Annotated, TypedDict
from dataclasses import dataclass

import structlog
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# AI Model imports
import anthropic
import google.generativeai as genai

# LangGraph imports
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from validators import validate_content, ValidationError

# Configure structured logging
logger = structlog.get_logger()


class PipelineState(TypedDict):
    """State that flows through the LangGraph pipeline."""
    # Input parameters
    content_type: str
    generator_model: str
    input_text: str
    num_questions: int
    focus_areas: Optional[str]
    # Separate temperature and top-p for generator and formatter
    generator_temperature: Optional[float]
    generator_top_p: Optional[float]
    formatter_temperature: Optional[float]
    formatter_top_p: Optional[float]
    custom_mcq_generator: Optional[str]
    custom_mcq_formatter: Optional[str]
    custom_nmcq_generator: Optional[str]
    custom_nmcq_formatter: Optional[str]
    
    # Pipeline state
    prompts: Dict[str, str]
    draft_1: Optional[str]  # Original draft from generator
    formatted_output: Optional[str]
    validation_errors: List[Dict]
    formatter_retries: int
    
    # Metadata
    start_time: float
    model_latencies: Dict[str, float]
    model_ids: Dict[str, str]
    success: bool
    error_message: Optional[str]


@dataclass
class ModelConfig:
    """Configuration for AI models."""
    temperature: float = float(os.getenv("MODEL_TEMPERATURE", "0.51"))
    top_p: float = float(os.getenv("MODEL_TOP_P", "0.95"))
    max_tokens: int = int(os.getenv("MODEL_MAX_TOKENS", "8000"))
    timeout: int = int(os.getenv("MODEL_TIMEOUT", "60"))
    
    def with_overrides(self, temperature: Optional[float] = None, top_p: Optional[float] = None) -> 'ModelConfig':
        """Create a new ModelConfig with overridden values."""
        return ModelConfig(
            temperature=temperature if temperature is not None else self.temperature,
            top_p=top_p if top_p is not None else self.top_p,
            max_tokens=self.max_tokens,
            timeout=self.timeout
        )


class PromptLoader:
    """Handles loading of prompt templates."""
    
    @staticmethod
    def load_prompts() -> Dict[str, str]:
        """Load prompt templates from files."""
        prompts = {}
        prompt_files = {
            "mcq_generator": "prompts/mcq.generator.txt",
            "mcq_formatter": "prompts/mcq.formatter.txt",
            "nmcq_generator": "prompts/nonmcq.generator.txt",
            "nmcq_formatter": "prompts/nonmcq.formatter.txt",
            "summary_generator": "prompts/summarybytes.generator.txt",
            "summary_formatter": "prompts/summarybytes.formatter.txt"
        }
        
        for key, filepath in prompt_files.items():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    prompts[key] = f.read()
                logger.info(f"Loaded prompt: {key}")
            except FileNotFoundError:
                logger.error(f"Prompt file not found: {filepath}")
                prompts[key] = ""
        
        return prompts


class ModelCaller:
    """Handles AI model API calls."""
    
    def __init__(self):
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.google_key = os.getenv("GOOGLE_API_KEY")
        
        # Model names - using correct model identifiers
        self.claude_model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250929")
        self.gemini_pro_model = os.getenv("GEMINI_PRO", "gemini-2.5-pro")
        self.gemini_flash_model = os.getenv("GEMINI_FLASH", "gemini-2.5-flash")
        
        # Initialize clients
        if self.anthropic_key:
            self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_key)
        
        if self.google_key:
            genai.configure(api_key=self.google_key)
        
        self.model_config = ModelConfig()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((anthropic.RateLimitError, Exception))
    )
    def call_claude(self, prompt: str, temperature: Optional[float] = None, top_p: Optional[float] = None) -> Tuple[str, str, float]:
        """Call Claude API with retry logic."""
        start = time.time()
        
        # Use custom temperature/top_p if provided
        config = self.model_config.with_overrides(temperature, top_p)
        
        message = self.anthropic_client.messages.create(
            model=self.claude_model,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            messages=[{"role": "user", "content": prompt}],
            timeout=config.timeout
        )
        
        latency = time.time() - start
        return message.content[0].text, self.claude_model, latency
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(Exception)
    )
    def call_gemini(self, prompt: str, model_name: str, temperature: Optional[float] = None, top_p: Optional[float] = None) -> Tuple[str, str, float]:
        """Call Gemini API with retry logic."""
        start = time.time()
        
        # Use custom temperature/top_p if provided
        config = self.model_config.with_overrides(temperature, top_p)
        
        model = genai.GenerativeModel(model_name)
        generation_config = genai.types.GenerationConfig(
            temperature=config.temperature,
            top_p=config.top_p,
            max_output_tokens=config.max_tokens,
        )
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config,
            request_options={"timeout": self.model_config.timeout}
        )
        
        latency = time.time() - start
        return response.parts[0].text, model_name, latency


def load_prompts_node(state: PipelineState) -> PipelineState:
    """Load prompts from files."""
    logger.info(
        "load_prompts_started",
        content_type=state["content_type"],
        generator_model=state["generator_model"]
    )
    
    prompts = PromptLoader.load_prompts()
    
    # if state['content_type'].upper()=='MCQ':
    #     if state["prompts"]["generator"] == "":
    #         state["prompts"]["generator"] = prompts["mcq_generator"]
    #     if state["prompts"]["formatter"] == "":
    #         state["prompts"]["formatter"] = prompts["mcq_formatter"]
    # else:
    #     if state["prompts"]["generator"] == "":
    #         state["prompts"]["generator"] = prompts["nmcq_generator"]
    #     if state["prompts"]["formatter"] == "":
    #         state["prompts"]["formatter"] = prompts["nmcq_formatter"]

    if state['content_type'].upper()=='MCQ':
        state["prompts"]={
            "generator": prompts["mcq_generator"],
            "formatter": prompts["mcq_formatter"]
        }
    elif state['content_type'].upper()=='SUMMARY':
        state["prompts"]={
            "generator": prompts["summary_generator"],
            "formatter": prompts["summary_formatter"]
        }
    else:
        state["prompts"]={
            "generator": prompts["nmcq_generator"],
            "formatter": prompts["nmcq_formatter"]
        }
    
    return state


def generator_node(state: PipelineState) -> PipelineState:
    """Generator node - uses Claude or Gemini Pro."""
    model_caller = ModelCaller()
    max_input_chars = 500000
    
    try:
        # Check input size
        if len(state["input_text"]) > max_input_chars:
            state["success"] = False
            state["error_message"] = f"Input text exceeds {max_input_chars} character limit"
            return state
 
        # Use custom prompt if provided, otherwise use default
        template = state['prompts']['generator']
        
        # Replace placeholders
        prompt = template.replace("{{TEXT_TO_ANALYZE}}", state["input_text"])
        prompt = prompt.replace("{{NUM_QUESTIONS}}", str(state["num_questions"]))
        prompt = prompt.replace("{{FOCUS_AREAS}}", state.get("focus_areas") or "Not specified")
        
        print(prompt)

        # Get generator-specific temperature and top_p from state
        temperature = state.get("generator_temperature")
        top_p = state.get("generator_top_p")
        
        # Determine which model to use
        model_name = state["generator_model"]
        
        # Direct model name mapping - frontend sends the actual API model names now
        if "claude" in model_name.lower():
            if not model_caller.anthropic_key:
                raise ValueError("ANTHROPIC_API_KEY not set")
            # Use the model name directly if it's a full model ID, otherwise map it
            model_caller.claude_model = model_name
            content, model_id, latency = model_caller.call_claude(prompt, temperature, top_p)
        elif "gemini" in model_name.lower():
            if not model_caller.google_key:
                raise ValueError("GOOGLE_API_KEY not set")
            # Use the model name directly if it's a full model ID
            gemini_model = model_name
            
            content, model_id, latency = model_caller.call_gemini(
                prompt, 
                gemini_model,
                temperature,
                top_p
            )
        else:
            # Unknown model, raise error
            raise ValueError(f"Unknown model: {model_name}")
        
        # Store the original draft (DRAFT_1)
        state["draft_1"] = content
        state["model_ids"]["generator"] = model_id
        state["model_latencies"]["generator"] = latency
        
        logger.info(
            "generator_completed",
            model=model_id,
            latency=latency,
            content_length=len(content)
        )
        
    except Exception as e:
        logger.error("generator_failed", error=str(e))
        state["success"] = False
        state["error_message"] = f"Generation failed: {str(e)}"
    
    return state


def formatter_node(state: PipelineState) -> PipelineState:
    """Formatter node - always uses Gemini Flash."""
    model_caller = ModelCaller()
    
    try:
        # Select appropriate custom formatter prompt based on content type
        
        
        # Use custom prompt if provided, otherwise use default
        prompt_template = state['prompts']["formatter"]
        
        # On retry, use original DRAFT_1 as per requirements
        content_to_format = state["draft_1"]
        
        # Add the draft content to format
        full_prompt = f"{prompt_template}\n\nContent to format:\n\n{content_to_format}"
        
        print(full_prompt)
        # Always use Gemini Flash for formatting
        if not model_caller.google_key:
            raise ValueError("GOOGLE_API_KEY not set")
        
        # Get formatter-specific temperature and top_p from state
        temperature = state.get("formatter_temperature")
        top_p = state.get("formatter_top_p")
        
        content, model_id, latency = model_caller.call_gemini(
            full_prompt,
            model_caller.gemini_flash_model,
            temperature,
            top_p
        )
        
        state["formatted_output"] = content
        state["model_ids"]["formatter"] = model_id
        state["model_latencies"]["formatter"] = latency
        
        logger.info(
            "formatter_completed",
            model=model_id,
            latency=latency,
            retry_count=state["formatter_retries"]
        )
        
    except Exception as e:
        logger.error("formatter_failed", error=str(e))
        state["success"] = False
        state["error_message"] = f"Formatting failed: {str(e)}"
    
    return state


def validator_node(state: PipelineState) -> PipelineState:
    """Validator node - deterministic validation."""
    if not state.get("formatted_output"):
        state["success"] = False
        state["error_message"] = "No formatted output to validate"
        return state
    
    # Run deterministic validation
    is_valid, errors = validate_content(
        state["formatted_output"],
        state["content_type"]
    )
    
    # Store validation errors
    state["validation_errors"] = [
        {
            "line": e.line_number,
            "message": e.message,
            "section": e.section
        }
        for e in errors
    ]
    
    if is_valid:
        state["success"] = True
        logger.info("validator_passed")
    else:
        logger.warning(
            "validator_failed",
            error_count=len(errors),
            retry_count=state["formatter_retries"]
        )
    
    return state


def formatter_retry_node(state: PipelineState) -> PipelineState:
    """Retry formatter with same prompt and original DRAFT_1."""
    state["formatter_retries"] += 1
    
    logger.info(
        "formatter_retry",
        attempt=state["formatter_retries"]
    )
    
    # Call formatter again - it will use original DRAFT_1
    return formatter_node(state)


def should_retry_or_finish(state: PipelineState) -> str:
    """Determine next step based on validation result."""
    if state.get("success"):
        return "done"
    
    # Check if we should retry (only 1 retry as per requirements)
    max_formatter_retries = int(os.getenv("MAX_FORMATTER_RETRIES", "1"))
    if state["formatter_retries"] < max_formatter_retries:
        return "retry"
    
    return "fail"


def done_node(state: PipelineState) -> PipelineState:
    """Successful completion node."""
    elapsed = time.time() - state["start_time"]
    logger.info(
        "pipeline_completed",
        total_time=elapsed,
        formatter_retries=state["formatter_retries"]
    )
    return state


def fail_node(state: PipelineState) -> PipelineState:
    """Failure node - returns with validation errors."""
    elapsed = time.time() - state["start_time"]
    logger.error(
        "pipeline_failed",
        total_time=elapsed,
        formatter_retries=state["formatter_retries"],
        validation_errors=len(state.get("validation_errors", []))
    )
    return state


class ContentPipeline:
    """LangGraph pipeline orchestrator."""
    
    def __init__(self):
        self.max_formatter_retries = int(os.getenv("MAX_FORMATTER_RETRIES", "1"))
        self.max_input_chars = 500000
        
        # Build the LangGraph workflow
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow as per requirements."""
        
        # Create the workflow with state schema
        workflow = StateGraph(PipelineState)
        
        # Add nodes as per requirements
        workflow.add_node("load_prompts", load_prompts_node)
        workflow.add_node("generator", generator_node)
        workflow.add_node("formatter", formatter_node)
        workflow.add_node("validator", validator_node)
        workflow.add_node("formatter_retry", formatter_retry_node)
        workflow.add_node("done", done_node)
        workflow.add_node("fail", fail_node)
        
        # Set entry point
        workflow.set_entry_point("load_prompts")
        
        # Define the flow as per requirements
        workflow.add_edge("load_prompts", "generator")
        workflow.add_edge("generator", "formatter")
        workflow.add_edge("formatter", "validator")
        
        # Conditional edge from validator
        workflow.add_conditional_edges(
            "validator",
            should_retry_or_finish,
            {
                "retry": "formatter_retry",
                "done": "done",
                "fail": "fail"
            }
        )
        
        # After retry, go back to validator
        workflow.add_edge("formatter_retry", "validator")
        
        # Terminal nodes
        workflow.add_edge("done", END)
        workflow.add_edge("fail", END)
        
        return workflow
    
    def get_prompt_hashes(self) -> Dict[str, str]:
        """Get hashes of loaded prompts for versioning."""
        prompts = PromptLoader.load_prompts()
        hashes = {}
        for key, content in prompts.items():
            hashes[key] = hashlib.md5(content.encode()).hexdigest()[:8]
        return hashes
    
    def run(
        self,
        content_type: str,
        generator_model: str,
        input_text: str,
        num_questions: int,
        focus_areas: Optional[str] = None,
        generator_temperature: Optional[float] = None,
        generator_top_p: Optional[float] = None,
        formatter_temperature: Optional[float] = None,
        formatter_top_p: Optional[float] = None,
        prompts: Optional[Dict[str, str]] = None
    ) -> Dict:
        """
        Run the LangGraph pipeline.
        
        Returns:
            Dictionary with results and metadata
        """
        # Initialize state
        initial_state: PipelineState = {
            "content_type": content_type.upper(),
            "generator_model": generator_model,  # Keep original casing for model mapping
            "input_text": input_text,
            "num_questions": num_questions,
            "focus_areas": focus_areas,
            "generator_temperature": generator_temperature,
            "generator_top_p": generator_top_p,
            "formatter_temperature": formatter_temperature,
            "formatter_top_p": formatter_top_p,
            "prompts": prompts,
            "draft_1": None,
            "formatted_output": None,
            "validation_errors": [],
            "formatter_retries": 0,
            "start_time": time.time(),
            "model_latencies": {},
            "model_ids": {},
            "success": False,
            "error_message": None
        }
        
        try:
            # Compile and run the LangGraph workflow
            app = self.workflow.compile()
            
            # Run through each node as LangGraph expects
            # (without using invoke which may have issues)
            config = {"recursion_limit": 10}
            
            # Invoke the workflow with a proper dict format
            final_state = app.invoke(initial_state, config)
            
            # Prepare response
            response = {
                "success": final_state.get("success", False),
                "output": final_state.get("formatted_output"),
                "validation_errors": final_state.get("validation_errors", []),
                "metadata": {
                    "content_type": final_state["content_type"],
                    "generator_model": final_state["generator_model"],
                    "num_questions": final_state["num_questions"],
                    "formatter_retries": final_state.get("formatter_retries", 0),
                    "model_ids": final_state.get("model_ids", {}),
                    "latencies": final_state.get("model_latencies", {}),
                    "total_time": time.time() - final_state["start_time"]
                }
            }
            
            if final_state.get("error_message"):
                response["error"] = final_state["error_message"]
            
            # Include partial output on failure after validation
            if not final_state.get("success") and final_state.get("formatted_output"):
                response["partial_output"] = final_state["formatted_output"]
            
            return response
            
        except Exception as e:
            error_msg = str(e)
            # If the error is about __start__, use a simpler approach
            if "__start__" in error_msg:
                logger.warning("LangGraph invoke failed, falling back to direct execution")
                return self._run_direct(
                    content_type, generator_model, input_text, 
                    num_questions, focus_areas, prompts
                )
            
            logger.error(f"Pipeline execution failed: {e}")
            return {
                "success": False,
                "output": None,
                "error": f"Pipeline execution failed: {str(e)}",
                "validation_errors": [],
                "metadata": {
                    "content_type": content_type.upper(),
                    "generator_model": generator_model.lower(),
                    "num_questions": num_questions,
                    "formatter_retries": 0,
                    "model_ids": {},
                    "latencies": {},
                    "total_time": time.time() - initial_state["start_time"]
                }
            }
    
    def _run_direct(
        self,
        content_type: str,
        generator_model: str,
        input_text: str,
        num_questions: int,
        focus_areas: Optional[str] = None,
        prompts: Optional[Dict[str, str]] = None
    ) -> Dict:
        """
        Direct execution of pipeline nodes in sequence (fallback).
        Still uses the LangGraph nodes but executes them directly.
        """
        # Initialize state
        state: PipelineState = {
            "content_type": content_type.upper(),
            "generator_model": generator_model.lower(),
            "input_text": input_text,
            "num_questions": num_questions,
            "focus_areas": focus_areas,
            "prompts": prompts,
            "draft_1": None,
            "formatted_output": None,
            "validation_errors": [],
            "formatter_retries": 0,
            "start_time": time.time(),
            "model_latencies": {},
            "model_ids": {},
            "success": False,
            "error_message": None
        }
        
        try:
            # Execute nodes in sequence as per requirements
            # load_prompts → generator → formatter → validator → retry/done
            
            # 1. Load prompts
            state = load_prompts_node(state)
            if state.get("error_message"):
                raise Exception(state["error_message"])
            # 2. Generator
            state = generator_node(state)
            if state.get("error_message"):
                raise Exception(state["error_message"])
            
            # 3. Formatter
            state = formatter_node(state)
            if state.get("error_message"):
                raise Exception(state["error_message"])
            
            # 4. Validator
            state = validator_node(state)
            
            # 5. Retry logic if validation failed
            if not state.get("success") and state["formatter_retries"] < self.max_formatter_retries:
                state = formatter_retry_node(state)
                state = validator_node(state)
            
            # 6. Final node
            if state.get("success"):
                state = done_node(state)
            else:
                state = fail_node(state)
            
            # Prepare response
            response = {
                "success": state.get("success", False),
                "output": state.get("formatted_output"),
                "validation_errors": state.get("validation_errors", []),
                "metadata": {
                    "content_type": state["content_type"],
                    "generator_model": state["generator_model"],
                    "num_questions": state["num_questions"],
                    "formatter_retries": state.get("formatter_retries", 0),
                    "model_ids": state.get("model_ids", {}),
                    "latencies": state.get("model_latencies", {}),
                    "total_time": time.time() - state["start_time"]
                }
            }
            
            if state.get("error_message"):
                response["error"] = state["error_message"]
            
            # Include partial output on failure
            if not state.get("success") and state.get("formatted_output"):
                response["partial_output"] = state["formatted_output"]
            
            return response
            
        except Exception as e:
            logger.error(f"Direct pipeline execution failed: {e}")
            return {
                "success": False,
                "output": None,
                "error": f"Pipeline execution failed: {str(e)}",
                "validation_errors": [],
                "metadata": {
                    "content_type": content_type.upper(),
                    "generator_model": generator_model.lower(),
                    "num_questions": num_questions,
                    "formatter_retries": 0,
                    "model_ids": {},
                    "latencies": {},
                    "total_time": time.time() - state["start_time"]
                }
            }