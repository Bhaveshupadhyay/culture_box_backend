# Use official python:3.14-slim as base and copy uv binary from ghcr
FROM python:3.14-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app

# Install dependencies using cache mounts
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Add project code and install it
ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Final slim runtime image
FROM python:3.14-slim
WORKDIR /app

# Copy the virtual environment and app code from builder
COPY --from=builder /app /app

# Place the virtualenv's bin path at the front of PATH
ENV PATH="/app/.venv/bin:$PATH"

# Set PYTHONPATH so that python can find the `app` module package inside /app
ENV PYTHONPATH="/app"

# Run the FastAPI app using production runner.
# Uses `sh -c` to dynamically bind to the $PORT environment variable injected by Render.
CMD ["sh", "-c", "fastapi run main.py --host 0.0.0.0 --port ${PORT:-8000}"]
