from typing import Optional, List, Dict, Any, Union
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from mcp_instance import mcp
from k8s_utils import get_k8s_client

def get_k8s_client(kubeconfig: Optional[str] = None):
    """Initialize Kubernetes client"""
    if kubeconfig:
        config.load_kube_config(config_file=kubeconfig)
    else:
        config.load_kube_config()
    return {
        'apps': client.AppsV1Api(),
        'core': client.CoreV1Api()
    }

@mcp.tool()
def get_replicasets(namespace: str = "default") -> List[Dict[str, Any]]:
    """Get all ReplicaSets in a namespace"""
    api = get_k8s_client()['apps']
    try:
        replicasets = api.list_namespaced_replica_set(namespace)
        return [
            {
                "name": rs.metadata.name,
                "namespace": rs.metadata.namespace,
                "replicas": rs.spec.replicas,
                "available_replicas": rs.status.available_replicas,
                "ready_replicas": rs.status.ready_replicas,
                "selector": rs.spec.selector.match_labels,
                "template": {
                    "containers": [
                        {
                            "name": container.name,
                            "image": container.image,
                            "ports": [
                                {
                                    "name": port.name,
                                    "container_port": port.container_port,
                                    "protocol": port.protocol
                                }
                                for port in container.ports
                            ] if container.ports else []
                        }
                        for container in rs.spec.template.spec.containers
                    ]
                },
                "creation_timestamp": rs.metadata.creation_timestamp,
                "labels": rs.metadata.labels,
                "annotations": rs.metadata.annotations
            }
            for rs in replicasets.items
        ]
    except ApiException as e:
        raise Exception(f"Failed to get ReplicaSets: {str(e)}")

@mcp.tool()
def get_replicaset_details(namespace: str, replicaset_name: str) -> Dict[str, Any]:
    """Get detailed information about a specific ReplicaSet"""
    api = get_k8s_client()['apps']
    try:
        rs = api.read_namespaced_replica_set(replicaset_name, namespace)
        return {
            "name": rs.metadata.name,
            "namespace": rs.metadata.namespace,
            "replicas": rs.spec.replicas,
            "available_replicas": rs.status.available_replicas,
            "ready_replicas": rs.status.ready_replicas,
            "fully_labeled_replicas": rs.status.fully_labeled_replicas,
            "selector": rs.spec.selector.match_labels,
            "template": {
                "containers": [
                    {
                        "name": container.name,
                        "image": container.image,
                        "ports": [
                            {
                                "name": port.name,
                                "container_port": port.container_port,
                                "protocol": port.protocol
                            }
                            for port in container.ports
                        ] if container.ports else [],
                        "resources": container.resources.to_dict() if container.resources else None,
                        "env": [
                            {
                                "name": env.name,
                                "value": env.value,
                                "value_from": env.value_from.to_dict() if env.value_from else None
                            }
                            for env in container.env
                        ] if container.env else []
                    }
                    for container in rs.spec.template.spec.containers
                ],
                "volumes": [
                    {
                        "name": volume.name,
                        "type": volume.__class__.__name__,
                        "details": volume.to_dict()
                    }
                    for volume in rs.spec.template.spec.volumes
                ] if rs.spec.template.spec.volumes else []
            },
            "creation_timestamp": rs.metadata.creation_timestamp,
            "labels": rs.metadata.labels,
            "annotations": rs.metadata.annotations,
            "owner_references": [
                {
                    "kind": ref.kind,
                    "name": ref.name,
                    "uid": ref.uid
                }
                for ref in rs.metadata.owner_references
            ] if rs.metadata.owner_references else []
        }
    except ApiException as e:
        raise Exception(f"Failed to get ReplicaSet details: {str(e)}")

@mcp.tool()
def create_replicaset(
    namespace: str,
    replicaset_name: str,
    image: str,
    replicas: int = 1,
    container_name: Optional[str] = None,
    container_port: Optional[int] = None,
    env_vars: Optional[Dict[str, str]] = None,
    labels: Optional[Dict[str, str]] = None,
    annotations: Optional[Dict[str, str]] = None,
    selector: Optional[Dict[str, str]] = None,
    resource_limits: Optional[Dict[str, str]] = None,
    resource_requests: Optional[Dict[str, str]] = None
) -> str:
    """Create a new ReplicaSet"""
    api = get_k8s_client()['apps']
    
    if container_name is None:
        container_name = replicaset_name
    
    if labels is None:
        labels = {"app": replicaset_name}
    
    if selector is None:
        selector = labels

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

    container_ports = []
    if container_port:
        container_ports = [
            client.V1ContainerPort(
                container_port=container_port,
                protocol="TCP"
            )
        ]

    replicaset = client.V1ReplicaSet(
        metadata=client.V1ObjectMeta(
            name=replicaset_name,
            namespace=namespace,
            labels=labels,
            annotations=annotations
        ),
        spec=client.V1ReplicaSetSpec(
            replicas=replicas,
            selector=client.V1LabelSelector(match_labels=selector),
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels=labels),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name=container_name,
                            image=image,
                            ports=container_ports,
                            env=container_env,
                            resources=resources
                        )
                    ]
                )
            )
        )
    )

    try:
        api.create_namespaced_replica_set(namespace=namespace, body=replicaset)
        return f"ReplicaSet {replicaset_name} created successfully"
    except ApiException as e:
        raise Exception(f"Failed to create ReplicaSet: {str(e)}")

@mcp.tool()
def update_replicaset(
    namespace: str,
    replicaset_name: str,
    replicas: Optional[int] = None,
    image: Optional[str] = None,
    env_vars: Optional[Dict[str, str]] = None,
    labels: Optional[Dict[str, str]] = None,
    annotations: Optional[Dict[str, str]] = None,
    resource_limits: Optional[Dict[str, str]] = None,
    resource_requests: Optional[Dict[str, str]] = None
) -> str:
    """Update an existing ReplicaSet"""
    api = get_k8s_client()['apps']
    try:
        # Get existing ReplicaSet
        rs = api.read_namespaced_replica_set(replicaset_name, namespace)
        
        # Update fields if provided
        if replicas is not None:
            rs.spec.replicas = replicas
        
        if image or env_vars or resource_limits or resource_requests:
            container = rs.spec.template.spec.containers[0]
            if image:
                container.image = image
            if env_vars:
                container.env = [
                    client.V1EnvVar(name=k, value=v)
                    for k, v in env_vars.items()
                ]
            if resource_limits or resource_requests:
                container.resources = client.V1ResourceRequirements(
                    limits=resource_limits,
                    requests=resource_requests
                )
        
        if labels:
            rs.metadata.labels = labels
            rs.spec.template.metadata.labels = labels
        if annotations:
            rs.metadata.annotations = annotations

        api.replace_namespaced_replica_set(
            name=replicaset_name,
            namespace=namespace,
            body=rs
        )
        return f"ReplicaSet {replicaset_name} updated successfully"
    except ApiException as e:
        raise Exception(f"Failed to update ReplicaSet: {str(e)}")

@mcp.tool()
def delete_replicaset(namespace: str, replicaset_name: str) -> str:
    """Delete a ReplicaSet"""
    api = get_k8s_client()['apps']
    try:
        api.delete_namespaced_replica_set(
            name=replicaset_name,
            namespace=namespace,
            body=client.V1DeleteOptions(
                propagation_policy='Foreground'
            )
        )
        return f"ReplicaSet {replicaset_name} deleted successfully"
    except ApiException as e:
        raise Exception(f"Failed to delete ReplicaSet: {str(e)}")

@mcp.tool()
def scale_replicaset(namespace: str, replicaset_name: str, replicas: int) -> str:
    """Scale a ReplicaSet to a specific number of replicas"""
    api = get_k8s_client()['apps']
    try:
        api.patch_namespaced_replica_set_scale(
            name=replicaset_name,
            namespace=namespace,
            body={"spec": {"replicas": replicas}}
        )
        return f"ReplicaSet {replicaset_name} scaled to {replicas} replicas"
    except ApiException as e:
        raise Exception(f"Failed to scale ReplicaSet: {str(e)}")

@mcp.tool()
def get_replicaset_pods(namespace: str, replicaset_name: str) -> List[Dict[str, Any]]:
    """Get all pods managed by a ReplicaSet"""
    api = get_k8s_client()['core']
    try:
        # Get ReplicaSet details to get the selector
        rs_api = get_k8s_client()['apps']
        rs = rs_api.read_namespaced_replica_set(replicaset_name, namespace)
        selector = rs.spec.selector.match_labels
        
        # Convert selector to label selector string
        label_selector = ",".join([f"{k}={v}" for k, v in selector.items()])
        
        # Get pods with the selector
        pods = api.list_namespaced_pod(
            namespace=namespace,
            label_selector=label_selector
        )
        
        return [
            {
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
                ]
            }
            for pod in pods.items
        ]
    except ApiException as e:
        raise Exception(f"Failed to get ReplicaSet pods: {str(e)}")

@mcp.tool()
def get_replicaset_events(namespace: str, replicaset_name: str) -> List[Dict[str, Any]]:
    """Get events related to a ReplicaSet"""
    api = get_k8s_client()['core']
    try:
        events = api.list_namespaced_event(
            namespace=namespace,
            field_selector=f"involvedObject.name={replicaset_name},involvedObject.kind=ReplicaSet"
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
        raise Exception(f"Failed to get ReplicaSet events: {str(e)}")

@mcp.tool()
def get_replicaset_rollout_status(namespace: str, replicaset_name: str) -> Dict[str, Any]:
    """Get the rollout status of a ReplicaSet"""
    api = get_k8s_client()['apps']
    try:
        rs = api.read_namespaced_replica_set(replicaset_name, namespace)
        return {
            "name": rs.metadata.name,
            "namespace": rs.metadata.namespace,
            "desired_replicas": rs.spec.replicas,
            "available_replicas": rs.status.available_replicas,
            "ready_replicas": rs.status.ready_replicas,
            "fully_labeled_replicas": rs.status.fully_labeled_replicas,
            "conditions": [
                {
                    "type": condition.type,
                    "status": condition.status,
                    "reason": condition.reason,
                    "message": condition.message,
                    "last_transition_time": condition.last_transition_time
                }
                for condition in rs.status.conditions
            ] if rs.status.conditions else []
        }
    except ApiException as e:
        raise Exception(f"Failed to get ReplicaSet rollout status: {str(e)}") 