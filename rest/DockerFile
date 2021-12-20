FROM python:3.6-slim

WORKDIR /server

COPY requirements.txt /server/
COPY rest-server.py /server/

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "rest-server.py"]