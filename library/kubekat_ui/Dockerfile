FROM python:3.6
RUN pip3 install Flask
RUN pip3 install kubernetes
RUN pip3 install flask_wtf
WORKDIR /usr/src/app

COPY ./kubekat_ui/app/ ./
COPY ./kubekat_kubernetes_api /usr/local/lib/python3.6/site-packages/kubekat_kubernetes_api
ENV FLASK_APP app.py

EXPOSE 5000
CMD ["python", "app.py", "--debug"]
