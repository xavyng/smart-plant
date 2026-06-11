import os
import json
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from google.cloud import bigquery
from backend.api.dependencies import get_bq_client

router = APIRouter(prefix="/api/v1/actions")


def _table() -> str:
    return f"`{os.getenv('GCP_PROJECT_ID')}.{os.getenv('BIGQUERY_DATASET')}.approved_actions`"


class ApproveRequest(BaseModel):
    decision: str
    approved_by: str
    recipient: str | None = None
    subject_override: str | None = None
    body_override: str | None = None


@router.get("/pending")
def get_pending(bq: bigquery.Client = Depends(get_bq_client)):
    rows = list(bq.query(f"SELECT * FROM {_table()} WHERE status = 'pending' ORDER BY created_at ASC").result())
    result = []
    for r in rows:
        d = dict(r)
        if isinstance(d.get("payload"), str):
            try:
                d["payload"] = json.loads(d["payload"])
            except (ValueError, TypeError):
                pass
        result.append(d)
    return result


@router.post("/{action_id}/approve")
def approve_action(action_id: str, body: ApproveRequest, bq: bigquery.Client = Depends(get_bq_client)):
    if body.decision not in ("approve", "reject"):
        raise HTTPException(status_code=422, detail="decision must be 'approve' or 'reject'")

    cfg = bigquery.QueryJobConfig(query_parameters=[
        bigquery.ScalarQueryParameter("action_id", "STRING", action_id)
    ])
    rows = list(bq.query(
        f"SELECT status FROM {_table()} WHERE action_id = @action_id", job_config=cfg
    ).result())

    if not rows:
        raise HTTPException(status_code=404, detail="action not found")
    if rows[0]["status"] in ("executed", "rejected", "execution_failed"):
        raise HTTPException(status_code=409, detail=f"terminal state: {rows[0]['status']}")

    new_status = "approved" if body.decision == "approve" else "rejected"

    has_overrides = (
        body.decision == "approve"
        and any([body.recipient, body.subject_override, body.body_override])
    )

    if has_overrides:
        payload_cfg = bigquery.QueryJobConfig(query_parameters=[
            bigquery.ScalarQueryParameter("action_id", "STRING", action_id)
        ])
        payload_rows = list(bq.query(
            f"SELECT payload FROM {_table()} WHERE action_id = @action_id",
            job_config=payload_cfg,
        ).result())
        raw_payload = payload_rows[0]["payload"] if payload_rows else None
        try:
            payload = json.loads(raw_payload) if isinstance(raw_payload, str) else (raw_payload or {})
        except (ValueError, TypeError):
            payload = {}

        if body.recipient:
            payload["recipient"] = body.recipient
        if body.subject_override:
            payload["subject"] = body.subject_override
        if body.body_override:
            payload["body"] = body.body_override

        update_cfg = bigquery.QueryJobConfig(query_parameters=[
            bigquery.ScalarQueryParameter("status", "STRING", new_status),
            bigquery.ScalarQueryParameter("approved_by", "STRING", body.approved_by),
            bigquery.ScalarQueryParameter("payload", "STRING", json.dumps(payload)),
            bigquery.ScalarQueryParameter("action_id", "STRING", action_id),
        ])
        bq.query(
            f"UPDATE {_table()} SET status = @status, approved_by = @approved_by, payload = @payload WHERE action_id = @action_id",
            job_config=update_cfg,
        ).result()
    else:
        update_cfg = bigquery.QueryJobConfig(query_parameters=[
            bigquery.ScalarQueryParameter("status", "STRING", new_status),
            bigquery.ScalarQueryParameter("approved_by", "STRING", body.approved_by),
            bigquery.ScalarQueryParameter("action_id", "STRING", action_id),
        ])
        bq.query(
            f"UPDATE {_table()} SET status = @status, approved_by = @approved_by WHERE action_id = @action_id",
            job_config=update_cfg,
        ).result()

    return {"action_id": action_id, "status": new_status}


from backend.agents.briefing import BriefingAgent


@router.get("/brief")
def get_brief():
    return {"brief": BriefingAgent().brief()}


@router.get("/history")
def get_action_history(
    days: int = Query(7, ge=1, le=30),
    bq: bigquery.Client = Depends(get_bq_client),
):
    rows = list(bq.query(f"""
        SELECT
          action_type,
          CASE
            WHEN EXTRACT(HOUR FROM created_at) >= 6
             AND EXTRACT(HOUR FROM created_at) < 14 THEN 'M'
            WHEN EXTRACT(HOUR FROM created_at) >= 14
             AND EXTRACT(HOUR FROM created_at) < 22 THEN 'A'
            ELSE 'N'
          END AS shift_code,
          FORMAT_DATE('%a', DATE(created_at)) AS day_name,
          DATE(created_at) AS date_val
        FROM {_table()}
        WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
        ORDER BY date_val ASC, shift_code ASC
    """).result())

    pivoted: dict[str, dict] = {}
    for row in rows:
        key = f"{row['shift_code']}-{row['day_name']}"
        if key not in pivoted:
            pivoted[key] = {
                "shift": key,
                "sensor_anomaly": 0,
                "pipeline_fix": 0,
                "shift_handover": 0,
            }
        action_type = row["action_type"]
        if action_type in pivoted[key]:
            pivoted[key][action_type] += 1

    return {"data": list(pivoted.values())[-14:]}


@router.get("/stats")
def get_action_stats(bq: bigquery.Client = Depends(get_bq_client)):
    rows = list(bq.query(f"""
        SELECT status, COUNT(*) AS count
        FROM {_table()}
        WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
        GROUP BY status
    """).result())

    stats = {
        "approved": 0,
        "rejected": 0,
        "executed": 0,
        "pending": 0,
        "execution_failed": 0,
    }
    for row in rows:
        if row["status"] in stats:
            stats[row["status"]] = int(row["count"])
    return stats
