FROM python:3.11-slim as base

ENV PYTHONFAULTHANDLER=1 \
     PYTHONUNBUFFERED=1 \
     PYTHONDONTWRITEBYTECODE=1 \
     PIP_DISABLE_PIP_VERSION_CHECK=on

WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt --no-cache-dir

COPY app /app/

FROM base as dev
RUN apt-get update && apt-get install gcc npm -y && apt-get clean
RUN npm install -g nodemon

FROM base as prod
ENV DEBUG False
