FROM python:3.11-slim

WORKDIR /app
ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
    PIP_DEFAULT_TIMEOUT=120

RUN sed -i 's|http://deb.debian.org/debian-security|http://mirrors.tuna.tsinghua.edu.cn/debian-security|g; s|http://deb.debian.org/debian|http://mirrors.tuna.tsinghua.edu.cn/debian|g' /etc/apt/sources.list.d/debian.sources \
    && apt-get update \
    && apt-get install -y --no-install-recommends chromium ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY zhenzhi_knowledge/ ./zhenzhi_knowledge/
RUN pip install --no-cache-dir --retries 5 .

ENV PYTHONPATH=/app

EXPOSE 8765

CMD ["python", "-m", "zhenzhi_knowledge", "--root", "/knowledge", "api", "serve", "--host", "0.0.0.0", "--port", "8765"]
