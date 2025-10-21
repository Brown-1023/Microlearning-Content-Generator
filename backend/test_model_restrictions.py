"""
Test script for model restrictions feature.
Tests the ability for admins to restrict models visible to non-admin users.
"""

import os
import json
import requests
from pathlib import Path

# Test configuration
BASE_URL = "http://localhost:4000"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
EDITOR_PASSWORD = os.getenv("EDITOR_PASSWORD", "")


class TestModelRestrictions:
    """Test model restrictions functionality."""
    
    def __init__(self):
        self.admin_token = None
        self.editor_token = None
        self.session = requests.Session()
    
    def login_as_admin(self):
        """Login as admin and get token."""
        response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"password": ADMIN_PASSWORD}
        )
        if response.status_code == 200:
            data = response.json()
            self.admin_token = data.get("token")
            print(f"✅ Admin login successful: {data.get('role')}")
            return True
        else:
            print(f"❌ Admin login failed: {response.status_code}")
            return False
    
    def login_as_editor(self):
        """Login as editor and get token."""
        response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"password": EDITOR_PASSWORD}
        )
        if response.status_code == 200:
            data = response.json()
            self.editor_token = data.get("token")
            print(f"✅ Editor login successful: {data.get('role')}")
            return True
        else:
            print(f"❌ Editor login failed: {response.status_code}")
            return False
    
    def get_models_as_admin(self):
        """Get available models as admin."""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = self.session.get(
            f"{BASE_URL}/api/models",
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Admin can see {len(data.get('models', []))} models")
            print(f"   All models available: {list(data.get('all_models', {}).keys())}")
            print(f"   Current restrictions: {data.get('restrictions')}")
            return data
        else:
            print(f"❌ Failed to get models as admin: {response.status_code}")
            return None
    
    def get_models_as_editor(self):
        """Get available models as editor."""
        headers = {"Authorization": f"Bearer {self.editor_token}"}
        response = self.session.get(
            f"{BASE_URL}/api/models",
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            print(f"✅ Editor can see {len(models)} models")
            for model in models:
                print(f"   - {model.get('name')} ({model.get('display_name')})")
            return data
        else:
            print(f"❌ Failed to get models as editor: {response.status_code}")
            return None
    
    def set_model_restrictions(self, enabled, allowed_models):
        """Set model restrictions as admin."""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = self.session.post(
            f"{BASE_URL}/api/models/restrictions",
            json={
                "enabled": enabled,
                "allowed_models": allowed_models
            },
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Model restrictions updated successfully")
            print(f"   Enabled: {data.get('restrictions', {}).get('enabled')}")
            print(f"   Allowed models: {data.get('restrictions', {}).get('allowed_models')}")
            return True
        else:
            print(f"❌ Failed to update model restrictions: {response.status_code}")
            if response.text:
                print(f"   Error: {response.text}")
            return False
    
    def test_editor_cannot_set_restrictions(self):
        """Test that editor cannot set model restrictions."""
        headers = {"Authorization": f"Bearer {self.editor_token}"}
        response = self.session.post(
            f"{BASE_URL}/api/models/restrictions",
            json={
                "enabled": True,
                "allowed_models": ["gemini-2.5-flash"]
            },
            headers=headers
        )
        if response.status_code == 403:
            print(f"✅ Editor correctly denied from setting restrictions")
            return True
        else:
            print(f"❌ Editor should not be able to set restrictions: {response.status_code}")
            return False
    
    def run_all_tests(self):
        """Run all model restriction tests."""
        print("\n" + "="*50)
        print("TESTING MODEL RESTRICTIONS FEATURE")
        print("="*50)
        
        # Step 1: Login as admin and editor
        print("\n1. Testing Authentication")
        print("-" * 30)
        if not self.login_as_admin():
            print("⚠️  Admin login failed - check ADMIN_PASSWORD")
            return
        
        if not self.login_as_editor():
            print("⚠️  Editor login failed - check EDITOR_PASSWORD")
            return
        
        # Step 2: Check initial state
        print("\n2. Checking Initial State")
        print("-" * 30)
        admin_models = self.get_models_as_admin()
        editor_models_before = self.get_models_as_editor()
        
        if admin_models and editor_models_before:
            print(f"   Initial state: Editor sees {len(editor_models_before.get('models', []))} models")
        
        # Step 3: Test editor cannot set restrictions
        print("\n3. Testing Role-Based Access Control")
        print("-" * 30)
        self.test_editor_cannot_set_restrictions()
        
        # Step 4: Enable restrictions with limited models
        print("\n4. Testing Model Restrictions - Limiting to 1 Model")
        print("-" * 30)
        
        # Get all available models
        all_model_ids = list(admin_models.get('all_models', {}).keys()) if admin_models else []
        
        if len(all_model_ids) > 0:
            # Restrict to just one model
            restricted_model = all_model_ids[0]
            success = self.set_model_restrictions(
                enabled=True,
                allowed_models=[restricted_model]
            )
            
            if success:
                # Check what editor sees now
                editor_models_after = self.get_models_as_editor()
                if editor_models_after:
                    restricted_count = len(editor_models_after.get('models', []))
                    if restricted_count == 1:
                        print(f"✅ Restriction working: Editor now sees only 1 model")
                    else:
                        print(f"❌ Expected 1 model but editor sees {restricted_count}")
        
        # Step 5: Test with multiple models
        print("\n5. Testing Model Restrictions - Multiple Models")
        print("-" * 30)
        
        if len(all_model_ids) >= 2:
            # Allow first two models
            allowed_models = all_model_ids[:2]
            success = self.set_model_restrictions(
                enabled=True,
                allowed_models=allowed_models
            )
            
            if success:
                editor_models_after = self.get_models_as_editor()
                if editor_models_after:
                    restricted_count = len(editor_models_after.get('models', []))
                    if restricted_count == 2:
                        print(f"✅ Restriction working: Editor now sees 2 models")
                    else:
                        print(f"❌ Expected 2 models but editor sees {restricted_count}")
        
        # Step 6: Disable restrictions
        print("\n6. Testing Disabling Restrictions")
        print("-" * 30)
        
        success = self.set_model_restrictions(
            enabled=False,
            allowed_models=[]
        )
        
        if success:
            editor_models_after = self.get_models_as_editor()
            if editor_models_after:
                unrestricted_count = len(editor_models_after.get('models', []))
                initial_count = len(editor_models_before.get('models', [])) if editor_models_before else 0
                
                if unrestricted_count == initial_count:
                    print(f"✅ Restrictions disabled: Editor sees all {unrestricted_count} models again")
                else:
                    print(f"⚠️  Model count mismatch: {unrestricted_count} vs initial {initial_count}")
        
        # Step 7: Test content generation with restricted model
        print("\n7. Testing Content Generation with Restricted Model")
        print("-" * 30)
        
        if len(all_model_ids) > 0:
            # Set restriction to one model
            restricted_model = all_model_ids[0]
            self.set_model_restrictions(
                enabled=True,
                allowed_models=[restricted_model]
            )
            
            # Try to generate content as editor with allowed model
            headers = {"Authorization": f"Bearer {self.editor_token}"}
            response = self.session.post(
                f"{BASE_URL}/run",
                json={
                    "content_type": "MCQ",
                    "generator_model": restricted_model,
                    "input_text": "Test content for model restriction",
                    "num_questions": 1
                },
                headers=headers
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ Editor can use allowed model: {restricted_model}")
            else:
                print(f"⚠️  Generation test status: {response.status_code}")
            
            # Try to use a non-allowed model (if available)
            if len(all_model_ids) > 1:
                forbidden_model = all_model_ids[1]
                response = self.session.post(
                    f"{BASE_URL}/run",
                    json={
                        "content_type": "MCQ",
                        "generator_model": forbidden_model,
                        "input_text": "Test content for model restriction",
                        "num_questions": 1
                    },
                    headers=headers
                )
                
                if response.status_code == 403:
                    print(f"✅ Editor correctly blocked from using non-allowed model")
                else:
                    print(f"❌ Expected 403 but got {response.status_code} for forbidden model")
        
        print("\n" + "="*50)
        print("TESTS COMPLETED")
        print("="*50)


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
    
    # Check passwords are set
    if not ADMIN_PASSWORD or not EDITOR_PASSWORD:
        print("⚠️  Please set ADMIN_PASSWORD and EDITOR_PASSWORD environment variables")
        print("   Or update them in the script")
        return
    
    # Run tests
    tester = TestModelRestrictions()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
