from typing import Optional, List, Dict, Any, Union
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from mcp_instance import mcp

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
def get_deployments(namespace: str = "default") -> List[str]:
    """Get all deployments in a namespace"""
    api = get_k8s_client()['apps']
    try:
        deployments = api.list_namespaced_deployment(namespace)
        return [deployment.metadata.name for deployment in deployments.items]
    except ApiException as e:
        raise Exception(f"Failed to get deployments: {str(e)}")

@mcp.tool()
def get_deployment_details(namespace: str, deployment_name: str) -> Dict[str, Any]:
    """Get detailed information about a specific deployment"""
    api = get_k8s_client()['apps']
    try:
        deployment = api.read_namespaced_deployment(deployment_name, namespace)
        return {
            "name": deployment.metadata.name,
            "replicas": deployment.spec.replicas,
            "available_replicas": deployment.status.available_replicas,
            "ready_replicas": deployment.status.ready_replicas,
            "updated_replicas": deployment.status.updated_replicas,
            "image": deployment.spec.template.spec.containers[0].image,
            "creation_timestamp": deployment.metadata.creation_timestamp
        }
    except ApiException as e:
        raise Exception(f"Failed to get deployment details: {str(e)}")

@mcp.tool()
def create_deployment(
    namespace: str,
    deployment_name: str,
    image: str,
    replicas: int = 1,
    container_port: int = 80,
    labels: Dict[str, str] = None,
    env_vars: Dict[str, str] = None
) -> str:
    """Create a new deployment"""
    api = get_k8s_client()['apps']
    
    if labels is None:
        labels = {"app": deployment_name}
    
    container_env = []
    if env_vars:
        container_env = [
            client.V1EnvVar(name=k, value=v)
            for k, v in env_vars.items()
        ]

    deployment = client.V1Deployment(
        metadata=client.V1ObjectMeta(name=deployment_name),
        spec=client.V1DeploymentSpec(
            replicas=replicas,
            selector=client.V1LabelSelector(match_labels=labels),
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels=labels),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name=deployment_name,
                            image=image,
                            ports=[client.V1ContainerPort(container_port=container_port)],
                            env=container_env
                        )
                    ]
                )
            )
        )
    )

    try:
        api.create_namespaced_deployment(namespace=namespace, body=deployment)
        return f"Deployment {deployment_name} created successfully"
    except ApiException as e:
        raise Exception(f"Failed to create deployment: {str(e)}")

@mcp.tool()
def create_deployment_with_strategy(
    namespace: str,
    deployment_name: str,
    image: str,
    replicas: int = 1,
    strategy_type: str = "RollingUpdate",
    max_surge: Union[int, str] = "25%",
    max_unavailable: Union[int, str] = "25%",
    container_port: int = 80,
    labels: Dict[str, str] = None,
    env_vars: Dict[str, str] = None
) -> str:
    """Create a deployment with specified update strategy"""
    api = get_k8s_client()['apps']
    
    if labels is None:
        labels = {"app": deployment_name}
    
    container_env = []
    if env_vars:
        container_env = [
            client.V1EnvVar(name=k, value=v)
            for k, v in env_vars.items()
        ]

    deployment = client.V1Deployment(
        metadata=client.V1ObjectMeta(name=deployment_name),
        spec=client.V1DeploymentSpec(
            replicas=replicas,
            strategy=client.V1DeploymentStrategy(
                type=strategy_type,
                rolling_update=client.V1RollingUpdateDeployment(
                    max_surge=max_surge,
                    max_unavailable=max_unavailable
                ) if strategy_type == "RollingUpdate" else None
            ),
            selector=client.V1LabelSelector(match_labels=labels),
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels=labels),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name=deployment_name,
                            image=image,
                            ports=[client.V1ContainerPort(container_port=container_port)],
                            env=container_env
                        )
                    ]
                )
            )
        )
    )

    try:
        api.create_namespaced_deployment(namespace=namespace, body=deployment)
        return f"Deployment {deployment_name} created successfully with {strategy_type} strategy"
    except ApiException as e:
        raise Exception(f"Failed to create deployment: {str(e)}")

@mcp.tool()
def create_deployment_with_resources(
    namespace: str,
    deployment_name: str,
    image: str,
    cpu_request: str = "100m",
    cpu_limit: str = "200m",
    memory_request: str = "128Mi",
    memory_limit: str = "256Mi",
    replicas: int = 1,
    container_port: int = 80,
    labels: Dict[str, str] = None,
    env_vars: Dict[str, str] = None
) -> str:
    """Create a deployment with resource limits and requests"""
    api = get_k8s_client()['apps']
    
    if labels is None:
        labels = {"app": deployment_name}
    
    container_env = []
    if env_vars:
        container_env = [
            client.V1EnvVar(name=k, value=v)
            for k, v in env_vars.items()
        ]

    deployment = client.V1Deployment(
        metadata=client.V1ObjectMeta(name=deployment_name),
        spec=client.V1DeploymentSpec(
            replicas=replicas,
            selector=client.V1LabelSelector(match_labels=labels),
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels=labels),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name=deployment_name,
                            image=image,
                            ports=[client.V1ContainerPort(container_port=container_port)],
                            env=container_env,
                            resources=client.V1ResourceRequirements(
                                requests={
                                    "cpu": cpu_request,
                                    "memory": memory_request
                                },
                                limits={
                                    "cpu": cpu_limit,
                                    "memory": memory_limit
                                }
                            )
                        )
                    ]
                )
            )
        )
    )

    try:
        api.create_namespaced_deployment(namespace=namespace, body=deployment)
        return f"Deployment {deployment_name} created successfully with resource limits"
    except ApiException as e:
        raise Exception(f"Failed to create deployment: {str(e)}")

@mcp.tool()
def create_deployment_with_health_checks(
    namespace: str,
    deployment_name: str,
    image: str,
    liveness_path: str = "/health",
    readiness_path: str = "/ready",
    initial_delay_seconds: int = 30,
    period_seconds: int = 10,
    timeout_seconds: int = 5,
    success_threshold: int = 1,
    failure_threshold: int = 3,
    replicas: int = 1,
    container_port: int = 80,
    labels: Dict[str, str] = None,
    env_vars: Dict[str, str] = None
) -> str:
    """Create a deployment with liveness and readiness probes"""
    api = get_k8s_client()['apps']
    
    if labels is None:
        labels = {"app": deployment_name}
    
    container_env = []
    if env_vars:
        container_env = [
            client.V1EnvVar(name=k, value=v)
            for k, v in env_vars.items()
        ]

    deployment = client.V1Deployment(
        metadata=client.V1ObjectMeta(name=deployment_name),
        spec=client.V1DeploymentSpec(
            replicas=replicas,
            selector=client.V1LabelSelector(match_labels=labels),
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels=labels),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name=deployment_name,
                            image=image,
                            ports=[client.V1ContainerPort(container_port=container_port)],
                            env=container_env,
                            liveness_probe=client.V1Probe(
                                http_get=client.V1HTTPGetAction(
                                    path=liveness_path,
                                    port=container_port
                                ),
                                initial_delay_seconds=initial_delay_seconds,
                                period_seconds=period_seconds,
                                timeout_seconds=timeout_seconds,
                                success_threshold=success_threshold,
                                failure_threshold=failure_threshold
                            ),
                            readiness_probe=client.V1Probe(
                                http_get=client.V1HTTPGetAction(
                                    path=readiness_path,
                                    port=container_port
                                ),
                                initial_delay_seconds=initial_delay_seconds,
                                period_seconds=period_seconds,
                                timeout_seconds=timeout_seconds,
                                success_threshold=success_threshold,
                                failure_threshold=failure_threshold
                            )
                        )
                    ]
                )
            )
        )
    )

    try:
        api.create_namespaced_deployment(namespace=namespace, body=deployment)
        return f"Deployment {deployment_name} created successfully with health checks"
    except ApiException as e:
        raise Exception(f"Failed to create deployment: {str(e)}")

@mcp.tool()
def update_deployment(
    namespace: str,
    deployment_name: str,
    image: str = None,
    replicas: int = None,
    env_vars: Dict[str, str] = None
) -> str:
    """Update an existing deployment"""
    api = get_k8s_client()['apps']
    try:
        current_deployment = api.read_namespaced_deployment(deployment_name, namespace)
        
        if image:
            current_deployment.spec.template.spec.containers[0].image = image
        if replicas is not None:
            current_deployment.spec.replicas = replicas
        if env_vars:
            current_deployment.spec.template.spec.containers[0].env = [
                client.V1EnvVar(name=k, value=v)
                for k, v in env_vars.items()
            ]

        api.patch_namespaced_deployment(
            name=deployment_name,
            namespace=namespace,
            body=current_deployment
        )
        return f"Deployment {deployment_name} updated successfully"
    except ApiException as e:
        raise Exception(f"Failed to update deployment: {str(e)}")

@mcp.tool()
def delete_deployment(namespace: str, deployment_name: str) -> str:
    """Delete a deployment"""
    api = get_k8s_client()['apps']
    try:
        api.delete_namespaced_deployment(
            name=deployment_name,
            namespace=namespace,
            body=client.V1DeleteOptions(
                propagation_policy='Foreground'
            )
        )
        return f"Deployment {deployment_name} deleted successfully"
    except ApiException as e:
        raise Exception(f"Failed to delete deployment: {str(e)}")

@mcp.tool()
def scale_deployment(namespace: str, deployment_name: str, replicas: int) -> str:
    """Scale a deployment to a specific number of replicas"""
    api = get_k8s_client()['apps']
    try:
        api.patch_namespaced_deployment_scale(
            name=deployment_name,
            namespace=namespace,
            body={"spec": {"replicas": replicas}}
        )
        return f"Deployment {deployment_name} scaled to {replicas} replicas"
    except ApiException as e:
        raise Exception(f"Failed to scale deployment: {str(e)}")

@mcp.tool()
def get_deployment_rollout_status(namespace: str, deployment_name: str) -> Dict[str, Any]:
    """Get the rollout status of a deployment"""
    api = get_k8s_client()['apps']
    try:
        deployment = api.read_namespaced_deployment(deployment_name, namespace)
        return {
            "name": deployment.metadata.name,
            "available_replicas": deployment.status.available_replicas,
            "ready_replicas": deployment.status.ready_replicas,
            "updated_replicas": deployment.status.updated_replicas,
            "conditions": [
                {
                    "type": condition.type,
                    "status": condition.status,
                    "reason": condition.reason,
                    "message": condition.message
                }
                for condition in deployment.status.conditions
            ]
        }
    except ApiException as e:
        raise Exception(f"Failed to get deployment rollout status: {str(e)}")

@mcp.tool()
def rollback_deployment(namespace: str, deployment_name: str, revision: int) -> str:
    """Rollback a deployment to a specific revision"""
    api = get_k8s_client()['apps']
    try:
        api.create_namespaced_deployment_rollback(
            name=deployment_name,
            namespace=namespace,
            body={
                "rollbackTo": {
                    "revision": revision
                }
            }
        )
        return f"Deployment {deployment_name} rolled back to revision {revision}"
    except ApiException as e:
        raise Exception(f"Failed to rollback deployment: {str(e)}")

@mcp.tool()
def get_deployment_history(namespace: str, deployment_name: str) -> List[Dict[str, Any]]:
    """Get the revision history of a deployment"""
    api = get_k8s_client()['apps']
    try:
        history = api.get_namespaced_deployment_revision_history(
            name=deployment_name,
            namespace=namespace
        )
        return [
            {
                "revision": revision.revision,
                "image": revision.spec.template.spec.containers[0].image,
                "replicas": revision.spec.replicas,
                "creation_timestamp": revision.metadata.creation_timestamp
            }
            for revision in history.items
        ]
    except ApiException as e:
        raise Exception(f"Failed to get deployment history: {str(e)}")

@mcp.tool()
def pause_deployment(namespace: str, deployment_name: str) -> str:
    """Pause a deployment"""
    api = get_k8s_client()['apps']
    try:
        api.patch_namespaced_deployment(
            name=deployment_name,
            namespace=namespace,
            body={"spec": {"paused": True}}
        )
        return f"Deployment {deployment_name} paused successfully"
    except ApiException as e:
        raise Exception(f"Failed to pause deployment: {str(e)}")

@mcp.tool()
def resume_deployment(namespace: str, deployment_name: str) -> str:
    """Resume a paused deployment"""
    api = get_k8s_client()['apps']
    try:
        api.patch_namespaced_deployment(
            name=deployment_name,
            namespace=namespace,
            body={"spec": {"paused": False}}
        )
        return f"Deployment {deployment_name} resumed successfully"
    except ApiException as e:
        raise Exception(f"Failed to resume deployment: {str(e)}")

@mcp.tool()
def get_deployment_events(namespace: str, deployment_name: str) -> List[Dict[str, Any]]:
    """Get events related to a deployment"""
    api = get_k8s_client()
    try:
        events = api['core'].list_namespaced_event(
            namespace=namespace,
            field_selector=f"involvedObject.name={deployment_name},involvedObject.kind=Deployment"
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
        raise Exception(f"Failed to get deployment events: {str(e)}") 