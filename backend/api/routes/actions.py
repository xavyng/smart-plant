import os
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from google.cloud import bigquery
from backend.api.dependencies import get_bq_client

router = APIRouter(prefix="/api/v1/actions")


def _table() -> str:
    return f"`{os.getenv('GCP_PROJECT_ID')}.{os.getenv('BIGQUERY_DATASET')}.approved_actions`"


class ApproveRequest(BaseModel):
    decision: str
    approved_by: str


@router.get("/pending")
def get_pending(bq: bigquery.Client = Depends(get_bq_client)):
    rows = list(bq.query(f"SELECT * FROM {_table()} WHERE status = 'pending' ORDER BY created_at ASC").result())
    return [dict(r) for r in rows]


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
