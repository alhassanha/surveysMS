FROM python:3.7.5
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /app
WORKDIR /app

COPY ./requirements.txt /app/
COPY Pipfile /app/
RUN pip install pipenv
RUN pipenv install -r requirements.txt

COPY . /app/