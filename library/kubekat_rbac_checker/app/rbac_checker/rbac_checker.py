from kubernetes import client, config, watch
from kubekat_kubernetes_api.kubekat_kubernetes_api import kubernetes_query


class rbac_checker():
    def __init__(self, app):
        self.__app = app
        self.__kubernetes_query = kubernetes_query(self.__app)
        self.__resource_list = []


    def check_namespace(self, namespace):
        output = [rolebinding for rolebinding in self.__kubernetes_query.list_role_binding_in_namespace(namespace)]
        for i in output:
            self.__app.logger.debug('RBAC found: {}'.format(i))
        return output


    def check_all_namespaces(self):
        output = self.__kubernetes_query.list_namespaces()

        for namespace in output:
            self.__app.logger.debug('Checking namespace %s', namespace)
            self.__resource_list += self.check_namespace(namespace)

        return self.__resource_list
