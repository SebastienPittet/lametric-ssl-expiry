# syntax=docker/dockerfile:1

FROM python:3.11.1-alpine3.17

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY ./app .

CMD [ "gunicorn" ]
