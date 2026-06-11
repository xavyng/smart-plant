"use client";

import { useState } from "react";
import { Check, X, ChevronDown, ChevronUp, Clock, User } from "lucide-react";
import { type PendingAction, decideAction } from "@/lib/api";

interface ActionItemProps {
  action: PendingAction;
  onDecision: () => void;
}

const TYPE_CONFIG: Record<string, { label: string; color: string; bg: string; border: string }> = {
  sensor_anomaly:             { label: "Sensor Anomaly", color: "#F59E0B", bg: "bg-warning/10", border: "border-warning/20" },
  investigate_sensor_anomaly: { label: "Sensor Anomaly", color: "#F59E0B", bg: "bg-warning/10", border: "border-warning/20" },
  pipeline_fix:               { label: "Pipeline Fix",   color: "#EF4444", bg: "bg-danger/10",  border: "border-danger/20"  },
  investigate_pipeline_failure:{ label: "Pipeline Fix",  color: "#EF4444", bg: "bg-danger/10",  border: "border-danger/20"  },
  shift_handover:             { label: "Shift Handover", color: "#3B82F6", bg: "bg-accent/10",  border: "border-accent/20"  },
};

function resolveConfig(actionType: string) {
  const key = actionType.toLowerCase().replace(/\s+/g, "_");
  return TYPE_CONFIG[key] ?? TYPE_CONFIG[actionType] ?? { label: "Action Required", color: "#94A3B8", bg: "bg-white/5", border: "border-border" };
}

function timeAgo(isoStr: string): string {
  const diff = Math.floor((Date.now() - new Date(isoStr).getTime()) / 1000);
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  return `${Math.floor(diff / 3600)}h ago`;
}

function getTitle(action: PendingAction): string {
  const p = action.payload as Record<string, string>;
  if (p.subject) return p.subject;
  if (action.action_type === "sensor_anomaly") return "Sensor Anomaly Detected";
  if (action.action_type === "pipeline_fix") return "Pipeline Fix Required";
  return "Action Required";
}

function formatPipelinePayload(p: Record<string, string>): string {
  const id = p.connector_id ?? "unknown";
  const reason = p.reason ?? "unknown reason";
  if (p.last_succeeded_at) {
    const d = new Date(p.last_succeeded_at);
    const ts = d.toLocaleString("en-US", { month: "short", day: "numeric", year: "numeric", hour: "2-digit", minute: "2-digit", timeZone: "UTC", timeZoneName: "short" });
    return `Connector "${id}" stopped syncing — ${reason}. Last successful sync: ${ts}.`;
  }
  return `Connector "${id}" stopped syncing — ${reason}.`;
}

function getBody(action: PendingAction): string {
  const p = action.payload as Record<string, unknown>;

  const str = (v: unknown): string | null => (typeof v === "string" && v ? v : null);

  const direct =
    str(p.diagnosis) ??
    str(p.body) ??
    str(p.description) ??
    str(p.summary) ??
    str(p.message);
  if (direct) return direct;

  const details = p.details as Record<string, unknown> | undefined;
  const detailMsg = details ? str(details.message) : null;
  if (detailMsg) return detailMsg;

  if (str(p.reason)) {
    const target = str(p.target);
    return target ? `${target} — ${p.reason}` : String(p.reason);
  }

  if (action.action_type === "pipeline_fix" || action.action_type === "investigate_pipeline_failure") {
    return formatPipelinePayload(p as Record<string, string>);
  }

  return JSON.stringify(action.payload, null, 2);
}

export default function ActionItem({ action, onDecision }: ActionItemProps) {
  const [expanded, setExpanded] = useState(false);
  const [loading, setLoading] = useState<"approve" | "reject" | null>(null);
  const cfg = resolveConfig(action.action_type);

  async function handle(decision: "approve" | "reject") {
    setLoading(decision);
    try {
      await decideAction(action.action_id, decision);
      onDecision();
    } catch {
      setLoading(null);
    }
  }

  return (
    <div className={`bg-card border ${cfg.border} rounded-2xl overflow-hidden`}>
      <button
        className="w-full flex items-start gap-3 p-4 text-left hover:bg-white/[0.02] transition-colors duration-150 cursor-pointer"
        onClick={() => setExpanded((e) => !e)}
        aria-expanded={expanded}
      >
        <span
          className={`shrink-0 mt-0.5 px-2.5 py-1 rounded-lg text-[11px] font-semibold ${cfg.bg}`}
          style={{ color: cfg.color }}
        >
          {cfg.label}
        </span>
        <div className="flex-1 min-w-0">
          <p className="text-slate-200 text-sm font-medium truncate">{getTitle(action)}</p>
          <div className="flex items-center gap-3 mt-1">
            <span className="flex items-center gap-1 text-slate-500 text-xs">
              <User size={10} /> {action.proposed_by}
            </span>
            <span className="flex items-center gap-1 text-slate-500 text-xs">
              <Clock size={10} /> {timeAgo(action.created_at)}
            </span>
          </div>
        </div>
        <span className="shrink-0 text-slate-600 mt-1">
          {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </span>
      </button>

      {expanded && (
        <div className="px-4 pb-4 border-t border-border/50">
          <p className="text-slate-300 text-sm leading-relaxed mt-3 whitespace-pre-line">{getBody(action)}</p>
        </div>
      )}

      <div className="flex items-center justify-end gap-2 px-4 py-3 border-t border-border/50 bg-black/10">
        <button
          onClick={() => handle("reject")}
          disabled={loading !== null}
          className="flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-medium text-danger border border-danger/25 hover:bg-danger/10 disabled:opacity-40 disabled:cursor-not-allowed transition-all duration-150 cursor-pointer"
        >
          <X size={11} />
          {loading === "reject" ? "Rejecting..." : "Reject"}
        </button>
        <button
          onClick={() => handle("approve")}
          disabled={loading !== null}
          className="flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-medium text-success border border-success/25 hover:bg-success/10 disabled:opacity-40 disabled:cursor-not-allowed transition-all duration-150 cursor-pointer"
        >
          <Check size={11} />
          {loading === "approve" ? "Approving..." : "Approve"}
        </button>
      </div>
    </div>
  );
}
