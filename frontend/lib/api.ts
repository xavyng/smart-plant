const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface PendingAction {
  action_id: string;
  action_type: string;
  proposed_by: string;
  payload: Record<string, unknown>;
  status: string;
  created_at: string;
}

export async function getPendingActions(): Promise<PendingAction[]> {
  const res = await fetch(`${BASE}/api/v1/actions/pending`, { cache: "no-store" });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function getBrief(): Promise<string> {
  const res = await fetch(`${BASE}/api/v1/actions/brief`, { cache: "no-store" });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  return data.brief as string;
}

export async function decideAction(
  actionId: string,
  decision: "approve" | "reject",
): Promise<void> {
  const res = await fetch(`${BASE}/api/v1/actions/${actionId}/approve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ decision, approved_by: "operator" }),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
}

export interface SensorReading {
  time: string;
  [sensorType: string]: string | number;
}

export async function getSensorReadings(
  minutes = 60,
  line?: number,
): Promise<SensorReading[]> {
  const params = new URLSearchParams({ minutes: String(minutes) });
  if (line !== undefined) params.set("line", String(line));
  const res = await fetch(`${BASE}/api/v1/sensors/readings?${params}`, {
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  return data.data as SensorReading[];
}

export interface HistoryItem {
  shift: string;
  sensor_anomaly: number;
  pipeline_fix: number;
  shift_handover: number;
}

export async function getActionHistory(days = 7): Promise<HistoryItem[]> {
  const res = await fetch(`${BASE}/api/v1/actions/history?days=${days}`, {
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  return data.data as HistoryItem[];
}

export interface ActionStats {
  approved: number;
  rejected: number;
  executed: number;
  pending: number;
  execution_failed: number;
}

export async function getActionStats(): Promise<ActionStats> {
  const res = await fetch(`${BASE}/api/v1/actions/stats`, { cache: "no-store" });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}
