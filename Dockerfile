FROM python:3.7-alpine

RUN pip3 install prometheus_client requests

ADD tesla.py /

EXPOSE 8000
CMD python3 /tesla.py
