FROM python:3.8-slim-buster
RUN apt-get update

RUN mkdir wd
WORKDIR wd
COPY app/requirements.txt .
RUN pip install -r requirements.txt

COPY app/ ./

CMD python Updatetopwords.py
