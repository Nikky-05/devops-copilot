from app.agents.devops_agent import run_agent


def analyze_deployment(repo: str, question: str | None = None) -> str:
    focus = question or (
        "Summarize the current deployment state: recent Actions workflow runs, "
        "open pull requests, and any red flags. Suggest next steps if anything looks off."
    )
    prompt = (
        f"Repository: {repo}\n"
        f"Task: {focus}\n\n"
        "Use the GitHub tools to inspect the actual live state. "
        "Cite specific PRs, workflow runs, or commits in your findings."
    )
    return run_agent(prompt)["reply"]
