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
        #output = api.connect_get_namespaced_pod_exec(pod, namespace, command=command)
        self.__app.logger.info("Executing command '{}' in pod '{}' from namespace '{}'".format(str(command), str(pod), str(namespace)))
        output = stream(api.connect_get_namespaced_pod_exec, pod, namespace, command=command, stderr=True, stdin=False, stdout=True, tty=False, container=container)
        self.__app.logger.info("Result: '{}'".format(output))
        return output

    def list_namespaces(self):
        api = client.CoreV1Api()
        output = api.list_namespace()
        return [namespace.metadata.name for namespace in output.items]


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
                                        first_container = pod.spec.containers[0].name
                                        output = self.__kubernetes_query.execute_command_in_pod(str(pod.metadata.namespace), str(pod.metadata.name), ['/bin/df'], container=str(pod.spec.containers[0].name))
                                        list_of_filesystems = output.splitlines()
                                        pvc_filesystem = ''
                                        for filesystem in list_of_filesystems:
                                            if volume_mount.mount_path in filesystem:
                                                data = filesystem.split()
                                                pvc_filesystem = data[4]
                                        usage = pvc_filesystem
                                    except Exception as e:
                                        self.__app.logger.error('ERROR: {} {} Exception while doing exec command:{}'.format(str(pod.metadata.namespace), str(pod.metadata.name), e))
                                        self.__app.logger.error('ERROR: Pod Status: {}'.format(str(pod.status.phase)))
                                        pass

                                    if usage != '':
                                        self.__pvc_list.append({
                                            'pod_name':pod.metadata.name,
                                            'namespace':pod.metadata.namespace,
                                            'volume_name':volume.name,
                                            'claim_name':volume.persistent_volume_claim.claim_name,
                                            'pvc_usage': usage
                                        })


    def check_all_namespaces(self):
        namespace_list = self.__kubernetes_query.list_namespaces()

        for namespace in namespace_list:
            self.__app.logger.info('CHECKING NAMESPACE {}'.format(namespace))
            self.check_namespace(namespace)

        self.filter_pods_without_pvc()

        return self.__pvc_list
