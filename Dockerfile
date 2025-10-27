FROM python:3.12-slim-bookworm as builder


RUN mkdir /erp-service
COPY /src/. /erp-service
WORKDIR /erp-service

RUN apt-get update \
      && apt-get install -y --no-install-recommends gcc libc-dev \
      && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip \
      && pip install --user -r requirements.txt

RUN apt-get purge -y --auto-remove gcc libc-dev

FROM python:3.12.11-slim-bookworm

COPY --from=builder /erp-service /erp-service
COPY --from=builder /root/.local /root/.local

WORKDIR /erp-service

ENV PATH=/root/.local:$PATH

EXPOSE 5001

# Flask 인스턴스: src/app/__init__.py 의 app
CMD ["python", "-m", "gunicorn", "-w", "2", "-k", "gthread", "--threads", "4", "--keep-alive", "10", "-b", "0.0.0.0:5001", "app:app"]