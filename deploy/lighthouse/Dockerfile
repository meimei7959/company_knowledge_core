FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY zhenzhi_knowledge/ ./zhenzhi_knowledge/

RUN pip install --no-cache-dir .

EXPOSE 8765

CMD ["python3", "-m", "zhenzhi_knowledge", "--root", "/knowledge", "api", "serve", "--host", "0.0.0.0", "--port", "8765"]
