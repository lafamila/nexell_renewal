FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app/src

COPY src/requirements.txt /app/
RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential \
 && python -m pip install --upgrade pip \
 && pip install -r /app/requirements.txt \
 && apt-get purge -y --auto-remove build-essential \
 && rm -rf /var/lib/apt/lists/*

COPY src/ /app/src

RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5001

# Flask 인스턴스: src/app/__init__.py 의 app
CMD ["python", "-m", "gunicorn", "-w", "4", "-k", "gthread", "--threads", "8", "-b", "0.0.0.0:5001", "--access-logfile", "-", "--error-logfile", "-", "--log-level", "debug", "--capture-output", "app:app"]