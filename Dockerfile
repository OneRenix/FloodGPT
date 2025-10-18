# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /app

# Install uv in builder (temporary, not in final image)
RUN pip install uv

# Copy only dependencies first (efficient caching layer)
COPY requirements.txt .

# Install dependencies using uv
RUN uv pip install --system -r requirements.txt

# Stage 2: Final lightweight runtime
FROM python:3.11-slim

WORKDIR /app

# Copy installed dependencies from builder layer
COPY --from=builder /usr/local /usr/local

# Copy app code
COPY . .

EXPOSE 8080

# ✅ Cloud Run will respect this correctly
CMD ["uvicorn", "api:api", "--host", "0.0.0.0", "--port", "8080"]
