FROM python:3.7-slim-buster

RUN adduser seekr

WORKDIR /home/seekr

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN apt-get update
RUN apt-get install -y --no-install-recommends gcc
RUN apt-get install -y --no-install-recommends default-libmysqlclient-dev

RUN venv/bin/pip install --default-timeout=100 -r requirements.txt
RUN venv/bin/pip install gunicorn

ENV SEEKR_DEBUG 0
ENV SEEKR_DATABASE prod
ENV SEEKR_ASYNC true
ENV RDS_DB_NAME seekr
ENV RDS_USERNAME admin
ENV RDS_PASSWORD password
ENV RDS_PORT 3306

COPY . ./
RUN chmod +x boot.sh

USER seekr

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]