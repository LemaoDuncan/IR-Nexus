let currentScenario = null;
let currentLogs = [];
let currentPackets = [];
let currentTimeline = [];
let currentArtifacts = null;
let lastScoreData = null;

async function loadScenarios() {
  const res = await fetch("/api/scenarios");
  const data = await res.json();
  const sel = document.getElementById("scenario");
  sel.innerHTML = "";
  data.forEach(s => {
    const opt = document.createElement("option");
    opt.value = s.id;
    opt.textContent = `${s.name} — ${s.description}`;
    sel.appendChild(opt);
  });
}

document.getElementById("btnGenerate").addEventListener("click", async () => {
  const scenario = document.getElementById("scenario").value;
  const difficulty = document.getElementById("difficulty").value;
  const res = await fetch("/api/generate", {
    method: "POST",
    headers: {"content-type": "application/json"},
    body: JSON.stringify({scenario, difficulty})
  });
  const data = await res.json();
  currentScenario = data.scenario;
  currentLogs = data.logs;
  currentPackets = data.packets;
  currentTimeline = data.timeline;
  currentArtifacts = null;
  lastScoreData = null;

  const brief = currentScenario.brief || "";
  const pb = currentScenario.playbook || {};
  document.getElementById("scenarioBrief").textContent = brief;
  document.getElementById("scenarioPlaybook").textContent = JSON.stringify(pb, null, 2);
  document.getElementById("logs").textContent = JSON.stringify(currentLogs.slice(0, 120), null, 2);
  document.getElementById("packets").textContent = JSON.stringify(currentPackets.slice(0, 80), null, 2);
  document.getElementById("timeline").textContent = JSON.stringify(currentTimeline.slice(0, 80), null, 2);
  document.getElementById("forensics").textContent = "";
  document.getElementById("feedback").textContent = "";
  document.getElementById("report").textContent = "";
});

document.getElementById("searchBtn").addEventListener("click", () => {
  if (!currentLogs.length) return;
  const q = document.getElementById("searchQ").value;
  const useRegex = document.getElementById("useRegex").checked;
  if (!q) {
    document.getElementById("logs").textContent = JSON.stringify(currentLogs.slice(0, 120), null, 2);
    return;
  }
  let results = [];
  if (useRegex) {
    try {
      const re = new RegExp(q, "i");
      results = currentLogs.filter(l => re.test(JSON.stringify(l)));
    } catch (e) {
      alert("Invalid regex: " + e.message);
      return;
    }
  } else {
    const ql = q.toLowerCase();
    results = currentLogs.filter(l => JSON.stringify(l).toLowerCase().includes(ql));
  }
  document.getElementById("logs").textContent = JSON.stringify(results.slice(0, 120), null, 2);
});

document.getElementById("forensicsBtn").addEventListener("click", async () => {
  if (!currentScenario) { alert("Generate a scenario first."); return; }
  const res = await fetch("/api/forensics", {
    method: "POST",
    headers: {"content-type": "application/json"},
    body: JSON.stringify({scenario: currentScenario})
  });
  const data = await res.json();
  currentArtifacts = data.artifacts;
  document.getElementById("forensics").textContent = JSON.stringify(currentArtifacts, null, 2);
});

document.getElementById("submitBtn").addEventListener("click", async () => {
  if (!currentScenario) { alert("Generate a scenario first."); return; }
  const actionsText = document.getElementById("actions").value || "";
  const userId = document.getElementById("userId").value || "default";
  const actions = actionsText.split(/\n|,/).map(s => s.trim()).filter(Boolean);
  const res = await fetch("/api/submit", {
    method: "POST",
    headers: {"content-type": "application/json"},
    body: JSON.stringify({scenario: currentScenario, actions, user: userId})
  });
  const data = await res.json();
  lastScoreData = data;
  document.getElementById("feedback").textContent =
    "Score: " + data.score + "\nBreakdown: " + JSON.stringify(data.breakdown, null, 2) +
    "\n\nFeedback:\n- " + data.feedback.join("\n- ");
});

document.getElementById("progressBtn").addEventListener("click", async () => {
  const userId = document.getElementById("userId").value || "default";
  const res = await fetch("/api/progress?user=" + encodeURIComponent(userId));
  const data = await res.json();
  document.getElementById("progress").textContent = JSON.stringify(data.progress, null, 2);
});

document.getElementById("reportBtn").addEventListener("click", async () => {
  if (!currentScenario) { alert("Generate a scenario first."); return; }
  if (!lastScoreData) { alert("Submit your actions for scoring first."); return; }
  const payload = {
    scenario: currentScenario,
    logs: currentLogs,
    packets: currentPackets,
    score: lastScoreData.score,
    breakdown: lastScoreData.breakdown,
    feedback: lastScoreData.feedback,
    artifacts: currentArtifacts || {}
  };
  const res = await fetch("/api/report", {
    method: "POST",
    headers: {"content-type": "application/json"},
    body: JSON.stringify(payload)
  });
  const data = await res.json();
  document.getElementById("report").textContent = JSON.stringify(data.report, null, 2);
});

loadScenarios();
