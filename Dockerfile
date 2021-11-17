FROM python:3.7-slim
ENV PYTHONUNBUFFERED=1
# set work directory
RUN mkdir /usr/src/app
COPY manage.py /usr/src/app
COPY apps /usr/src/app
#ADD WFMBCM_App /usr/src/app/WFMBCM_App
#ADD WFMBCM_db /usr/src/app/WFMBCM_db

WORKDIR /usr/src/app
# set environment variables
# install dependencies
RUN apt-get update && apt-get install -y git
RUN pip install -U pip

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
CMD manage.py migrate
CMD exec gunicorn apps.wsgi:application --bind 0.0.0.0:8000 --workers 10
