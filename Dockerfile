FROM python:3.6
RUN pip3 install Flask
RUN pip3 install kubernetes
WORKDIR /usr/src/app

COPY app/ ./
ENV FLASK_APP app.py

EXPOSE 5000
CMD ["python", "app.py", "--debug"]
