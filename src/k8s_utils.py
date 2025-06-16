from typing import Optional, Dict, Any
from kubernetes import client, config
from kubernetes.client.rest import ApiException

def get_k8s_client(kubeconfig: Optional[str] = None) -> Dict[str, Any]:
    """Initialize Kubernetes client with certificate validation disabled"""
    configuration = client.Configuration()
    
    # Load kubeconfig
    if kubeconfig:
        config.load_kube_config(config_file=kubeconfig, client_configuration=configuration)
    else:
        config.load_kube_config(client_configuration=configuration)
    
    # Disable SSL certificate verification
    configuration.verify_ssl = False
    
    # Create API clients
    return {
        'core': client.CoreV1Api(client.ApiClient(configuration)),
        'apps': client.AppsV1Api(client.ApiClient(configuration))
    } 