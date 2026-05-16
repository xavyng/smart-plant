\# Smart Plant - AI Plant Manager



\*\*Built for Google Cloud Rapid Agent Hackathon 2026 (Fivetran Track)\*\*



An intelligent multi-agent system that monitors factory operations, diagnoses issues, and proposes actions — all with human-in-the-loop approval.



\## What It Does



Smart Plant is your AI co-pilot for factory operations:



\- \*\*Monitors\*\* 50+ sensors across 3 production lines in real-time

\- \*\*Investigates\*\* issues ("Why is Line 2 slow?" → "Motor 2B bearing failure likely")

\- \*\*Proposes actions\*\* (email supervisor, schedule maintenance, order parts)

\- \*\*Waits for approval\*\* before executing (human-in-the-loop)

\- \*\*Auto-repairs\*\* broken data pipelines using Fivetran MCP



\## Architecture

Factory Sensors → MQTT → Custom Fivetran Connector → BigQuery

↓

Gemini Agents

↓

Gmail | Calendar | Docs APIs



\## Tech Stack



\- \*\*AI\*\*: Gemini 2.5 (via Google ADK)

\- \*\*Data Warehouse\*\*: Google BigQuery

\- \*\*Data Pipeline\*\*: Fivetran + Custom MQTT Connector SDK

\- \*\*Pipeline Monitoring\*\*: Fivetran MCP Server

\- \*\*Frontend\*\*: Next.js + React + Tailwind CSS

\- \*\*Backend\*\*: Python + FastAPI

\- \*\*Infrastructure\*\*: Google Cloud Run



\## Key Features



1\. \*\*Custom Fivetran Connector\*\* - Ingests MQTT sensor data (custom-built using Connector SDK)

2\. \*\*Multi-Agent System\*\* - 6 specialized agents (Orchestrator, Investigator, Pipeline Health, Action, Briefing, Memory)

3\. \*\*Real-time Dashboard\*\* - WebSocket streaming of agent activity

4\. \*\*Human-in-the-Loop\*\* - All actions require approval

5\. \*\*Auto-Healing Pipelines\*\* - Detects and repairs broken Fivetran connectors



\## Getting Started



Coming soon...



\## Demo Video



Coming soon...



\## License



Apache 2.0 - See \[LICENSE](LICENSE) file for details



\## Team

Xavier and Syed Aqeel

\---



\*\*Hackathon\*\*: Google Cloud Rapid Agent Hackathon 2026  

\*\*Track\*\*: Fivetran  

\*\*Status\*\*: In Development 

