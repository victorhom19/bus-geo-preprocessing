FROM python:3.10

RUN pip install poetry
RUN poetry self add poetry-plugin-export

WORKDIR /src

ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_VIRTUALENVS_CREATE=false

COPY poetry.lock pyproject.toml /src/

RUN poetry install --no-interaction --no-ansi --no-root

COPY app alembic.ini config.py /src/
