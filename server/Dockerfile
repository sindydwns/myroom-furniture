FROM python:3.12-alpine3.20

RUN apk update
RUN apk add git vim sudo curl gcc make dumb-init

RUN pip install --upgrade pip
RUN pip install fastapi[all]

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

WORKDIR /app/srcs

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["uvicorn", "server:app", "--reload", "--host=0.0.0.0", "--port=8000"]