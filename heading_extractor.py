import fitz
import re
import json
import os

def extract_title(pdf_doc: fitz.Document) -> str:
    meta_title = (pdf_doc.metadata.get("title") or "").strip()
    if meta_title and not re.search(r'\.(pdf|docx?|pptx?|cdr)$', meta_title, re.IGNORECASE) \
       and "Microsoft Word" not in meta_title:
        return meta_title

    try:
        first_page = pdf_doc.load_page(0)
    except Exception:
        return ""

    blocks = first_page.get_text("dict")["blocks"]
    title_text = ""
    max_size = 0.0
    for block in blocks:
        if "lines" not in block:
            continue
        for line in block["lines"]:
            text = "".join(span["text"] for span in line["spans"]).strip()
            if not text:
                continue
            line_max_size = max(span["size"] for span in line["spans"])
            if line_max_size > max_size and block["bbox"][1] < first_page.rect.height * 0.25:
                max_size = line_max_size
                title_text = text
    return title_text.strip()
def extract_headings(pdf_doc: fitz.Document):
    headings = []
    all_font_sizes = []
    
    for page_index in range(len(pdf_doc)):  # Use len(pdf_doc) for safety
        page = pdf_doc.load_page(page_index)
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    size = span["size"]
                    if 5 < size < 100:
                        all_font_sizes.append(size)
    
    median_size = sorted(all_font_sizes)[len(all_font_sizes) // 2] if all_font_sizes else 12

    text_frequency = {}
    for page_index in range(len(pdf_doc)):
        page = pdf_doc.load_page(page_index)
        for line in page.get_text("text").splitlines():
            key = line.strip()
            if key:
                text_frequency[key] = text_frequency.get(key, 0) + 1

    candidates = []
    for page_index in range(len(pdf_doc)):
        page = pdf_doc.load_page(page_index)
        if re.search(r'table of contents', page.get_text("text"), re.IGNORECASE):
            continue
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                text = "".join(span["text"] for span in line["spans"]).strip()
                if not text or len(text) > 100:
                    continue
                if text_frequency.get(text, 0) > max(2, len(pdf_doc) * 0.5):
                    continue
                if text.endswith('.') or re.match(r'^\d{1,2} [A-Z]{3,9} \d{4}$', text):
                    continue

                sizes = [span["size"] for span in line["spans"] if span["text"].strip()]
                max_line_size = max(sizes) if sizes else 0
                font_names = [span["font"] for span in line["spans"]]
                is_bold = any("Bold" in f or "Black" in f for f in font_names)
                letters = re.findall(r'[A-Za-z]', text)
                is_allcaps = letters and all(c.isupper() for c in letters)

                numbering = None
                num_match = re.match(r'^(\d+(\.\d+)+)\s', text) or re.match(r'^(\d+)\s', text)
                let_match = re.match(r'^([A-Za-z]\.)\s', text)
                if num_match:
                    numbering = num_match.group(1)
                elif let_match:
                    numbering = let_match.group(1)

                large = median_size and max_line_size > median_size * 1.15
                cond = (numbering and (large or is_bold or is_allcaps)) or (large or is_bold or (is_allcaps and len(text) < 50))
                if not cond:
                    continue

                # Safe bounding box extraction
                try:
                    bboxes = page.search_for(text)
                    y_pos = bboxes[0].y1 if bboxes else 0
                except Exception:
                    y_pos = 0

                candidates.append({
                    "text": text,
                    "page": page_index + 1,
                    "size": max_line_size,
                    "numbering": numbering,
                    "y": y_pos
                })

    candidates.sort(key=lambda x: (x["page"], -x["size"]))
    outline = []
    for h in candidates:
        level = 1
        if h["numbering"]:
            if re.match(r'^\d+(\.\d+)+$', h["numbering"]):
                level = h["numbering"].count('.') + 1
            elif re.match(r'^[A-Za-z]\.$', h["numbering"]):
                level = 1
        else:
            if h["size"] < median_size * 1.2:
                level = 3
            elif h["size"] < median_size * 1.5:
                level = 2
        outline.append({"level": f"H{int(level)}", "text": h["text"], "page": h["page"]})

    
    return outline

def save_json(data, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
def main():
    input_dir = "input"
    output_dir = "output"
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_dir, filename)
            try:
                with fitz.open(pdf_path) as doc:
                    title = extract_title(doc)
                    outline = extract_headings(doc)
                    result = {
                        "title": title,
                        "outline": outline
                    }
                    out_path = os.path.join(output_dir, filename.replace(".pdf", ".json"))
                    save_json(result, out_path)
                    print(f"✅ Extracted: {filename} → {out_path}")
            except Exception as e:
                print(f"❌ Error processing {filename}: {str(e)}")


if __name__ == "__main__":
    main()
