FROM --platform=linux/amd64 python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir pymupdf scikit-learn

CMD ["python", "main.py"]
