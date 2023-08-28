FROM python:3.10-slim as poetry
# `python:3.10-slim` is built on debian bookworm

ARG UID
ARG GID

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV POETRY_HOME "/opt/poetry"
ENV PATH "$POETRY_HOME/bin:$PATH"

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -

FROM poetry

WORKDIR /app/src
ENV HOME="/app"

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
      ffmpeg tesseract-ocr tesseract-ocr-pol \
      vim \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry lock \
    && poetry install --no-interaction --no-ansi

RUN test -n "$UID"
RUN test -n "$GID"

RUN groupadd -g "$GID" dev \
    && adduser --uid "$UID" --gid "$GID" --no-create-home dev \
    && chown 'dev:dev' -R "$HOME"
RUN su \
      --preserve-environment \
      --command='\
        poetry config virtualenvs.create false \
        && poetry lock \
        && poetry install --no-interaction --no-ansi' \
      dev

ENTRYPOINT ["bash"]
