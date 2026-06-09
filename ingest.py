import argparse
import json
import os
import sys
import traceback
from pathlib import Path
from cleaner import clean_file
from classifier import classify_file
from chunker import chunk_file

# Force stdout to use UTF-8 encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Root path configuration
ROOT_DIR = Path(__file__).parent.resolve()
EXTRACTED_DIR = ROOT_DIR / "extracted_json"
CLEANED_DIR = ROOT_DIR / "cleaned_json"
CLASSIFIED_DIR = ROOT_DIR / "classified_json"
CHUNKED_DIR = ROOT_DIR / "chunked_json"
STATE_FILE = ROOT_DIR / "processing_state.json"


def load_state() -> dict:
    """Load current progress state from file."""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
        except Exception as e:
            print(f"Warning: Could not read state file, initializing fresh: {e}")
    return {"vagad": {}, "kvo": {}}


def save_state(state: dict):
    """Save progress state to file."""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def process_pipeline(source: str, state: dict):
    """
    Process all JSON files for a given source (vagad or kvo) through:
    1. Text Cleaning
    2. Page-level Classification
    3. Semantic Chunking
    """
    source_extracted_dir = EXTRACTED_DIR / source
    
    if not source_extracted_dir.exists():
        print(f"Directory not found: {source_extracted_dir}")
        return

    # Find all extracted JSON files
    json_files = sorted(source_extracted_dir.glob("*.json"))
    print(f"\n--- Ingesting {source.upper()} ({len(json_files)} files) ---")

    # Initialize state keys if not present
    if source not in state:
        state[source] = {}

    for idx, json_path in enumerate(json_files):
        filename = json_path.name
        
        # Initialize file state if new
        if filename not in state[source]:
            state[source][filename] = {
                "cleaned": False,
                "classified": False,
                "chunked": False
            }

        file_state = state[source][filename]
        
        # Check if file is fully processed
        if file_state["cleaned"] and file_state["classified"] and file_state["chunked"]:
            # Fully done, skip
            continue
            
        print(f"[{idx+1}/{len(json_files)}] Pipeline processing: {filename}")

        # Step 1: Clean
        if not file_state["cleaned"]:
            try:
                input_path = json_path
                output_path = CLEANED_DIR / source / filename
                print(f"  Cleaning text...")
                clean_file(input_path, output_path)
                file_state["cleaned"] = True
                save_state(state)
            except Exception as e:
                print(f"  Error cleaning {filename}: {e}")
                traceback.print_exc()
                return  # Terminate pipeline on error

        # Step 2: Classify (Gemini API)
        if not file_state["classified"]:
            try:
                input_path = CLEANED_DIR / source / filename
                output_path = CLASSIFIED_DIR / source / filename
                print(f"  Classifying pages (Gemini API)...")
                classify_file(input_path, output_path)
                file_state["classified"] = True
                save_state(state)
            except Exception as e:
                err_str = str(e).lower()
                # Stop processing on Quota limits
                if "quota" in err_str or "429" in err_str or "limit" in err_str:
                    print(f"\n[CRITICAL] API Quota Exceeded. Stopping ingestion pipeline safely. State saved.")
                    sys.exit(0)
                print(f"  Error classifying {filename}: {e}")
                traceback.print_exc()
                return  # Terminate on error

        # Step 3: Chunk
        if not file_state["chunked"]:
            try:
                input_path = CLASSIFIED_DIR / source / filename
                output_path = CHUNKED_DIR / source / filename
                print(f"  Generating semantic chunks...")
                chunk_file(input_path, output_path)
                file_state["chunked"] = True
                save_state(state)
            except Exception as e:
                print(f"  Error chunking {filename}: {e}")
                traceback.print_exc()
                return  # Terminate on error

        print(f"  Completed pipeline for {filename}\n")

    print(f"Ingestion pipeline completed for {source.upper()}.")


def main():
    parser = argparse.ArgumentParser(description="Multilingual Community RAG Ingestion Pipeline")
    parser.add_argument(
        "--source", 
        choices=["vagad", "kvo", "all"], 
        default="all", 
        help="Select the source publication to process (default: all)"
    )
    args = parser.parse_args()

    # Create directory structure
    for d in ["cleaned_json", "classified_json", "chunked_json"]:
        for s in ["vagad", "kvo"]:
            (ROOT_DIR / d / s).mkdir(parents=True, exist_ok=True)

    state = load_state()

    try:
        if args.source == "all":
            process_pipeline("vagad", state)
            process_pipeline("kvo", state)
        else:
            process_pipeline(args.source, state)
    except KeyboardInterrupt:
        print("\nPipeline execution cancelled by user. State saved safely.")


if __name__ == "__main__":
    main()
