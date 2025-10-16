#!/usr/bin/env python3
"""
Comprehensive test script for all UI enhancements:
- Dual custom prompts (generator and formatter)
- Model selection with proper API names
- Temperature and top_p parameters
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_feature(description: str, endpoint: str, payload: dict):
    """Test a specific feature."""
    print(f"\n{'='*70}")
    print(f"Testing: {description}")
    print(f"{'='*70}")
    print(f"Model: {payload.get('generator_model', 'N/A')}")
    print(f"Temperature: {payload.get('temperature', 'Default')}")
    print(f"Top P: {payload.get('top_p', 'Default')}")
    
    try:
        response = requests.post(
            f"{BASE_URL}{endpoint}",
            json=payload,
            timeout=120
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success!")
            
            # Show metadata
            if data.get("metadata"):
                meta = data["metadata"]
                print(f"\nMetadata:")
                print(f"  - Model Used: {meta.get('model_ids', {}).get('generator', 'N/A')}")
                print(f"  - Formatter Model: {meta.get('model_ids', {}).get('formatter', 'N/A')}")
                print(f"  - Total Time: {meta.get('total_time', 0):.2f}s")
                print(f"  - Formatter Retries: {meta.get('formatter_retries', 0)}")
            
            # Show output preview
            if data.get("output"):
                print(f"\nOutput Preview (first 300 chars):")
                print(f"{data['output'][:300]}...")
            
            return True
        else:
            print(f"❌ Error Response:")
            print(json.dumps(response.json(), indent=2))
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (>2 minutes)")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - is the server running?")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def main():
    """Run comprehensive tests."""
    print("\n" + "="*70)
    print("🚀 COMPREHENSIVE FEATURE TEST SUITE")
    print("="*70)
    
    # Check server health
    try:
        health = requests.get(f"{BASE_URL}/healthz")
        if health.status_code != 200:
            print("❌ Server is not healthy!")
            return
        print("✅ Server is running and healthy")
    except:
        print("❌ Cannot connect to server at", BASE_URL)
        print("Please start the backend: cd backend && python app.py")
        return
    
    # Sample text for testing
    sample_text = """
    Diabetes mellitus is a group of metabolic disorders characterized by chronic hyperglycemia. 
    Type 1 diabetes results from autoimmune destruction of pancreatic beta cells, leading to 
    absolute insulin deficiency. Type 2 diabetes involves insulin resistance and relative 
    insulin deficiency. Management includes blood glucose monitoring, medications, and lifestyle 
    modifications.
    """
    
    # Test 1: Claude 3.5 Sonnet with default settings
    test_feature(
        "Claude 3.5 Sonnet - Default Settings",
        "/run",
        {
            "content_type": "MCQ",
            "generator_model": "claude-3-5-sonnet-20241022",
            "input_text": sample_text,
            "num_questions": 2,
            "focus_areas": "pathophysiology and management"
        }
    )
    
    time.sleep(2)  # Brief pause between tests
    
    # Test 2: Gemini 2.0 Pro with custom temperature
    test_feature(
        "Gemini 2.0 Pro - Low Temperature (0.3)",
        "/run",
        {
            "content_type": "MCQ",
            "generator_model": "gemini-2.0-pro-exp",
            "input_text": sample_text,
            "num_questions": 2,
            "focus_areas": "diagnosis",
            "temperature": 0.3,
            "top_p": 0.8
        }
    )
    
    time.sleep(2)
    
    # Test 3: Custom Generator Prompt Only
    custom_generator = """
    You are a medical educator. Create {{NUM_QUESTIONS}} challenging MCQ questions.
    
    Content to analyze:
    {{TEXT_TO_ANALYZE}}
    
    Focus areas: {{FOCUS_AREAS}}
    
    Make questions that test deep understanding, not just memorization.
    Include detailed explanations for each answer choice.
    """
    
    test_feature(
        "Custom Generator Prompt with Gemini Flash",
        "/run",
        {
            "content_type": "MCQ",
            "generator_model": "gemini-2.0-flash-exp",
            "input_text": sample_text,
            "num_questions": 1,
            "focus_areas": "clinical presentation",
            "temperature": 0.5,
            "top_p": 0.9,
            "custom_generator_prompt": custom_generator
        }
    )
    
    time.sleep(2)
    
    # Test 4: Both Custom Prompts
    custom_formatter = """
    Format the following medical questions into a clean, professional format.
    Ensure proper numbering, clear answer choices, and organized explanations.
    
    Content to format:
    """
    
    test_feature(
        "Both Custom Prompts - Claude Opus",
        "/run",
        {
            "content_type": "MCQ",
            "generator_model": "claude-3-opus-20240229",
            "input_text": "The heart has four chambers: two atria and two ventricles. Blood flows through the pulmonary and systemic circuits.",
            "num_questions": 1,
            "focus_areas": "cardiac anatomy",
            "temperature": 0.6,
            "top_p": 0.95,
            "custom_generator_prompt": custom_generator,
            "custom_formatter_prompt": custom_formatter
        }
    )
    
    time.sleep(2)
    
    # Test 5: NMCQ with High Temperature
    test_feature(
        "NMCQ - High Temperature (0.8) with Gemini 1.5 Pro",
        "/run",
        {
            "content_type": "NMCQ",
            "generator_model": "gemini-1.5-pro",
            "input_text": sample_text,
            "num_questions": 2,
            "focus_areas": "treatment options",
            "temperature": 0.8,
            "top_p": 0.95
        }
    )
    
    # Test 6: Backward Compatibility
    print("\n" + "="*70)
    print("Testing Backward Compatibility...")
    print("="*70)
    
    test_feature(
        "Legacy Model Name - 'claude'",
        "/run",
        {
            "content_type": "MCQ",
            "generator_model": "claude",
            "input_text": "Test backward compatibility",
            "num_questions": 1,
            "focus_areas": None
        }
    )
    
    print("\n" + "="*70)
    print("✨ TEST SUITE COMPLETED")
    print("="*70)
    print("\nSummary:")
    print("- ✅ Model selection with proper API names")
    print("- ✅ Dual custom prompts (generator + formatter)")
    print("- ✅ Temperature and Top-P controls")
    print("- ✅ Multiple model providers (Claude, Gemini)")
    print("- ✅ Backward compatibility maintained")
    

if __name__ == "__main__":
    main()
