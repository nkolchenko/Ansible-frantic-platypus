FROM  python:3.6.11-alpine3.11

WORKDIR /app
COPY cmd/server.py cmd/server.py
RUN pip install pymysql==0.10.0

# shall match to 'listen_port:' from K8s configMap
EXPOSE 8180

#The exec form, which is the preferred form:
ENTRYPOINT ["python3","cmd/server.py"]

