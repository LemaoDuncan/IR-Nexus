from datetime import datetime

def build_report(scenario, logs, packets, score, breakdown, feedback, artifacts=None):
    if artifacts is None:
        artifacts = {}
    title = f"IR Nexus - Incident Report: {scenario.get('name')}"
    category = scenario.get("category", "unknown")
    brief = scenario.get("brief", "")
    return {
        "title": title,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "scenario": {
            "id": scenario.get("id"),
            "name": scenario.get("name"),
            "description": scenario.get("description"),
            "category": category,
            "difficulty": scenario.get("difficulty"),
            "brief": brief
        },
        "executive_summary": (
            f"This training exercise simulated a {category} incident ({scenario.get('name')}). "
            f"The analyst achieved a score of {score}/100."
        ),
        "score_breakdown": breakdown,
        "feedback": feedback,
        "log_samples": logs[:20],
        "packet_samples": packets[:20],
        "forensic_artifacts": artifacts
    }
