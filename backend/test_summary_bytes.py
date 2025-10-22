"""
Test script for Summary Bytes generation feature.
"""

import os
import json
import requests
from pathlib import Path

# Test configuration
BASE_URL = "http://localhost:4000"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")

# Sample Hematology/Oncology content for testing Summary Bytes
SAMPLE_CONTENT = """
VITAMIN B12 AND FOLATE DEFICIENCY

Vitamin B12 (cobalamin) and folate deficiencies are common causes of megaloblastic anemia. Understanding their pathophysiology, diagnosis, and management is crucial for hematology practice.

PATHOPHYSIOLOGY
Both deficiencies impair DNA synthesis, leading to megaloblastic changes:
- B12 is essential for methylmalonyl-CoA mutase and methionine synthase
- Folate functions in one-carbon transfer reactions for nucleotide synthesis
- Deficiency causes ineffective erythropoiesis and pancytopenia
- Neurological complications unique to B12 deficiency (subacute combined degeneration)

CAUSES
B12 Deficiency:
- Pernicious anemia (anti-intrinsic factor antibodies)
- Malabsorption (celiac disease, Crohn's, gastric surgery)
- Dietary insufficiency (strict vegans)
- Medications (metformin, PPIs)

Folate Deficiency:
- Inadequate dietary intake
- Increased requirements (pregnancy, hemolysis)
- Malabsorption (celiac disease)
- Medications (methotrexate, trimethoprim)

DIAGNOSIS
Laboratory findings:
- Macrocytic anemia (MCV >100 fL)
- Hypersegmented neutrophils
- Low B12 (<200 pg/mL) or folate (<2 ng/mL)
- Elevated methylmalonic acid (B12 deficiency specific)
- Elevated homocysteine (both deficiencies)
- Anti-intrinsic factor antibodies for pernicious anemia

TREATMENT
B12 Deficiency:
- Parenteral: 1000 mcg IM daily x 1 week, then weekly x 4, then monthly
- High-dose oral: 1000-2000 mcg daily (even for pernicious anemia)
- Neurologic symptoms may be irreversible if treatment delayed

Folate Deficiency:
- Oral folate 1-5 mg daily
- Always rule out B12 deficiency first (folate can mask B12 deficiency)
- Continue supplementation for 4 months after correction
"""


class TestSummaryBytes:
    """Test Summary Bytes functionality."""
    
    def __init__(self):
        self.token = None
        self.session = requests.Session()
    
    def login(self):
        """Login as admin and get token."""
        response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"password": ADMIN_PASSWORD}
        )
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("token")
            print(f"✅ Login successful as {data.get('role')}")
            return True
        else:
            print(f"❌ Login failed: {response.status_code}")
            return False
    
    def test_summary_generation(self):
        """Test Summary Bytes generation."""
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Test parameters
        params = {
            "content_type": "SUMMARY",
            "generator_model": "gemini-2.5-pro",  # or claude-sonnet-4-5-20250929
            "input_text": SAMPLE_CONTENT,
            "num_questions": 2,  # Generate 2 Summary Bytes
            "focus_areas": "diagnosis and treatment"
        }
        
        print("\n📊 Testing Summary Bytes Generation")
        print("-" * 40)
        print(f"Model: {params['generator_model']}")
        print(f"Number of Summary Bytes: {params['num_questions']}")
        print(f"Focus Areas: {params['focus_areas']}")
        
        # Make request
        response = self.session.post(
            f"{BASE_URL}/run",
            json=params,
            headers=headers,
            timeout=120  # 2 minutes timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success"):
                print("\n✅ Summary Bytes generated successfully!")
                
                # Display formatted output
                if result.get("formatted_output"):
                    print("\n" + "="*50)
                    print("GENERATED SUMMARY BYTES:")
                    print("="*50)
                    print(result["formatted_output"])
                    print("="*50)
                
                # Display metadata
                if result.get("metadata"):
                    metadata = result["metadata"]
                    print("\n📊 Generation Metadata:")
                    print(f"  - Total time: {metadata.get('total_time', 0):.2f}s")
                    print(f"  - Generator model: {metadata.get('generator_model')}")
                    print(f"  - Formatter retries: {metadata.get('formatter_retries', 0)}")
                    
                    if metadata.get("model_latencies"):
                        print(f"  - Generator latency: {metadata['model_latencies'].get('generator', 0):.2f}s")
                        print(f"  - Formatter latency: {metadata['model_latencies'].get('formatter', 0):.2f}s")
                
                # Check for validation errors
                if result.get("validation_errors"):
                    print("\n⚠️ Validation errors found:")
                    for error in result["validation_errors"]:
                        print(f"  - Line {error.get('line_number')}: {error.get('message')}")
                else:
                    print("\n✅ No validation errors - content is properly formatted!")
                
                return True
            else:
                print(f"\n❌ Generation failed: {result.get('error')}")
                return False
        else:
            print(f"\n❌ Request failed: {response.status_code}")
            if response.text:
                print(f"Error: {response.text}")
            return False
    
    def test_prompt_templates(self):
        """Test that Summary prompt templates are available."""
        headers = {"Authorization": f"Bearer {self.token}"}
        
        print("\n📝 Testing Summary Prompt Templates")
        print("-" * 40)
        
        response = self.session.get(
            f"{BASE_URL}/api/prompts",
            headers=headers
        )
        
        if response.status_code == 200:
            prompts = response.json()
            
            # Check for Summary prompts
            has_generator = "summary_generator" in prompts and prompts["summary_generator"]
            has_formatter = "summary_formatter" in prompts and prompts["summary_formatter"]
            
            if has_generator:
                print("✅ Summary generator prompt found")
                print(f"   Length: {len(prompts['summary_generator'])} characters")
            else:
                print("❌ Summary generator prompt missing")
            
            if has_formatter:
                print("✅ Summary formatter prompt found")
                print(f"   Length: {len(prompts['summary_formatter'])} characters")
            else:
                print("❌ Summary formatter prompt missing")
            
            return has_generator and has_formatter
        else:
            print(f"❌ Failed to fetch prompts: {response.status_code}")
            return False
    
    def run_all_tests(self):
        """Run all Summary Bytes tests."""
        print("\n" + "="*50)
        print("TESTING SUMMARY BYTES FEATURE")
        print("="*50)
        
        # Step 1: Login
        print("\n1. Authentication")
        print("-" * 30)
        if not self.login():
            print("⚠️  Login failed - check ADMIN_PASSWORD")
            return
        
        # Step 2: Check prompt templates
        print("\n2. Prompt Templates")
        print("-" * 30)
        prompts_ok = self.test_prompt_templates()
        
        if not prompts_ok:
            print("⚠️  Summary prompt templates not found!")
            print("   Please ensure the prompt files exist in backend/prompts/")
        
        # Step 3: Test generation
        print("\n3. Summary Bytes Generation")
        print("-" * 30)
        generation_ok = self.test_summary_generation()
        
        # Summary
        print("\n" + "="*50)
        print("TEST SUMMARY")
        print("="*50)
        
        if prompts_ok and generation_ok:
            print("✅ All tests passed! Summary Bytes feature is working correctly.")
        else:
            print("⚠️  Some tests failed. Please review the output above.")


def main():
    """Run the test suite."""
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/healthz")
        if response.status_code != 200:
            print("❌ Server not responding at", BASE_URL)
            print("   Please start the backend server first")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server at", BASE_URL)
        print("   Please start the backend server with: python backend/run.py")
        return
    
    # Check password is set
    if not ADMIN_PASSWORD:
        print("⚠️  Please set ADMIN_PASSWORD environment variable")
        print("   Or update it in the script")
        return
    
    # Run tests
    tester = TestSummaryBytes()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
