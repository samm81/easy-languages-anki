FROM python:3.10-slim as poetry
# debian bookworm based

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

# TODO solve the `root` issue
RUN su 1000 \
      poetry config virtualenvs.create false \
        && poetry lock \
        && poetry install --no-interaction --no-ansi

ENTRYPOINT ["bash"]
