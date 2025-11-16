CATEGORIES = ["detection", "containment", "eradication", "recovery", "reporting"]

def score_response(scenario, actions):
    text = " ".join(a.lower() for a in actions)
    rubric = scenario.get("rubric", {})
    total_possible = sum(rubric.get(c, 0) for c in CATEGORIES) or 100

    cat_scores = {c: 0.0 for c in CATEGORIES}

    if any(w in text for w in ["identify", "ioc", "host-", "ip ", "domain", "ransom", "sql", "phish", "ssh", "cloudtrail"]):
        cat_scores["detection"] = 0.8
    if any(w in text for w in ["isolate", "contain", "segregate", "quarantine", "disable account", "lock account", "block ip", "block domain"]):
        cat_scores["containment"] = 0.8
    if any(w in text for w in ["kill process", "terminate", "remove malware", "wipe", "reimage", "remove access key", "remove policy"]):
        cat_scores["eradication"] = 0.7
    if any(w in text for w in ["restore", "backup", "recover", "bring back online", "resume service"]):
        cat_scores["recovery"] = 0.6
    if any(w in text for w in ["report", "executive summary", "ioc list", "lessons learned", "post-incident", "summary"]):
        cat_scores["reporting"] = 0.7

    final_score = 0
    breakdown = {}
    for cat in CATEGORIES:
        weight = rubric.get(cat, 0)
        value = cat_scores[cat] * weight
        breakdown[cat] = int(value)
        final_score += int(value)

    if total_possible != 100:
        final_score = int(final_score * (100.0 / max(total_possible, 1)))

    feedback_parts = []
    if breakdown.get("detection", 0) == 0:
        feedback_parts.append("Add more focus on identifying IOCs, hosts, and accounts involved.")
    if breakdown.get("containment", 0) == 0:
        feedback_parts.append("Include explicit containment steps: isolate hosts, block IPs/domains, disable accounts.")
    if breakdown.get("eradication", 0) == 0:
        feedback_parts.append("Describe how you would remove malware or attacker access.")
    if breakdown.get("recovery", 0) == 0:
        feedback_parts.append("Mention how services and data would be safely restored.")
    if breakdown.get("reporting", 0) == 0:
        feedback_parts.append("Add an executive-style summary and include key IOCs.")

    if not feedback_parts:
        feedback_parts.append("Strong plan across detection, containment, eradication, recovery, and reporting.")
    return final_score, breakdown, feedback_parts
