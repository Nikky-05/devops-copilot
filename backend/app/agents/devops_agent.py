from functools import lru_cache
from typing import Any

from langchain_core.tools import BaseTool, tool
from langgraph.prebuilt import create_react_agent

from app.agents.prompts import DEVOPS_SYSTEM_PROMPT
from app.mcp.docker_client import get_docker_tools
from app.mcp.filesystem_client import get_filesystem_tools
from app.mcp.github_client import get_github_tools
from app.mcp.kubernetes_client import get_kubernetes_tools
from app.mcp.postgres_client import get_postgres_tools
from app.models.llm import get_chat_llm
from app.rag.retriever import retrieve


@tool
def retrieve_docs(query: str, k: int = 4) -> list[dict]:
    """Search runbooks, deployment docs, incident reports, and architecture docs for passages relevant to the query."""
    return [
        {
            "content": d.page_content,
            "source": d.metadata.get("source"),
            "category": d.metadata.get("category"),
        }
        for d in retrieve(query, k=k)
    ]


def _collect_tools() -> list[BaseTool]:
    tools: list[BaseTool] = [retrieve_docs]
    tools.extend(get_github_tools())
    tools.extend(get_filesystem_tools())
    tools.extend(get_postgres_tools())
    tools.extend(get_docker_tools())
    tools.extend(get_kubernetes_tools())
    return tools


@lru_cache(maxsize=1)
def get_devops_agent():
    return create_react_agent(
        model=get_chat_llm(),
        tools=_collect_tools(),
        prompt=DEVOPS_SYSTEM_PROMPT,
    )


def available_tool_names() -> list[str]:
    return [t.name for t in _collect_tools()]


def run_agent(user_message: str, history: list[dict] | None = None) -> dict[str, Any]:
    agent = get_devops_agent()
    messages = list(history or []) + [{"role": "user", "content": user_message}]
    result = agent.invoke({"messages": messages})
    final = result["messages"][-1]
    return {
        "reply": final.content,
        "messages": result["messages"],
    }
