# IR Nexus v3 — Elite Realistic Edition (High-Volume Logs)

This build of IR Nexus adds high-volume, noisy logs and packets to make investigations feel more like a real SOC.

- ~200–350 logs for medium difficulty, 400–600 for hard
- High background noise across Windows, Linux, Web, Cloud
- Scenario-specific attack chains embedded in the noise
- Timeline, forensics, scoring, and reporting included

## Run

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8080
```

Then open http://localhost:8080
