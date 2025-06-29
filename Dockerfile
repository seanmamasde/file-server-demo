# base stage
FROM python:3.12-slim AS base
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_HOME=/opt/poetry \
    POETRY_VIRTUALENVS_CREATE=false

RUN apt-get update && apt-get install -y --no-install-recommends build-essential curl \
 && curl -sSL https://install.python-poetry.org | python3 - \
 && ln -s $POETRY_HOME/bin/poetry /usr/local/bin/poetry \
 && apt-get purge -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY ["pyproject.toml", "poetry.lock", "./"]
RUN poetry install --only main --no-interaction --no-ansi --no-root \
 && poetry cache clear pypi --all

# runtime stage
FROM python:3.12-slim
WORKDIR /app
COPY --from=base /usr/local /usr/local
COPY app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EXPOSE 8000
