from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents.devops_agent import available_tool_names, run_agent
from app.services.deployment_service import analyze_deployment
from app.services.incident_service import analyze_incident

router = APIRouter()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User message.")
    history: list[dict] | None = Field(
        default=None,
        description="Prior conversation turns as a list of {role, content} dicts.",
    )


class ChatResponse(BaseModel):
    reply: str


class DeploymentAnalyzeRequest(BaseModel):
    repo: str = Field(..., description="GitHub repository in 'owner/repo' format.")
    question: str | None = Field(
        default=None,
        description="Optional focused question about the deployment.",
    )


class IncidentAnalyzeRequest(BaseModel):
    description: str = Field(..., min_length=1, description="Incident description or symptom.")
    namespace: str = Field(default="default", description="Kubernetes namespace to inspect.")


class ToolsResponse(BaseModel):
    tools: list[str]


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    try:
        result = run_agent(req.message, history=req.history)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return ChatResponse(reply=result["reply"])


@router.post("/deployments/analyze", response_model=ChatResponse)
def deployments_analyze(req: DeploymentAnalyzeRequest) -> ChatResponse:
    try:
        reply = analyze_deployment(req.repo, req.question)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return ChatResponse(reply=reply)


@router.post("/incidents/analyze", response_model=ChatResponse)
def incidents_analyze(req: IncidentAnalyzeRequest) -> ChatResponse:
    try:
        reply = analyze_incident(req.description, req.namespace)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return ChatResponse(reply=reply)


@router.get("/tools", response_model=ToolsResponse)
def list_tools() -> ToolsResponse:
    return ToolsResponse(tools=available_tool_names())
