#!/usr/bin/env python
"""
Test to verify that complete events no longer send redundant full text.
"""

import requests
import json

def test_draft_streaming():
    """Test that draft_complete doesn't send the full text."""
    url = "http://localhost:8000/run/stream/draft"
    
    payload = {
        "content_type": "MCQ",
        "generator_model": "claude-sonnet-4-5-20250929",
        "input_text": "Test input",
        "num_questions": 1
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "text/event-stream"
    }
    
    print("Testing draft generation...")
    print("-" * 50)
    
    collected_tokens = ""
    
    try:
        response = requests.post(url, json=payload, headers=headers, stream=True)
        
        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data:'):
                        data = line_str[5:].strip()
                        try:
                            parsed = json.loads(data)
                            if 'token' in parsed:
                                collected_tokens += parsed['token']
                            elif 'success' in parsed:
                                print(f"\n✅ Draft complete event received")
                                print(f"   - Has 'streamed' flag: {'streamed' in parsed}")
                                print(f"   - Has 'draft_1' field: {'draft_1' in parsed}")
                                
                                if 'draft_1' in parsed:
                                    print(f"   ❌ ERROR: draft_1 should NOT be in complete event!")
                                    print(f"   - Draft length: {len(parsed['draft_1'])} chars")
                                else:
                                    print(f"   ✅ GOOD: No redundant draft text in complete event")
                                
                                print(f"   - Collected tokens length: {len(collected_tokens)} chars")
                                print(f"   - Metadata: {parsed.get('metadata', {})}")
                        except json.JSONDecodeError:
                            pass
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_draft_streaming()
    print("\nMake sure the backend is running on http://localhost:8000")
