import fitz  # PyMuPDF
import json
import os

def extract_headings(pdf_path):
    doc = fitz.open(pdf_path)
    title = ""
    headings = []

    font_sizes = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("dict")["blocks"]

        for b in blocks:
            if "lines" not in b:
                continue
            for line in b["lines"]:
                text = ""
                sizes = []
                for span in line["spans"]:
                    text += span["text"].strip() + " "
                    sizes.append(span["size"])
                
                text = text.strip()
                if not text:
                    continue

                avg_size = sum(sizes) / len(sizes)
                font_sizes.append(avg_size)

                # Heuristic: largest text on first page → title
                if page_num == 0 and avg_size > 15 and not title:
                    title = text

                # Classify based on font size (simple thresholds, refine later)
                if avg_size > 15:
                    level = "H1"
                elif avg_size > 12:
                    level = "H2"
                elif avg_size > 10:
                    level = "H3"
                else:
                    continue

                headings.append({
                    "level": level,
                    "text": text,
                    "page": page_num + 1
                })

    return {
        "title": title,
        "outline": headings
    }

def save_json(data, output_path):
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

# Example run
if __name__ == "__main__":
    input_dir = "input"
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.endswith(".pdf"):
            result = extract_headings(os.path.join(input_dir, filename))
            out_filename = filename.replace(".pdf", ".json")
            save_json(result, os.path.join(output_dir, out_filename))
