import Sidebar from "@/components/Sidebar";
import { Bot, CheckCircle2, Clock } from "lucide-react";

const AGENTS = [
  {
    name: "Investigator Agent",
    description: "Polls sensor readings every 60s. Detects anomalies using Gemini and routes findings to the orchestrator.",
    status: "running",
    lastRun: "58s ago",
    color: "#F59E0B",
    bgColor: "bg-warning/10",
    runs: 1440,
    anomalies: 12,
  },
  {
    name: "Pipeline Forensics Agent",
    description: "Monitors Fivetran connector health. Analyses failures and proposes remediation steps.",
    status: "running",
    lastRun: "2m ago",
    color: "#EF4444",
    bgColor: "bg-danger/10",
    runs: 720,
    anomalies: 1,
  },
  {
    name: "Shift Handover Copilot",
    description: "Runs at 06:00, 14:00, 22:00. Generates a structured shift summary and writes a pending HITL action.",
    status: "running",
    lastRun: "4h ago",
    color: "#3B82F6",
    bgColor: "bg-accent/10",
    runs: 21,
    anomalies: 0,
  },
  {
    name: "Briefing Agent",
    description: "Generates a 2–3 sentence plain-English summary of the last hour's activity on demand.",
    status: "running",
    lastRun: "On demand",
    color: "#10B981",
    bgColor: "bg-success/10",
    runs: 284,
    anomalies: 0,
  },
  {
    name: "Action Agent",
    description: "Polls approved_actions table every 5s. Executes approved actions and marks them as executed or failed.",
    status: "running",
    lastRun: "3s ago",
    color: "#8B5CF6",
    bgColor: "bg-violet/10",
    runs: 17280,
    anomalies: 0,
  },
];

export default function AgentsPage() {
  return (
    <div className="flex min-h-screen bg-bg">
      <Sidebar />
      <main className="flex-1 min-w-0 overflow-y-auto">
        <header className="sticky top-0 z-10 bg-bg/80 backdrop-blur-md border-b border-border px-6 py-4">
          <h1 className="text-white text-lg font-semibold">Agents</h1>
          <p className="text-slate-500 text-xs mt-1">AI agent fleet status and activity</p>
        </header>

        <div className="p-6 space-y-4">
          {AGENTS.map((agent) => (
            <div key={agent.name} className="bg-card border border-border rounded-2xl p-5">
              <div className="flex items-start gap-4">
                <div className={`w-10 h-10 rounded-xl ${agent.bgColor} flex items-center justify-center shrink-0 mt-0.5`}>
                  <Bot size={17} color={agent.color} strokeWidth={1.75} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3 flex-wrap">
                    <h3 className="text-white text-sm font-semibold">{agent.name}</h3>
                    <span className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-lg bg-success/10 text-success text-[11px] font-semibold">
                      <CheckCircle2 size={10} />
                      Running
                    </span>
                  </div>
                  <p className="text-slate-500 text-sm mt-1 leading-relaxed">{agent.description}</p>

                  <div className="flex items-center gap-5 mt-3">
                    <div>
                      <p className="text-slate-600 text-[10px] uppercase tracking-wider font-medium">Last Run</p>
                      <p className="text-slate-300 text-sm font-medium flex items-center gap-1 mt-0.5">
                        <Clock size={11} className="text-slate-500" />
                        {agent.lastRun}
                      </p>
                    </div>
                    <div>
                      <p className="text-slate-600 text-[10px] uppercase tracking-wider font-medium">Total Runs</p>
                      <p className="text-slate-300 text-sm font-medium mt-0.5 tabular-nums">{agent.runs.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-slate-600 text-[10px] uppercase tracking-wider font-medium">Anomalies Found</p>
                      <p className={`text-sm font-medium mt-0.5 tabular-nums ${agent.anomalies > 0 ? "text-warning" : "text-slate-500"}`}>
                        {agent.anomalies}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
