FROM python:3.8-slim-buster



RUN sudo apt-get update
RUN sudo apt-get install nano

RUN sudo mkdir wd
WORKDIR wd
COPY app/requirements.txt .
RUN pip3 install -r requirements.txt

COPY app/ ./

CMD [ "gunicorn", "--workers=5", "--threads=1", "-b 0.0.0.0:80", "app:server"]
