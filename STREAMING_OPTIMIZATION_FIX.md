# Streaming Optimization: Eliminating Redundant Text in Complete Events

## Problem
After streaming content token-by-token, the `draft_complete` and `format_complete` events were sending the entire text again in the JSON response. This caused several issues:
1. **Bandwidth waste**: Doubling the data transmission
2. **Performance impact**: Large JSON payloads can be slow to parse
3. **Potential errors**: Large JSON responses could hit size limits

## Example of the Problem

```
event: draft_token
data: {"token": "This", "stage": "generator"}

event: draft_token
data: {"token": " is", "stage": "generator"}

event: draft_token
data: {"token": " content", "stage": "generator"}

event: draft_complete
data: {"success": true, "draft_1": "This is content....[ENTIRE TEXT AGAIN]", ...}
```

The entire content was being sent twice - once as individual tokens, then again in the complete event.

## The Solution

### Backend Changes (`backend/pipeline.py`)

1. **`run_stream_draft_only` method**:
   - Removed `draft_1` from the `draft_complete` event
   - Added `"streamed": True` flag to indicate content was already streamed
   - Added `draft_length` to metadata for debugging

2. **`run_stream_format_only` method**:
   - Removed `output` from the `format_complete` event
   - Added `"streamed": True` flag
   - Added `output_length` to metadata

### Frontend Changes (`frontend/pages/index.tsx`)

1. **Added refs for streaming content**:
   ```typescript
   const streamingDraftRef = useRef<string>('');
   const streamingFormattedRef = useRef<string>('');
   ```

2. **Updated token handlers to update refs**:
   ```typescript
   onDraftToken: (token: string) => {
     setStreamingDraft(prev => {
       const newContent = prev + token;
       streamingDraftRef.current = newContent; // Store in ref
       return newContent;
     });
   }
   ```

3. **Updated complete handlers to use refs**:
   ```typescript
   onComplete: (result: any) => {
     if (result.streamed) {
       // Use accumulated content from ref
       setStreamDraft(streamingDraftRef.current);
     }
   }
   ```

## Benefits

1. **Reduced bandwidth**: ~50% reduction in data transfer for long content
2. **Faster response**: No need to parse large JSON payloads
3. **Better streaming experience**: Cleaner separation between streaming and metadata
4. **Memory efficiency**: Avoids duplicate string storage in memory

## New Event Structure

### Before
```json
{
  "event": "draft_complete",
  "data": {
    "success": true,
    "draft_1": "[ENTIRE CONTENT HERE - REDUNDANT]",
    "metadata": {...}
  }
}
```

### After
```json
{
  "event": "draft_complete",
  "data": {
    "success": true,
    "streamed": true,
    "metadata": {
      "draft_length": 1234,
      ...
    }
  }
}
```

## Testing

Use the test script to verify the optimization:

```bash
python backend/test_no_redundant_text.py
```

This will confirm that:
1. Tokens are streamed individually
2. Complete events don't contain redundant text
3. The `streamed` flag is present
4. Metadata includes content length for debugging

## Backward Compatibility

The frontend includes fallback logic:
- If `streamed: true` → Use accumulated tokens from ref
- If `draft_1` or `output` is provided → Use that (backward compatibility)

This ensures the system works with both old and new backend versions.
