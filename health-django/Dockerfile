FROM python:latest

WORKDIR /usr/src/app

RUN apt-get update && rm -rf /var/lib/apt/lists/*

COPY health/ ./
COPY docker-entrypoint.sh ./

RUN pip install -r requirements.txt

EXPOSE 8000

ENTRYPOINT ["./docker-entrypoint.sh"]

