# Adobe India Hackathon 2025 – Round 1A Submission

## Challenge: Round 1A – Understand Your Document

This solution extracts a structured outline from raw PDF documents. It identifies the document **title** and hierarchical headings (**H1**, **H2**, **H3**), along with **page numbers**, enabling machine understanding of PDF structure.

---

## Approach

The solution uses **PyMuPDF (fitz)** to parse PDF content and applies heuristics for:

- **Title Detection**:
  - Prefer PDF metadata if it’s meaningful.
  - Otherwise, select the largest text near the top of the first page.

- **Heading Detection**:
  - Based on font size, boldness, all-caps style, and structured numbering (like `1.1`, `A.`, etc.).
  - Repetitive text and footers are filtered using text frequency.
  - Headings are classified into levels H1, H2, and H3.

---

## Folder Structure

```
adobe-hackathon/
├── input/                 # PDF files go here
├── output/                # Extracted JSON files will be saved here
├── test_without_docker.py  # Main Python script
├── Dockerfile             # Docker configuration
└── README.md              # This file
```

---

## Input/Output Format

For each `input/filename.pdf`, a corresponding `output/filename.json` is generated in the format:

```json
{
  "title": "Understanding AI",
  "outline": [
    { "level": "H1", "text": "Introduction", "page": 1 },
    { "level": "H2", "text": "What is AI?", "page": 2 },
    { "level": "H3", "text": "History of AI", "page": 3 }
  ]
}
```

---

## Dependencies

- Python 3.10+
- PyMuPDF (`fitz`)

All dependencies are installed within the Docker container.

---

## How to Build and Run

### Build the Docker Image

```bash
docker build --platform linux/amd64 -t mysolution:somerandomidentifier .
```

### Run the Docker Container

#### For PowerShell (Windows):
```powershell
docker run --rm ^
  -v ${PWD}/input:/app/input ^
  -v ${PWD}/output:/app/output ^
  --network none ^
  mysolution:somerandomidentifier
```

#### For Bash (Linux/macOS):
```bash
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --network none \
  mysolution:somerandomidentifier
```

This processes all PDFs in the `input/` folder and saves the outputs to `output/`.

---

## Constraint Compliance

- Fully offline (no internet/API calls)
- No hardcoded rules or file-specific logic
- Model-free (logic-based, no ML models used)
- Processes ≤ 50-page PDF in under 10 seconds
- Docker image runs on CPU (amd64) with ≤ 200MB of dependencies

---

## Notes

This module will serve as the foundation for Round 1B, where semantic understanding and persona-specific insights will be layered over the extracted structure.
