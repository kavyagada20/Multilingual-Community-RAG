import re
import json
import sys
from pathlib import Path

# Force stdout to use UTF-8 encoding so Gujarati/Unicode prints correctly in Windows terminal
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def clean_text(text: str) -> str:
    """
    Clean OCR text block:
    - Normalize carriage returns to standard newlines.
    - Remove duplicate/multiple spaces.
    - Trim trailing/leading whitespace of each line.
    - Replace 3 or more consecutive newlines with exactly 2 newlines (normalize paragraph breaks).
    - Strip general leading/trailing document whitespace.
    """
    if not text:
        return ""
    
    # 1. Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # 2. Trim whitespace on each line and remove redundant spaces
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        # Replace multiple spaces with a single space
        line = re.sub(r' {2,}', ' ', line)
        line = line.strip()
        cleaned_lines.append(line)
        
    text = '\n'.join(cleaned_lines)
    
    # 3. Replace 3+ consecutive newlines with 2 newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

def clean_file(input_json_path: Path, output_json_path: Path):
    """
    Load extracted JSON, clean text page-by-page, and save to output.
    """
    with open(input_json_path, "r", encoding="utf-8") as f:
        pages_data = json.load(f)
        
    cleaned_pages = []
    for page in pages_data:
        cleaned_page = page.copy()
        original_text = page.get("text", "")
        cleaned_text = clean_text(original_text)
        
        cleaned_page["text"] = cleaned_text
        cleaned_page["char_count"] = len(cleaned_text)
        cleaned_page["original_char_count"] = len(original_text)
        cleaned_page["method"] = page.get("method", "gemini-3.1-flash-lite-ocr") + "-cleaned"
        
        cleaned_pages.append(cleaned_page)
        
    # Ensure parent directory exists
    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_pages, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    # Test execution
    test_text = "  શ્રી વાગડ  વિશા   ઓસવાળ   \n\n\n\n  મામા - ભાણેજ   \n  "
    print("Original:")
    print(repr(test_text))
    print("\nCleaned:")
    print(repr(clean_text(test_text)))
