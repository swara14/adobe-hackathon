import fitz  # PyMuPDF
import json
from collections import defaultdict
import sys

def extract_text_elements(doc):
    elements = []
    for page_number in range(min(len(doc), 50)):
        page = doc[page_number]
        blocks = page.get_text("dict")["blocks"]

        for b in blocks:
            for l in b.get("lines", []):
                for s in l.get("spans", []):
                    if s['text'].strip():  # skip empty
                        elements.append({
                            "text": s['text'].strip(),
                            "size": round(s['size'], 1),
                            "font": s['font'],
                            "bold": "Bold" in s['font'],
                            "page": page_number + 1,
                            "x": s['bbox'][0],
                            "y": s['bbox'][1],
                        })
    return elements

def detect_title(elements):
    # Heuristic: largest bold text near top of first page
    first_page_elements = [e for e in elements if e['page'] == 1]
    candidates = sorted(first_page_elements, key=lambda e: (-e['size'], e['y']))
    for e in candidates:
        if e['bold'] and len(e['text'].split()) > 2:
            return e['text']
    return candidates[0]['text'] if candidates else "Unknown Title"

def classify_headings(elements):
    # Get unique font sizes
    size_freq = defaultdict(int)
    for e in elements:
        size_freq[e['size']] += 1

    # Assume top 3 largest sizes are H1 > H2 > H3
    top_sizes = sorted(size_freq.keys(), reverse=True)[:3]
    size_to_level = {}
    if len(top_sizes) > 0:
        size_to_level[top_sizes[0]] = "H1"
    if len(top_sizes) > 1:
        size_to_level[top_sizes[1]] = "H2"
    if len(top_sizes) > 2:
        size_to_level[top_sizes[2]] = "H3"

    headings = []
    for e in elements:
        level = size_to_level.get(e['size'], None)
        if level:
            # Skip overly long text (not headings)
            if len(e['text']) < 100:
                headings.append({
                    "level": level,
                    "text": e['text'],
                    "page": e['page']
                })
    return headings

def extract_outline(pdf_path):
    doc = fitz.open(pdf_path)
    elements = extract_text_elements(doc)
    title = detect_title(elements)
    outline = classify_headings(elements)
    return {
        "title": title,
        "outline": outline
    }

if __name__ == "__main__":
    import json

    # Hardcoded input and output file paths
    pdf_path = "IP-report.pdf"       # Change this to your actual file path
    output_path = "output.json"      # Output file name

    result = extract_outline(pdf_path)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Extracted and saved to {output_path}")
