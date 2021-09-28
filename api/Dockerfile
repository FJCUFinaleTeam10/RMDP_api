# pull official base image
FROM python:3.9.5-alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables


# install dependencies
RUN apk --no-cache add gcc libc-dev geos-dev musl-dev linux-headers g++
RUN pip install -U pip

COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt
#RUN pip install -r requirements.txt

# copy entrypoint.sh
#COPY ./entrypoint.sh /usr/src/app/entrypoint.sh

# copy project
COPY . /usr/src/app/

# run entrypoint.sh
#ENTRYPOINT ["/usr/src/app/entrypoint.sh"]