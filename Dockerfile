FROM python:3.7
RUN mkdir -p /app 
COPY requirements.txt /app


WORKDIR /app
RUN pip install -r requirements.txt
ADD . /app
