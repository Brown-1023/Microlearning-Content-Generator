"""
Comprehensive test file for MCQ validator
Tests various formats to ensure proper validation
"""

from validators import MCQValidator

# Test 1: Original problematic MCQ with multi-paragraph sections
test_mcq_1 = """Question 1--VITT diagnosis post-vaccine, next step
A 42-year-old woman presents to the emergency department with severe headache, nausea, and blurred vision that began 7 days after receiving her first dose of an adenoviral-vectored COVID-19 vaccine. She has no prior history of thrombotic events and takes no medications. Physical examination reveals papilledema on fundoscopic examination. Laboratory studies show: platelet count 45,000/microL (normal 150,000-400,000/microL), hemoglobin 13.2 g/dL, white blood cell count 8,500/microL, D-dimer 15.2 mg/L (normal <0.5 mg/L), fibrinogen 185 mg/dL (normal 200-400 mg/dL), and normal PT/INR and aPTT. MRI with venography confirms cerebral venous sinus thrombosis. A rapid HIT immunoassay (lateral flow assay) is negative. The patient has never received heparin products.

Which of the following is the most appropriate next step in establishing the diagnosis?

A) Repeat rapid HIT assay in 48 hours
B) Order PF4 antibody ELISA testing
C) Proceed with lupus anticoagulant panel
D) Obtain factor V Leiden mutation testing
E) Perform bone marrow biopsy immediately

Correct Answer: B

Explanation of the Correct Answer:

B) Order PF4 antibody ELISA testing is the most appropriate next step. This patient presents with a classic constellation of findings for vaccine-induced immune thrombotic thrombocytopenia (VITT). The window between vaccination and development of symptoms was approximately 5 to 10 days in most cases, which precisely matches this patient's 7-day timeline. Her platelet count of 45,000/microL falls within the typical platelet count range of patients with definite VITT of 10,000 to 100,000/microL; median platelet counts were generally <50,000/microL. The markedly elevated D-dimer of 15.2 mg/L often greatly exceeds 10 mg/L, and cerebral venous sinus thrombosis represents one of the characteristic unusual thrombosis sites. PF4 antibody testing using ELISA (enzyme-linked immunosorbent assay) is part of the diagnostic laboratory testing for VITT. Most critically, rapid HIT assays are generally negative in VITT and should not be used to confirm or exclude the diagnosis due to poor sensitivity, making PF4 ELISA the definitive next diagnostic step. VITT and VITT-like disorders are caused by antibodies that recognize platelet factor 4 (PF4), establishing PF4 antibody detection as the cornerstone of diagnosis.

Analysis of Other Options (Distractors):

A) Repeat rapid HIT assay in 48 hours is not the best choice because rapid HIT assays are generally negative in VITT and should not be used to confirm or exclude the diagnosis due to poor sensitivity. Repeating a test with poor sensitivity for this condition would delay appropriate diagnosis and treatment. The negative rapid HIT assay in this clinical context is expected and does not rule out VITT.

C) Proceed with lupus anticoagulant panel is not the best choice because while antiphospholipid syndrome can cause thrombosis and thrombocytopenia, the temporal relationship to vaccination (7 days post-adenoviral vaccine), the specific thrombosis location (CVT), and the extremely elevated D-dimer are classic for VITT rather than antiphospholipid syndrome. Testing for lupus anticoagulant would not address the most likely diagnosis given the clinical presentation and would delay appropriate VITT-specific management.

D) Obtain factor V Leiden mutation testing is not the best choice because inherited thrombophilias like factor V Leiden do not cause acute thrombocytopenia or the dramatically elevated D-dimer levels seen in this patient. The temporal association with vaccination and the acute presentation with thrombocytopenia make an inherited thrombophilia an unlikely primary explanation. This testing would be more appropriate for evaluation of unprovoked thrombosis without the acute features present here.

E) Perform bone marrow biopsy immediately is not the best choice because bone marrow biopsy is not indicated in the acute diagnostic evaluation of suspected VITT. The thrombocytopenia in VITT is immune-mediated (caused by antibody-induced platelet activation and consumption), not due to bone marrow failure or infiltration. The pathophysiology involves antibodies forming multimolecular complexes on platelet surfaces that activate platelets via low affinity platelet FcγIIa receptors, indicating a peripheral consumptive process rather than a production problem requiring bone marrow evaluation.

Key Insights: VITT should be strongly suspected when thrombocytopenia (platelet count 10,000-100,000/microL), unusual site thrombosis (especially CVT), and markedly elevated D-dimer (>10 mg/L) occur 5-10 days after adenoviral-vectored COVID-19 vaccination. Rapid HIT immunoassays have poor sensitivity for VITT and are generally negative; they should not be used to confirm or exclude the diagnosis. PF4 antibody ELISA testing is the appropriate diagnostic modality. Prompt recognition and confirmation of VITT through PF4 antibody testing is critical because management includes specific interventions (therapeutic anticoagulation, IVIG, avoidance of platelet transfusions except for critical bleeding) that differ from standard thrombocytopenia or thrombosis management."""

# Test 2: MCQ with different title format
test_mcq_2 = """Question 2 - Diabetes Management
A patient with Type 2 diabetes presents with poor glycemic control.

A) Increase insulin dose
B) Add metformin
C) Lifestyle modifications
D) Check HbA1c

Answer: C

Explanation:
Lifestyle modifications are the first-line treatment for Type 2 diabetes.

Analysis of Other Options:
A) Increasing insulin may lead to hypoglycemia.
B) Metformin is useful but not first-line.
D) HbA1c is for monitoring, not treatment.

Key Insights: Always start with lifestyle modifications in Type 2 diabetes management."""

# Test 3: MCQ with "Analysis of the Other Options" (with "the")
test_mcq_3 = """Question 3 - Heart Failure Management
A 65-year-old patient with heart failure presents with dyspnea.

A) Diuretics
B) ACE inhibitors
C) Beta-blockers
D) Digoxin

Correct Answer: A

Explanation of the Correct Answer:
Diuretics are the first-line treatment for symptomatic heart failure.

Analysis of the Other Options (Distractors):
B) ACE inhibitors are for long-term management.
C) Beta-blockers should be started when stable.
D) Digoxin is reserved for specific cases.

Key Insights: Symptomatic relief with diuretics is the priority."""

# Test 4: MCQ with just "Distractors:" header
test_mcq_4 = """Question 4 - Asthma Exacerbation
A child presents with acute asthma exacerbation.

A) Oral steroids
B) Short-acting beta-agonists
C) Long-acting beta-agonists
D) Antibiotics

Correct Answer: B

Explanation:
Short-acting beta-agonists provide immediate bronchodilation.

Distractors:
A) Steroids take time to work.
C) Long-acting agents are for maintenance.
D) Antibiotics are not indicated unless infection is present.

Key Insights: Quick relief is the priority in acute exacerbations."""

# Test 5: Multiple MCQs in one content
test_mcq_multiple = """Question 1 - Hypertension
A patient with newly diagnosed hypertension.

A) ACE inhibitors
B) Beta-blockers
C) Calcium channel blockers
D) Diuretics

Answer: A

Explanation:
ACE inhibitors are first-line for most patients.

Analysis of Other Options:
B) Beta-blockers for specific indications.
C) CCBs are alternative first-line.
D) Diuretics are good for elderly.

Key Insights: Consider patient factors when choosing antihypertensives.

Question 2 - Pneumonia Treatment
Patient with community-acquired pneumonia.

A) Amoxicillin
B) Azithromycin
C) Ciprofloxacin
D) Vancomycin

Correct Answer: A

Explanation of the Correct Answer:
Amoxicillin is first-line for CAP in many guidelines.

Analysis of Other Options (Distractors):
B) Azithromycin for atypical coverage.
C) Ciprofloxacin not first-line.
D) Vancomycin for MRSA only.

Key Insights: Choose antibiotics based on local resistance patterns."""

def test_mcq_validation(test_name, mcq_content, expected_valid=True):
    """Test MCQ validation and print results"""
    print(f"\n{'='*50}")
    print(f"Testing: {test_name}")
    print(f"{'='*50}")
    
    validator = MCQValidator()
    is_valid, errors = validator.validate(mcq_content)
    
    print(f"Expected: {'VALID' if expected_valid else 'INVALID'}")
    print(f"Result: {'VALID' if is_valid else 'INVALID'}")
    
    if errors:
        print(f"\nFound {len(errors)} errors:")
        for error in errors:
            if error.line_number:
                print(f"  Line {error.line_number}: {error.message}")
            else:
                print(f"  Line N/A: {error.message}")
    else:
        print("No errors found!")
    
    # Check if result matches expectation
    if (is_valid and expected_valid) or (not is_valid and not expected_valid):
        print(">> Test PASSED")
    else:
        print(">> Test FAILED")
    
    return is_valid == expected_valid

def run_all_tests():
    """Run all validation tests"""
    results = []
    
    # Test valid MCQs
    results.append(test_mcq_validation("MCQ with multi-paragraph sections", test_mcq_1, True))
    results.append(test_mcq_validation("MCQ with simple format", test_mcq_2, True))
    results.append(test_mcq_validation("MCQ with 'the' in analysis header", test_mcq_3, True))
    results.append(test_mcq_validation("MCQ with 'Distractors' header", test_mcq_4, True))
    results.append(test_mcq_validation("Multiple MCQs", test_mcq_multiple, True))
    
    # Test invalid MCQ
    invalid_mcq = """This is not a valid MCQ format.
It doesn't have proper structure."""
    results.append(test_mcq_validation("Invalid MCQ format", invalid_mcq, False))
    
    # Print summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print(f"{'='*50}")
    passed = sum(results)
    total = len(results)
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print(">> ALL TESTS PASSED!")
    else:
        print(f">> {total - passed} tests failed")
    
    return passed == total

if __name__ == "__main__":
    all_passed = run_all_tests()
    exit(0 if all_passed else 1)
