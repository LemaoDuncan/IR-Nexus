from dateutil import parser

def build_timeline(scenario, logs, packets):
    events = []
    for l in logs:
        try:
            parser.isoparse(l.get("time"))
            events.append({
                "time": l["time"],
                "type": "log",
                "summary": f"{l.get('source')} - {l.get('event')}: {l.get('message')}"
            })
        except Exception:
            continue
    for p in packets:
        try:
            parser.isoparse(p.get("time"))
            events.append({
                "time": p["time"],
                "type": "packet",
                "summary": f"{p.get('proto')} {p.get('src_ip')} -> {p.get('dst_ip')}"
            })
        except Exception:
            continue
    events.sort(key=lambda e: e["time"])
    return events
