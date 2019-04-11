# Docker images must be built from parent folder

docker build --no-cache -t sendotux/kubernetes-pvc-checker:latest -f kubekat_pvc_checker/Dockerfile . && docker push sendotux/kubernetes-pvc-checker:latest
