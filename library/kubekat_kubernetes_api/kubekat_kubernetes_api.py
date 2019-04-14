from kubernetes import client, config, watch
from kubernetes.stream import stream

class kubernetes_query():
    def __init__(self, app):
        self.__config = config.load_incluster_config()
        self.__app = app

    def list_deployments_in_namespace(self, namespace):
        api = client.AppsV1Api()
        output = api.list_namespaced_deployment(namespace)
        return [deployment.metadata for deployment in output.items]

    def list_statefulsets_in_namespace(self, namespace):
        api = client.AppsV1Api()
        output = api.list_namespaced_stateful_set(namespace)
        return [statefulset.metadata for statefulset in output.items]

    def list_persistent_volume_claims_in_namespace(self, namespace):
        api = client.CoreV1Api()
        output = api.list_namespaced_persistent_volume_claim(namespace)
        return [pvc.metadata for pvc in output.items]

    def list_pods_in_namespace(self, namespace):
        api = client.CoreV1Api()
        output = api.list_namespaced_pod(namespace)
        return [pod for pod in output.items]

    def execute_command_in_pod(self, namespace, pod, command, container):
        api = client.CoreV1Api()
        output = stream(api.connect_get_namespaced_pod_exec, pod, namespace, command=command, stderr=True, stdin=False, stdout=True, tty=False, container=container)
        return output

    def list_namespaces(self):
        api = client.CoreV1Api()
        output = api.list_namespace()
        return [namespace.metadata.name for namespace in output.items]
