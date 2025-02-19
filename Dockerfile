FROM python:3.12.3-alpine

RUN apk update && pip install poetry 

WORKDIR /app

COPY . /app

RUN  poetry config virtualenvs.create false && poetry lock --no-update && poetry install

ENTRYPOINT ["/bin/sh"]
