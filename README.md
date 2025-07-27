# Adobe India Hackathon 2025 – Round 1A Submission

## Challenge: Round 1A – Understand Your Document

This solution extracts a structured outline from raw PDF documents. It identifies the document title and hierarchical headings (H1, H2, H3), with page numbers, to enable machine understanding of PDF structure.

## Approach

The solution is built using PyMuPDF (`fitz`) to parse and analyze PDF content. The extraction logic involves:

- **Title Detection:** Uses metadata if available and valid, otherwise selects the largest text element in the top 25% of the first page.
- **Heading Detection:** Heuristics are applied using font size, bold fonts, all-caps text, and numbering patterns to classify heading levels.
- **Level Classification:** 
  - Numbered formats (e.g., "1.", "2.1.") are used to estimate levels.
  - Larger font sizes and bold text indicate higher-level headings.
  - Common repeated lines and irrelevant footers are filtered.

Headings are returned with their hierarchical level, text, and page number.

## Folder Structure

