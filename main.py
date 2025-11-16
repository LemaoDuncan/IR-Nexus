from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import json, uvicorn, os

import scenarios, loggen, packetgen, timeline, scoring, forensics, reportgen

app = FastAPI(title="IR Nexus v3 - Elite Realistic")
app.mount("/static", StaticFiles(directory="static"), name="static")

PROGRESS_FILE = "progress.json"

def load_progress():
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_progress(data):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

@app.get("/", response_class=HTMLResponse)
async def home():
    return FileResponse("static/index.html")

@app.get("/api/scenarios")
async def api_scenarios():
    return JSONResponse(scenarios.list_scenarios())

@app.post("/api/generate")
async def api_generate(req: Request):
    body = await req.json()
    scen_id = body.get("scenario")
    difficulty = body.get("difficulty", "medium")
    scen = scenarios.generate_scenario(scen_id, difficulty=difficulty)
    logs = loggen.generate_logs(scen)
    packets = packetgen.generate_packets(scen)
    tl = timeline.build_timeline(scen, logs, packets)
    return JSONResponse({"scenario": scen, "logs": logs, "packets": packets, "timeline": tl})

@app.post("/api/submit")
async def api_submit(req: Request):
    body = await req.json()
    scen = body.get("scenario", {})
    actions = body.get("actions", [])
    user = body.get("user", "default")

    score, breakdown, feedback = scoring.score_response(scen, actions)

    prog = load_progress()
    rec = prog.get(user, {"attempts": 0, "best_score": 0})
    rec["attempts"] = rec.get("attempts", 0) + 1
    rec["last_score"] = score
    rec["best_score"] = max(rec.get("best_score", 0), score)
    prog[user] = rec
    save_progress(prog)

    return JSONResponse({"score": score, "breakdown": breakdown, "feedback": feedback})

@app.get("/api/progress")
async def api_progress(user: str = "default"):
    prog = load_progress()
    return JSONResponse({"progress": prog.get(user, {})})

@app.post("/api/forensics")
async def api_forensics(req: Request):
    body = await req.json()
    scen = body.get("scenario", {})
    arts = forensics.get_artifacts_for_scenario(scen)
    return JSONResponse({"artifacts": arts})

@app.post("/api/report")
async def api_report(req: Request):
    body = await req.json()
    scen = body.get("scenario", {})
    logs = body.get("logs", [])
    packets = body.get("packets", [])
    score = body.get("score", 0)
    breakdown = body.get("breakdown", {})
    feedback = body.get("feedback", [])
    artifacts = body.get("artifacts", {})
    rep = reportgen.build_report(scen, logs, packets, score, breakdown, feedback, artifacts)
    return JSONResponse({"report": rep})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=8080)
