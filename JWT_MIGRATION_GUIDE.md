# JWT Authentication Migration Guide for Vercel Deployment

## Overview
The application has been migrated from session-based authentication to JWT (JSON Web Token) based authentication to work properly with Vercel's serverless environment.

## Why JWT?
- **Stateless**: JWT tokens are self-contained and don't require server-side storage
- **Serverless Compatible**: Perfect for Vercel's serverless functions that don't maintain state
- **Persistent**: Tokens persist across page refreshes when stored in cookies

## What Changed

### Backend Changes
1. **Removed session storage**: No more in-memory session storage
2. **Added JWT token generation**: Using PyJWT library to create signed tokens
3. **Updated authentication endpoints**:
   - `/api/auth/login` now returns a JWT token
   - `/api/auth/check` validates JWT tokens from Authorization header
   - Authentication uses `Bearer <token>` format in Authorization header

### Frontend Changes
1. **Token Storage**: JWT tokens are stored in cookies (client-side)
2. **Authorization Headers**: All API requests include `Authorization: Bearer <token>` header
3. **Persistent Login**: Authentication persists across page refreshes

## Deployment Steps for Vercel

### 1. Install Dependencies
The backend now requires PyJWT. This has been added to `requirements.txt`:
```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Variables
Set these environment variables in your Vercel project:

```bash
# Required
EDITOR_PASSWORD=your_secure_password
APP_SECRET=your_jwt_secret_key  # Generate with: openssl rand -hex 32

# API Keys
GOOGLE_API_KEY=your_google_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

**Important**: The `APP_SECRET` is used to sign JWT tokens. Keep it secure and never commit it to version control!

### 3. Frontend Environment
Update your frontend environment variables in Vercel:
```bash
NEXT_PUBLIC_API_URL=https://your-backend-api-url.vercel.app
```

### 4. CORS Configuration
The backend's CORS settings in `backend/config.py` should include your Vercel frontend URL:
```python
cors_origins: list = [
    "https://your-frontend.vercel.app",
    # ... other origins
]
```

### 5. Deploy Backend
Deploy the backend to Vercel:
```bash
vercel --prod
```

### 6. Deploy Frontend
Deploy the frontend to Vercel:
```bash
cd frontend
vercel --prod
```

## Testing the Authentication

### Manual Testing
1. Open your deployed frontend
2. Enter your password to login
3. Refresh the page - you should remain logged in
4. Check browser DevTools > Application > Cookies - you should see `auth_token`

### Automated Testing
Run the test script:
```bash
cd backend
python test_jwt_auth.py
```

## Security Considerations

1. **JWT Secret**: Keep your `APP_SECRET` secure and unique per environment
2. **Token Expiration**: Tokens expire after 24 hours
3. **HTTPS Only**: Always use HTTPS in production
4. **Secure Cookies**: The frontend stores tokens in cookies with `sameSite: 'strict'`

## Troubleshooting

### Issue: Logged out after refresh
**Solution**: Ensure `APP_SECRET` environment variable is set in Vercel

### Issue: 401 Unauthorized errors
**Solution**: Check that the frontend is sending the Authorization header correctly

### Issue: CORS errors
**Solution**: Update `cors_origins` in `backend/config.py` to include your Vercel URLs

### Issue: Token expired
**Solution**: Tokens expire after 24 hours. Users need to login again.

## Rollback Plan
If you need to rollback to session-based auth:
1. Restore the original `backend/app.py` from git
2. Restore the original `frontend/services/auth.ts`
3. Remove PyJWT from `requirements.txt`

## Benefits of This Migration
✅ **Persistent authentication** across page refreshes
✅ **Stateless architecture** perfect for serverless
✅ **Better scalability** - no server-side session storage
✅ **Improved security** with signed tokens
✅ **Works perfectly with Vercel's** serverless functions

## Questions?
If you encounter any issues, check the test script output first:
```bash
python backend/test_jwt_auth.py
```

This will verify that JWT authentication is working correctly.
