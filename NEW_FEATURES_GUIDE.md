# New Features Guide - Enhanced UI Controls

## Overview
The UI has been updated with advanced controls for fine-tuning the content generation process. These new features provide greater flexibility and control over the AI models and their outputs.

## New Features

### 1. **Enhanced Model Selection**
The generator model selection has been expanded to include specific model versions from both Anthropic and Google:

**Anthropic Models:**
- Claude Sonnet 3.5
- Claude Sonnet 4.5
- Claude Opus

**Google Models:**
- Gemini 2.5 Pro
- Gemini 1.5 Pro
- Gemini 2.5 Flash

### 2. **Temperature Control**
A new temperature slider (0.0 to 1.0) controls the randomness of the model's output:
- **Lower values (0.0-0.3):** More focused, deterministic responses
- **Medium values (0.4-0.6):** Balanced creativity and consistency
- **Higher values (0.7-1.0):** More creative, varied responses

**Default:** 0.51

### 3. **Top-P Control**
The Top-P (nucleus sampling) parameter (0.0 to 1.0) controls the diversity of word choices:
- **Lower values:** More conservative word selection
- **Higher values:** Broader vocabulary usage

**Default:** 0.95

### 4. **Custom Prompt Support**
An advanced feature that allows users to override the default prompt templates:
- Toggle "Use Custom Prompt (Advanced)" to enable
- Write your own prompt using these placeholders:
  - `{{TEXT_TO_ANALYZE}}` - The input text
  - `{{NUM_QUESTIONS}}` - Number of questions to generate
  - `{{FOCUS_AREAS}}` - Focus areas (if specified)

## How to Use

### Basic Usage
1. Select your content type (MCQ or Non-MCQ)
2. Choose a generator model from the dropdown
3. Adjust temperature and top-p sliders as needed
4. Enter your input text and parameters
5. Click "Generate Content"

### Advanced Usage with Custom Prompts
1. Enable "Use Custom Prompt (Advanced)"
2. Enter your custom prompt template
3. Include the required placeholders
4. The system will replace placeholders with your input values

### Example Custom Prompt
```
Generate {{NUM_QUESTIONS}} challenging medical questions based on:

{{TEXT_TO_ANALYZE}}

Focus on: {{FOCUS_AREAS}}

Requirements:
- Include clinical scenarios
- Provide detailed explanations
- Target advanced learners
```

## API Changes

### Request Parameters
The `/run` endpoint now accepts additional parameters:

```json
{
  "content_type": "MCQ",
  "generator_model": "claude-sonnet-3.5",
  "input_text": "...",
  "num_questions": 3,
  "focus_areas": "diagnosis",
  "temperature": 0.5,        // NEW: Optional (0.0-1.0)
  "top_p": 0.95,            // NEW: Optional (0.0-1.0)
  "custom_prompt": "..."     // NEW: Optional custom prompt template
}
```

### Model Name Mapping
Frontend model names are automatically mapped to the appropriate API model identifiers:
- `claude-sonnet-3.5` → `claude-3-5-sonnet-20241022`
- `claude-sonnet-4.5` → `claude-sonnet-4-5-20250929`
- `claude-opus` → `claude-3-opus-20240229`
- `gemini-2.5-pro` → `gemini-2.0-pro-exp`
- `gemini-1.5-pro` → `gemini-1.5-pro`
- `gemini-2.5-flash` → `gemini-2.0-flash-exp`

## Testing

A test script is provided to verify the new features:

```bash
cd backend
python test_new_features.py
```

This script tests:
- Temperature and top_p parameters
- Different model variants
- Custom prompt functionality
- Backward compatibility

## Important Notes

1. **Custom Prompts:** When using custom prompts, ensure the output still follows the expected format for proper validation
2. **Temperature/Top-P:** These parameters affect both the generator and formatter stages
3. **Model Availability:** Some models may require specific API keys or permissions
4. **Backward Compatibility:** The original "claude" and "gemini" model names still work for compatibility

## UI Screenshots

The updated UI includes:
- Model dropdown with grouped options
- Temperature and Top-P sliders with numeric inputs
- Custom prompt section with toggle and textarea
- Visual feedback for all controls

## Troubleshooting

**Issue:** Model not available
**Solution:** Ensure you have the correct API keys set for the model provider

**Issue:** Custom prompt not producing valid output
**Solution:** Check that your prompt instructs the model to follow the required format (MCQ or NMCQ structure)

**Issue:** Temperature/Top-P not affecting output
**Solution:** Verify the values are within range (0.0-1.0) and try more extreme values to see the effect

## Future Enhancements
- Save and load custom prompt templates
- Preset configurations for different use cases
- Per-model default temperature/top-p values
- Prompt template library
