FROM python:3.7.5
ENV PYTHONUNBUFFERED = 1
RUN mkdir /app
WORKDIR /app
RUN apt-get update && \
    apt-get install -y \
        zlib1g-dev
RUN apt-get update && \
    apt-get install -y \
        libgeos-dev
COPY ./requirements.txt /app/
RUN pip install -r requirements.txt
COPY . /app/