# Adobe India Hackathon – Round 1B Submission  
**Persona-Driven Document Intelligence**

## Objective

This solution extracts and ranks the most relevant sections from a collection of input PDFs based on a given **persona** and **job-to-be-done**.

The extracted structure is output in a standardized JSON format, including both section-level relevance and sub-section analysis.

---

## Approach

The system performs the following steps:

1. Parses each PDF to identify potential headings using font size, boldness, and case style.
2. Extracts the full text of each section based on page boundaries.
3. Uses TF-IDF and cosine similarity to rank section content against the concatenated `persona + job-to-be-done` query.
4. Outputs the most relevant sections with:
   - Title
   - Page number
   - Importance rank
   - Refined content

No external APIs or models are used. The solution is fully offline and deterministic.

---

## Input Structure

Place the following in the `input/` directory:

- `metadata.json`: Describes the persona, job-to-be-done, and filenames of PDFs

### Sample `metadata.json`

```json
{
  "documents": ["doc1.pdf", "doc2.pdf"],
  "persona": "PhD Researcher in Computational Biology",
  "job_to_be_done": "Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks"
}
```

> 

---

## Output

After running, a single output file will be created at `output/result.json`.

### Sample Format:

```json
{
  "metadata": {
    "documents": ["doc1.pdf", "doc2.pdf"],
    "persona": "...",
    "job_to_be_done": "...",
    "processed_at": "2025-07-28T10:00:00"
  },
  "extracted_sections": [
    {
      "document": "doc1.pdf",
      "page": 4,
      "section_title": "Methodologies in GNNs",
      "importance_rank": 1
    }
  ],
  "subsection_analysis": [
    {
      "document": "doc1.pdf",
      "page": 4,
      "section_title": "Methodologies in GNNs",
      "refined_text": "This section explores supervised vs unsupervised GNNs, message-passing frameworks..."
    }
  ]
}
```

---

## How to Build

```bash
docker build --platform linux/amd64 -t round1b-solution:latest .
```

---

## How to Run

### Linux / macOS / WSL:

```bash
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --network none \
  round1b-solution:latest
```

### Windows PowerShell:

```powershell
docker run --rm `
  -v "${PWD}\input:/app/input" `
  -v "${PWD}\output:/app/output" `
  --network "none" `
  round1b-solution:latest
```


---

## Constraints Compliance

| Constraint         | Status |
|--------------------|--------|
| Offline execution  |  Yes |
| CPU-only           |  Yes |
| Model size ≤ 1GB   |  N/A (no model used) |
| Time ≤ 60s for 5 PDFs |  Yes |
| Platform: amd64    |  Yes |

---

## Dependencies

- Python 3.10
- PyMuPDF (fitz)
- scikit-learn (for TF-IDF and cosine similarity)

All dependencies are installed in the Docker image.

---

## Contact

For questions or feedback, please contact: annika22082@iiitd.ac.in, swara22524@iiitd.ac.in

