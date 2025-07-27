# main.py
import os
import json
import fitz  # PyMuPDF
import re
import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def extract_text_by_section(pdf_doc):
    headings = []
    all_font_sizes = []

    for page_index in range(len(pdf_doc)):
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

    candidates = []
    for page_index in range(len(pdf_doc)):
        page = pdf_doc.load_page(page_index)
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                text = "".join(span["text"] for span in line["spans"]).strip()
                if not text or len(text) > 100:
                    continue

                sizes = [span["size"] for span in line["spans"] if span["text"].strip()]
                max_line_size = max(sizes) if sizes else 0
                font_names = [span["font"] for span in line["spans"]]
                is_bold = any("Bold" in f or "Black" in f for f in font_names)
                is_allcaps = text.isupper()

                if max_line_size > median_size * 1.15 or is_bold or is_allcaps:
                    candidates.append({
                        "text": text,
                        "page": page_index + 1,
                        "size": max_line_size
                    })

    return candidates


def get_section_texts(doc, headings):
    page_to_text = {}
    for i in range(len(doc)):
        page_to_text[i + 1] = doc.load_page(i).get_text("text")

    section_contents = []
    for i, h in enumerate(headings):
        start_page = h["page"]
        end_page = headings[i + 1]["page"] if i + 1 < len(headings) else len(doc)
        section_text = ""
        for p in range(start_page, end_page + 1):
            section_text += page_to_text.get(p, "")
        section_contents.append({
            "document": h["document"],
            "page": h["page"],
            "section_title": h["text"],
            "text": section_text
        })
    return section_contents


def compute_relevance_scores(sections, query):
    corpus = [query] + [sec["text"] for sec in sections]
    tfidf = TfidfVectorizer(stop_words='english').fit_transform(corpus)
    scores = cosine_similarity(tfidf[0:1], tfidf[1:]).flatten()
    for i, score in enumerate(scores):
        sections[i]["score"] = float(score)
    sections.sort(key=lambda x: -x["score"])
    return sections


def main():
    input_dir = "input"
    output_dir = "output"
    metadata_path = os.path.join(input_dir, "metadata.json")
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    persona = metadata["persona"]
    job = metadata["job_to_be_done"]
    docs = metadata["documents"]

    all_sections = []

    for filename in docs:
        filepath = os.path.join(input_dir, filename)
        try:
            with fitz.open(filepath) as doc:
                headings = extract_text_by_section(doc)
                for h in headings:
                    h["document"] = filename
                all_sections.extend(headings)
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")

    refined_sections = compute_relevance_scores(
        get_section_texts(fitz.open(os.path.join(input_dir, docs[0])), all_sections),
        persona + " " + job
    )

    output = {
        "metadata": {
            "documents": docs,
            "persona": persona,
            "job_to_be_done": job,
            "processed_at": datetime.datetime.utcnow().isoformat()
        },
        "extracted_sections": [],
        "subsection_analysis": []
    }

    for rank, sec in enumerate(refined_sections[:10], 1):
        output["extracted_sections"].append({
            "document": sec["document"],
            "page": sec["page"],
            "section_title": sec["section_title"],
            "importance_rank": rank
        })
        output["subsection_analysis"].append({
            "document": sec["document"],
            "page": sec["page"],
            "section_title": sec["section_title"],
            "refined_text": sec["text"][:1000]  # optionally truncate
        })

    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "result.json"), "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
