from functools import lru_cache

from kubernetes import client as k8s
from kubernetes import config as k8s_config
from langchain_core.tools import BaseTool, tool

from app.utils.config import get_settings


@lru_cache(maxsize=1)
def _load_config() -> None:
    settings = get_settings()
    if settings.kubeconfig_path:
        k8s_config.load_kube_config(config_file=settings.kubeconfig_path)
        return
    try:
        k8s_config.load_incluster_config()
    except k8s_config.ConfigException:
        k8s_config.load_kube_config()


@lru_cache(maxsize=1)
def _core() -> k8s.CoreV1Api:
    _load_config()
    return k8s.CoreV1Api()


@lru_cache(maxsize=1)
def _apps() -> k8s.AppsV1Api:
    _load_config()
    return k8s.AppsV1Api()


@tool
def k8s_list_pods(namespace: str = "default") -> list[dict]:
    """List pods in a namespace with phase, readiness, and restart counts."""
    return [
        {
            "name": p.metadata.name,
            "phase": p.status.phase,
            "ready": all(cs.ready for cs in (p.status.container_statuses or [])),
            "restarts": sum(cs.restart_count for cs in (p.status.container_statuses or [])),
            "start_time": str(p.status.start_time),
        }
        for p in _core().list_namespaced_pod(namespace).items
    ]


@tool
def k8s_pod_logs(name: str, namespace: str = "default", tail_lines: int = 100) -> str:
    """Fetch the last `tail_lines` log lines from a pod."""
    return _core().read_namespaced_pod_log(
        name=name, namespace=namespace, tail_lines=tail_lines
    )


@tool
def k8s_list_deployments(namespace: str = "default") -> list[dict]:
    """List deployments in a namespace with replica counts."""
    return [
        {
            "name": d.metadata.name,
            "replicas": d.status.replicas,
            "ready_replicas": d.status.ready_replicas,
            "available_replicas": d.status.available_replicas,
            "updated_replicas": d.status.updated_replicas,
        }
        for d in _apps().list_namespaced_deployment(namespace).items
    ]


@tool
def k8s_deployment_status(name: str, namespace: str = "default") -> dict:
    """Return detailed status and conditions for a Kubernetes deployment."""
    d = _apps().read_namespaced_deployment_status(name=name, namespace=namespace)
    return {
        "name": d.metadata.name,
        "generation": d.metadata.generation,
        "observed_generation": d.status.observed_generation,
        "replicas": d.status.replicas,
        "ready_replicas": d.status.ready_replicas,
        "conditions": [
            {
                "type": c.type,
                "status": c.status,
                "reason": c.reason,
                "message": c.message,
            }
            for c in (d.status.conditions or [])
        ],
    }


def get_kubernetes_tools() -> list[BaseTool]:
    try:
        _load_config()
        _core().get_api_resources()
    except Exception:
        return []
    return [k8s_list_pods, k8s_pod_logs, k8s_list_deployments, k8s_deployment_status]
