#!/usr/bin/env python3
"""
Test script for the new features:
- Custom prompt support
- Temperature and top_p parameters
- Enhanced model selection
"""

import requests
import json
import sys
from typing import Dict, Any

# API configuration
BASE_URL = "http://localhost:8000"
API_KEY = None  # Set if password protection is enabled

def test_endpoint(endpoint: str, payload: Dict[str, Any], description: str):
    """Test a specific endpoint with given payload."""
    print(f"\n{'=' * 60}")
    print(f"Testing: {description}")
    print(f"{'=' * 60}")
    
    headers = {}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    
    try:
        response = requests.post(
            f"{BASE_URL}{endpoint}",
            json=payload,
            headers=headers,
            timeout=120
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success!")
            if data.get("metadata"):
                print(f"Model Used: {data['metadata'].get('model_ids', {}).get('generator', 'N/A')}")
                print(f"Total Time: {data['metadata'].get('total_time', 'N/A'):.2f}s")
            if data.get("output"):
                print(f"Output Preview (first 500 chars):\n{data['output'][:500]}...")
        else:
            print(f"❌ Error: {response.text}")
            
        return response
        
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Is it running?")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    return None


def run_tests():
    """Run all test cases."""
    
    # Test 1: Standard MCQ generation with custom temperature
    test_endpoint(
        "/run",
        {
            "content_type": "MCQ",
            "generator_model": "gemini-2.5-pro",
            "input_text": "The cardiovascular system consists of the heart, blood vessels, and blood. The heart pumps blood through arteries and veins.",
            "num_questions": 2,
            "focus_areas": "heart anatomy",
            "temperature": 0.3,
            "top_p": 0.9
        },
        "MCQ Generation with Low Temperature (0.3)"
    )
    
    # Test 2: NMCQ with high temperature for more creativity
    test_endpoint(
        "/run",
        {
            "content_type": "NMCQ",
            "generator_model": "claude-sonnet-3.5",
            "input_text": "Diabetes mellitus is a metabolic disorder characterized by high blood sugar levels. Type 1 diabetes involves autoimmune destruction of pancreatic beta cells.",
            "num_questions": 2,
            "focus_areas": "pathophysiology",
            "temperature": 0.8,
            "top_p": 0.95
        },
        "NMCQ Generation with High Temperature (0.8) using Claude"
    )
    
    # Test 3: Custom prompt usage
    custom_prompt = """Create {{NUM_QUESTIONS}} medical quiz questions about the following text:

{{TEXT_TO_ANALYZE}}

Focus specifically on: {{FOCUS_AREAS}}

Format each question with:
- Question number and title
- Clinical scenario
- Multiple choice options (A-D)
- Correct answer
- Brief explanation

Make the questions challenging but educational."""
    
    test_endpoint(
        "/run",
        {
            "content_type": "MCQ",
            "generator_model": "gemini-2.5-flash",
            "input_text": "The liver is the largest internal organ and performs over 500 functions including detoxification, protein synthesis, and bile production.",
            "num_questions": 1,
            "focus_areas": "liver functions",
            "custom_prompt": custom_prompt,
            "temperature": 0.5,
            "top_p": 0.9
        },
        "Custom Prompt with Gemini Flash"
    )
    
    # Test 4: Different model variants
    models_to_test = [
        ("claude-sonnet-4.5", "Claude Sonnet 4.5"),
        ("gemini-1.5-pro", "Gemini 1.5 Pro"),
    ]
    
    for model_name, display_name in models_to_test:
        test_endpoint(
            "/run",
            {
                "content_type": "MCQ",
                "generator_model": model_name,
                "input_text": "Antibiotics are medications used to treat bacterial infections. They work by either killing bacteria or preventing their reproduction.",
                "num_questions": 1,
                "focus_areas": None,
                "temperature": 0.5,
                "top_p": 0.95
            },
            f"Testing Model: {display_name}"
        )


def check_health():
    """Check if the API is healthy."""
    print("\n🏥 Checking API Health...")
    try:
        response = requests.get(f"{BASE_URL}/healthz")
        if response.status_code == 200:
            data = response.json()
            print("✅ API is healthy")
            print(f"Status: {data['status']}")
            for check, status in data['checks'].items():
                print(f"  - {check}: {'✅' if status else '❌'}")
            return True
        else:
            print("❌ API health check failed")
            return False
    except Exception as e:
        print(f"❌ Could not connect to API: {e}")
        return False


def main():
    """Main test runner."""
    print("🚀 Testing New Features in Microlearning Content Generator")
    print(f"API URL: {BASE_URL}")
    
    if not check_health():
        print("\n⚠️  API is not available. Please start the backend server first:")
        print("  cd backend && python app.py")
        sys.exit(1)
    
    print("\n📝 Starting Tests...")
    run_tests()
    
    print("\n" + "=" * 60)
    print("✨ All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
