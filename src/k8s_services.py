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
        'core': client.CoreV1Api()
    }

@mcp.tool()
def get_services(namespace: str = "default") -> List[Dict[str, Any]]:
    """Get all services in a namespace"""
    api = get_k8s_client()['core']
    try:
        services = api.list_namespaced_service(namespace)
        return [
            {
                "name": service.metadata.name,
                "namespace": service.metadata.namespace,
                "type": service.spec.type,
                "cluster_ip": service.spec.cluster_ip,
                "external_ip": service.spec.external_i_ps,
                "ports": [
                    {
                        "name": port.name,
                        "port": port.port,
                        "target_port": port.target_port,
                        "protocol": port.protocol
                    }
                    for port in service.spec.ports
                ],
                "selector": service.spec.selector,
                "creation_timestamp": service.metadata.creation_timestamp
            }
            for service in services.items
        ]
    except ApiException as e:
        raise Exception(f"Failed to get services: {str(e)}")

@mcp.tool()
def get_service_details(namespace: str, service_name: str) -> Dict[str, Any]:
    """Get detailed information about a specific service"""
    api = get_k8s_client()['core']
    try:
        service = api.read_namespaced_service(service_name, namespace)
        return {
            "name": service.metadata.name,
            "namespace": service.metadata.namespace,
            "type": service.spec.type,
            "cluster_ip": service.spec.cluster_ip,
            "external_ip": service.spec.external_i_ps,
            "ports": [
                {
                    "name": port.name,
                    "port": port.port,
                    "target_port": port.target_port,
                    "protocol": port.protocol
                }
                for port in service.spec.ports
            ],
            "selector": service.spec.selector,
            "creation_timestamp": service.metadata.creation_timestamp,
            "labels": service.metadata.labels,
            "annotations": service.metadata.annotations
        }
    except ApiException as e:
        raise Exception(f"Failed to get service details: {str(e)}")

@mcp.tool()
def create_service(
    namespace: str,
    service_name: str,
    selector: Dict[str, str],
    port: int = 80,
    target_port: int = 80,
    service_type: str = "ClusterIP"
) -> str:
    """Create a new service"""
    api = get_k8s_client()['core']
    
    service = client.V1Service(
        metadata=client.V1ObjectMeta(name=service_name),
        spec=client.V1ServiceSpec(
            selector=selector,
            ports=[client.V1ServicePort(port=port, target_port=target_port)],
            type=service_type
        )
    )

    try:
        api.create_namespaced_service(namespace=namespace, body=service)
        return f"Service {service_name} created successfully"
    except ApiException as e:
        raise Exception(f"Failed to create service: {str(e)}")

@mcp.tool()
def update_service(
    namespace: str,
    service_name: str,
    selector: Optional[Dict[str, str]] = None,
    ports: Optional[List[Dict[str, Any]]] = None,
    service_type: Optional[str] = None,
    external_ips: Optional[List[str]] = None,
    labels: Optional[Dict[str, str]] = None,
    annotations: Optional[Dict[str, str]] = None
) -> str:
    """Update an existing service"""
    api = get_k8s_client()['core']
    try:
        # Get existing service
        service = api.read_namespaced_service(service_name, namespace)
        
        # Update fields if provided
        if selector:
            service.spec.selector = selector
        if ports:
            service.spec.ports = [
                client.V1ServicePort(
                    name=port.get("name"),
                    port=port["port"],
                    target_port=port.get("target_port"),
                    protocol=port.get("protocol", "TCP")
                )
                for port in ports
            ]
        if service_type:
            service.spec.type = service_type
        if external_ips:
            service.spec.external_i_ps = external_ips
        if labels:
            service.metadata.labels = labels
        if annotations:
            service.metadata.annotations = annotations

        api.replace_namespaced_service(
            name=service_name,
            namespace=namespace,
            body=service
        )
        return f"Service {service_name} updated successfully"
    except ApiException as e:
        raise Exception(f"Failed to update service: {str(e)}")

@mcp.tool()
def delete_service(namespace: str, service_name: str) -> str:
    """Delete a service"""
    api = get_k8s_client()['core']
    try:
        api.delete_namespaced_service(
            name=service_name,
            namespace=namespace
        )
        return f"Service {service_name} deleted successfully"
    except ApiException as e:
        raise Exception(f"Failed to delete service: {str(e)}")

@mcp.tool()
def get_service_endpoints(namespace: str, service_name: str) -> Dict[str, Any]:
    """Get endpoints for a service"""
    api = get_k8s_client()['core']
    try:
        endpoints = api.read_namespaced_endpoints(service_name, namespace)
        return {
            "service_name": endpoints.metadata.name,
            "namespace": endpoints.metadata.namespace,
            "subsets": [
                {
                    "addresses": [
                        {
                            "ip": address.ip,
                            "hostname": address.hostname,
                            "node_name": address.node_name
                        }
                        for address in subset.addresses
                    ],
                    "ports": [
                        {
                            "name": port.name,
                            "port": port.port,
                            "protocol": port.protocol
                        }
                        for port in subset.ports
                    ]
                }
                for subset in endpoints.subsets
            ]
        }
    except ApiException as e:
        raise Exception(f"Failed to get service endpoints: {str(e)}")

@mcp.tool()
def get_service_events(namespace: str, service_name: str) -> List[Dict[str, Any]]:
    """Get events related to a service"""
    api = get_k8s_client()['core']
    try:
        events = api.list_namespaced_event(
            namespace=namespace,
            field_selector=f"involvedObject.name={service_name},involvedObject.kind=Service"
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
        raise Exception(f"Failed to get service events: {str(e)}")

@mcp.tool()
def patch_service(
    namespace: str,
    service_name: str,
    patch_data: Dict[str, Any]
) -> str:
    """Patch a service with specific changes"""
    api = get_k8s_client()['core']
    try:
        api.patch_namespaced_service(
            name=service_name,
            namespace=namespace,
            body=patch_data
        )
        return f"Service {service_name} patched successfully"
    except ApiException as e:
        raise Exception(f"Failed to patch service: {str(e)}")

@mcp.tool()
def get_service_accounts(namespace: str = "default") -> List[Dict[str, Any]]:
    """Get all service accounts in a namespace"""
    api = get_k8s_client()['core']
    try:
        service_accounts = api.list_namespaced_service_account(namespace)
        return [
            {
                "name": sa.metadata.name,
                "namespace": sa.metadata.namespace,
                "secrets": [secret.name for secret in sa.secrets] if sa.secrets else [],
                "image_pull_secrets": [secret.name for secret in sa.image_pull_secrets] if sa.image_pull_secrets else [],
                "creation_timestamp": sa.metadata.creation_timestamp,
                "labels": sa.metadata.labels,
                "annotations": sa.metadata.annotations
            }
            for sa in service_accounts.items
        ]
    except ApiException as e:
        raise Exception(f"Failed to get service accounts: {str(e)}")

@mcp.tool()
def create_service_account(
    namespace: str,
    service_account_name: str,
    labels: Optional[Dict[str, str]] = None,
    annotations: Optional[Dict[str, str]] = None,
    secrets: Optional[List[str]] = None,
    image_pull_secrets: Optional[List[str]] = None
) -> str:
    """Create a new service account"""
    api = get_k8s_client()['core']
    
    service_account = client.V1ServiceAccount(
        metadata=client.V1ObjectMeta(
            name=service_account_name,
            namespace=namespace,
            labels=labels,
            annotations=annotations
        ),
        secrets=[client.V1ObjectReference(name=secret) for secret in secrets] if secrets else None,
        image_pull_secrets=[client.V1LocalObjectReference(name=secret) for secret in image_pull_secrets] if image_pull_secrets else None
    )

    try:
        api.create_namespaced_service_account(namespace=namespace, body=service_account)
        return f"Service account {service_account_name} created successfully"
    except ApiException as e:
        raise Exception(f"Failed to create service account: {str(e)}")

@mcp.tool()
def get_service_health(
    namespace: str,
    service_name: str,
    port: Optional[int] = None,
    path: str = "/health",
    timeout: int = 5
) -> Dict[str, Any]:
    """Check the health of a service by making HTTP requests to its endpoints"""
    api = get_k8s_client()['core']
    try:
        # Get service endpoints
        endpoints = api.read_namespaced_endpoints(service_name, namespace)
        
        if not endpoints.subsets:
            return {
                "status": "unhealthy",
                "reason": "No endpoints available",
                "details": []
            }

        health_results = []
        for subset in endpoints.subsets:
            for address in subset.addresses:
                for port_info in subset.ports:
                    if port and port_info.port != port:
                        continue
                    
                    try:
                        import requests
                        from requests.exceptions import RequestException
                        
                        url = f"http://{address.ip}:{port_info.port}{path}"
                        response = requests.get(url, timeout=timeout)
                        
                        health_results.append({
                            "endpoint": f"{address.ip}:{port_info.port}",
                            "status": "healthy" if response.status_code == 200 else "unhealthy",
                            "status_code": response.status_code,
                            "response_time": response.elapsed.total_seconds()
                        })
                    except RequestException as e:
                        health_results.append({
                            "endpoint": f"{address.ip}:{port_info.port}",
                            "status": "unhealthy",
                            "error": str(e)
                        })

        return {
            "status": "healthy" if all(r["status"] == "healthy" for r in health_results) else "unhealthy",
            "details": health_results
        }
    except ApiException as e:
        raise Exception(f"Failed to check service health: {str(e)}")

@mcp.tool()
def get_service_metrics(
    namespace: str,
    service_name: str,
    duration: str = "5m"
) -> Dict[str, Any]:
    """Get metrics for a service (requires Prometheus)"""
    api = get_k8s_client()['core']
    try:
        # Get service details
        service = api.read_namespaced_service(service_name, namespace)
        
        # Get endpoints
        endpoints = api.read_namespaced_endpoints(service_name, namespace)
        
        metrics = {
            "service_name": service_name,
            "namespace": namespace,
            "type": service.spec.type,
            "endpoints": len(endpoints.subsets[0].addresses) if endpoints.subsets else 0,
            "ports": [
                {
                    "name": port.name,
                    "port": port.port,
                    "protocol": port.protocol
                }
                for port in service.spec.ports
            ],
            "selector": service.spec.selector
        }
        
        # Note: To get actual metrics, you would need to query Prometheus
        # This is a placeholder for the metrics structure
        metrics["prometheus_metrics"] = {
            "request_rate": "N/A",
            "error_rate": "N/A",
            "latency": "N/A",
            "duration": duration
        }
        
        return metrics
    except ApiException as e:
        raise Exception(f"Failed to get service metrics: {str(e)}")

@mcp.tool()
def get_service_dependencies(
    namespace: str,
    service_name: str
) -> Dict[str, Any]:
    """Get service dependencies and relationships"""
    api = get_k8s_client()['core']
    try:
        # Get service details
        service = api.read_namespaced_service(service_name, namespace)
        
        # Get all services in the namespace
        all_services = api.list_namespaced_service(namespace)
        
        dependencies = {
            "service_name": service_name,
            "namespace": namespace,
            "dependencies": [],
            "dependents": []
        }
        
        # Check for dependencies based on selectors
        for other_service in all_services.items:
            if other_service.metadata.name != service_name:
                # Check if this service depends on other_service
                if service.spec.selector and all(
                    other_service.metadata.labels.get(k) == v
                    for k, v in service.spec.selector.items()
                ):
                    dependencies["dependencies"].append({
                        "name": other_service.metadata.name,
                        "type": other_service.spec.type,
                        "ports": [
                            {
                                "name": port.name,
                                "port": port.port,
                                "protocol": port.protocol
                            }
                            for port in other_service.spec.ports
                        ]
                    })
                
                # Check if other_service depends on this service
                if other_service.spec.selector and all(
                    service.metadata.labels.get(k) == v
                    for k, v in other_service.spec.selector.items()
                ):
                    dependencies["dependents"].append({
                        "name": other_service.metadata.name,
                        "type": other_service.spec.type,
                        "ports": [
                            {
                                "name": port.name,
                                "port": port.port,
                                "protocol": port.protocol
                            }
                            for port in other_service.spec.ports
                        ]
                    })
        
        return dependencies
    except ApiException as e:
        raise Exception(f"Failed to get service dependencies: {str(e)}")

@mcp.tool()
def get_service_network_policy(
    namespace: str,
    service_name: str
) -> Dict[str, Any]:
    """Get network policies affecting a service"""
    api = get_k8s_client()['core']
    try:
        # Get service details
        service = api.read_namespaced_service(service_name, namespace)
        
        # Get all network policies in the namespace
        networking_api = client.NetworkingV1Api()
        network_policies = networking_api.list_namespaced_network_policy(namespace)
        
        affecting_policies = []
        for policy in network_policies.items:
            # Check if policy affects this service
            if policy.spec.pod_selector and all(
                service.metadata.labels.get(k) == v
                for k, v in policy.spec.pod_selector.match_labels.items()
            ):
                affecting_policies.append({
                    "name": policy.metadata.name,
                    "ingress_rules": [
                        {
                            "from": [
                                {
                                    "pod_selector": rule.from_[0].pod_selector.match_labels if rule.from_[0].pod_selector else None,
                                    "namespace_selector": rule.from_[0].namespace_selector.match_labels if rule.from_[0].namespace_selector else None
                                }
                                for rule in policy.spec.ingress
                            ],
                            "ports": [
                                {
                                    "protocol": port.protocol,
                                    "port": port.port
                                }
                                for port in policy.spec.ingress[0].ports
                            ] if policy.spec.ingress and policy.spec.ingress[0].ports else []
                        }
                    ] if policy.spec.ingress else [],
                    "egress_rules": [
                        {
                            "to": [
                                {
                                    "pod_selector": rule.to[0].pod_selector.match_labels if rule.to[0].pod_selector else None,
                                    "namespace_selector": rule.to[0].namespace_selector.match_labels if rule.to[0].namespace_selector else None
                                }
                                for rule in policy.spec.egress
                            ],
                            "ports": [
                                {
                                    "protocol": port.protocol,
                                    "port": port.port
                                }
                                for port in policy.spec.egress[0].ports
                            ] if policy.spec.egress and policy.spec.egress[0].ports else []
                        }
                    ] if policy.spec.egress else []
                })
        
        return {
            "service_name": service_name,
            "namespace": namespace,
            "network_policies": affecting_policies
        }
    except ApiException as e:
        raise Exception(f"Failed to get service network policy: {str(e)}") 