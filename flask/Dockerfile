FROM python:3.6
RUN pip3 install Flask
WORKDIR /usr/src/app
RUN mkdir static templates

COPY app/ ./
ENV FLASK_APP app.py

EXPOSE 5000
CMD ["python", "app.py", "--debug"]

