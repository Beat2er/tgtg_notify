FROM python:3.8-slim-buster
MAINTAINER FelixSommer mail@felix-sommer.de
WORKDIR /app
COPY requirements.txt requirements.txt
COPY main.py main.py
COPY toogoodtogo.py toogoodtogo.py
COPY telegramBot.py telegramBot.py
RUN pip3 install -r requirements.txt
CMD [ "python3", "main.py"]
