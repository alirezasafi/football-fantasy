FROM python:3.7-alpine

COPY . /app

WORKDIR /app

# RUN apt-get install -y libmysqlclient-dev

# RUN pip install -r requirements.txt

RUN apk add mariadb-connector-c-dev ;\
    apk add --virtual .build-deps \
        build-base \
        mariadb-dev ;\
    pip install -qq -r requirements.txt; \
ENTRYPOINT ["python"]

CMD ["router.py"]