# Prompt Loading Error Fix

## Error Details

```
2025-11-06 10:39:44 [error] Draft generation error: 'mcq_generator'
```

This error occurred when trying to generate a draft using the new two-step generation process.

## Root Cause

The error was caused by a mismatch in how prompts were stored vs. how they were accessed:

1. **`load_prompts_node()` function** stores prompts with generic keys:
   ```python
   state["prompts"] = {
       "generator": prompts["mcq_generator"],  # Stored as "generator"
       "formatter": prompts["mcq_formatter"]   # Stored as "formatter"
   }
   ```

2. **`run_stream_draft_only()` method** was trying to access with specific keys:
   ```python
   prompt_key = "mcq_generator"  # Looking for "mcq_generator"
   prompt_template = state['prompts'][prompt_key]  # KeyError!
   ```

## The Fix

Instead of using `load_prompts_node()` which has a specific structure for the full pipeline, the new streaming methods now:

1. Load all prompts directly using `PromptLoader.load_prompts()`
2. Select the appropriate prompt based on content type

### Updated Code in `run_stream_draft_only()`:

```python
# Load all prompts directly
all_prompts = PromptLoader.load_prompts()

# Select the appropriate generator prompt based on content type
if content_type.upper() == "MCQ":
    prompt_template = all_prompts.get("mcq_generator", "")
elif content_type.upper() == "NMCQ":
    prompt_template = all_prompts.get("nmcq_generator", "")
elif content_type.upper() == "SUMMARY":
    prompt_template = all_prompts.get("summary_generator", "")
```

### Updated Code in `run_stream_format_only()`:

```python
# Load all prompts directly
all_prompts = PromptLoader.load_prompts()

# Select the appropriate formatter prompt based on content type
if content_type.upper() == "MCQ":
    prompt_template = all_prompts.get("mcq_formatter", "")
elif content_type.upper() == "NMCQ":
    prompt_template = all_prompts.get("nmcq_formatter", "")
elif content_type.upper() == "SUMMARY":
    prompt_template = all_prompts.get("summary_formatter", "")
```

## Files Modified

- `backend/pipeline.py`
  - `run_stream_draft_only()` method (lines 593-631)
  - `run_stream_format_only()` method (lines 743-772)

## Testing

After applying the fix:

1. Restart the backend server
2. Try generating content through the UI
3. The two-step process should work:
   - Click "Generate Content" → Draft streams successfully
   - Click "Format Draft" → Formatting streams successfully

## Benefits of This Approach

1. **Simpler**: Direct prompt loading without intermediate state manipulation
2. **Clearer**: Explicit mapping between content type and prompt file
3. **Consistent**: Both draft and format methods use the same approach
4. **Maintainable**: Easy to add new content types in the future
