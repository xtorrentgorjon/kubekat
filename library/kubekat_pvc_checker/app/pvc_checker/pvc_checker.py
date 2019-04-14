from kubekat_kubernetes_api.kubekat_kubernetes_api import kubernetes_query

class pvc_checker():
    def __init__(self, app):
        self.__app = app
        self.__pod_list = []
        self.__pvc_list = []
        self.__kubernetes_query = kubernetes_query(self.__app)

    def check_namespace(self, namespace):
        list_pod_namespace = self.__kubernetes_query.list_pods_in_namespace(namespace)
        for pvc in list_pod_namespace:
            self.__app.logger.info('Namespace {}, {}'.format(namespace, str(pvc.metadata.name)))
            self.__pod_list.append(pvc)

    def filter_pods_without_pvc(self):
        for pod in self.__pod_list:
            if pod.spec.volumes != None and pod.status.phase == "Running":
                for volume in pod.spec.volumes:
                    if (volume.persistent_volume_claim != None):
                        for container in pod.spec.containers:
                            for volume_mount in container.volume_mounts:
                                if volume_mount.name == volume.name:
                                    usage = ''
                                    try:
                                        # self.__app.logger.info("Executing command '{}' in pod '{}' from namespace '{}'".format(str(command), str(pod), str(namespace)))
                                        # self.__app.logger.info("Result: '{}'".format(output))
                                        first_container = pod.spec.containers[0].name
                                        output = self.__kubernetes_query.execute_command_in_pod(str(pod.metadata.namespace), str(pod.metadata.name), ['/bin/df'], container=str(pod.spec.containers[0].name))
                                        list_of_filesystems = output.splitlines()
                                        self.__app.logger.error("DEBUG: On container '{}', detected filesystems '{}'".format(first_container, list_of_filesystems))
                                        pvc_filesystem = ''
                                        for filesystem in list_of_filesystems:
                                            if volume_mount.mount_path in filesystem:
                                                data = filesystem.split()
                                                pvc_filesystem = data[4]
                                            else:
                                                self.__app.logger.error("DEBUG: On container '{}', mount '{}' not in '{}'".format(first_container, volume_mount.mount_path, list_of_filesystems))
                                        usage = pvc_filesystem
                                    except Exception as e:
                                        self.__app.logger.error('ERROR: {} {} Exception while doing exec command:{}'.format(str(pod.metadata.namespace), str(pod.metadata.name), e))
                                        self.__app.logger.error('ERROR: Pod Status: {}'.format(str(pod.status.phase)))
                                        pass
                                    self.__app.logger.error("DEBUG: On container '{}', usage '{}'".format(first_container, usage))
                                    if usage != '':
                                        self.__pvc_list.append({
                                            'pod_name':pod.metadata.name,
                                            'namespace':pod.metadata.namespace,
                                            'volume_name':volume.name,
                                            'claim_name':volume.persistent_volume_claim.claim_name,
                                            'pvc_usage': usage
                                        })
                                    else:
                                        self.__pvc_list.append({
                                            'pod_name':pod.metadata.name,
                                            'namespace':pod.metadata.namespace,
                                            'volume_name':volume.name,
                                            'claim_name':volume.persistent_volume_claim.claim_name,
                                            'pvc_usage': 'N/A'
                                        })


    def check_all_namespaces(self):
        namespace_list = self.__kubernetes_query.list_namespaces()

        for namespace in namespace_list:
            self.__app.logger.info('CHECKING NAMESPACE {}'.format(namespace))
            self.check_namespace(namespace)

        self.filter_pods_without_pvc()

        self.__app.logger.info("DEBUG: Returned PVC list'{}'".format(self.__pvc_list))

        return self.__pvc_list
