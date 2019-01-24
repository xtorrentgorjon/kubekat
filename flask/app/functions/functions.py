class label_checker():
    def __init__(self, namespaces):
        self.__resources_with_label = []
        self.__resources_without_label = []
        self.__namespaces = namespaces

    def check_namespace(self, namespace):
        output = [\
        [namespace, "app1"],\
        [namespace, "app2"],\
        [namespace, "app3"]\
        ]
        self.__resources_without_label.append(output)

    def check_all_namespaces(self):
        for namespace in self.__namespaces:
            self.check_namespace(namespace)

        return self.__resources_without_label
