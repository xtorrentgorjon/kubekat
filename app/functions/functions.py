from kubernetes import client, config, watch

class kubernetes_query():
    def __init__(self):
        self.__config = config.load_incluster_config()
    def query(self, namespace):
        api = client.AppsV1beta1Api()
        deployment_list = api.list_namespaced_deployment(namespace)
        return deployment_list

class label_checker():
    def __init__(self, namespaces, app):
        self.__resources_with_label = []
        self.__resources_without_label = []
        self.__namespaces = namespaces
        self.app = app

    def check_namespace(self, namespace):
        kq = kubernetes_query()
        output = kq.query(namespace)

        for deployment in output.items:
            out_deployment = [str(deployment.metadata.namespace),str(deployment.metadata.name)]
            self.__resources_without_label.append(out_deployment)
        #out_deployment = [output["items"][0]["metadata"]["namespace"], output["items"][0]["metadata"]["name"]]
        #out_deployment = [str(output.items[0].metadata.namespace), "NAME"]
        #self.app.logger.info('%s', out_deployment[0])
        #self.__resources_without_label.append(out_deployment)

    def check_all_namespaces(self):
        for namespace in self.__namespaces:
            self.app.logger.info('CHECKING NAMESPACE %s', namespace)
            self.check_namespace(namespace)

        return self.__resources_without_label
