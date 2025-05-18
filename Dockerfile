FROM python:3.12-slim AS builder

# Install Poetry
RUN pip install poetry

# Set Poetry configuration to not create a virtual environment
RUN poetry config virtualenvs.create false

WORKDIR /app

# Copy only dependency definitions for efficient caching
COPY pyproject.toml poetry.lock* ./

# Install runtime dependencies only (no dev dependencies)
RUN poetry install --no-interaction --no-root

# Final image
FROM python:3.12-slim

# Create a non-root user for better security
RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -s /bin/bash -m appuser

WORKDIR /app

# Copy dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .
RUN poetry install --no-interaction --only-root

# Set permissions
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose the port your server listens on
EXPOSE 8844

# Health check
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD curl -f http://localhost:8844/.well-known/health || exit 1

# Run using the package entry point defined in pyproject.toml
CMD ["mcp-server"]
