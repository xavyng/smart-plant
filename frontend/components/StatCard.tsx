import { type LucideIcon } from "lucide-react";

interface StatCardProps {
  label: string;
  value: string | number;
  sub?: string;
  icon: LucideIcon;
  status?: "normal" | "ok" | "warning" | "critical";
}

const styles = {
  normal: { iconBg: "bg-slate-800", iconColor: "#64748B", valueColor: "text-white" },
  ok:     { iconBg: "bg-success/10", iconColor: "#10B981", valueColor: "text-success" },
  warning:{ iconBg: "bg-warning/10", iconColor: "#F59E0B", valueColor: "text-warning" },
  critical:{ iconBg: "bg-danger/10", iconColor: "#EF4444", valueColor: "text-danger" },
};

export default function StatCard({ label, value, sub, icon: Icon, status = "normal" }: StatCardProps) {
  const s = styles[status];
  return (
    <div className="bg-card border border-border rounded-2xl p-5">
      <div className="flex items-start justify-between mb-3">
        <p className="text-slate-400 text-xs font-medium uppercase tracking-wider">{label}</p>
        <div className={`w-8 h-8 rounded-lg ${s.iconBg} flex items-center justify-center`}>
          <Icon size={15} color={s.iconColor} strokeWidth={2} />
        </div>
      </div>
      <p className={`text-3xl font-bold tabular-nums leading-none ${s.valueColor}`}>{value}</p>
      {sub && <p className="text-slate-600 text-xs mt-2">{sub}</p>}
    </div>
  );
}
