# Role-Based Access Control Guide

## Overview

The Microlearning Content Generator implements a two-tier access control system with **Admin** and **Editor** roles. Users are authenticated based on their password, which determines their access level and available features.

## User Roles

### 👑 Admin Role
Full access to all features including system configuration and prompt management.

**Capabilities:**
- ✅ Generate MCQ and Non-MCQ content
- ✅ Select AI models (Claude/Gemini)
- ✅ Set number of questions and focus areas
- ✅ View and edit prompt templates
- ✅ Adjust advanced settings (temperature, top-p)
- ✅ Access system configuration
- ✅ Download generated content

### ✍️ Editor Role
Standard access for content generation without system configuration privileges.

**Capabilities:**
- ✅ Generate MCQ and Non-MCQ content
- ✅ Select AI models (Claude/Gemini)
- ✅ Set number of questions and focus areas
- ✅ Download generated content
- ❌ Cannot view/edit prompt templates
- ❌ Cannot adjust temperature/top-p settings
- ❌ Cannot access system configuration

## Setup Instructions

### 1. Configure Passwords

Set the following environment variables in your `.env` file:

```bash
# Authentication
ADMIN_PASSWORD=your_secure_admin_password
EDITOR_PASSWORD=your_secure_editor_password
APP_SECRET=your_jwt_secret_key
```

### 2. Password Requirements

- **Length**: Minimum 8 characters recommended
- **Complexity**: Use a mix of letters, numbers, and special characters
- **Uniqueness**: Use different passwords for admin and editor roles
- **Security**: Never commit passwords to version control

### 3. Example Configuration

**Development Environment (.env):**
```bash
ADMIN_PASSWORD=Admin@2025Secure!
EDITOR_PASSWORD=Editor#2025Pass!
APP_SECRET=generate-random-32-char-string-here
```

**Production Environment (Cloud Run):**
```bash
# Store in Google Secret Manager
gcloud secrets create admin-password --data-file=-
gcloud secrets create editor-password --data-file=-
gcloud secrets create app-secret --data-file=-

# Deploy with secrets
gcloud run deploy microlearning-generator \
  --set-secrets="ADMIN_PASSWORD=admin-password:latest" \
  --set-secrets="EDITOR_PASSWORD=editor-password:latest" \
  --set-secrets="APP_SECRET=app-secret:latest"
```

## User Interface Differences

### Admin View
When logged in as admin, users will see:
- Advanced Settings toggle (temperature, top-p controls)
- Prompt Templates section with edit capabilities
- "👑 Admin" badge in the header
- Full access to all API endpoints

### Editor View
When logged in as editor, users will see:
- Standard generation form only
- No advanced settings or prompt templates
- "✍️ Editor" badge in the header
- Limited API access (403 errors for restricted endpoints)

## API Access Control

### Public Endpoints
No authentication required:
- `GET /` - API root
- `GET /healthz` - Health check
- `POST /api/auth/login` - Login endpoint

### Authenticated Endpoints
Requires valid JWT token:
- `POST /run` - Generate content (both roles)
- `GET /api/auth/check` - Check authentication status
- `POST /api/auth/logout` - Logout

### Admin-Only Endpoints
Requires admin role:
- `GET /api/prompts` - View prompt templates
- `POST /api/prompts` - Update prompt templates
- `GET /api/settings` - View advanced settings

## Authentication Flow

1. **Login Request**
   ```javascript
   POST /api/auth/login
   {
     "password": "admin123"
   }
   ```

2. **Response with Role**
   ```javascript
   {
     "success": true,
     "message": "Logged in successfully",
     "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
     "role": "admin"  // or "editor"
   }
   ```

3. **Subsequent Requests**
   Include JWT token in Authorization header:
   ```
   Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
   ```

4. **Token Payload**
   JWT tokens include the user's role:
   ```javascript
   {
     "exp": 1234567890,
     "iat": 1234567890,
     "authorized": true,
     "role": "admin"  // or "editor"
   }
   ```

## Security Considerations

### Password Management
- Store passwords in environment variables or secret management systems
- Never hardcode passwords in source code
- Use different passwords for different environments
- Rotate passwords regularly
- Monitor failed login attempts

### Token Security
- JWT tokens expire after 24 hours
- Tokens are stored as HttpOnly cookies in the frontend
- Use HTTPS in production to prevent token interception
- Implement rate limiting on login attempts

### Access Control
- Backend validates role on every protected request
- Frontend UI adapts based on user role
- API returns 403 Forbidden for unauthorized access
- Sensitive operations require admin role

## Testing Role Access

### Manual Testing

1. **Test Admin Access:**
   - Login with admin password
   - Verify access to prompt templates
   - Verify ability to change temperature/top-p
   - Check admin badge displays

2. **Test Editor Access:**
   - Login with editor password
   - Verify prompt templates are hidden
   - Verify advanced settings are hidden
   - Check editor badge displays
   - Verify content generation still works

### Automated Testing

Run the test script to verify role-based access:

```python
# test_roles.py
import requests

# Test admin login
admin_response = requests.post("http://localhost:8000/api/auth/login", 
                               json={"password": "admin123"})
admin_token = admin_response.json()["token"]

# Test admin can access prompts
prompts_response = requests.get("http://localhost:8000/api/prompts",
                                headers={"Authorization": f"Bearer {admin_token}"})
assert prompts_response.status_code == 200

# Test editor login
editor_response = requests.post("http://localhost:8000/api/auth/login",
                                json={"password": "editor123"})
editor_token = editor_response.json()["token"]

# Test editor cannot access prompts
prompts_response = requests.get("http://localhost:8000/api/prompts",
                                headers={"Authorization": f"Bearer {editor_token}"})
assert prompts_response.status_code == 403
```

## Migration Guide

### From Single Password to Role-Based

If migrating from the old single-password system:

1. **Update Environment Variables:**
   ```bash
   # Old
   EDITOR_PASSWORD=single_password
   
   # New
   ADMIN_PASSWORD=admin_password
   EDITOR_PASSWORD=editor_password
   ```

2. **Update Deployment Configuration:**
   - Add `ADMIN_PASSWORD` to your deployment secrets
   - Keep `EDITOR_PASSWORD` for backward compatibility
   - Update documentation for users

3. **Communicate Changes:**
   - Notify admin users of their new password
   - Notify editor users if their password changed
   - Document the new capabilities for each role

## Troubleshooting

### Issue: Cannot Login
- Verify passwords are set in environment variables
- Check for typos in password
- Ensure backend is running and accessible

### Issue: Features Not Showing/Hiding
- Clear browser cache and cookies
- Verify JWT token contains correct role
- Check browser console for errors

### Issue: 403 Forbidden Errors
- Verify user has correct role for the operation
- Check JWT token is being sent in headers
- Ensure token hasn't expired (24-hour lifetime)

### Issue: Both Passwords Give Admin Access
- Check if both `ADMIN_PASSWORD` and `EDITOR_PASSWORD` are set
- Verify they have different values
- Restart backend after changing environment variables

## Future Enhancements

Potential improvements to the role system:

1. **Additional Roles:**
   - Viewer (read-only access)
   - Reviewer (can validate but not generate)
   - Super Admin (user management)

2. **User Management:**
   - Database-backed user accounts
   - Password reset functionality
   - User activity logging

3. **Advanced Permissions:**
   - Per-prompt template permissions
   - Model-specific access control
   - Rate limiting per role

4. **Integration Options:**
   - Google IAP integration
   - LDAP/Active Directory
   - OAuth2/OIDC providers
