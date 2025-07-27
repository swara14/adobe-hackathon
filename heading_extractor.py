import fitz  # PyMuPDF
import json
import os
from collections import Counter
import re

def extract_headings(pdf_path):
    doc = fitz.open(pdf_path)
    title = ""
    headings = []
    font_sizes = []
    text_blocks = []

    # 1. Collect detailed text block information with context
    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("dict")["blocks"]

        for b in blocks:
            if "lines" not in b:
                continue
            block_text = ""
            sizes = []
            fonts = []
            bboxes = []
            is_bold = False
            is_all_caps = False
            line_count = 0
            for line in b["lines"]:
                line_text = ""
                line_sizes = []
                line_fonts = []
                line_bold = False
                line_all_caps = True
                for span in line["spans"]:
                    span_text = span["text"].strip()
                    if not span_text:
                        continue
                    line_text += span_text + " "
                    line_sizes.append(span["size"])
                    line_fonts.append(span["font"])
                    if "bold" in span["font"].lower() or span["flags"] & 16:
                        line_bold = True
                    if span_text != span_text.upper():
                        line_all_caps = False
                line_text = line_text.strip()
                if line_text:
                    block_text += line_text + " "
                    sizes.extend(line_sizes)
                    fonts.append(line_fonts[0])
                    is_bold = is_bold or line_bold
                    is_all_caps = is_all_caps or line_all_caps
                    bboxes.append(line["bbox"])
                    line_count += 1
            block_text = block_text.strip()
            if block_text and sizes:
                avg_size = sum(sizes) / len(sizes)
                font_sizes.append(avg_size)
                text_blocks.append({
                    "text": block_text,
                    "size": avg_size,
                    "font": fonts[0],
                    "is_bold": is_bold,
                    "is_all_caps": is_all_caps,
                    "bbox": bboxes[0],
                    "line_count": line_count,
                    "page": page_num + 1,
                    "word_count": len(block_text.split())
                })

    # 2. Analyze font sizes and estimate thresholds
    font_counter = Counter([round(fs, 1) for fs in font_sizes])
    sorted_fonts = sorted(font_counter.items(), key=lambda x: (-x[0], -x[1]))
    top_sizes = [fs[0] for fs in sorted_fonts[:4]]
    h1_size = top_sizes[0] if top_sizes else 0
    h2_size = top_sizes[1] if len(top_sizes) > 1 else h1_size * 0.9
    h3_size = top_sizes[2] if len(top_sizes) > 2 else h2_size * 0.9
    body_size = top_sizes[3] if len(top_sizes) > 3 else h3_size * 0.8

    # 3. Content-based heading detection
    heading_keywords = r"^(chapter|section|part|article|abstract|introduction|conclusion|results|discussion|methodology|references|appendix)\s*\d*|^(\d+\.?(\d+\.?)*\s+)|^\w+\.\s+"
    for i, block in enumerate(text_blocks):
        text = block["text"]
        size = block["size"]
        is_bold = block["is_bold"]
        is_all_caps = block["is_all_caps"]
        page = block["page"]
        bbox = block["bbox"]
        word_count = block["word_count"]
        line_count = block["line_count"]

        # Heuristics for headings
        is_short = word_count < 15
        is_single_line = line_count == 1
        is_keyword = re.match(heading_keywords, text.lower(), re.IGNORECASE)
        is_numbered = re.match(r"^\d+(\.\d+)*\s", text)
        is_at_top = bbox[1] < 100
        has_large_gap = False
        is_followed_by_body = False
        if i > 0:
            prev_bbox = text_blocks[i-1]["bbox"]
            if bbox[1] - prev_bbox[3] > 20:
                has_large_gap = True
        if i < len(text_blocks) - 1:
            next_block = text_blocks[i+1]
            if next_block["word_count"] > 20 and next_block["line_count"] > 2:
                is_followed_by_body = True

        # Scoring system for heading likelihood
        score = 0
        if is_keyword:
            score += 3
        if is_numbered:
            score += 2
        if is_bold or is_all_caps:
            score += 2
        if is_short and is_single_line:
            score += 2
        if is_at_top or has_large_gap:
            score += 1
        if is_followed_by_body:
            score += 1
        if abs(size - h1_size) < 0.5 or abs(size - h2_size) < 0.5 or abs(size - h3_size) < 0.5:
            score += 1

        # Classify based on score and font size
        level = None
        if score >= 5 and (abs(size - h1_size) < 0.5 or (page == 1 and is_at_top)):
            level = "H1"
            if not title and page == 1 and is_at_top:
                title = text
        elif score >= 4 and abs(size - h2_size) < 0.5:
            level = "H2"
        elif score >= 3 and abs(size - h3_size) < 0.5:
            level = "H3"
        else:
            continue

        headings.append({
            "level": level,
            "text": text,
            "page": page,
            "score": score,
            "y_position": bbox[1]
        })

    # 4. Post-process for title and hierarchy
    if not title and headings:
        for h in headings:
            if h["page"] == 1 and h["level"] in ["H1", "H2"] and h["y_position"] < 100:
                title = h["text"]
                break

    # 5. Ensure hierarchical consistency
    final_headings = []
    last_level = None
    for h in headings:
        if last_level == "H1" and h["level"] == "H3":
            h["level"] = "H2"  # Promote H3 to H2 if it follows H1 directly
        final_headings.append(h)
        last_level = h["level"]

    return {
        "title": title,
        "outline": final_headings
    }

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
                result = extract_headings(pdf_path)
                out_path = os.path.join(output_dir, filename.replace(".pdf", ".json"))
                save_json(result, out_path)
                print(f"✅ Extracted: {filename} → {out_path}")
            except Exception as e:
                print(f"❌ Error processing {filename}: {str(e)}")

if __name__ == "__main__":
    main()
