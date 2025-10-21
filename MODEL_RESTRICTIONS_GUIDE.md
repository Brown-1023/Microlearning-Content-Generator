# Model Restrictions Guide

This guide explains how admins can control which AI models are visible to non-admin users, creating a more streamlined experience.

## Overview

The Model Restrictions feature allows administrators to:
- Control which AI models are available to editor/non-admin users
- Streamline the user interface by showing only specific models
- Easily enable/disable restrictions through the web interface
- Maintain full access to all models for admin users

## How It Works

### For Administrators

1. **Access Model Restrictions Panel**
   - Log in with admin credentials
   - The "Model Restrictions" panel appears at the top of the interface (admin-only)
   - Click the panel header to expand it

2. **Configure Restrictions**
   - **Enable/Disable**: Toggle "Enable Model Restrictions" to activate the feature
   - **Select Models**: When enabled, choose which models non-admin users can access
   - **Save Changes**: Click "Save Restrictions" to apply your configuration

3. **Model Selection Options**
   - Select individual models by checking their checkboxes
   - Use "Select All" or "Deselect All" for bulk operations
   - At least one model must be selected when restrictions are enabled

### For Non-Admin Users (Editors)

- Users will only see the models that admins have made available
- If only one model is available, the interface becomes more streamlined
- The model dropdown will show a helpful message about availability
- Users cannot modify model restrictions

## Configuration Storage

Model restrictions are stored in:
- **Backend**: `backend/config/model_restrictions.json`
- **Format**: JSON file with `enabled` flag and `allowed_models` array

Example configuration:
```json
{
  "enabled": true,
  "allowed_models": [
    "gemini-2.5-flash",
    "claude-sonnet-4-5-20250929"
  ]
}
```

## API Endpoints

### Get Available Models
```
GET /api/models
```
Returns models based on user role and current restrictions.

**Response for Admin:**
```json
{
  "models": [...],          // Models available to this user
  "all_models": {...},      // All possible models (admin only)
  "restrictions": {...}     // Current restriction settings (admin only)
}
```

**Response for Editor:**
```json
{
  "models": [...],          // Only allowed models
  "all_models": null,       // Not provided to non-admins
  "restrictions": null      // Not provided to non-admins
}
```

### Update Model Restrictions (Admin Only)
```
POST /api/models/restrictions
```

**Request Body:**
```json
{
  "enabled": true,
  "allowed_models": ["gemini-2.5-flash", "claude-sonnet-4-5-20250929"]
}
```

## Security & Access Control

- Only administrators can view and modify model restrictions
- Editors/non-admin users cannot bypass restrictions
- The backend validates model selection on every generation request
- If a user tries to use a restricted model, they receive a 403 Forbidden error

## Use Cases

### Single Model Configuration
Perfect for organizations that want to:
- Standardize on one AI model for consistency
- Reduce complexity for end users
- Control costs by limiting to specific models

### Limited Model Set
Useful when you want to:
- Offer choice between 2-3 vetted models
- Exclude experimental or expensive models
- Provide different models for different use cases

### No Restrictions (Default)
When disabled:
- All users see all available models
- Maximum flexibility for all users
- Suitable for development or small teams

## Testing

A test script is provided to verify the feature works correctly:

```bash
# Set environment variables
export ADMIN_PASSWORD=your_admin_password
export EDITOR_PASSWORD=your_editor_password

# Run the test script
python backend/test_model_restrictions.py
```

The test script verifies:
- Admin can set and modify restrictions
- Editor cannot modify restrictions
- Model visibility changes based on restrictions
- Content generation respects model restrictions

## Troubleshooting

### Models Not Appearing for Users
1. Check if restrictions are enabled in the Model Restrictions panel
2. Verify at least one model is selected
3. Ensure the selected models have valid API keys configured

### Restrictions Not Saving
1. Verify you're logged in as admin
2. Check browser console for errors
3. Ensure the backend has write permissions to `backend/config/`

### All Models Still Visible
1. Confirm restrictions are enabled (not just configured)
2. Try refreshing the page after saving
3. Check the `model_restrictions.json` file exists and is valid

## Best Practices

1. **Start Conservative**: Begin with all models available, then gradually restrict
2. **Communicate Changes**: Inform users before changing available models
3. **Test First**: Use the test script to verify changes before deploying
4. **Monitor Usage**: Check if users encounter issues with restricted models
5. **Document Choices**: Keep notes on why certain models are restricted

## Migration from Environment Variables

Previously, model restrictions could be set via the `ALLOWED_MODELS` environment variable. This is now deprecated in favor of the UI-based approach, which offers:
- Dynamic updates without server restart
- Better user experience
- Visual feedback on current settings
- Easier management for non-technical admins
