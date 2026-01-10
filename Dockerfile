# syntax=docker/dockerfile:1

FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN pip install --no-cache-dir build

# Copy source files
COPY pyproject.toml README.md ./
COPY src/ src/
COPY skills/ skills/
COPY schemas/ schemas/

# Build wheel
RUN python -m build --wheel

# Runtime stage
FROM python:3.11-slim

LABEL org.opencontainers.image.title="API Governor"
LABEL org.opencontainers.image.description="API governance and breaking change detection for OpenAPI specs"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.source="https://github.com/yourorg/api-governance-skill"
LABEL org.opencontainers.image.licenses="MIT"

WORKDIR /app

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser

# Copy wheel and install
COPY --from=builder /app/dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm /tmp/*.whl

# Copy skill files (policies, examples)
COPY --chown=appuser:appuser skills/ /app/skills/
COPY --chown=appuser:appuser schemas/ /app/schemas/

# Create output directory
RUN mkdir -p /app/governance && chown appuser:appuser /app/governance

USER appuser

# Set default policy path
ENV API_GOVERNOR_POLICY_PATH=/app/skills/api-governor/policy/default.internal.yaml

ENTRYPOINT ["api-governor"]
CMD ["--help"]
