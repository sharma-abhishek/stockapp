FROM python:2.7
ADD . /app/
WORKDIR /app/
RUN pip install -r requirements.txt
COPY docker-entrypoint.sh /usr/local/bin/
RUN ["chmod", "+x", "/usr/local/bin/docker-entrypoint.sh"]
ENTRYPOINT ["docker-entrypoint.sh"]