"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { getSensorReadings, type SensorReading } from "@/lib/api";

const SENSOR_CONFIG: Record<string, { color: string; gradientId: string }> = {
  temperature: { color: "#3B82F6", gradientId: "g-temp"    },
  vibration:   { color: "#F59E0B", gradientId: "g-vib"     },
  throughput:  { color: "#10B981", gradientId: "g-through"  },
  pressure:    { color: "#8B5CF6", gradientId: "g-press"    },
};
const FALLBACK_COLORS = ["#3B82F6", "#F59E0B", "#10B981", "#8B5CF6", "#06B6D4"];

const LINES = [null, 1, 2, 3] as const;
type LineFilter = (typeof LINES)[number];

function ChartTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-[#1E2D45] border border-[#2A3F5F] rounded-xl p-3 shadow-2xl text-xs">
      <p className="text-slate-400 font-medium mb-2">{label}</p>
      {payload.map((p: any) => (
        <div key={p.dataKey} className="flex items-center gap-2 mb-1 last:mb-0">
          <div className="w-2 h-2 rounded-full" style={{ backgroundColor: p.color }} />
          <span className="text-slate-300 capitalize">{p.dataKey}</span>
          <span className="ml-auto text-white font-semibold pl-4">{p.value}</span>
        </div>
      ))}
    </div>
  );
}

export default function SensorTrendChart() {
  const [data, setData] = useState<SensorReading[]>([]);
  const [loading, setLoading] = useState(true);
  const [line, setLine] = useState<LineFilter>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setData(await getSensorReadings(60, line ?? undefined));
    } catch {
      /* keep stale */
    } finally {
      setLoading(false);
    }
  }, [line]);

  useEffect(() => { load(); }, [load]);

  const sensorTypes = useMemo(
    () => (data.length > 0 ? Object.keys(data[0]).filter((k) => k !== "time") : []),
    [data],
  );

  const ticks = useMemo(() => {
    const step = Math.max(1, Math.floor(data.length / 5));
    return data.filter((_, i) => i % step === 0).map((d) => d.time as string);
  }, [data]);

  return (
    <div className="bg-card border border-border rounded-2xl overflow-hidden">
      <div className="flex items-center justify-between px-5 py-4 border-b border-border gap-4 flex-wrap">
        <div>
          <h3 className="text-white text-sm font-semibold">Sensor Readings</h3>
          <p className="text-slate-500 text-xs mt-0.5">Last 60 min · avg per minute</p>
        </div>
        <div className="flex items-center gap-1">
          {LINES.map((l) => (
            <button
              key={String(l)}
              onClick={() => setLine(l)}
              className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-all duration-150 cursor-pointer ${
                line === l
                  ? "bg-accent/20 text-accent"
                  : "text-slate-500 hover:text-slate-300"
              }`}
            >
              {l === null ? "All" : `L${l}`}
            </button>
          ))}
          {!loading && data.length > 0 && (
            <div className="flex items-center gap-1.5 ml-2">
              <span className="relative flex h-1.5 w-1.5">
                <span className="animate-ping absolute h-full w-full rounded-full bg-success opacity-50" />
                <span className="relative rounded-full h-1.5 w-1.5 bg-success" />
              </span>
              <span className="text-success text-[10px] font-medium">Live</span>
            </div>
          )}
        </div>
      </div>

      <div className="p-5">
        {loading ? (
          <div className="h-[240px] bg-border/20 rounded-xl animate-pulse" />
        ) : data.length === 0 ? (
          <div className="h-[240px] flex flex-col items-center justify-center gap-2">
            <p className="text-slate-500 text-sm">No sensor data yet</p>
            <p className="text-slate-700 text-xs">Run the sensor simulator to populate this chart</p>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={240}>
            <AreaChart data={data} margin={{ top: 4, right: 4, bottom: 0, left: -16 }}>
              <defs>
                {sensorTypes.map((type, i) => {
                  const cfg = SENSOR_CONFIG[type];
                  const color = cfg?.color ?? FALLBACK_COLORS[i % FALLBACK_COLORS.length];
                  const id = cfg?.gradientId ?? `g-${type}`;
                  return (
                    <linearGradient key={id} id={id} x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={color} stopOpacity={0.3} />
                      <stop offset="95%" stopColor={color} stopOpacity={0} />
                    </linearGradient>
                  );
                })}
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1A2A42" vertical={false} />
              <XAxis
                dataKey="time"
                ticks={ticks}
                tick={{ fill: "#475569", fontSize: 10 }}
                tickLine={false}
                axisLine={{ stroke: "#1A2A42" }}
              />
              <YAxis
                tick={{ fill: "#475569", fontSize: 10 }}
                tickLine={false}
                axisLine={false}
              />
              <Tooltip content={<ChartTooltip />} cursor={{ stroke: "#2A3F5F", strokeWidth: 1 }} />
              <Legend
                wrapperStyle={{ fontSize: "11px", color: "#64748B", paddingTop: "12px" }}
                iconType="circle"
                iconSize={7}
                formatter={(v) => String(v).charAt(0).toUpperCase() + String(v).slice(1)}
              />
              {sensorTypes.map((type, i) => {
                const cfg = SENSOR_CONFIG[type];
                const color = cfg?.color ?? FALLBACK_COLORS[i % FALLBACK_COLORS.length];
                const id = cfg?.gradientId ?? `g-${type}`;
                return (
                  <Area
                    key={type}
                    type="monotone"
                    dataKey={type}
                    stroke={color}
                    strokeWidth={2}
                    fill={`url(#${id})`}
                    dot={false}
                    activeDot={{ r: 4, strokeWidth: 0 }}
                  />
                );
              })}
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
