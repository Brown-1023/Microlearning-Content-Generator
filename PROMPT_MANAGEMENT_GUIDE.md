# Prompt Management Guide

## Overview

The Microlearning Content Generator now features a centralized prompt management system that allows administrators to modify and save prompt templates directly to the backend. This eliminates the need to send custom prompts with each generation request.

## How It Works

### For Administrators

1. **Access Prompt Templates**
   - Login with admin credentials
   - The "Prompt Templates" section appears in the UI
   - All four prompt templates are loaded from the backend

2. **Edit Prompts**
   - Click on the "Prompt Templates" section to expand it
   - Edit any of the four prompts:
     - MCQ Generator Prompt
     - MCQ Formatter Prompt
     - Non-MCQ Generator Prompt
     - Non-MCQ Formatter Prompt

3. **Save Changes**
   - Click "Save All Prompts" button
   - Prompts are permanently saved to the backend files
   - Success/error message appears
   - All future generations will use these saved prompts

4. **Reset to Defaults**
   - Click "Reset All to Defaults" to revert changes
   - Individual prompts can be reset using the ↻ button

### For Editors

- Editors cannot see or modify prompt templates
- All content generation uses the prompts saved by administrators
- This ensures consistency across all editor-generated content

## Technical Details

### Backend Changes

1. **Prompt Storage**
   - Prompts are stored in `backend/prompts/` directory:
     - `mcq.generator.txt`
     - `mcq.formatter.txt`
     - `nonmcq.generator.txt`
     - `nonmcq.formatter.txt`

2. **API Endpoints**
   - `GET /api/prompts` - Retrieve current prompts (admin only)
   - `POST /api/prompts` - Save new prompts (admin only)

3. **Generation Process**
   - The `/run` endpoint no longer accepts custom prompts
   - Always uses the saved prompt files
   - Ensures all users get consistent results

### Frontend Changes

1. **Prompt Management UI**
   - Only visible to admin users
   - Real-time editing with textarea fields
   - Save status notifications

2. **Generation Request**
   - No longer sends custom prompt fields
   - Simplified payload with only essential parameters

## Benefits

### Centralized Management
- Single source of truth for all prompts
- No need to copy/paste prompts between sessions
- Changes apply immediately to all users

### Security
- Only administrators can modify prompts
- Prevents unauthorized prompt injection
- Maintains quality control

### Performance
- Smaller request payloads (no prompt text)
- Faster API calls
- Reduced network traffic

### Consistency
- All editors use the same prompts
- Predictable output quality
- Easier to maintain and update

## Usage Example

### Admin Workflow

1. **Login as Admin**
   ```
   Password: [admin_password]
   ```

2. **Navigate to Prompt Templates**
   - Click on "Prompt Templates" section
   - View all four prompts

3. **Make Changes**
   ```
   Example: Add instruction to MCQ Generator
   "Generate exactly {{NUM_QUESTIONS}} multiple choice questions..."
   ```

4. **Save Prompts**
   - Click "Save All Prompts"
   - Wait for confirmation message

5. **Test Generation**
   - Generate content to verify changes
   - All outputs will use new prompts

### Editor Workflow

1. **Login as Editor**
   ```
   Password: [editor_password]
   ```

2. **Generate Content**
   - Select content type and model
   - Enter input text
   - Click "Generate Content"
   - Uses prompts saved by admin

## Best Practices

### Prompt Versioning

1. **Before Major Changes**
   - Copy current prompts to a backup file
   - Document the change reason
   - Test with sample inputs

2. **Testing Changes**
   - Make incremental changes
   - Test with various input types
   - Verify output quality

3. **Documentation**
   - Keep a changelog of prompt modifications
   - Document prompt structure and placeholders
   - Note any model-specific optimizations

### Prompt Structure

Ensure prompts maintain required placeholders:
- `{{TEXT_TO_ANALYZE}}` - Input text
- `{{NUM_QUESTIONS}}` - Number of questions
- `{{FOCUS_AREAS}}` - Optional focus areas

## Troubleshooting

### Issue: Changes Not Saving

**Symptoms:**
- Save button shows error
- Changes don't persist

**Solutions:**
- Verify admin role
- Check file permissions on server
- Ensure prompt files exist

### Issue: Generation Fails After Changes

**Symptoms:**
- Generation errors after saving prompts
- Validation failures

**Solutions:**
- Verify placeholder syntax
- Check prompt format requirements
- Reset to defaults if needed

### Issue: Prompts Not Loading

**Symptoms:**
- Empty prompt fields
- Error loading prompts

**Solutions:**
- Check API connectivity
- Verify authentication token
- Ensure backend is running

## Security Considerations

### Access Control
- Only admin passwords can modify prompts
- JWT tokens include role information
- Backend validates role on each request

### Input Validation
- Prompts are plain text only
- No code execution in prompts
- Sanitized before saving

### Audit Trail
- Consider logging prompt changes
- Track who made changes and when
- Monitor for unauthorized access attempts

## Future Enhancements

### Potential Improvements

1. **Version Control**
   - Git integration for prompt history
   - Rollback to previous versions
   - Diff view for changes

2. **Prompt Library**
   - Multiple prompt sets
   - A/B testing capabilities
   - Template marketplace

3. **Advanced Features**
   - Prompt validation rules
   - Preview before saving
   - Bulk import/export

4. **Collaboration**
   - Comments on prompts
   - Approval workflow
   - Change notifications

## Migration Notes

### From Custom Prompts to Saved Prompts

If migrating from the old system where prompts were sent with each request:

1. **Save Current Prompts**
   - Login as admin
   - Copy any custom prompts to the editor
   - Click "Save All Prompts"

2. **Update Frontend Code**
   - Remove custom prompt fields from requests
   - Update to latest frontend version

3. **Verify Functionality**
   - Test generation with both roles
   - Confirm prompts persist
   - Check output quality

## Summary

The new prompt management system provides:
- ✅ Centralized prompt control
- ✅ Role-based access management
- ✅ Persistent prompt storage
- ✅ Simplified generation requests
- ✅ Consistent output quality

This ensures that administrators have full control over the AI prompts while editors can focus on content generation without worrying about prompt configuration.
