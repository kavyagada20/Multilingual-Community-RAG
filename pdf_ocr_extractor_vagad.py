import fitz           # PyMuPDF  — renders PDF pages as images
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image
import json, os, re, sys, time
from pathlib import Path

# Force stdout to use UTF-8 encoding so Gujarati/Unicode prints correctly in Windows terminal
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# ----------------------------------------------------------------
# CONFIG — change these if your folders are different
INPUT_FOLDER  = r"C:\Users\kavyagada\Downloads\Multilingual-Community-RAG\vagad patrika"
OUTPUT_FOLDER = r"C:\Users\kavyagada\Downloads\Multilingual-Community-RAG\extracted_json\vagad"
# ----------------------------------------------------------------

# Load environment variables (API Key)
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found in environment variables. "
        "Please create a .env file in the root directory containing:\n"
        "GEMINI_API_KEY=your_api_key"
    )

print("Initializing Gemini API Client...")
genai.configure(api_key=api_key, transport='rest')
model = genai.GenerativeModel("gemini-3.1-flash-lite")
print("Model ready.\n")


def get_pdf_date(filename):
    """
    Pull the publication date from filename.
    Example: '01-04-2026.pdf'  →  '2026-04-01'
    """
    match = re.search(r'(\d{2})-(\d{2})-(\d{4})', filename)
    if match:
        day, month, year = match.groups()
        return f"{year}-{month}-{day}"   # ISO format YYYY-MM-DD
    return "unknown"


def extract_one_page(page, page_num, filename, pub_date):
    """
    Convert one PDF page → PNG image → run OCR via Gemini API → return structured data.
    The image file is temporary and deleted after OCR.
    """
    # Step A: Render the page as an image at 300 DPI
    mat = fitz.Matrix(300 / 72, 300 / 72)
    pix = page.get_pixmap(matrix=mat)

    # Save as temporary file (unique by process ID to avoid locking conflicts)
    img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"temp_page_{os.getpid()}.png")
    pix.save(img_path)

    # Step B: Run Gemini OCR on the image
    full_text = ""
    try:
        # Respect Gemini API free tier rate limits (15 RPM -> 5.5 seconds per request)
        time.sleep(5.5)
        
        with Image.open(img_path) as img:
            response = model.generate_content([
                "Perform OCR on this image. Extract all text (both Gujarati and English) exactly as it appears. "
                "Do not translate, do not summarize, and do not add any comments or extra formatting. "
                "Just output the recognized text.",
                img
            ])
            full_text = response.text.strip()
    except Exception as e:
        err_msg = str(e).lower()
        if "quota" in err_msg or "429" in err_msg or "limit" in err_msg:
            print(f"\nCRITICAL ERROR: API quota/limit exceeded. Stopping script to prevent generating empty JSONs.")
            print(f"Details: {e}")
            raise e
        print(f"    Warning: OCR failed for page {page_num} with error: {e}")

    # Step C: Delete the temporary image
    if os.path.exists(img_path):
        os.remove(img_path)

    return {
        "source":           filename,
        "publication_date": pub_date,
        "page_num":         page_num,
        "text":             full_text,
        "char_count":       len(full_text),
        "method":           "gemini-3.1-flash-lite-ocr"
    }


def process_one_pdf(pdf_path, output_file):
    """Process all pages of one PDF. Saves page-by-page to output_file."""
    filename = Path(pdf_path).name
    pub_date = get_pdf_date(filename)

    print(f"  Publication date: {pub_date}")
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    
    # Load existing progress if any
    pages_data = []
    if output_file.exists():
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                pages_data = json.load(f)
            print(f"  Resuming: Found {len(pages_data)} pages already processed in {output_file.name}")
        except Exception as e:
            print(f"  Warning: Could not read existing JSON {output_file.name}, starting fresh: {e}")
            pages_data = []

    # Map existing processed page numbers
    processed_pages = {p["page_num"] for p in pages_data if p.get("char_count", 0) > 0}

    for i, page in enumerate(doc):
        page_num = i + 1
        if page_num in processed_pages:
            # Skip page since it was already successfully processed
            continue
            
        print(f"  Extracting page {page_num} of {total_pages}...", flush=True)
        result = extract_one_page(page, page_num, filename, pub_date)
        
        # Replace existing placeholder entry or append
        existing_idx = next((idx for idx, p in enumerate(pages_data) if p["page_num"] == page_num), None)
        if existing_idx is not None:
            pages_data[existing_idx] = result
        else:
            pages_data.append(result)

        print(f"    -> {result['char_count']} characters extracted")

        # Save JSON immediately after this page
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(pages_data, f, ensure_ascii=False, indent=2)

    doc.close()
    return pages_data


def run_batch():
    """Process all PDFs in INPUT_FOLDER, save JSON to OUTPUT_FOLDER."""
    Path(OUTPUT_FOLDER).mkdir(exist_ok=True)
    pdfs = sorted(Path(INPUT_FOLDER).glob("*.pdf"))

    if not pdfs:
        print(f"No PDF files found in {INPUT_FOLDER}")
        return

    print(f"Found {len(pdfs)} PDF files")
    print(f"Each PDF has ~17-18 pages")
    print(f"Estimated total time: ~6-10 hours (run overnight)\n")

    for idx, pdf_path in enumerate(pdfs):
        output_file = Path(OUTPUT_FOLDER) / f"{pdf_path.stem}.json"

        # Check if the file is completely processed
        if output_file.exists():
            try:
                # Open PDF to get total pages
                doc = fitz.open(str(pdf_path))
                total_pdf_pages = len(doc)
                doc.close()
                
                # Check how many pages are in JSON
                with open(output_file, "r", encoding="utf-8") as f:
                    saved_pages = json.load(f)
                
                # If we have all pages and they all have content
                if len(saved_pages) >= total_pdf_pages and all(p.get("char_count", 0) > 0 for p in saved_pages):
                    print(f"[{idx+1}/{len(pdfs)}] Already done, skipping: {pdf_path.name}")
                    continue
            except Exception:
                # If error reading JSON or PDF, we don't skip it
                pass

        print(f"[{idx+1}/{len(pdfs)}] Processing: {pdf_path.name}")
        pages_data = process_one_pdf(str(pdf_path), output_file)

        total_chars = sum(p["char_count"] for p in pages_data)
        print(f"  Finished: {output_file.name} ({total_chars:,} total chars)\n")

    print("=" * 50)
    print("ALL DONE. Checking quality...")
    check_quality()


def check_quality():
    """Print a summary to know if extraction worked well."""
    jsons = list(Path(OUTPUT_FOLDER).glob("*.json"))
    total = good = empty = 0

    for jf in jsons:
        with open(jf, encoding="utf-8") as f:
            pages = json.load(f)
        for p in pages:
            total += 1
            if p["char_count"] > 200:
                good += 1
            elif p["char_count"] < 50:
                empty += 1

    print(f"Total pages     : {total}")
    print(f"Good (>200 chars) : {good}  ({100*good//max(1,total)}%)")
    print(f"Empty (<50 chars) : {empty}")
    if good / max(1, total) > 0.75:
        print("\n[OK] Extraction looks good! Proceed to next phase.")
    else:
        print("\n[WARNING] Many empty pages. Check PDF quality or try DPI=400.")


# Run it
run_batch()
