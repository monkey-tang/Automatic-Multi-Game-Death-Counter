# Fuzzy OCR Matching Guide

## What is Fuzzy OCR Matching?

Fuzzy OCR matching handles common OCR misreadings where letters are confused with similar-looking numbers:
- O → 0 (zero)
- I → 1 (one)
- E → 3 (three)
- A → 4 (four)
- S → 5 (five)
- G → 6 (six)
- T → 7 (seven)
- B → 8 (eight)
- Z → 2 (two)

**Example:** If OCR reads "Y0UD13D" instead of "YOUDIED", fuzzy matching will still detect it as a death.

## How to Switch Between Fuzzy and Direct Matching

### Method 1: Edit games_config.json (Recommended)

1. Open `games_config.json` in a text editor
2. Find the `"settings"` section
3. Change the value of `"fuzzy_ocr_matching"`:
   - `true` = Fuzzy matching enabled (handles OCR misreadings)
   - `false` = Direct matching only (faster, but requires exact matches)
4. Save the file
5. Restart the daemon for changes to take effect

**Example:**
```json
{
  "settings": {
    "fuzzy_ocr_matching": false,  // Changed to false for direct matching
    ...
  }
}
```

### Method 2: Default Setting

If you don't specify `"fuzzy_ocr_matching"` in the config, it defaults to `true` (fuzzy matching enabled).

## When to Use Each Mode

### Use Fuzzy Matching (Default) When:
- OCR quality is inconsistent
- Text appears pixelated or low-resolution
- You want maximum detection reliability
- You don't mind slightly slower processing

### Use Direct Matching When:
- OCR quality is consistently high
- Text appears clear and high-resolution
- You want maximum performance
- All keyword variations are already in the keywords list

## Performance Comparison

- **Fuzzy Matching:** Slower (~5-10% overhead), but more robust
- **Direct Matching:** Faster, but requires exact keyword matches in the keywords list

## Current Status

Check the daemon startup log to see which mode is active:
```
Fuzzy OCR Matching: ENABLED (can be changed in games_config.json)
```
or
```
Fuzzy OCR Matching: DISABLED (can be changed in games_config.json)
```

## Notes

- Fuzzy matching only works on English OCR text (not Japanese/other languages)
- The keywords list should still include common variations for best results
- Changing this setting requires a daemon restart to take effect
