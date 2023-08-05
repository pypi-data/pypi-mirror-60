from kubernetes import client, config

class K8sCLI:

    def is_installed(self):
        try:
            config.load_kube_config()
            return True
        except:
            return False