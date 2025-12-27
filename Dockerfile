# syntax=docker/dockerfile:1

FROM python:3.14-alpine3.23

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY ./app .

CMD [ "gunicorn" ]
