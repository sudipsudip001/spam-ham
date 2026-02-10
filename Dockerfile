FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# This creates a folder named /app INSIDE the container
WORKDIR /app

# Copy files from your local SPAM-HAM folder to the container's /app
# Note: We use "." because we will run the build command from inside SPAM-HAM
COPY uv.lock pyproject.toml ./

RUN uv sync --frozen --no-install-project --no-dev

# Copy everything else
COPY . .

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]