FROM python:3.12-slim-bookworm
LABEL org.opencontainers.image.source="https://github.com/dception01/linux_container_workshop"
WORKDIR /app
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd --uid 10001 --create-home workshop
COPY --chown=workshop:workshop app/ .
USER workshop
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
