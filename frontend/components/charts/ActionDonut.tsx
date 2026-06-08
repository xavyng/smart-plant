"use client";

import { useEffect, useState } from "react";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";
import { getActionStats, type ActionStats } from "@/lib/api";

interface ActionDonutProps {
  pendingCount: number;
}

function ChartTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null;
  const d = payload[0];
  return (
    <div className="bg-[#1E2D45] border border-[#2A3F5F] rounded-xl p-2.5 shadow-2xl text-xs">
      <span style={{ color: d.payload.color }} className="font-medium">{d.name}: </span>
      <span className="text-white font-semibold">{d.value}</span>
    </div>
  );
}

export default function ActionDonut({ pendingCount }: ActionDonutProps) {
  const [stats, setStats] = useState<ActionStats | null>(null);

  useEffect(() => {
    getActionStats()
      .then(setStats)
      .catch(() => {/* keep null */});
  }, [pendingCount]);

  const approved = stats?.approved ?? 0;
  const rejected = stats?.rejected ?? 0;
  const executed = stats?.executed ?? 0;

  const data = [
    { name: "Executed",  value: executed,     color: "#10B981" },
    { name: "Approved",  value: approved,      color: "#3B82F6" },
    { name: "Rejected",  value: rejected,      color: "#EF4444" },
    { name: "Pending",   value: pendingCount,  color: "#F59E0B" },
  ].filter((d) => d.value > 0);

  const total = data.reduce((s, d) => s + d.value, 0);
  const resolvedRate = total > 0 ? Math.round(((executed + approved) / total) * 100) : 0;

  return (
    <div className="bg-card border border-border rounded-2xl overflow-hidden">
      <div className="px-5 py-4 border-b border-border">
        <h3 className="text-white text-sm font-semibold">Action Resolution</h3>
        <p className="text-slate-500 text-xs mt-0.5">This week · {total} total</p>
      </div>
      <div className="flex items-center gap-4 p-5">
        <div className="relative shrink-0">
          <ResponsiveContainer width={110} height={110}>
            <PieChart>
              <Pie
                data={total > 0 ? data : [{ name: "Empty", value: 1, color: "#1A2A42" }]}
                innerRadius={36}
                outerRadius={50}
                dataKey="value"
                strokeWidth={0}
                paddingAngle={total > 0 ? 2 : 0}
              >
                {(total > 0 ? data : [{ color: "#1A2A42" }]).map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip content={<ChartTooltip />} />
            </PieChart>
          </ResponsiveContainer>
          <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
            <span className="text-2xl font-bold text-white tabular-nums">{resolvedRate}%</span>
            <span className="text-[9px] text-slate-500 font-medium">resolved</span>
          </div>
        </div>
        <div className="flex-1 space-y-2.5">
          {data.length > 0 ? (
            data.map(({ name, value, color }) => (
              <div key={name} className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: color }} />
                <span className="text-slate-400 text-xs flex-1">{name}</span>
                <span className="text-white text-xs font-semibold tabular-nums">{value}</span>
              </div>
            ))
          ) : (
            <p className="text-slate-600 text-xs">No data yet</p>
          )}
        </div>
      </div>
    </div>
  );
}
