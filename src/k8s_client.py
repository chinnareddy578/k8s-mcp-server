from typing import Any, Optional
from kubernetes import client
from mcp_instance import mcp
from k8s_utils import get_k8s_client

@mcp.tool()
def get_pods(namespace: str = "default"):
    """Get all pods in a given namespace"""
    api = get_k8s_client()['core']
    return [pod.metadata.name for pod in api.list_namespaced_pod(namespace).items]

@mcp.tool()
def get_pods_for_all_namespaces():
    """Get pods for all namespaces"""
    api = get_k8s_client()['core']
    return [pod.metadata.name for pod in api.list_pod_for_all_namespaces().items]

@mcp.tool()
def get_namespaces():
    """Get all namespaces"""
    api = get_k8s_client()['core']
    return [namespace.metadata.name for namespace in api.list_namespace().items]

@mcp.tool()
def get_nodes():
    """Get all nodes"""
    api = get_k8s_client()['core']
    return [node.metadata.name for node in api.list_node().items]

@mcp.tool()
def get_services():
    """Get all services"""
    api = get_k8s_client()['core']
    return [service.metadata.name for service in api.list_service_for_all_namespaces().items]

@mcp.tool()
def get_deployments():
    """Get all deployments"""
    api = get_k8s_client()['apps']
    return [deployment.metadata.name for deployment in api.list_deployment_for_all_namespaces().items]

@mcp.tool()
def get_replicasets():
    """Get all replicasets"""
    api = get_k8s_client()['apps']
    return [replicaset.metadata.name for replicaset in api.list_replica_set_for_all_namespaces().items]

@mcp.tool()
def get_statefulsets():
    """Get all statefulsets""" 
    api = get_k8s_client()['apps']
    return [statefulset.metadata.name for statefulset in api.list_stateful_set_for_all_namespaces().items]

@mcp.tool()
def get_jobs():
    """Get all jobs"""
    api = get_k8s_client()['core']
    return [job.metadata.name for job in api.list_job_for_all_namespaces().items]

@mcp.tool()
def get_configmaps():
    """Get all configmaps"""
    api = get_k8s_client()['core']
    return [configmap.metadata.name for configmap in api.list_config_map_for_all_namespaces().items]

@mcp.tool()
def get_endpoints():
    """Get all endpoints"""
    api = get_k8s_client()['core']
    return [endpoint.metadata.name for endpoint in api.list_endpoints_for_all_namespaces().items]

@mcp.tool()
def get_pvc():
    """Get all pvc"""
    api = get_k8s_client()['core']
    return [pvc.metadata.name for pvc in api.list_persistent_volume_claim_for_all_namespaces().items]

@mcp.tool()
def get_storageclasses():
    """Get all storageclasses"""
    api = get_k8s_client()['core']
    return [storageclass.metadata.name for storageclass in api.list_storage_class().items]

@mcp.tool()
def get_events():
    """Get all events from all namespaces"""
    api = get_k8s_client()['core']
    return [event.metadata.name for event in api.list_event_for_all_namespaces().items]

@mcp.tool()
def create_pod(namespace: str = "default", pod_name: str = "default-pod", image: str = "nginx:latest", replicas: int = 1):
    """Create a pod"""
    api = get_k8s_client()['core']
    pod = client.V1Pod(
        metadata=client.V1ObjectMeta(name=pod_name),
        spec=client.V1PodSpec(
            containers=[
                client.V1Container(
                    name=pod_name,
                    image=image
                )
            ]
        )
    )
    api.create_namespaced_pod(namespace, pod)
    return "Pod created successfully"