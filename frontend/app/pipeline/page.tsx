import Sidebar from "@/components/Sidebar";
import { GitBranch, CheckCircle2, Clock, AlertTriangle, Database } from "lucide-react";

const SYNC_LOG = [
  { id: "sync-001", table: "sensor_readings", rows: 1240, duration: "1.2s", status: "success", time: "14:00:03" },
  { id: "sync-002", table: "agent_memory",   rows: 18,   duration: "0.3s", status: "success", time: "14:00:03" },
  { id: "sync-003", table: "investigations",  rows: 4,    duration: "0.2s", status: "success", time: "13:00:05" },
  { id: "sync-004", table: "sensor_readings", rows: 1107, duration: "1.1s", status: "success", time: "13:00:04" },
  { id: "sync-005", table: "sensor_readings", rows: 0,    duration: "0.1s", status: "failed",  time: "12:00:03" },
  { id: "sync-006", table: "agent_memory",   rows: 22,   duration: "0.3s", status: "success", time: "12:00:02" },
];

export default function PipelinePage() {
  return (
    <div className="flex min-h-screen bg-bg">
      <Sidebar />
      <main className="flex-1 min-w-0 overflow-y-auto">
        <header className="sticky top-0 z-10 bg-bg/80 backdrop-blur-md border-b border-border px-6 py-4">
          <h1 className="text-white text-lg font-semibold">Pipeline</h1>
          <p className="text-slate-500 text-xs mt-1">Fivetran connector status and sync history</p>
        </header>

        <div className="p-6 space-y-5">
          {/* Connector status cards */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { label: "Connector",    value: "Active",      icon: GitBranch,    color: "text-success", iconBg: "bg-success/10", iconColor: "#10B981" },
              { label: "Last Sync",    value: "2 min ago",   icon: Clock,        color: "text-white",   iconBg: "bg-slate-800",  iconColor: "#64748B" },
              { label: "Tables Synced",value: "3",           icon: Database,     color: "text-white",   iconBg: "bg-slate-800",  iconColor: "#64748B" },
              { label: "Failed Syncs", value: "1",           icon: AlertTriangle,color: "text-warning", iconBg: "bg-warning/10", iconColor: "#F59E0B" },
            ].map(({ label, value, icon: Icon, color, iconBg, iconColor }) => (
              <div key={label} className="bg-card border border-border rounded-2xl p-5">
                <div className="flex items-start justify-between mb-3">
                  <p className="text-slate-400 text-xs font-medium uppercase tracking-wider">{label}</p>
                  <div className={`w-8 h-8 rounded-lg ${iconBg} flex items-center justify-center`}>
                    <Icon size={15} color={iconColor} strokeWidth={2} />
                  </div>
                </div>
                <p className={`text-3xl font-bold ${color}`}>{value}</p>
              </div>
            ))}
          </div>

          {/* Sync log table */}
          <div className="bg-card border border-border rounded-2xl overflow-hidden">
            <div className="px-5 py-4 border-b border-border">
              <h3 className="text-white text-sm font-semibold">Sync Log</h3>
              <p className="text-slate-500 text-xs mt-0.5">Recent Fivetran connector runs</p>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border">
                    <th className="text-left px-5 py-3 text-slate-500 text-xs font-medium uppercase tracking-wider">Table</th>
                    <th className="text-left px-5 py-3 text-slate-500 text-xs font-medium uppercase tracking-wider">Rows</th>
                    <th className="text-left px-5 py-3 text-slate-500 text-xs font-medium uppercase tracking-wider">Duration</th>
                    <th className="text-left px-5 py-3 text-slate-500 text-xs font-medium uppercase tracking-wider">Time</th>
                    <th className="text-left px-5 py-3 text-slate-500 text-xs font-medium uppercase tracking-wider">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {SYNC_LOG.map((row) => (
                    <tr key={row.id} className="border-b border-border/50 hover:bg-white/[0.02] transition-colors">
                      <td className="px-5 py-3 text-slate-300 font-medium">{row.table}</td>
                      <td className="px-5 py-3 text-slate-400 tabular-nums">{row.rows.toLocaleString()}</td>
                      <td className="px-5 py-3 text-slate-400 tabular-nums">{row.duration}</td>
                      <td className="px-5 py-3 text-slate-500 tabular-nums">{row.time}</td>
                      <td className="px-5 py-3">
                        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-semibold ${
                          row.status === "success"
                            ? "bg-success/10 text-success"
                            : "bg-danger/10 text-danger"
                        }`}>
                          {row.status === "success" ? (
                            <CheckCircle2 size={10} />
                          ) : (
                            <AlertTriangle size={10} />
                          )}
                          {row.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
