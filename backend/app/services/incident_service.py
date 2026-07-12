from app.agents.devops_agent import run_agent


def analyze_incident(description: str, namespace: str = "default") -> str:
    prompt = (
        f"Incident description: {description}\n\n"
        "Work through this incident:\n"
        "1. Call retrieve_docs to search runbooks and incident reports for related procedures. Cite sources.\n"
        f"2. If Kubernetes is configured, check pod status and recent logs in the `{namespace}` namespace.\n"
        "3. If GitHub is configured, check whether any recent deployment might be related.\n\n"
        "Give a concise diagnosis and concrete next steps. Do NOT execute any mutating actions — "
        "describe the commands the operator should run themselves."
    )
    return run_agent(prompt)["reply"]
