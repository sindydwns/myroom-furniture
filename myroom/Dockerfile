FROM python:3.11

RUN apt update -y
RUN apt install -y git vim sudo curl gcc make dumb-init

RUN pip install --upgrade pip
RUN pip install poetry

WORKDIR /app
COPY pyproject.toml poetry.lock* .
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

WORKDIR /app/myroom

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["uvicorn", "server:app", "--reload", "--host=0.0.0.0", "--port=8000"]
