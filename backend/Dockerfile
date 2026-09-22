FROM python:3.12-slim AS builder

WORKDIR /build

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential default-libmysqlclient-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

FROM python:3.12-slim AS runtime

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt \
    && rm -rf /wheels

COPY entrypoint.sh /usr/local/bin/campusloop-entrypoint
RUN chmod +x /usr/local/bin/campusloop-entrypoint

COPY . .

EXPOSE 8000

ENTRYPOINT ["campusloop-entrypoint"]

CMD ["sh", "-c", "gunicorn campusloop.wsgi:application --bind 0.0.0.0:${PORT:-8000} --access-logfile -"]
