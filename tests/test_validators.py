"""
Unit tests for validators as per Milestone 1 requirements.
"""

import pytest
from validators import MCQValidator, NMCQValidator, validate_content, ValidationError


class TestMCQValidator:
    """Unit tests for MCQ validator."""
    
    def test_valid_mcq_format(self):
        """Test a properly formatted MCQ passes validation."""
        content = """Question 1 - Test Question
This is a clinical vignette that ends with a question?

A) First option
B) Second option  
C) Third option
D) Fourth option

Correct Answer: B

Explanation of the Correct Answer:
This explains why B is the correct answer.

Analysis of Other Options:
A) Why option A is incorrect
C) Why option C is incorrect
D) Why option D is incorrect

Key Insights: This is the key learning point from this question."""
        
        validator = MCQValidator()
        is_valid, errors = validator.validate(content)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_accepts_answer_variations(self):
        """Test validator accepts both 'Answer:' and 'Correct Answer:' as per requirements."""
        # Test with "Answer:" format
        content1 = """Question 1 - Test
Vignette?

A) Option A
B) Option B
C) Option C
D) Option D

Answer: A

Explanation:
Explanation text.

Analysis of Other Options:
B) Analysis

Key Insights: Point."""
        
        # Test with "Correct Answer:" format
        content2 = content1.replace("Answer:", "Correct Answer:")
        
        validator = MCQValidator()
        
        is_valid1, errors1 = validator.validate(content1)
        is_valid2, errors2 = validator.validate(content2)
        
        assert is_valid1 is True
        assert is_valid2 is True
    
    def test_accepts_option_format_variations(self):
        """Test validator accepts both A) and A. option formats."""
        content = """Question 1 - Test
Vignette?

A. Option A
B. Option B
C. Option C
D. Option D

Correct Answer: A

Explanation:
Text.

Analysis of Other Options:
B. Analysis

Key Insights: Point."""
        
        validator = MCQValidator()
        is_valid, errors = validator.validate(content)
        
        assert is_valid is True


class TestNMCQValidator:
    """Unit tests for NMCQ validator."""
    
    def test_valid_nmcq_format(self):
        """Test a properly formatted NMCQ passes validation."""
        content = """Clinical Vignette 1: Test Case
A patient presents with symptoms.

Questions and Answers:

1. True/False: Is this a true/false question?
Answer: True
Explanation: This explains the answer.

2. Yes/No: Is this a yes/no question?
Answer: No  
Explanation: This explains why.

3. Drop Down Question: Select the best option
Option A
Option B
Option C
Answer: Option B
Explanation: Why B is correct."""
        
        validator = NMCQValidator()
        is_valid, errors = validator.validate(content)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_dropdown_variations(self):
        """Test dropdown accepts variations like 'Drop-Down' or 'Drop Down Questions'."""
        content = """Clinical Vignette 1: Test
Scenario.

1. Drop-Down Question: Select one
Option A
Option B
Answer: Option A
Explanation: Explanation."""
        
        validator = NMCQValidator()
        is_valid, errors = validator.validate(content)
        
        assert is_valid is True


class TestGoldenSamples:
    """Golden tests with provided samples."""
    
    def test_mcq_golden_sample(self):
        """Test with golden MCQ sample from docs."""
        # This would use actual samples from the docs
        sample = """Question 1 - VITT Diagnosis
A 34-year-old woman presents with severe headache 10 days after adenovirus infection. Labs show platelets 45,000/microL, D-dimer 12,500 ng/mL. What is the most appropriate diagnostic test?

A) ADAMTS13 activity level
B) Rapid HIT assay
C) PF4/polyanion ELISA
D) Bone marrow biopsy

Correct Answer: C

Explanation of the Correct Answer:
PF4/polyanion ELISA is the recommended initial test for VITT-like disorders.

Analysis of Other Options:
A) ADAMTS13 is for TTP diagnosis
B) Rapid HIT assays have poor sensitivity for VITT
D) Bone marrow biopsy is not indicated

Key Insights: VITT requires specific PF4 antibody testing, not rapid HIT assays."""
        
        is_valid, errors = validate_content(sample, "MCQ")
        assert is_valid is True
    
    def test_nmcq_golden_sample(self):
        """Test with golden NMCQ sample from docs."""
        sample = """Clinical Vignette 1: Lymphocytosis Case
A 22-year-old presents with fever and atypical lymphocytes.

Questions and Answers:

1. True/False: Atypical lymphocytes are diagnostic of EBV.
Answer: False
Explanation: Can be seen in other viral infections too.

2. Yes/No: Is flow cytometry required initially?
Answer: No
Explanation: Clinical picture suggests reactive process."""
        
        is_valid, errors = validate_content(sample, "NMCQ")
        assert is_valid is True


class TestNegativeCases:
    """Negative test cases."""
    
    def test_empty_content(self):
        """Test empty content fails validation."""
        is_valid, errors = validate_content("", "MCQ")
        assert is_valid is False
        assert len(errors) > 0
    
    def test_invalid_content_type(self):
        """Test invalid content type."""
        is_valid, errors = validate_content("Some content", "INVALID")
        assert is_valid is False
        assert any("invalid content type" in e.message.lower() for e in errors)
    
    def test_missing_required_sections(self):
        """Test missing required sections fails validation."""
        # MCQ without Key Insights
        incomplete_mcq = """Question 1 - Test
Stem?

A) A
B) B
C) C
D) D

Correct Answer: A"""
        
        is_valid, errors = validate_content(incomplete_mcq, "MCQ")
        assert is_valid is False
        assert any("explanation" in e.message.lower() for e in errors)
