from kubernetes import client, config, watch
from kubekat_kubernetes_api.kubekat_kubernetes_api import kubernetes_query
from hashlib import sha1


class label_checker():
    def __init__(self, app):
        self.__app = app
        self.__kubernetes_query = kubernetes_query(self.__app)
        self.__resource_list = []
        self.__resource_correct_labels = []
        self.__resource_incorrect_labels = []

    def get_correct_resources(self):
        return self.__resource_correct_labels

    def get_incorrect_resources(self):
        return self.__resource_incorrect_labels

    def filter_resource_by_label(self, exist_filter):
        self.__app.logger.debug('Current filter %s', exist_filter)
        if exist_filter == ['']: # If there is no filter, accept all.
            for resource in self.__resource_list:
                self.__resource_correct_labels.append(resource)
        else:
            for resource in self.__resource_list:
                filtered = False
                labels = []
                if resource["metadata"].labels == None: # If resource has no labels, automatically classify it as invalid.
                    labels = [{"id": None, "key": None, "value": None}]
                    filtered = True
                else:
                    labels = [{"id":str(sha1((str(labelkey)+str(labelvalue)).encode('utf-8')).hexdigest()), "key":labelkey, "value": labelvalue} for labelkey, labelvalue in resource["metadata"].labels.items()]
                    for i in labels:
                        self.__app.logger.debug('Element {}, Label element < {} >'.format(resource["metadata"].name, (i["id"], i["key"], i["value"])))
                    for filter in exist_filter:
                        if ":" in filter: # If : exists, must check full key:value pair.
                            filter = filter.split(":")
                            filter_label_key = filter[0].strip()
                            filter_label_value = filter[1].strip()
                            if filter_label_key not in resource["metadata"].labels:
                                filtered = True
                            elif str(filter_label_value) == str(resource["metadata"].labels[filter_label_key]):
                                filtered = False
                            else:
                                filtered = True
                        else: # Check only that label exists.
                            if filter not in resource["metadata"].labels:
                                filtered = True


                resource = {
                    'namespace':resource["metadata"].namespace,
                    'name':resource["metadata"].name,
                    'labels':labels,
                    'type':resource["type"],
                }
                if filtered:
                    self.__resource_incorrect_labels.append(resource)
                else:
                    self.__resource_correct_labels.append(resource)


    def check_namespace(self, namespace):
        output = [{"metadata": deployment, "type": "deployment"}
            for deployment in self.__kubernetes_query.list_deployments_in_namespace(namespace)]
        output += [{"metadata": statefulset, "type": "statefulset"}
            for statefulset in self.__kubernetes_query.list_statefulsets_in_namespace(namespace)]
        return output


    def check_all_namespaces(self):
        output = self.__kubernetes_query.list_namespaces()

        for namespace in output:
            self.__app.logger.debug('Checking namespace %s', namespace)
            self.__resource_list += self.check_namespace(namespace)

        return self.__resource_list
