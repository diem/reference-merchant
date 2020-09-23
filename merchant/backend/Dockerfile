FROM python:3.7-slim

WORKDIR /merchant-backend

RUN apt-get update && apt-get install -y gcc git netcat
RUN pip install pipenv

COPY Pipfile Pipfile.lock ./
RUN pipenv install --deploy --system

COPY run_web.sh ./
COPY src ./src/

ENTRYPOINT "./run_web.sh"
