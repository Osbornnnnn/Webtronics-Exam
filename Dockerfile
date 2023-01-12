FROM python:3.10-slim-buster AS builder

RUN mkdir -p /opt/Webtronics/app

WORKDIR /opt/Webtronics

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY app /opt/Webtronics/app

WORKDIR /opt/Webtronics/app
CMD python -m uvicorn main:application --reload
