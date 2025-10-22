"""
Validators for MCQ and NMCQ formatted content.
These are deterministic validators that check structure and format compliance.
"""

import re
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass


@dataclass
class ValidationError:
    """Represents a validation error with details."""
    line_number: Optional[int]
    message: str
    section: Optional[str] = None


class MCQValidator:
    """Validator for Multiple Choice Questions format."""
    
    def __init__(self):
        # Regex patterns for MCQ validation
        self.title_pattern = re.compile(r'^Question\s+\d+(?:\s*[-–—]{1,2}\s*.+)?$', re.IGNORECASE)
        self.option_pattern = re.compile(r'^[A-E][\)\.]\s+.+$')
        self.correct_answer_pattern = re.compile(r'^(?:Correct Answer|Answer):\s*[A-E]$', re.IGNORECASE)
        self.explanation_header_pattern = re.compile(
            r'^(?:Explanation of the Correct Answer|Explanation):?\s*$', re.IGNORECASE
        )
        # Match various forms of the analysis header with optional "the" and parentheses content
        self.analysis_header_pattern = re.compile(
            r'^(?:Analysis of (?:the )?Other Options(?:\s*\([^)]*\))?|Distractors):?\s*$', 
            re.IGNORECASE
        )
        self.key_insights_pattern = re.compile(r'^Key Insights:?\s*', re.IGNORECASE)
    
    def validate(self, content: str) -> Tuple[bool, List[ValidationError]]:
        """
        Validate MCQ formatted content.
        
        Args:
            content: The formatted MCQ text to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        lines = content.strip().split('\n')
        
        if not lines:
            errors.append(ValidationError(None, "Empty content"))
            return False, errors
        
        i = 0
        question_count = 0
        
        while i < len(lines):
            # Skip blank lines between questions
            while i < len(lines) and not lines[i].strip():
                i += 1
            
            if i >= len(lines):
                break
                
            # Check if this line is a question title
            if not self.title_pattern.match(lines[i].strip()):
                # If we haven't found any questions yet, this is an error
                if question_count == 0:
                    errors.append(ValidationError(
                        i + 1, 
                        "Invalid format: Content must start with a question title",
                        "Format"
                    ))
                    return False, errors
                else:
                    # Otherwise, we're done processing questions
                    break
                    
            question_start = i
            question_count += 1
            
            # 1. Process title line
            i += 1
            
            # 2. Find and validate vignette (everything before options)
            vignette_found = False
            vignette_lines = []
            while i < len(lines):
                line = lines[i].strip()
                # Check if we've reached the options section
                if self.option_pattern.match(line):
                    break
                # Collect non-empty lines as part of vignette
                if line:
                    vignette_found = True
                    vignette_lines.append(line)
                i += 1
            
            if not vignette_found:
                errors.append(ValidationError(
                    question_start + 2,
                    f"Question {question_count}: Missing vignette/stem",
                    "Vignette"
                ))
            
            # 3. Check options (4-5 required, must be consecutive)
            options_found = []
            option_start = i
            while i < len(lines) and self.option_pattern.match(lines[i].strip()):
                option_letter = lines[i].strip()[0]
                options_found.append(option_letter)
                i += 1
            
            if len(options_found) < 4 or len(options_found) > 5:
                errors.append(ValidationError(
                    option_start + 1,
                    f"Question {question_count}: Found {len(options_found)} options, expected 4-5",
                    "Options"
                ))
            
            # Check for consecutive options
            expected_options = ['A', 'B', 'C', 'D', 'E'][:len(options_found)]
            if options_found != expected_options:
                errors.append(ValidationError(
                    option_start + 1,
                    f"Question {question_count}: Options not in sequence. Found {options_found}",
                    "Options"
                ))
            
            # Skip blank lines
            while i < len(lines) and not lines[i].strip():
                i += 1
            
            # 4. Check correct answer
            correct_answer_found = False
            if i < len(lines) and self.correct_answer_pattern.match(lines[i].strip()):
                correct_answer_found = True
                answer_letter = lines[i].strip()[-1]
                if options_found and answer_letter not in options_found:
                    errors.append(ValidationError(
                        i + 1,
                        f"Question {question_count}: Correct answer '{answer_letter}' not in options",
                        "Answer"
                    ))
                i += 1
            else:
                errors.append(ValidationError(
                    i + 1 if i < len(lines) else None,
                    f"Question {question_count}: Missing or invalid 'Correct Answer:' line",
                    "Answer"
                ))
            
            # Skip blank lines
            while i < len(lines) and not lines[i].strip():
                i += 1
            
            # 5. Check explanation section
            explanation_found = False
            if i < len(lines) and self.explanation_header_pattern.match(lines[i].strip()):
                i += 1
                # Skip blank lines after header
                while i < len(lines) and not lines[i].strip():
                    i += 1
                # Check for explanation content (multi-paragraph allowed)
                if i < len(lines) and lines[i].strip():
                    explanation_found = True
                    # Skip all explanation content until we find Analysis header or Key Insights
                    while i < len(lines):
                        line = lines[i].strip()
                        if line and (self.analysis_header_pattern.match(line) or 
                                    self.key_insights_pattern.match(line)):
                            break
                        i += 1
            
            if not explanation_found:
                errors.append(ValidationError(
                    i + 1 if i < len(lines) else None,
                    f"Question {question_count}: Missing explanation section",
                    "Explanation"
                ))
            
            # Skip blank lines
            while i < len(lines) and not lines[i].strip():
                i += 1
            
            # 6. Check analysis of other options
            analysis_found = False
            if i < len(lines) and self.analysis_header_pattern.match(lines[i].strip()):
                i += 1
                analysis_found = True
                # Skip all analysis content until we find Key Insights or next question
                while i < len(lines):
                    line = lines[i].strip()
                    if line and (self.key_insights_pattern.match(line) or 
                                self.title_pattern.match(line)):
                        break
                    i += 1
            
            if not analysis_found:
                errors.append(ValidationError(
                    i + 1 if i < len(lines) else None,
                    f"Question {question_count}: Missing 'Analysis of Other Options' section",
                    "Analysis"
                ))
            
            # Skip blank lines
            while i < len(lines) and not lines[i].strip():
                i += 1
            
            # 7. Check key insights
            key_insights_found = False
            if i < len(lines) and self.key_insights_pattern.match(lines[i].strip()):
                key_insights_found = True
                i += 1
                # Skip all key insights content until we find next question or end of content
                while i < len(lines):
                    line = lines[i].strip()
                    # If we find a new question title, stop here
                    if line and self.title_pattern.match(line):
                        break
                    i += 1
            
            if not key_insights_found:
                errors.append(ValidationError(
                    i + 1 if i < len(lines) else None,
                    f"Question {question_count}: Missing 'Key Insights' section",
                    "Key Insights"
                ))
        
        return len(errors) == 0, errors


class NMCQValidator:
    """Validator for Non-MCQ (Clinical Vignette) format."""
    
    def __init__(self):
        # Regex patterns for NMCQ validation
        self.title_pattern = re.compile(r'^Clinical Vignette\s+\d+:\s+.+$', re.IGNORECASE)
        self.qa_header_pattern = re.compile(r'^Questions and Answers:\s*$', re.IGNORECASE)
        self.question_pattern = re.compile(
            r'^(\d+)\.\s*(True/False|Yes/No|Drop Down Question[s]?|Drop-?Down(?: Question[s]?)?)\s*:\s*(.+)$',
            re.IGNORECASE
        )
        self.answer_pattern = re.compile(r'^Answer:\s*(.+)$', re.IGNORECASE)
        self.explanation_pattern = re.compile(r'^Explanation:\s*(.+)$', re.IGNORECASE)
    
    def validate(self, content: str) -> Tuple[bool, List[ValidationError]]:
        """
        Validate NMCQ formatted content.
        
        Args:
            content: The formatted NMCQ text to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        lines = content.strip().split('\n')
        
        if not lines:
            errors.append(ValidationError(None, "Empty content"))
            return False, errors
        
        i = 0
        vignette_count = 0
        
        while i < len(lines):
            # Skip blank lines
            while i < len(lines) and not lines[i].strip():
                i += 1
            
            if i >= len(lines):
                break
            
            vignette_start = i
            vignette_count += 1
            
            # 1. Check title line
            if not self.title_pattern.match(lines[i].strip()):
                errors.append(ValidationError(
                    i + 1,
                    f"Vignette {vignette_count}: Invalid title format. Expected 'Clinical Vignette N: Title'",
                    "Title"
                ))
            i += 1
            
            # 2. Check vignette body (at least one non-empty line)
            vignette_found = False
            while i < len(lines):
                line = lines[i].strip()
                if self.qa_header_pattern.match(line) or self.question_pattern.match(line):
                    break
                if line:
                    vignette_found = True
                i += 1
            
            if not vignette_found:
                errors.append(ValidationError(
                    vignette_start + 2,
                    f"Vignette {vignette_count}: Missing vignette body",
                    "Body"
                ))
            
            # 3. Check for Questions and Answers header (optional)
            if i < len(lines) and self.qa_header_pattern.match(lines[i].strip()):
                i += 1
            
            # Skip blank lines
            while i < len(lines) and not lines[i].strip():
                i += 1
            
            # 4. Check questions
            question_count = 0
            while i < len(lines):
                # Check if this is the start of a new vignette
                if self.title_pattern.match(lines[i].strip()):
                    break
                
                # Skip blank lines
                while i < len(lines) and not lines[i].strip():
                    i += 1
                    
                if i >= len(lines) or self.title_pattern.match(lines[i].strip()):
                    break
                
                # Check for question
                match = self.question_pattern.match(lines[i].strip())
                if match:
                    question_count += 1
                    q_num = match.group(1)
                    q_type = match.group(2).lower()
                    q_text = match.group(3)
                    
                    if int(q_num) != question_count:
                        errors.append(ValidationError(
                            i + 1,
                            f"Vignette {vignette_count}, Question numbering error: expected {question_count}, got {q_num}",
                            "Question"
                        ))
                    
                    i += 1
                    
                    # For Drop Down questions, check for options
                    options_found = []
                    if 'drop' in q_type.lower():
                        # Look for options
                        while i < len(lines):
                            line = lines[i].strip()
                            if self.answer_pattern.match(line) or self.question_pattern.match(line):
                                break
                            if line and not line.startswith('Options:'):
                                options_found.append(line)
                            elif line.startswith('Options:'):
                                # Parse comma-separated options
                                opts = line[8:].strip()
                                options_found.extend([o.strip() for o in re.split(r'[,|]', opts)])
                                i += 1
                                break
                            if line:
                                i += 1
                            else:
                                i += 1
                                break
                        
                        if len(options_found) < 2:
                            errors.append(ValidationError(
                                i,
                                f"Vignette {vignette_count}, Question {question_count}: Drop Down requires at least 2 options",
                                "Options"
                            ))
                    
                    # Check for Answer
                    answer_found = False
                    if i < len(lines):
                        match_answer = self.answer_pattern.match(lines[i].strip())
                        if match_answer:
                            answer_found = True
                            answer_value = match_answer.group(1).strip()
                            
                            # Validate answer based on question type
                            if 'true/false' in q_type.lower():
                                if answer_value not in ['True', 'False']:
                                    errors.append(ValidationError(
                                        i + 1,
                                        f"Vignette {vignette_count}, Question {question_count}: True/False answer must be 'True' or 'False'",
                                        "Answer"
                                    ))
                            elif 'yes/no' in q_type.lower():
                                if answer_value not in ['Yes', 'No']:
                                    errors.append(ValidationError(
                                        i + 1,
                                        f"Vignette {vignette_count}, Question {question_count}: Yes/No answer must be 'Yes' or 'No'",
                                        "Answer"
                                    ))
                            i += 1
                    
                    if not answer_found:
                        errors.append(ValidationError(
                            i,
                            f"Vignette {vignette_count}, Question {question_count}: Missing Answer",
                            "Answer"
                        ))
                    
                    # Check for Explanation
                    explanation_found = False
                    if i < len(lines):
                        match_exp = self.explanation_pattern.match(lines[i].strip())
                        if match_exp:
                            exp_text = match_exp.group(1).strip()
                            if exp_text:
                                explanation_found = True
                            i += 1
                            # Skip multi-line explanations
                            while i < len(lines) and lines[i].strip() and \
                                  not self.question_pattern.match(lines[i].strip()) and \
                                  not self.title_pattern.match(lines[i].strip()):
                                i += 1
                    
                    if not explanation_found:
                        errors.append(ValidationError(
                            i,
                            f"Vignette {vignette_count}, Question {question_count}: Missing or empty Explanation",
                            "Explanation"
                        ))
                else:
                    # If we can't parse it as a question and it's not a title, skip it
                    if not self.title_pattern.match(lines[i].strip()):
                        i += 1
                    else:
                        break
            
            if question_count == 0:
                errors.append(ValidationError(
                    vignette_start + 3,
                    f"Vignette {vignette_count}: No questions found",
                    "Questions"
                ))
        
        return len(errors) == 0, errors


class SummaryValidator:
    """Validator for Summary Bytes content."""
    
    def __init__(self):
        # More flexible patterns to match various formats
        # Pattern to match numbered headers - can be "1. Summary Block:" or just "1." followed by title
        self.header_pattern = re.compile(r'^\d+\..*', re.IGNORECASE)
        # Pattern to match "High Yield Points:" with or without bullets
        self.high_yield_pattern = re.compile(r'^[•\-\s]*High\s+Yield\s+Points\s*:?', re.IGNORECASE)
        # Pattern to match "Additional Concepts:" with or without bullets
        self.additional_pattern = re.compile(r'^[•\-\s]*Additional\s+Concepts\s*:?', re.IGNORECASE)
        # Pattern to match "Key Insights:" with or without bullets
        self.key_insights_pattern = re.compile(r'^[•\-\s]*Key\s+Insights\s*:?', re.IGNORECASE)
    
    def validate(self, content: str) -> Tuple[bool, List[ValidationError]]:
        """
        Validate Summary Bytes format.
        More flexible validation to handle various formatter outputs.
        Expected format (flexible):
        1. [Some title or Summary Block: Title]
        High Yield Points:
          - [points]
        Additional Concepts:
          - [concepts]  
        Key Insights:
          [paragraph]
        """
        if not content or not content.strip():
            return False, [ValidationError(0, "Empty content", "Content")]
        
        lines = content.strip().split('\n')
        errors = []
        summary_count = 0
        
        # Convert content to lowercase for searching
        content_lower = content.lower()
        
        # Check if we have any numbered items (indicates summary blocks)
        has_numbered_items = any(re.match(r'^\s*\d+\.', line) for line in lines)
        
        # Check for the presence of key sections in the entire content
        has_high_yield = 'high yield' in content_lower
        has_key_insights = 'key insight' in content_lower
        
        # If we have the key sections, consider it valid structure
        if has_high_yield and has_key_insights:
            # Count how many summary blocks we have by looking for numbered items
            for line in lines:
                if re.match(r'^\s*\d+\.', line):
                    summary_count += 1
            
            # If no numbered items but we have the sections, still count as at least one
            if summary_count == 0 and has_high_yield:
                summary_count = 1
            
            # Do a more detailed check for each block
            i = 0
            current_block = 0
            
            while i < len(lines):
                line = lines[i].strip()
                
                # Check for numbered header
                if re.match(r'^\s*\d+\.', line):
                    current_block += 1
                    header_line = i
                    
                    # Look ahead for required sections within this block
                    block_end = len(lines)
                    for j in range(i + 1, len(lines)):
                        if re.match(r'^\s*\d+\.', lines[j]):
                            block_end = j
                            break
                    
                    # Check for High Yield Points in this block
                    block_text = '\n'.join(lines[i:block_end])
                    block_lower = block_text.lower()
                    
                    if 'high yield' not in block_lower:
                        errors.append(ValidationError(
                            header_line,
                            f"Summary Block {current_block}: Missing High Yield Points section",
                            "High Yield Points"
                        ))
                    
                    if 'key insight' not in block_lower:
                        errors.append(ValidationError(
                            header_line,
                            f"Summary Block {current_block}: Missing Key Insights section",
                            "Key Insights"
                        ))
                    
                    # Check if Key Insights has content
                    key_insights_index = block_lower.find('key insight')
                    if key_insights_index != -1:
                        # Look for content after Key Insights
                        remaining_text = block_text[key_insights_index + 11:].strip()
                        # Remove the colon if present
                        if remaining_text.startswith(':'):
                            remaining_text = remaining_text[1:].strip()
                        
                        # Check if there's meaningful content (more than just whitespace or separators)
                        if not remaining_text or len(remaining_text) < 20:
                            errors.append(ValidationError(
                                header_line,
                                f"Summary Block {current_block}: Key Insights appears empty or too short",
                                "Key Insights"
                            ))
                
                i += 1
        else:
            # If we don't have the basic structure, report the missing elements
            if not has_high_yield:
                errors.append(ValidationError(
                    0,
                    "No 'High Yield Points' sections found in content",
                    "Structure"
                ))
            
            if not has_key_insights:
                errors.append(ValidationError(
                    0,
                    "No 'Key Insights' sections found in content",
                    "Structure"
                ))
            
            if not has_numbered_items and not has_high_yield:
                errors.append(ValidationError(
                    0,
                    "No Summary Blocks found in content (looking for numbered sections or High Yield Points)",
                    "Structure"
                ))
        
        # If we found no summary blocks at all, report it
        if summary_count == 0 and len(errors) == 0:
            # If there are no errors yet but no blocks found, be more lenient
            # Just check if the content has the right keywords
            if has_high_yield and has_key_insights:
                # Content has the right sections, just not numbered - that's okay
                pass
            else:
                errors.append(ValidationError(
                    0,
                    "No properly formatted Summary Blocks found in content",
                    "Structure"
                ))
        
        return len(errors) == 0, errors


def validate_content(content: str, content_type: str) -> Tuple[bool, List[ValidationError]]:
    """
    Main validation function.
    
    Args:
        content: The formatted content to validate
        content_type: Either 'MCQ', 'NMCQ', or 'SUMMARY'
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    if content_type.upper() == 'MCQ':
        validator = MCQValidator()
    elif content_type.upper() == 'NMCQ':
        validator = NMCQValidator()
    elif content_type.upper() == 'SUMMARY':
        validator = SummaryValidator()
    else:
        return False, [ValidationError(None, f"Invalid content type: {content_type}")]
    
    return validator.validate(content)
