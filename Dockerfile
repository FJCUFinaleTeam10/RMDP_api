# pull official base image
FROM python:3.9.5-alpine
ENV PYTHONUNBUFFERED=1
# set work directory
WORKDIR /usr/src/app
# set environment variables
# install dependencies
RUN apk --no-cache add gcc libc-dev geos-dev musl-dev linux-headers g++
RUN pip install -U pip

COPY requirements.txt ./
RUN pip install -r requirements.txt