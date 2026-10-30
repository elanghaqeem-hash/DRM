FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /work
COPY pyproject.toml ./
COPY services ./services
COPY infra/migrations ./infra/migrations
COPY infra/alembic.ini ./infra/alembic.ini
RUN pip install --no-cache-dir . && useradd --system --uid 10001 drm
USER 10001
EXPOSE 8000
CMD ["uvicorn", "services.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
