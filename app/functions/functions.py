from kubernetes import client, config, watch

class kubernetes_query():
    def __init__(self):
        self.__config = config.load_incluster_config()

    def list_deployments_in_namespace(self, namespace):
        api = client.AppsV1Api()
        output = api.list_namespaced_deployment(namespace)
        deployment_list = []
        for deployment in output.items:
            out_deployment = deployment.metadata
            deployment_list.append(out_deployment)
        return deployment_list


    def list_namespaces(self):
        api = client.CoreV1Api()
        output = api.list_namespace()
        namespace_list = []
        for namespace in output.items:
            namespace_list.append(str(namespace.metadata.name))
        return namespace_list


class label_checker():
    def __init__(self, app):
        self.__app = app
        self.__kq = kubernetes_query()
        self.__deployment_list = []
        self.__deployment_correct_labels = []
        self.__deployment_incorrect_labels = []

    def get_correct_deployments(self):
        return self.__deployment_correct_labels

    def get_incorrect_deployments(self):
        return self.__deployment_incorrect_labels

    def filter_deployment_by_label(self, exist_filter):
        self.__app.logger.debug('Current filter %s', exist_filter)
        if exist_filter == ['']:
            for deployment in self.__deployment_list:
                self.__deployment_correct_labels.append(deployment)
        else:
            for deployment in self.__deployment_list:
                filtered = False
                for filter in exist_filter:
                    if ":" in filter:
                        filter = filter.split(":")
                        if filter[0] not in deployment.labels:
                            filtered = True
                        elif str(filter[1]) == str(deployment.labels[str(filter[0])]):
                            filtered = False
                        else:
                            filtered = True
                    else:
                        if filter not in deployment.labels:
                            filtered = True
                if filtered:
                    self.__deployment_incorrect_labels.append(deployment)
                else:
                    self.__deployment_correct_labels.append(deployment)


    def check_namespace(self, namespace):
        output = self.__kq.list_deployments_in_namespace(namespace)
        return output


    def check_all_namespaces(self):
        output = self.__kq.list_namespaces()

        for namespace in output:
            self.__app.logger.debug('Checking namespace %s', namespace)
            deployments_in_namespace = self.check_namespace(namespace)
            self.__deployment_list += deployments_in_namespace

        return self.__deployment_list
