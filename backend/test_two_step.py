#!/usr/bin/env python
"""
Test script for two-step content generation process.
Tests the new draft and format endpoints.
"""

import asyncio
import json
from pathlib import Path
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_two_step_generation():
    """Test the two-step generation process."""
    from pipeline import ContentPipeline
    
    print("="*60)
    print("TESTING TWO-STEP CONTENT GENERATION")
    print("="*60)
    
    pipeline = ContentPipeline()
    
    # Test parameters
    params = {
        "content_type": "MCQ",
        "generator_model": "claude-sonnet-3.5",
        "input_text": "The mitochondria is the powerhouse of the cell. It produces ATP through cellular respiration.",
        "num_questions": 1,
        "generator_temperature": 0.7
    }
    
    # Step 1: Generate Draft
    print("\nSTEP 1: GENERATING DRAFT")
    print("-"*40)
    
    draft_content = ""
    token_count = 0
    
    async for event in pipeline.run_stream_draft_only(**params):
        if event.get("event") == "draft_token":
            data = json.loads(event["data"])
            token = data.get("token", "")
            draft_content += token
            token_count += 1
            print(token, end="", flush=True)
        elif event.get("event") == "draft_complete":
            data = json.loads(event["data"])
            print(f"\n\n✅ Draft complete!")
            print(f"   Tokens streamed: {token_count}")
            print(f"   Draft length: {len(draft_content)} chars")
            draft_1 = data.get("draft_1", "")
    
    # Step 2: Format Draft
    print("\nSTEP 2: FORMATTING DRAFT")
    print("-"*40)
    
    format_params = {
        "draft_1": draft_1,
        "content_type": params["content_type"],
        "generator_model": params["generator_model"],
        "input_text": params["input_text"],
        "num_questions": params["num_questions"],
        "formatter_temperature": 0.5
    }
    
    formatted_content = ""
    format_tokens = 0
    
    async for event in pipeline.run_stream_format_only(**format_params):
        if event.get("event") == "formatted_token":
            data = json.loads(event["data"])
            token = data.get("token", "")
            formatted_content += token
            format_tokens += 1
            print(token, end="", flush=True)
        elif event.get("event") == "format_complete":
            data = json.loads(event["data"])
            print(f"\n\n✅ Formatting complete!")
            print(f"   Tokens streamed: {format_tokens}")
            print(f"   Formatted length: {len(formatted_content)} chars")
            print(f"   Success: {data.get('success')}")
            
            validation_errors = data.get("validation_errors", [])
            if validation_errors:
                print(f"   ⚠️ Validation errors: {len(validation_errors)}")
                for err in validation_errors[:3]:  # Show first 3 errors
                    print(f"      - {err}")
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)
    
    return True

if __name__ == "__main__":
    import os
    
    # Check for API keys
    if not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
        print("ERROR: No API keys found in environment")
        print("Please set ANTHROPIC_API_KEY or GOOGLE_API_KEY")
        sys.exit(1)
    
    # Run the async test
    success = asyncio.run(test_two_step_generation())
    sys.exit(0 if success else 1)
