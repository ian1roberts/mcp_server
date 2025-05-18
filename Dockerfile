FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY openapi.yaml /mcp/openapi.yaml


EXPOSE 8844

CMD ["python", "mcp_server.py"]
