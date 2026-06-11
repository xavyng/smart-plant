"use client";

import { useCallback, useEffect, useState } from "react";
import { CheckCircle2, RefreshCw } from "lucide-react";
import Sidebar from "@/components/Sidebar";
import ActionItem from "@/components/ActionItem";
import { getPendingActions, type PendingAction } from "@/lib/api";

export default function ApprovalsPage() {
  const [actions, setActions] = useState<PendingAction[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchActions = useCallback(async (background = false) => {
    if (!background) setLoading(true);
    try {
      setActions(await getPendingActions());
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchActions();
    const id = setInterval(() => fetchActions(true), 10_000);
    return () => clearInterval(id);
  }, [fetchActions]);

  return (
    <div className="flex min-h-screen bg-bg">
      <Sidebar />
      <main className="flex-1 min-w-0 overflow-y-auto">
        <header className="sticky top-0 z-10 bg-bg/80 backdrop-blur-md border-b border-border px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-white text-lg font-semibold">Approvals</h1>
            <p className="text-slate-500 text-xs mt-1">Review and action pending AI recommendations</p>
          </div>
          <button
            onClick={async () => { setRefreshing(true); await fetchActions(true); setRefreshing(false); }}
            disabled={refreshing}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-500 border border-border hover:text-white hover:border-border-light disabled:opacity-50 transition-all duration-150 cursor-pointer"
          >
            <RefreshCw size={11} className={refreshing ? "animate-spin" : ""} />
            {refreshing ? "Refreshing..." : "Refresh"}
          </button>
        </header>

        <div className="p-6">
          {loading ? (
            <div className="space-y-3">
              {[0, 1, 2].map((i) => (
                <div key={i} className="h-[72px] bg-card border border-border rounded-2xl animate-pulse" />
              ))}
            </div>
          ) : actions.length === 0 ? (
            <div className="bg-card border border-border rounded-2xl p-16 flex flex-col items-center text-center">
              <CheckCircle2 size={28} className="text-success mb-3" strokeWidth={1.5} />
              <p className="text-slate-300 text-sm font-medium">All caught up</p>
              <p className="text-slate-600 text-xs mt-1">No pending actions at this time</p>
            </div>
          ) : (
            <div className="space-y-3">
              <div className="flex items-center gap-2 mb-1">
                <p className="text-slate-400 text-xs font-semibold uppercase tracking-wider">Pending</p>
                <span className="px-2 py-0.5 rounded-full text-[11px] font-semibold bg-warning/15 text-warning">
                  {actions.length}
                </span>
              </div>
              {actions.map((action) => (
                <ActionItem key={action.action_id} action={action} onDecision={() => fetchActions(true)} />
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
