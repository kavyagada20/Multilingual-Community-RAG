import json
import re
from pathlib import Path

def split_into_sentences(text: str) -> list:
    """
    Split a text block into sentences based on Gujarati/English punctuation.
    """
    # Split by periods, question marks, exclamation marks, or newlines
    sentence_endings = re.compile(r'([.?!।|])')
    parts = sentence_endings.split(text)
    
    sentences = []
    # Reassemble the split parts with their punctuation
    for i in range(0, len(parts) - 1, 2):
        sentence = (parts[i] + parts[i+1]).strip()
        if sentence:
            sentences.append(sentence)
    if len(parts) % 2 != 0:
        last_part = parts[-1].strip()
        if last_part:
            sentences.append(last_part)
            
    return sentences

def build_page_chunks(text: str, target_size: int = 1000, overlap_size: int = 150) -> list:
    """
    Generate paragraph-based semantic chunks:
    - Split by paragraphs first.
    - If a paragraph is too long (> target_size), split it into sentences.
    - Group items into chunks of ~800-1000 characters.
    - Ensure an overlap of ~100-150 characters between consecutive chunks.
    """
    if not text.strip():
        return []

    # 1. Break text into semantic units (paragraphs, or sentences if paragraph is too large)
    paragraphs = text.split('\n\n')
    units = []
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(para) <= target_size:
            units.append(para)
        else:
            # Paragraph is too large; split into sentences to maintain size limits
            sentences = split_into_sentences(para)
            for sentence in sentences:
                if len(sentence) <= target_size:
                    units.append(sentence)
                else:
                    # If a single sentence is still too large, split by words (hard limit)
                    words = sentence.split(' ')
                    current_sub = []
                    current_len = 0
                    for word in words:
                        if current_len + len(word) + 1 <= target_size:
                            current_sub.append(word)
                            current_len += len(word) + 1
                        else:
                            units.append(" ".join(current_sub))
                            current_sub = [word]
                            current_len = len(word)
                    if current_sub:
                        units.append(" ".join(current_sub))

    # 2. Group units into chunks with overlap
    chunks = []
    current_units = []
    current_len = 0

    for i, unit in enumerate(units):
        unit_len = len(unit)
        
        # If adding the unit fits within our target size
        if current_len + (2 if current_len > 0 else 0) + unit_len <= target_size:
            current_units.append(unit)
            current_len += (2 if current_len > 0 else 0) + unit_len
        else:
            # Finalize current chunk
            if current_units:
                chunk_text = "\n\n".join(current_units)
                chunks.append(chunk_text)
            
            # Start new chunk with overlap
            # Find how many units from the end of current_units we can carry over to fit the overlap
            overlap_units = []
            overlap_len = 0
            for prev_unit in reversed(current_units):
                prev_len = len(prev_unit)
                if overlap_len + prev_len + (2 if overlap_len > 0 else 0) <= overlap_size:
                    overlap_units.insert(0, prev_unit)
                    overlap_len += prev_len + (2 if overlap_len > 0 else 0)
                else:
                    break
            
            current_units = overlap_units + [unit]
            current_len = sum(len(u) for u in current_units) + (2 * (len(current_units) - 1) if len(current_units) > 1 else 0)

    # Add final remaining units
    if current_units:
        chunk_text = "\n\n".join(current_units)
        # Avoid duplicate chunk if it is exactly the same as the last one
        if not chunks or chunks[-1] != chunk_text:
            chunks.append(chunk_text)

    # 3. Guardrail: If no chunks were generated (e.g. text was very short)
    if not chunks and text.strip():
        chunks.append(text.strip())

    return chunks

def chunk_file(input_json_path: Path, output_json_path: Path):
    """
    Load classified JSON file, chunk text page-by-page preserving categories,
    and save the list of chunks with metadata.
    """
    with open(input_json_path, "r", encoding="utf-8") as f:
        pages_data = json.load(f)

    all_chunks = []
    source_name = input_json_path.name

    for page in pages_data:
        page_num = page.get("page_num")
        page_text = page.get("text", "")
        categories = page.get("categories", ["Other"])
        pub_date = page.get("publication_date", "unknown")
        
        page_chunks = build_page_chunks(page_text)
        
        for idx, chunk_text in enumerate(page_chunks):
            all_chunks.append({
                "chunk_id": f"{source_name.split('.')[0]}_p{page_num}_c{idx+1}",
                "source": source_name.replace(".json", ".pdf"),
                "publication_date": pub_date,
                "page_num": page_num,
                "chunk_num": idx + 1,
                "categories": categories,
                "text": chunk_text,
                "char_count": len(chunk_text),
                "method": "paragraph-semantic-chunking"
            })

    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)
    
    print(f"  Chunked {source_name}: generated {len(all_chunks)} chunks.")

if __name__ == "__main__":
    # Self-test chunking
    test_text = "\n\n".join([f"Paragraph {i}: This is some sample text for paragraph {i}. " * 5 for i in range(1, 10)])
    print(f"Total length: {len(test_text)}")
    res = build_page_chunks(test_text)
    for idx, c in enumerate(res):
        print(f"\n--- Chunk {idx+1} (Len: {len(c)}) ---")
        print(c)
