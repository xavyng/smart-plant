# Smart Plant - AI Factory Monitor

**Built for Google Cloud Rapid Agent Hackathon 2026 (Fivetran Track)**

An AI agent system that monitors factory sensors, detects anomalies, and proposes actions — with a human operator approving everything before it executes.

## What It Does

- Watches sensor data (temperature, vibration, throughput, pressure) across 3 production lines in real-time
- Flags anomalies — e.g. motor temperature breach + vibration spike = likely bearing failure
- Detects data pipeline failures and proposes an auto-repair via the Fivetran API
- Queues actions (maintenance emails, pipeline fixes, shift handover summaries) for human approval
- Operator reviews, edits if needed, and approves from a dashboard — then the agent executes

## Architecture

```
Factory Sensors → Fivetran Custom Connector SDK → BigQuery
                                                       ↓
                                              AI Agents (Google ADK + Gemini 2.5 Flash)
                                                       ↓
                                         Approvals Dashboard (Next.js)
                                                       ↓
                                     Gmail / Fivetran API (on approval)
```

## Tech Stack

- **AI**: Gemini 2.5 Flash via Google ADK (multi-agent orchestration)
- **Data Pipeline**: Fivetran + Custom Connector SDK (MQTT sensor ingestion)
- **Data Warehouse**: Google BigQuery
- **Backend**: Python + FastAPI — deployed on Google Cloud Run
- **Frontend**: Next.js + Tailwind CSS — deployed on Vercel
- **Notifications**: Gmail SMTP

## Agents

| Agent | Role |
|---|---|
| Investigator | Polls BigQuery every 60s, flags sensor anomalies |
| Pipeline Forensics | Checks Fivetran connector health, proposes repair if stalled |
| Action Agent | Executes approved actions (send email, unpause connector + force sync) |
| Briefing Agent | Summarizes current plant state on demand using Gemini |
| Shift Handover | Generates end-of-shift summary for incoming operator |

## Key Features

- **HITL Approvals** — every AI-proposed action sits in a queue until a human approves, edits, or rejects it
- **Live pipeline status** — dashboard card polls Fivetran every 15s and shows red/green connector state
- **Auto-healing** — approving a pipeline_fix action PATCHes Fivetran to unpause the connector and triggers a force sync
- **Edit before send** — operators can modify the recipient, subject, and body of any email before approving

## Running Locally

```bash
# Backend
python -m venv venv
venv\Scripts\activate
pip install -r backend/requirements.txt
uvicorn backend.api.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

Copy `.env.example` to `.env` and fill in your credentials (GCP project, BigQuery dataset, Fivetran API keys, Gmail app password).

## Demo Scripts

```bash
# Inject a sensor anomaly (bypasses Gemini, goes straight to Approvals)
venv\Scripts\python scripts\inject_pending_action.py anomaly

# Inject a pipeline failure action
venv\Scripts\python scripts\inject_pending_action.py pipeline

# Inject a shift handover summary
venv\Scripts\python scripts\inject_pending_action.py handover

# Write critical sensor readings directly to BigQuery (triggers investigator)
venv\Scripts\python scripts\inject_anomaly.py
```

## License

Apache 2.0

## Team

Xavier and Syed Aqeel

---

**Hackathon**: Google Cloud Rapid Agent Hackathon 2026
**Track**: Fivetran
**Live demo**: https://smart-plant-dashboard.vercel.app
