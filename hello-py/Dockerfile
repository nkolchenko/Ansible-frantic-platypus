FROM  python:3.6.11-alpine3.11 as build

WORKDIR /app
COPY cmd/server.py cmd/server.py
RUN pip install pymysql
EXPOSE 8180

#The exec form, which is the preferred form:
ENTRYPOINT ["python3","cmd/server.py"]

