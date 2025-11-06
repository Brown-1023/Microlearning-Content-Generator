#!/usr/bin/env python
"""
Quick test to verify the draft generation fix.
"""

import requests
import json

# Test the draft endpoint
url = "http://localhost:8000/run/stream/draft"

payload = {
    "content_type": "MCQ",
    "generator_model": "claude-sonnet-4-5-20250929",
    "input_text": "The mitochondria is the powerhouse of the cell.",
    "num_questions": 1,
    "generator_temperature": 0.7,
    "generator_top_p": 0.95
}

headers = {
    "Content-Type": "application/json",
    "Accept": "text/event-stream"
}

print("Testing draft generation endpoint...")
print(f"Payload: {json.dumps(payload, indent=2)}")
print("-" * 50)

try:
    response = requests.post(url, json=payload, headers=headers, stream=True)
    
    if response.status_code == 200:
        print("✅ Connection successful, streaming response:")
        print("-" * 50)
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data:'):
                    data = line_str[5:].strip()
                    try:
                        parsed = json.loads(data)
                        if 'error' in parsed:
                            print(f"❌ Error: {parsed['error']}")
                        elif 'token' in parsed:
                            print(parsed['token'], end='', flush=True)
                        elif 'progress' in parsed:
                            print(f"\n📊 Progress: {parsed.get('message', '')}")
                        elif 'success' in parsed:
                            print(f"\n✅ Draft complete! Success: {parsed['success']}")
                    except json.JSONDecodeError:
                        pass
    else:
        print(f"❌ Error: Status {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Connection error: {e}")
    print("Make sure the backend is running on http://localhost:8000")
