FROM python:3.6
RUN pip3 install Flask
RUN pip3 install matplotlib
RUN pip3 install influxdb
RUN pip3 install mysql-connector
WORKDIR /usr/src/app
RUN mkdir static templates

COPY app/ ./
ENV FLASK_APP app.py
ENV AM_I_ADMIN "NO"
ENV INFLUXDB_NAME "uptime"
ENV INFLUXDB_HOST ""
ENV MYSQL_USERNAME ""
ENV MYSQL_PASSWORD ""
ENV MYSQL_HOST ""
ENV MYSQL_DATABASE_NAME ""

EXPOSE 5000
CMD ["python", "app.py", "--debug"]

