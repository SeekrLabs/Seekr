FROM python:3.8-slim-buster
WORKDIR /home/seekr

RUN apt-get -y update
RUN apt-get install -y wget gnupg2 curl
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable
# install chromedriver
RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/
# set display port to avoid crash
ENV DISPLAY=:99

RUN apt-get install -y --no-install-recommends gcc
RUN apt-get install -y --no-install-recommends default-libmysqlclient-dev

RUN python -m venv venv
COPY requirements.txt requirements.txt
RUN venv/bin/pip install --upgrade pip
RUN venv/bin/pip install --default-timeout=100 -r requirements.txt
RUN venv/bin/pip install gunicorn

ENV SEEKR_DEBUG 0
ENV SEEKR_DATABASE prod
ENV SEEKR_ASYNC true
ENV LINKEDIN_EMAIL waltonwang98@gmail.com
ENV GOOGLE_SE_ID 010165119647807024814:q2yquzvdkdo

COPY . ./
RUN chmod +x boot.sh

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
