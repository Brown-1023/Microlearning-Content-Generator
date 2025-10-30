# Prompts Reset to Defaults - Fixed!

## Problem Solved
The "Reset All to Defaults" button in the admin panel now properly resets prompts to their original default values, not to the last saved custom prompts.

## How It Works

### 1. Automatic Backup Creation
When the backend starts for the first time, it automatically creates backup copies of all original prompt files:
- `mcq.generator.txt` → `mcq.generator.default.txt`
- `mcq.formatter.txt` → `mcq.formatter.default.txt`
- `nonmcq.generator.txt` → `nonmcq.generator.default.txt`
- `nonmcq.formatter.txt` → `nonmcq.formatter.default.txt`
- `summarybytes.generator.txt` → `summarybytes.generator.default.txt`
- `summarybytes.formatter.txt` → `summarybytes.formatter.default.txt`

### 2. Three Separate API Endpoints

#### `/api/prompts` (GET)
- Returns the **current** prompts (may be modified by admin)
- Used when loading the admin panel

#### `/api/prompts/defaults` (GET)
- Returns the **original default** prompts from backup files
- Used for the reset functionality

#### `/api/prompts/reset` (POST)
- Resets all prompts to their original defaults
- Copies the `.default.txt` files back to the working `.txt` files

### 3. Frontend Changes

The admin panel now:
1. Loads **current prompts** when opened (which may be customized)
2. Also loads **original default prompts** separately (for reset functionality)
3. When "Reset All to Defaults" is clicked:
   - Calls the backend to reset prompt files
   - Updates the UI with original defaults
   - Shows success message

## Usage

### For Admins

1. **View Current Prompts**: The prompts shown when you open the admin panel are your current active prompts

2. **Modify Prompts**: 
   - Edit any prompt text
   - Click "Save All Prompts" to save your changes

3. **Reset to Original Defaults**:
   - Click "Reset All to Defaults" button
   - All prompts will be restored to their original values
   - The changes are saved immediately

### Important Notes

- The original default prompts are preserved in `.default.txt` files
- These backup files are created automatically on first run
- The backup files are never modified by the admin panel
- You can always return to the original prompts no matter how many times you've customized them

## Technical Details

### Backend Structure
```
backend/prompts/
├── mcq.generator.txt           # Current working prompt
├── mcq.generator.default.txt   # Original default backup
├── mcq.formatter.txt           # Current working prompt
├── mcq.formatter.default.txt   # Original default backup
└── ... (same pattern for all prompts)
```

### API Responses

**Get Current Prompts**
```
GET /api/prompts
Returns: Current prompts from .txt files
```

**Get Default Prompts**
```
GET /api/prompts/defaults
Returns: Original prompts from .default.txt files
```

**Reset to Defaults**
```
POST /api/prompts/reset
Action: Copies .default.txt → .txt
Returns: Success status and message
```

## Troubleshooting

### If Reset Doesn't Work

1. **Check if backup files exist**:
   ```bash
   ls backend/prompts/*.default.txt
   ```

2. **Recreate backups manually** (if needed):
   ```bash
   # In backend directory
   cd prompts
   for f in *.txt; do
     if [[ ! "$f" == *.default.txt ]]; then
       cp "$f" "${f%.txt}.default.txt"
     fi
   done
   ```

3. **Check permissions**: Ensure the backend has write permissions to the prompts directory

### If Prompts Are Missing

The system will automatically create backup files on startup if they don't exist. Simply restart the backend:
```bash
cd backend
python run.py
```

## Benefits

✅ **True Reset**: Always returns to original defaults, not last saved state
✅ **Preserved Originals**: Original prompts are never lost
✅ **Automatic Backup**: No manual backup needed
✅ **Immediate Feedback**: Success/error messages shown in UI
✅ **Consistent State**: Backend and frontend stay synchronized
