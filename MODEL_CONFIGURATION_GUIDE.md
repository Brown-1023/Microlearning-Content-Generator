# Model Configuration Guide

## Quick Reference

This guide provides instructions for configuring and updating AI models in the Microlearning Content Generator pipeline.

## Current Model Configuration

| Role | Model | Environment Variable | Default Value |
|------|-------|---------------------|---------------|
| Generator (Option 1) | Claude Sonnet 4.5 | `CLAUDE_MODEL` | `claude-sonnet-4-5-20250929` |
| Generator (Option 2) | Gemini 2.5 Pro | `GEMINI_PRO` | `gemini-2.5-pro` |
| Formatter | Gemini 2.5 Flash | `GEMINI_FLASH` | `gemini-2.5-flash` |

## Model Parameters

### Separate Controls for Generator and Formatter

The system now provides **separate temperature and top-p controls** for the generator and formatter models:

| Parameter | Environment Variable | Default | Range | Description |
|-----------|---------------------|---------|-------|-------------|
| **Generator Settings** | | | | |
| Generator Temperature | `MODEL_TEMPERATURE` | 0.51 | 0.0-1.0 | Controls randomness in content generation |
| Generator Top-P | `MODEL_TOP_P` | 0.95 | 0.0-1.0 | Nucleus sampling for generation |
| **Formatter Settings** | | | | |
| Formatter Temperature | `MODEL_TEMPERATURE` | 0.51 | 0.0-1.0 | Controls randomness in formatting |
| Formatter Top-P | `MODEL_TOP_P` | 0.95 | 0.0-1.0 | Nucleus sampling for formatting |
| **Other Settings** | | | | |
| Max Tokens | `MODEL_MAX_TOKENS` | 8000 | 1-32000 | Maximum output length |
| Timeout | `MODEL_TIMEOUT` | 60 | 10-300 | API timeout in seconds |
| Max Input | `MAX_INPUT_CHARS` | 500000 | 1-1000000 | Maximum input characters |
| Formatter Retries | `MAX_FORMATTER_RETRIES` | 1 | 0-3 | Retry attempts on validation failure |

### Why Separate Controls?

- **Generator Temperature/Top-P**: Controls how creative and varied the initial content generation is
  - Higher values (0.7-0.9) for more creative, diverse questions
  - Lower values (0.3-0.5) for more focused, predictable content

- **Formatter Temperature/Top-P**: Controls how the content is formatted
  - Lower values (0.1-0.3) for consistent, strict formatting
  - Higher values (0.5-0.7) for more varied formatting styles

This separation allows you to have creative content generation while maintaining strict formatting standards.

## Configuration Methods

### Method 1: Environment Variables (.env file)

Create or edit `.env` file in the project root:

```bash
# Model Versions
CLAUDE_MODEL=claude-sonnet-4-5-20250929
GEMINI_PRO=gemini-2.5-pro
GEMINI_FLASH=gemini-2.5-flash

# Model Parameters
MODEL_TEMPERATURE=0.51
MODEL_TOP_P=0.95
MODEL_MAX_TOKENS=8000
MODEL_TIMEOUT=60

# Pipeline Settings
MAX_INPUT_CHARS=500000
MAX_FORMATTER_RETRIES=1
```

### Method 2: Direct Configuration File Edit

Edit `backend/config.py`:

```python
class Settings(BaseSettings):
    # Model Configuration
    claude_model: str = Field(default="claude-sonnet-4-5-20250929", env="CLAUDE_MODEL")
    gemini_pro: str = Field(default="gemini-2.5-pro", env="GEMINI_PRO")
    gemini_flash: str = Field(default="gemini-2.5-flash", env="GEMINI_FLASH")
    
    # Model Parameters
    model_temperature: float = Field(default=0.51, env="MODEL_TEMPERATURE")
    model_top_p: float = Field(default=0.95, env="MODEL_TOP_P")
    model_max_tokens: int = Field(default=8000, env="MODEL_MAX_TOKENS")
```

### Method 3: Cloud Run Deployment Variables

When deploying to Cloud Run:

```bash
gcloud run deploy microlearning-generator \
  --update-env-vars="CLAUDE_MODEL=claude-3-opus-20240229,MODEL_TEMPERATURE=0.7,MODEL_TOP_P=0.9"
```

## Common Configuration Scenarios

### Scenario 1: Updating to New Claude Model

When Anthropic releases a new model:

```bash
# In .env
CLAUDE_MODEL=claude-3.5-sonnet-20241022  # Example future model

# Test locally
cd backend
python test_cli.py generate --type MCQ --model claude
```

### Scenario 2: Adjusting for More Creative Output

For more varied content generation:

```bash
# In .env
MODEL_TEMPERATURE=0.8  # Increase from 0.51
MODEL_TOP_P=0.98       # Increase from 0.95
```

### Scenario 3: Handling Longer Inputs/Outputs

For processing larger documents:

```bash
# In .env
MAX_INPUT_CHARS=750000   # Increase from 500000
MODEL_MAX_TOKENS=12000   # Increase from 8000
MODEL_TIMEOUT=120        # Increase from 60 seconds
```

### Scenario 4: Improving Consistency

For more predictable outputs:

```bash
# In .env
MODEL_TEMPERATURE=0.3    # Decrease for consistency
MODEL_TOP_P=0.85         # Narrow the sampling
MAX_FORMATTER_RETRIES=2  # Allow more formatting attempts
```

## Pipeline Architecture

```
Input Text → [Generator] → Draft Content → [Formatter] → Formatted Content → [Validator]
                 ↑                              ↑                               ↓
          (Claude or Gemini Pro)         (Gemini Flash)                  (Pass/Fail)
                                                                               ↓
                                                                         (Retry if fail)
```

## Model-Specific Settings

### Claude Models

Claude models support these specific parameters in `backend/pipeline.py`:

```python
response = self.anthropic.messages.create(
    model=model,  # From CLAUDE_MODEL env var
    max_tokens=max_tokens,
    temperature=temperature,
    top_p=top_p,
    messages=[{"role": "user", "content": prompt}]
)
```

### Gemini Models

Gemini models use these settings:

```python
generation_config = {
    "temperature": temperature,  # From MODEL_TEMPERATURE
    "top_p": top_p,             # From MODEL_TOP_P
    "max_output_tokens": max_tokens,  # From MODEL_MAX_TOKENS
}
```

## Testing Configuration Changes

### 1. Verify Current Settings

```bash
cd backend
python -c "from config import settings; import json; print(json.dumps({
    'claude_model': settings.claude_model,
    'gemini_pro': settings.gemini_pro,
    'gemini_flash': settings.gemini_flash,
    'temperature': settings.model_temperature,
    'top_p': settings.model_top_p,
    'max_tokens': settings.model_max_tokens,
    'max_input': settings.max_input_chars
}, indent=2))"
```

### 2. Test Generation with New Settings

```bash
# Test MCQ generation
python test_cli.py generate --type MCQ --model claude --text "Sample educational content about photosynthesis..."

# Test NMCQ generation  
python test_cli.py generate --type NMCQ --model gemini --text "Clinical case about diabetes management..."
```

### 3. Run Validation Suite

```bash
python test_all_features.py
python test_four_prompts.py
```

## Troubleshooting

### Issue: Model Not Found

```bash
Error: Model 'claude-xyz' not found
```
**Solution:** Check exact model name from provider documentation

### Issue: Rate Limiting

```bash
Error: 429 Too Many Requests
```
**Solution:** 
- Increase `MODEL_TIMEOUT`
- Add retry logic with exponential backoff
- Use multiple API keys

### Issue: Output Truncation

```bash
Output appears cut off or incomplete
```
**Solution:**
- Increase `MODEL_MAX_TOKENS`
- Check token limits for specific model
- Consider chunking large inputs

### Issue: Inconsistent Outputs

```bash
Outputs vary too much between runs
```
**Solution:**
- Decrease `MODEL_TEMPERATURE` (try 0.3-0.4)
- Decrease `MODEL_TOP_P` (try 0.8-0.9)
- Review and refine prompt templates

### Issue: Validation Failures

```bash
Formatter output fails validation repeatedly
```
**Solution:**
- Increase `MAX_FORMATTER_RETRIES`
- Adjust temperature for formatter (usually lower is better)
- Review prompt templates for clarity

## Best Practices

1. **Test Before Production:** Always test configuration changes locally first
2. **Gradual Changes:** Adjust parameters incrementally (±0.1 for temperature/top_p)
3. **Document Changes:** Keep a log of configuration changes and their effects
4. **Monitor Costs:** Higher token limits and retries increase API costs
5. **Version Control:** Track configuration changes in git
6. **Backup Settings:** Keep a copy of working configurations
7. **Load Testing:** Test with various input sizes and complexity
8. **Error Handling:** Ensure proper error messages for configuration issues

## Configuration Checklist for New Models

- [ ] Update model name in environment variables
- [ ] Verify API key has access to new model
- [ ] Test with small sample input
- [ ] Run full validation test suite
- [ ] Check output format compatibility
- [ ] Update prompt templates if needed
- [ ] Test with maximum input size
- [ ] Verify cost implications
- [ ] Update documentation
- [ ] Deploy to staging first
- [ ] Monitor logs after deployment
- [ ] Create rollback plan

## Support

For model-specific issues:
- **Claude/Anthropic:** Check [Anthropic Documentation](https://docs.anthropic.com)
- **Gemini/Google:** Check [Google AI Documentation](https://ai.google.dev)
- **Internal:** Review `backend/pipeline.py` for implementation details
