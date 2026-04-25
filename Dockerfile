FROM python:3.12.8-slim-bookworm

RUN apt-get update && apt-get install -y gcc libpq-dev 

ENV PYTHONUNBUFFERED=1
WORKDIR /src
COPY ./requirements.txt /src/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY ./ /src/
