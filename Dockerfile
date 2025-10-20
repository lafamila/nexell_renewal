FROM python:3.12.11-slim-bookworm as builder

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

CMD ["python", "./__main__.py"]