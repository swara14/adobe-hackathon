# Adobe India Hackathon – Round 1B: Persona-Driven Document Intelligence

## Overview

This solution extracts and ranks the most relevant sections from a collection of PDFs based on a given **persona** and **job-to-be-done**.

---

## Input

Place PDF documents and a `metadata.json` file inside the `/input` directory.

Example metadata:

```json
{
  "documents": ["doc1.pdf", "doc2.pdf"],
  "persona": "PhD Researcher in Computational Biology",
  "job_to_be_done": "Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks"
}
