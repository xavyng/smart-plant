"use client";

import dynamic from "next/dynamic";
import { useCallback, useEffect, useRef, useState } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  Clock,
  RefreshCw,
  Workflow,
} from "lucide-react";
import { getBrief, getPendingActions, type PendingAction } from "@/lib/api";
import Sidebar from "./Sidebar";
import StatCard from "./StatCard";
import ActionItem from "./ActionItem";
import BriefingPanel from "./BriefingPanel";

const SensorTrendChart = dynamic(() => import("./charts/SensorTrendChart"), {
  ssr: false,
  loading: () => <ChartSkeleton height={310} label="Sensor Readings" sub="Last 60 min · Production Line 3" />,
});
const AlertHistoryChart = dynamic(() => import("./charts/AlertHistoryChart"), {
  ssr: false,
  loading: () => <ChartSkeleton height={270} label="Alert History" sub="Past 7 shifts" />,
});
const ActionDonut = dynamic(() => import("./charts/ActionDonut"), {
  ssr: false,
  loading: () => <div className="bg-card border border-border rounded-2xl h-[184px] animate-pulse" />,
});

function ChartSkeleton({ height, label, sub }: { height: number; label: string; sub: string }) {
  return (
    <div className="bg-card border border-border rounded-2xl overflow-hidden" style={{ height }}>
      <div className="px-5 py-4 border-b border-border">
        <div className="h-4 w-36 bg-border rounded animate-pulse mb-1.5" />
        <div className="h-3 w-48 bg-border/60 rounded animate-pulse" />
      </div>
      <div className="p-5 flex items-center justify-center h-[calc(100%-65px)]">
        <p className="text-slate-700 text-sm">{label} · {sub}</p>
      </div>
    </div>
  );
}

const AGENTS = [
  { name: "Investigator", color: "#F59E0B" },
  { name: "Pipeline Forensics", color: "#EF4444" },
  { name: "Shift Handover", color: "#3B82F6" },
  { name: "Briefing Agent", color: "#10B981" },
  { name: "Action Agent", color: "#8B5CF6" },
];

const REFRESH_MS = 10_000;

function currentShift() {
  const h = new Date().getHours();
  if (h >= 6 && h < 14) return { name: "Morning", hours: "06:00 – 14:00" };
  if (h >= 14 && h < 22) return { name: "Afternoon", hours: "14:00 – 22:00" };
  return { name: "Night", hours: "22:00 – 06:00" };
}

export default function Dashboard() {
  const [actions, setActions] = useState<PendingAction[]>([]);
  const [brief, setBrief] = useState<string | null>(null);
  const [loadingActions, setLoadingActions] = useState(true);
  const [loadingBrief, setLoadingBrief] = useState(true);
  const [apiError, setApiError] = useState<string | null>(null);
  const [lastRefreshed, setLastRefreshed] = useState<Date | null>(null);
  const [clock, setClock] = useState("");
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    const tick = () => setClock(new Date().toLocaleTimeString("en-GB", { hour12: false }));
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, []);

  const fetchActions = useCallback(async () => {
    setLoadingActions(true);
    try {
      setActions(await getPendingActions());
      setApiError(null);
    } catch {
      setApiError("API unreachable");
    } finally {
      setLoadingActions(false);
      setLastRefreshed(new Date());
    }
  }, []);

  const fetchBrief = useCallback(async () => {
    setLoadingBrief(true);
    try {
      setBrief(await getBrief());
    } catch {
      /* keep stale */
    } finally {
      setLoadingBrief(false);
    }
  }, []);

  const refresh = useCallback(() => {
    fetchActions();
    fetchBrief();
  }, [fetchActions, fetchBrief]);

  useEffect(() => {
    refresh();
    timer.current = setInterval(refresh, REFRESH_MS);
    return () => { if (timer.current) clearInterval(timer.current); };
  }, [refresh]);

  const criticalCount = actions.filter(
    (a) => a.action_type === "sensor_anomaly" || a.action_type === "pipeline_fix",
  ).length;
  const shift = currentShift();

  return (
    <div className="flex min-h-screen bg-bg">
      <Sidebar />

      <main className="flex-1 min-w-0 overflow-y-auto">
        {/* Header */}
        <header className="sticky top-0 z-10 bg-bg/80 backdrop-blur-md border-b border-border px-6 py-4 flex items-center justify-between gap-4">
          <div>
            <h1 className="text-white text-lg font-semibold leading-none">Dashboard</h1>
            <p className="text-slate-500 text-xs mt-1">
              {apiError ? (
                <span className="text-danger">{apiError}</span>
              ) : lastRefreshed ? (
                `Updated ${lastRefreshed.toLocaleTimeString("en-GB", { hour12: false })}`
              ) : (
                "Loading..."
              )}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-slate-400 text-sm tabular-nums font-medium">{clock}</span>
            <button
              onClick={refresh}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-500 border border-border hover:text-white hover:border-border-light transition-all duration-150 cursor-pointer"
            >
              <RefreshCw size={11} />
              Refresh
            </button>
          </div>
        </header>

        <div className="p-6 space-y-5">
          {/* Stats */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              label="Pending Actions"
              value={loadingActions ? "—" : actions.length}
              sub={actions.length === 0 ? "All clear" : `${actions.length} awaiting review`}
              icon={Clock}
              status={loadingActions ? "normal" : actions.length > 0 ? "warning" : "ok"}
            />
            <StatCard
              label="Critical Alerts"
              value={loadingActions ? "—" : criticalCount}
              sub={criticalCount > 0 ? "Needs attention" : "No active alerts"}
              icon={AlertTriangle}
              status={loadingActions ? "normal" : criticalCount > 0 ? "critical" : "ok"}
            />
            <StatCard
              label="Pipeline"
              value="Active"
              sub="Fivetran connector running"
              icon={Workflow}
              status="ok"
            />
            <StatCard
              label="Current Shift"
              value={shift.name}
              sub={shift.hours}
              icon={CheckCircle2}
              status="normal"
            />
          </div>

          {/* Charts row */}
          <div className="grid grid-cols-1 lg:grid-cols-5 gap-5">
            <div className="lg:col-span-3">
              <SensorTrendChart />
            </div>
            <div className="lg:col-span-2 space-y-4">
              <ActionDonut pendingCount={actions.length} />
              <BriefingPanel brief={brief} loading={loadingBrief} onRefresh={fetchBrief} />
            </div>
          </div>

          {/* Lower row */}
          <div className="grid grid-cols-1 lg:grid-cols-5 gap-5">
            <div className="lg:col-span-3">
              <AlertHistoryChart />
            </div>
            <div className="lg:col-span-2">
              <div className="bg-card border border-border rounded-2xl overflow-hidden">
                <div className="px-5 py-4 border-b border-border">
                  <h3 className="text-white text-sm font-semibold">Agent Status</h3>
                  <p className="text-slate-500 text-xs mt-0.5">All systems operational</p>
                </div>
                <div className="p-5 space-y-3">
                  {AGENTS.map(({ name, color }) => (
                    <div key={name} className="flex items-center gap-3">
                      <div className="relative">
                        <div className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
                        <div
                          className="absolute inset-0 rounded-full animate-ping opacity-40"
                          style={{ backgroundColor: color }}
                        />
                      </div>
                      <span className="text-slate-400 text-sm flex-1">{name}</span>
                      <span className="text-xs font-medium px-2 py-0.5 rounded-md bg-success/10 text-success">
                        Running
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Pending approvals */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <h2 className="text-slate-400 text-xs font-semibold uppercase tracking-wider">
                Pending Approvals
              </h2>
              {!loadingActions && actions.length > 0 && (
                <span className="px-2 py-0.5 rounded-full text-[11px] font-semibold bg-warning/15 text-warning">
                  {actions.length}
                </span>
              )}
            </div>

            {loadingActions ? (
              <div className="space-y-3">
                {[0, 1].map((i) => (
                  <div key={i} className="h-[72px] bg-card border border-border rounded-2xl animate-pulse" />
                ))}
              </div>
            ) : actions.length === 0 ? (
              <div className="bg-card border border-border rounded-2xl p-10 flex flex-col items-center text-center">
                <CheckCircle2 size={24} className="text-success mb-3" strokeWidth={1.5} />
                <p className="text-slate-300 text-sm font-medium">All caught up</p>
                <p className="text-slate-600 text-xs mt-1">No pending actions at this time</p>
              </div>
            ) : (
              actions.map((action) => (
                <ActionItem key={action.action_id} action={action} onDecision={fetchActions} />
              ))
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
