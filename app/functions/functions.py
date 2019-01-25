from kubernetes import client, config, watch

class kubernetes_query():
    def __init__(self):
        self.__config = config.load_incluster_config()
        self.__resources_without_label = []

    def list_deployments_in_namespace(self, namespace):
        api = client.AppsV1Api()
        output = api.list_namespaced_deployment(namespace)

        for deployment in output.items:
            namespace = str(deployment.metadata.namespace)
            name = str(deployment.metadata.name)
            out_deployment = [namespace, name]
            self.__resources_without_label.append(out_deployment)
        return self.__resources_without_label


    def list_namespaces(self):
        api = client.CoreV1Api()
        output = api.list_namespace()
        namespace_list = []
        for namespace in output.items:
            namespace_list.append(str(namespace.metadata.name))
        return namespace_list


class label_checker():
    def __init__(self, app):
        self.app = app

    def check_namespace(self, namespace):
        kq = kubernetes_query()
        output = kq.list_deployments_in_namespace(namespace)
        return output


    def check_all_namespaces(self):
        deployments_in_namespace = []
        kq = kubernetes_query()
        output = kq.list_namespaces()
        self.app.logger.info('Namespace list: %s', output)

        for namespace in output:
            self.app.logger.info('CHECKING NAMESPACE %s', namespace)
            deployments_in_namespace.append(self.check_namespace(namespace))
            self.app.logger.info('Apps checked so far: %s', deployments_in_namespace)

        return deployments_in_namespace
