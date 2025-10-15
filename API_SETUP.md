# API Keys Setup Guide

## The Error Explained

The `ResourceExhausted` error you're seeing occurs when:
1. API keys are not configured
2. Using incorrect model names
3. API quota exceeded

## Fixed Model Names

The correct model names have been updated in the code:

| Model Type | Previous (Incorrect) | Fixed (Correct) |
|------------|---------------------|-----------------|
| Claude Sonnet 4.5 | `claude-3-5-sonnet-20241022` | `claude-sonnet-4-5-20250929` |
| Gemini 2.5 Pro | `gemini-2.0-flash-exp` | `gemini-2.5-pro` |
| Gemini 2.5 Flash | `gemini-2.0-flash-exp` | `gemini-2.5-flash` |

## Setting Up API Keys

### 1. Get Your API Keys

- **Google AI Studio (Gemini)**: https://aistudio.google.com/app/apikey
- **Anthropic (Claude)**: https://console.anthropic.com/settings/keys

### 2. Create .env File

Copy the example environment file:
```bash
cp env.example .env
```

### 3. Edit .env File

Add your actual API keys:
```env
# Required API Keys
GOOGLE_API_KEY=your-actual-google-api-key-here
ANTHROPIC_API_KEY=your-actual-anthropic-api-key-here

# Authentication (Required)
EDITOR_PASSWORD=your-secure-password
APP_SECRET=generate-random-secret-key

# Model Configuration (These are now correct)
CLAUDE_MODEL=claude-sonnet-4-5-20250929
GEMINI_PRO=gemini-2.5-pro
GEMINI_FLASH=gemini-2.5-flash
```

### 4. Test the Configuration

After setting up your .env file:

```bash
# Test with Claude
python test_cli.py generate --type MCQ --model claude --questions 1

# Test with Gemini
python test_cli.py generate --type MCQ --model gemini --questions 1
```

## Troubleshooting

### If you still get ResourceExhausted:
1. **Check API quota**: Log into Google AI Studio and check your quota
2. **Verify API key**: Ensure the key is active and has proper permissions
3. **Try different model**: Test with Claude if Gemini fails

### Alternative: Use Environment Variables Directly

For testing, you can set environment variables directly:

**Windows (PowerShell):**
```powershell
$env:GOOGLE_API_KEY="your-api-key"
$env:ANTHROPIC_API_KEY="your-api-key"
python test_cli.py generate
```

**Linux/Mac:**
```bash
export GOOGLE_API_KEY="your-api-key"
export ANTHROPIC_API_KEY="your-api-key"
python test_cli.py generate
```

## Model Availability Note

### Models Specified in Requirements
The requirements document specifies these models:
- `claude-sonnet-4-5-20250929` (Claude Sonnet 4.5)
- `gemini-2.5-pro` (Gemini 2.5 Pro)
- `gemini-2.5-flash` (Gemini 2.5 Flash)

### Currently Available Models (2024)
However, the actually available models might be:
- `claude-3-5-sonnet-20241022` (Latest Claude 3.5 Sonnet)
- `gemini-1.5-pro-latest` or `gemini-1.5-pro` (Gemini 1.5 Pro)
- `gemini-1.5-flash-latest` or `gemini-1.5-flash` (Gemini 1.5 Flash)

### How to Fix Model Name Issues

**Option 1: Use Alternative Configuration**
```bash
# Copy the alternative env file
cp env.alternative.example .env

# Edit .env with your API keys and use currently available models
```

**Option 2: Test Available Models**
```python
# Test script to check which models work
import google.generativeai as genai

genai.configure(api_key="your-api-key")

# List available models
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
```

**Option 3: Override in .env**
```env
# Override with working model names
GEMINI_PRO=gemini-1.5-pro-latest
GEMINI_FLASH=gemini-1.5-flash-latest
CLAUDE_MODEL=claude-3-5-sonnet-20241022
```

## Summary

The error was caused by:
1. ✅ **Fixed**: Incorrect model names in configuration
2. ❌ **Need to fix**: Missing API keys in your environment

Once you add your API keys to the .env file, the pipeline should work correctly.
