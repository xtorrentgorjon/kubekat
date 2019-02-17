from kubernetes import client, config, watch

class kubernetes_query():
    def __init__(self):
        self.__config = config.load_incluster_config()

    def list_deployments_in_namespace(self, namespace):
        api = client.AppsV1Api()
        output = api.list_namespaced_deployment(namespace)
        deployment_list = []
        for deployment in output.items:
            #out_deployment = deployment.metadata
            deployment_list.append(deployment.metadata)
        return deployment_list

    def list_statefulsets_in_namespace(self, namespace):
        api = client.AppsV1Api()
        output = api.list_namespaced_stateful_set(namespace)
        statefulset_list = []
        for statefulset in output.items:
            #out_statefulset = statefulset.metadata
            statefulset_list.append(statefulset.metadata)
        return statefulset_list


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
        self.__resource_list = []
        self.__resource_correct_labels = []
        self.__resource_incorrect_labels = []

    def get_correct_resources(self):
        return self.__resource_correct_labels

    def get_incorrect_resources(self):
        return self.__resource_incorrect_labels

    def filter_resource_by_label(self, exist_filter):
        self.__app.logger.debug('Current filter %s', exist_filter)
        if exist_filter == ['']:
            for resource in self.__resource_list:
                self.__resource_correct_labels.append(resource)
        else:
            for resource in self.__resource_list:
                self.__app.logger.debug('Checking resource %s', resource)
                filtered = False
                for filter in exist_filter:
                    if ":" in filter:
                        filter = filter.split(":")
                        filter_label_key = filter[0].rstrip().lstrip()
                        filter_label_value = filter[1].rstrip().lstrip()
                        if filter_label_key not in resource.labels:
                            filtered = True
                        elif str(filter_label_value) == str(resource.labels[filter_label_key]):
                            filtered = False
                        else:
                            filtered = True
                    else:
                        if resource.labels == None:
                            filtered = True
                        elif filter not in resource.labels:
                            filtered = True
                if filtered:
                    self.__resource_incorrect_labels.append(resource)
                else:
                    self.__resource_correct_labels.append(resource)


    def check_namespace(self, namespace):
        output_deployments = self.__kq.list_deployments_in_namespace(namespace)
        output_statefulsets = self.__kq.list_statefulsets_in_namespace(namespace)
        output = output_deployments + output_statefulsets
        return output


    def check_all_namespaces(self):
        output = self.__kq.list_namespaces()

        for namespace in output:
            self.__app.logger.debug('Checking namespace %s', namespace)
            resources_in_namespace = self.check_namespace(namespace)
            self.__resource_list += resources_in_namespace

        return self.__resource_list
