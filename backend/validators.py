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
        self.analysis_header_pattern = re.compile(
            r'^(?:Analysis of the Other Options \(Distractors\)|Analysis of Other Options|Distractors):?\s*$', 
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
                
            question_start = i
            question_count += 1
            
            # 1. Check title line
            if not self.title_pattern.match(lines[i].strip()):
                errors.append(ValidationError(
                    i + 1, 
                    f"Question {question_count}: Invalid title format. Expected 'Question N - Title'",
                    "Title"
                ))
            i += 1
            
            # 2. Check vignette (at least one non-empty line before options)
            vignette_found = False
            vignette_lines = 0
            while i < len(lines):
                line = lines[i].strip()
                if self.option_pattern.match(line):
                    break
                if line:
                    vignette_found = True
                    vignette_lines += 1
                i += 1
            
            if not vignette_found:
                errors.append(ValidationError(
                    question_start + 2,
                    f"Question {question_count}: Missing vignette/stem",
                    "Vignette"
                ))
            
            # 3. Check options (4-5 required)
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
            if i < len(lines) and self.correct_answer_pattern.match(lines[i].strip()):
                answer_letter = lines[i].strip()[-1]
                if answer_letter not in options_found:
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
            
            # 5. Check explanation header and content
            explanation_found = False
            if i < len(lines) and self.explanation_header_pattern.match(lines[i].strip()):
                i += 1
                # Check for explanation content
                if i < len(lines) and lines[i].strip():
                    explanation_found = True
                    # Skip explanation lines
                    while i < len(lines) and lines[i].strip() and \
                          not self.analysis_header_pattern.match(lines[i].strip()):
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
                # Skip analysis content
                while i < len(lines) and lines[i].strip() and \
                      not self.key_insights_pattern.match(lines[i].strip()):
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
                # Skip key insights content
                while i < len(lines) and lines[i].strip() and \
                      not self.title_pattern.match(lines[i].strip()):
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


def validate_content(content: str, content_type: str) -> Tuple[bool, List[ValidationError]]:
    """
    Main validation function.
    
    Args:
        content: The formatted content to validate
        content_type: Either 'MCQ' or 'NMCQ'
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    if content_type.upper() == 'MCQ':
        validator = MCQValidator()
    elif content_type.upper() == 'NMCQ':
        validator = NMCQValidator()
    else:
        return False, [ValidationError(None, f"Invalid content type: {content_type}")]
    
    return validator.validate(content)
