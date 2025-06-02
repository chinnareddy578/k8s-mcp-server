from typing import Optional, List, Dict, Any, Union
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from mcp_instance import mcp
import base64

def get_k8s_client(kubeconfig: Optional[str] = None):
    """Initialize Kubernetes client"""
    if kubeconfig:
        config.load_kube_config(config_file=kubeconfig)
    else:
        config.load_kube_config()
    return {
        'core': client.CoreV1Api(),
        'exec': client.CoreV1Api()
    }

@mcp.tool()
def get_pod_details(namespace: str, pod_name: str) -> Dict[str, Any]:
    """Get detailed information about a specific pod"""
    api = get_k8s_client()['core']
    try:
        pod = api.read_namespaced_pod(pod_name, namespace)
        return {
            "name": pod.metadata.name,
            "namespace": pod.metadata.namespace,
            "status": pod.status.phase,
            "host_ip": pod.status.host_ip,
            "pod_ip": pod.status.pod_ip,
            "start_time": pod.status.start_time,
            "containers": [
                {
                    "name": container.name,
                    "image": container.image,
                    "ready": container.ready,
                    "restart_count": container.restart_count,
                    "state": container.state
                }
                for container in pod.status.container_statuses
            ],
            "conditions": [
                {
                    "type": condition.type,
                    "status": condition.status,
                    "reason": condition.reason,
                    "message": condition.message
                }
                for condition in pod.status.conditions
            ]
        }
    except ApiException as e:
        raise Exception(f"Failed to get pod details: {str(e)}")

@mcp.tool()
def get_pod_logs(
    namespace: str,
    pod_name: str,
    container: Optional[str] = None,
    tail_lines: Optional[int] = None,
    previous: bool = False
) -> str:
    """Get logs from a pod"""
    api = get_k8s_client()['core']
    try:
        return api.read_namespaced_pod_log(
            name=pod_name,
            namespace=namespace,
            container=container,
            tail_lines=tail_lines,
            previous=previous
        )
    except ApiException as e:
        raise Exception(f"Failed to get pod logs: {str(e)}")

@mcp.tool()
def create_pod(
    namespace: str,
    pod_name: str,
    image: str,
    container_port: int = 80,
    env_vars: Dict[str, str] = None,
    labels: Dict[str, str] = None,
    node_selector: Dict[str, str] = None,
    resource_limits: Dict[str, str] = None,
    resource_requests: Dict[str, str] = None
) -> str:
    """Create a new pod with specified configuration"""
    api = get_k8s_client()['core']
    
    if labels is None:
        labels = {"app": pod_name}
    
    container_env = []
    if env_vars:
        container_env = [
            client.V1EnvVar(name=k, value=v)
            for k, v in env_vars.items()
        ]

    resources = None
    if resource_limits or resource_requests:
        resources = client.V1ResourceRequirements(
            limits=resource_limits,
            requests=resource_requests
        )

    pod = client.V1Pod(
        metadata=client.V1ObjectMeta(
            name=pod_name,
            labels=labels
        ),
        spec=client.V1PodSpec(
            containers=[
                client.V1Container(
                    name=pod_name,
                    image=image,
                    ports=[client.V1ContainerPort(container_port=container_port)],
                    env=container_env,
                    resources=resources
                )
            ],
            node_selector=node_selector
        )
    )

    try:
        api.create_namespaced_pod(namespace=namespace, body=pod)
        return f"Pod {pod_name} created successfully"
    except ApiException as e:
        raise Exception(f"Failed to create pod: {str(e)}")

@mcp.tool()
def delete_pod(namespace: str, pod_name: str) -> str:
    """Delete a pod"""
    api = get_k8s_client()['core']
    try:
        api.delete_namespaced_pod(
            name=pod_name,
            namespace=namespace,
            body=client.V1DeleteOptions(
                propagation_policy='Foreground'
            )
        )
        return f"Pod {pod_name} deleted successfully"
    except ApiException as e:
        raise Exception(f"Failed to delete pod: {str(e)}")

@mcp.tool()
def get_pod_events(namespace: str, pod_name: str) -> List[Dict[str, Any]]:
    """Get events related to a pod"""
    api = get_k8s_client()['core']
    try:
        events = api.list_namespaced_event(
            namespace=namespace,
            field_selector=f"involvedObject.name={pod_name},involvedObject.kind=Pod"
        )
        return [
            {
                "type": event.type,
                "reason": event.reason,
                "message": event.message,
                "last_timestamp": event.last_timestamp,
                "count": event.count
            }
            for event in events.items
        ]
    except ApiException as e:
        raise Exception(f"Failed to get pod events: {str(e)}")

@mcp.tool()
def get_pod_metrics(namespace: str, pod_name: str) -> Dict[str, Any]:
    """Get resource usage metrics for a pod"""
    api = get_k8s_client()['core']
    try:
        # Note: This requires metrics-server to be installed in the cluster
        metrics = api.get_namespaced_pod_metrics(pod_name, namespace)
        return {
            "pod": metrics.metadata.name,
            "timestamp": metrics.timestamp,
            "window": metrics.window,
            "containers": [
                {
                    "name": container.name,
                    "usage": {
                        "cpu": container.usage.get("cpu", "0"),
                        "memory": container.usage.get("memory", "0")
                    }
                }
                for container in metrics.containers
            ]
        }
    except ApiException as e:
        raise Exception(f"Failed to get pod metrics: {str(e)}")

@mcp.tool()
def get_pod_security_context(namespace: str, pod_name: str) -> Dict[str, Any]:
    """Get security context information for a pod"""
    api = get_k8s_client()['core']
    try:
        pod = api.read_namespaced_pod(pod_name, namespace)
        return {
            "pod_security_context": pod.spec.security_context,
            "container_security_contexts": [
                {
                    "container_name": container.name,
                    "security_context": container.security_context
                }
                for container in pod.spec.containers
            ]
        }
    except ApiException as e:
        raise Exception(f"Failed to get pod security context: {str(e)}")

@mcp.tool()
def get_pod_volumes(namespace: str, pod_name: str) -> List[Dict[str, Any]]:
    """Get volume information for a pod"""
    api = get_k8s_client()['core']
    try:
        pod = api.read_namespaced_pod(pod_name, namespace)
        return [
            {
                "name": volume.name,
                "type": volume.__class__.__name__,
                "details": volume.to_dict()
            }
            for volume in pod.spec.volumes
        ]
    except ApiException as e:
        raise Exception(f"Failed to get pod volumes: {str(e)}")

@mcp.tool()
def get_pod_network_policy(namespace: str, pod_name: str) -> Dict[str, Any]:
    """Get network policy information for a pod"""
    api = get_k8s_client()['core']
    try:
        pod = api.read_namespaced_pod(pod_name, namespace)
        return {
            "pod_name": pod.metadata.name,
            "namespace": pod.metadata.namespace,
            "labels": pod.metadata.labels,
            "annotations": pod.metadata.annotations
        }
    except ApiException as e:
        raise Exception(f"Failed to get pod network policy: {str(e)}")

@mcp.tool()
def get_pod_health_check(namespace: str, pod_name: str) -> Dict[str, Any]:
    """Get health check configuration for a pod"""
    api = get_k8s_client()['core']
    try:
        pod = api.read_namespaced_pod(pod_name, namespace)
        return {
            "pod_name": pod.metadata.name,
            "containers": [
                {
                    "name": container.name,
                    "liveness_probe": container.liveness_probe,
                    "readiness_probe": container.readiness_probe,
                    "startup_probe": container.startup_probe
                }
                for container in pod.spec.containers
            ]
        }
    except ApiException as e:
        raise Exception(f"Failed to get pod health check: {str(e)}") 