import os
import json
import time
import sys
import re
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv

# Force stdout to use UTF-8 encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Load env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")

genai.configure(api_key=api_key, transport='rest')
model = genai.GenerativeModel("gemini-3.1-flash-lite")

CATEGORIES = [
    "Marriage", "Death", "Sports", "Advertisement", 
    "Business", "Religious", "Event", "Trust Notice", "Other"
]

CLASSIFIER_PROMPT = """
You are an expert archive cataloger. Categorize the given newspaper page text (which may contain a mix of Gujarati and English) into one or more of the following categories:
- Marriage (wedding invites, congratulations, match-making notices, etc.)
- Death (obituaries, condolences, prayer meetings/prarthana sabha details, etc.)
- Sports (tournaments, congratulations to sports achievements, etc.)
- Advertisement (commercial services, products, shops, home loans, classes, etc.)
- Business (job notices, hiring, partnership offers, business listings, etc.)
- Religious (temple events, dhwajarohan, diksha, discourse/katha details, etc.)
- Event (social gatherings, seminars, general non-religious community programs, exhibitions, etc.)
- Trust Notice (community general meetings, election notifications, balance sheet summaries, updates from trust boards, etc.)
- Other (anything not fitting the above, like general articles or standard non-informative headers/footers)

Guidelines:
1. You can choose MULTIPLE categories if the page contains multiple sections or advertisements.
2. Provide a brief, concise rationale (1-2 sentences) explaining why you chose these categories.
3. Be highly accurate, especially for Death (prarthana sabha) and Marriage.

TEXT:
\"\"\"
{text}
\"\"\"
"""

# JSON schema definition for structured output
GENERATION_CONFIG = {
    "response_mime_type": "application/json",
    "response_schema": {
        "type": "OBJECT",
        "properties": {
            "categories": {
                "type": "ARRAY",
                "items": {
                    "type": "STRING",
                    "enum": CATEGORIES
                },
                "description": "Selected categories that apply to this page."
            },
            "rationale": {
                "type": "STRING",
                "description": "Brief explanation for the categorization."
            }
        },
        "required": ["categories", "rationale"]
    }
}

def classify_page(text: str, max_retries: int = 3) -> dict:
    """
    Call Gemini API to classify the page text with retry backoff.
    """
    if not text.strip() or len(text.strip()) < 10:
        return {"categories": ["Other"], "rationale": "Empty or extremely short page text."}
        
    for attempt in range(max_retries):
        try:
            # Respect rate limit strictly (15 RPM -> 5.5 seconds delay between requests)
            time.sleep(5.5)
            
            response = model.generate_content(
                CLASSIFIER_PROMPT.format(text=text),
                generation_config=GENERATION_CONFIG
            )
            
            # Parse response JSON
            result = json.loads(response.text.strip())
            return result
        except Exception as e:
            err_str = str(e).lower()
            # If rate limit (429) or quota limit, raise immediately so orchestrator can stop and save state
            if "quota" in err_str or "429" in err_str or "limit" in err_str:
                print(f"\nCRITICAL: API limit exceeded during classification: {e}")
                raise e
                
            print(f"  Attempt {attempt+1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                # Fallback to Other on persistent failures
                return {
                    "categories": ["Other"],
                    "rationale": f"API classification failed repeatedly: {e}"
                }

def classify_file(input_json_path: Path, output_json_path: Path):
    """
    Classify each page of the JSON file and save to the output path.
    """
    with open(input_json_path, "r", encoding="utf-8") as f:
        pages_data = json.load(f)
        
    classified_pages = []
    print(f"  Classifying {input_json_path.name} ({len(pages_data)} pages)...")
    
    for page in pages_data:
        page_num = page.get("page_num")
        page_text = page.get("text", "")
        
        print(f"    Classifying page {page_num}...", end="", flush=True)
        classification = classify_page(page_text)
        print(f" categories: {classification.get('categories')}")
        
        classified_page = page.copy()
        classified_page["categories"] = classification.get("categories", ["Other"])
        classified_page["rationale"] = classification.get("rationale", "")
        classified_page["method"] = page.get("method", "") + "-classified"
        
        classified_pages.append(classified_page)
        
    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(classified_pages, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    # Quick self-test
    test_str = "સ્વ. વેલજી ખીમજી ગડા (ઉં.વ. ૮૨) નું મરણ થયેલ છે. શોકાતુર ગડા પરિવાર."
    print("Testing classification of obituary text...")
    res = classify_page(test_str)
    print(json.dumps(res, indent=2))
