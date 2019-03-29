FROM python:3.6
RUN pip3 install Flask
RUN pip3 install kubernetes
WORKDIR /usr/src/app

COPY ./kubekat_pvc_checker/app/ ./
#COPY ./kubernetes_api ./pvc_checker/kubernetes_api
COPY ./kubekat_kubernetes_api /usr/local/lib/python3.6/site-packages/kubekat_kubernetes_api
RUN ls -la
RUN ls -la pvc_checker/
RUN ls -la /usr/local/lib/python3.6/site-packages
ENV FLASK_APP app.py

EXPOSE 5000
CMD ["python", "app.py", "--debug"]
