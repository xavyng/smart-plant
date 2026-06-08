"use client";

import { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { getActionHistory, type HistoryItem } from "@/lib/api";

function ChartTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-[#1E2D45] border border-[#2A3F5F] rounded-xl p-3 shadow-2xl text-xs">
      <p className="text-slate-400 font-medium mb-2">{label}</p>
      {payload.map((p: any) => (
        <div key={p.dataKey} className="flex items-center gap-2 mb-1 last:mb-0">
          <div className="w-2 h-2 rounded-full" style={{ backgroundColor: p.fill }} />
          <span className="text-slate-300">{p.name}</span>
          <span className="ml-auto text-white font-semibold pl-4">{p.value}</span>
        </div>
      ))}
    </div>
  );
}

export default function AlertHistoryChart() {
  const [data, setData] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getActionHistory(7)
      .then(setData)
      .catch(() => {/* keep empty */})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="bg-card border border-border rounded-2xl overflow-hidden">
      <div className="px-5 py-4 border-b border-border">
        <h3 className="text-white text-sm font-semibold">Alert History</h3>
        <p className="text-slate-500 text-xs mt-0.5">Past 7 shifts by action type</p>
      </div>
      <div className="p-5">
        {loading ? (
          <div className="h-[200px] bg-border/20 rounded-xl animate-pulse" />
        ) : data.length === 0 ? (
          <div className="h-[200px] flex flex-col items-center justify-center gap-2">
            <p className="text-slate-500 text-sm">No action history yet</p>
            <p className="text-slate-700 text-xs">Actions will appear here once agents start running</p>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={data} margin={{ top: 4, right: 4, bottom: 0, left: -16 }} barGap={3}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1A2A42" vertical={false} />
              <XAxis
                dataKey="shift"
                tick={{ fill: "#475569", fontSize: 10 }}
                tickLine={false}
                axisLine={{ stroke: "#1A2A42" }}
              />
              <YAxis
                tick={{ fill: "#475569", fontSize: 10 }}
                tickLine={false}
                axisLine={false}
                allowDecimals={false}
              />
              <Tooltip content={<ChartTooltip />} cursor={{ fill: "rgba(255,255,255,0.02)" }} />
              <Legend
                wrapperStyle={{ fontSize: "11px", color: "#64748B", paddingTop: "12px" }}
                iconType="circle"
                iconSize={7}
              />
              <Bar dataKey="sensor_anomaly" name="Sensor Anomaly" fill="#F59E0B" radius={[3, 3, 0, 0]} maxBarSize={14} />
              <Bar dataKey="pipeline_fix"   name="Pipeline Fix"   fill="#EF4444" radius={[3, 3, 0, 0]} maxBarSize={14} />
              <Bar dataKey="shift_handover" name="Shift Handover" fill="#3B82F6" radius={[3, 3, 0, 0]} maxBarSize={14} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
