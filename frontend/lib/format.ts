import { type PendingAction } from "@/lib/api";

type P = Record<string, unknown>;
const str = (v: unknown): string | null => (typeof v === "string" && v ? v : null);

export function getActionBody(action: PendingAction): string {
  const p = action.payload as P;
  const atype = action.action_type.toLowerCase();

  const direct =
    str(p.diagnosis) ??
    str(p.body) ??
    str(p.description) ??
    str(p.summary) ??
    str(p.message);
  if (direct) return direct;

  const details = p.details as P | undefined;
  if (details) {
    const msg = str(details.message);
    if (msg) return msg;
  }

  if (atype === "pipeline_fix" || atype === "investigate_pipeline_failure") {
    const connector = str(p.connector_id) ?? "unknown";
    const reason = str(p.reason) ?? "unknown reason";
    const last = str(p.last_succeeded_at);
    const lastLine = last
      ? `\nLast successful sync: ${new Date(last).toLocaleString("en-US", {
          month: "short", day: "numeric", year: "numeric",
          hour: "2-digit", minute: "2-digit", timeZone: "UTC", timeZoneName: "short",
        })}`
      : "";
    return `Connector "${connector}" has stopped syncing.\nReason: ${reason}${lastLine}`;
  }

  if (atype === "sensor_anomaly" || atype === "investigate_sensor_anomaly" || atype === "maintenance_email") {
    const target = str(p.target) ?? str(p.sensor_name) ?? "unknown sensor";
    const reason = str(p.reason) ?? "";
    return reason ? `${target} — ${reason}` : `Anomaly detected on ${target}`;
  }

  if (str(p.reason)) {
    const target = str(p.target);
    return target ? `${target} — ${p.reason}` : String(p.reason);
  }

  return JSON.stringify(action.payload, null, 2);
}

export function getActionTitle(action: PendingAction): string {
  const p = action.payload as P;
  if (str(p.subject)) return p.subject as string;
  const atype = action.action_type.toLowerCase();
  if (atype === "sensor_anomaly" || atype === "investigate_sensor_anomaly" || atype === "maintenance_email") {
    const target = str(p.target) ?? str(p.sensor_name);
    return target ? `Sensor Anomaly — ${target}` : "Sensor Anomaly Detected";
  }
  if (atype === "pipeline_fix" || atype === "investigate_pipeline_failure") {
    const connector = str(p.connector_id);
    return connector ? `Pipeline Failure — ${connector}` : "Pipeline Fix Required";
  }
  return "Action Required";
}
