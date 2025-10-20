# Quick Configuration Reference Card

## 🚀 Most Common Tasks

### Update Model Version
```bash
# Edit .env file
CLAUDE_MODEL=claude-3.5-sonnet-NEW_VERSION
GEMINI_PRO=gemini-2.5-pro-NEW_VERSION
GEMINI_FLASH=gemini-2.5-flash-NEW_VERSION

# Restart backend
cd backend && python run.py
```

### Adjust Output Quality
```bash
# For MORE creative/varied outputs:
MODEL_TEMPERATURE=0.7  # (default: 0.51)
MODEL_TOP_P=0.98       # (default: 0.95)

# For MORE consistent/predictable outputs:
MODEL_TEMPERATURE=0.3  # (default: 0.51)
MODEL_TOP_P=0.85       # (default: 0.95)
```

### Change Input/Output Limits
```bash
MAX_INPUT_CHARS=750000    # (default: 500000)
MODEL_MAX_TOKENS=12000    # (default: 8000)
MODEL_TIMEOUT=120         # (default: 60)
```

## 📁 Key Files

| File | Purpose |
|------|---------|
| `.env` | Local environment variables |
| `backend/config.py` | Default configuration values |
| `backend/pipeline.py` | Model initialization & calls |
| `backend/prompts/*.txt` | Prompt templates |

## 🧪 Test Commands

```bash
# Check current configuration
cd backend
python -c "from config import settings; print(f'Temperature: {settings.model_temperature}')"

# Test MCQ generation
python test_cli.py generate --type MCQ --model claude

# Test NMCQ generation
python test_cli.py generate --type NMCQ --model gemini

# Run all tests
python test_all_features.py
```

## ☁️ Cloud Run Deployment

```bash
# Deploy with new settings
gcloud run deploy microlearning-generator \
  --update-env-vars="MODEL_TEMPERATURE=0.7,CLAUDE_MODEL=new-model-name"

# View current settings
gcloud run services describe microlearning-generator \
  --region=us-central1 --format="value(spec.template.spec.containers[0].env[].value)"
```

## 🔢 Parameter Ranges

| Parameter | Min | Max | Default | Sweet Spot |
|-----------|-----|-----|---------|------------|
| Temperature | 0.0 | 1.0 | 0.51 | 0.4-0.7 |
| Top-P | 0.0 | 1.0 | 0.95 | 0.85-0.95 |
| Max Tokens | 100 | 32000 | 8000 | 5000-10000 |
| Timeout (sec) | 10 | 300 | 60 | 60-120 |
| Input Chars | 100 | 1M | 500k | 100k-500k |
| Retries | 0 | 3 | 1 | 1-2 |

## ⚠️ Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| "Model not found" | Check exact model name spelling |
| "Rate limit exceeded" | Increase MODEL_TIMEOUT, add delays |
| "Output truncated" | Increase MODEL_MAX_TOKENS |
| "Too random outputs" | Decrease MODEL_TEMPERATURE |
| "Validation failures" | Increase MAX_FORMATTER_RETRIES |
| "Input too large" | Increase MAX_INPUT_CHARS |

## 📊 Model Comparison

| Model | Best For | Speed | Cost |
|-------|----------|-------|------|
| Claude Sonnet 4.5 | Complex reasoning, nuanced content | Medium | Higher |
| Gemini 2.5 Pro | Balanced performance, general use | Fast | Medium |
| Gemini 2.5 Flash | Quick formatting, simple tasks | Very Fast | Lower |

## 🎯 Optimization Tips

1. **Start conservative:** Temperature 0.4-0.5 for production
2. **Test incrementally:** Change by ±0.1 at a time
3. **Monitor costs:** Higher tokens = higher costs
4. **Cache results:** Reuse outputs when possible
5. **Batch requests:** Process multiple items together

## 📝 Environment Template

```bash
# Copy to .env and customize
GOOGLE_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
EDITOR_PASSWORD=your_password
APP_SECRET=your_secret

# Models (update versions here)
CLAUDE_MODEL=claude-sonnet-4-5-20250929
GEMINI_PRO=gemini-2.5-pro
GEMINI_FLASH=gemini-2.5-flash

# Parameters (adjust as needed)
MODEL_TEMPERATURE=0.51
MODEL_TOP_P=0.95
MODEL_MAX_TOKENS=8000
MODEL_TIMEOUT=60
MAX_INPUT_CHARS=500000
MAX_FORMATTER_RETRIES=1
```

---
*Keep this reference handy for quick configuration changes!*
