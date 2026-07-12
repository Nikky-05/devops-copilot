from functools import lru_cache

import docker
from langchain_core.tools import BaseTool, tool


@lru_cache(maxsize=1)
def _client() -> docker.DockerClient:
    return docker.from_env()


@tool
def docker_list_containers(all_containers: bool = False) -> list[dict]:
    """List Docker containers. Set `all_containers=True` to include stopped ones."""
    return [
        {
            "id": c.short_id,
            "name": c.name,
            "image": c.image.tags[0] if c.image.tags else c.image.id,
            "status": c.status,
        }
        for c in _client().containers.list(all=all_containers)
    ]


@tool
def docker_container_logs(name_or_id: str, tail: int = 100) -> str:
    """Fetch the last `tail` log lines from a Docker container."""
    logs = _client().containers.get(name_or_id).logs(tail=tail)
    return logs.decode("utf-8", errors="replace")


@tool
def docker_container_inspect(name_or_id: str) -> dict:
    """Return raw inspect data (config, state, network) for a Docker container."""
    return _client().containers.get(name_or_id).attrs


def get_docker_tools() -> list[BaseTool]:
    try:
        _client().ping()
    except Exception:
        return []
    return [docker_list_containers, docker_container_logs, docker_container_inspect]
