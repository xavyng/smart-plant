from datetime import datetime, timezone, timedelta
from unittest.mock import patch


def _get_is_healthy():
    with patch.dict("os.environ", {
        "GCP_PROJECT_ID": "p", "BIGQUERY_DATASET": "d",
        "FIVETRAN_API_KEY": "k", "FIVETRAN_API_SECRET": "s", "FIVETRAN_CONNECTOR_ID": "c"
    }):
        from backend.agents.pipeline_health import is_pipeline_healthy
        return is_pipeline_healthy


def test_healthy_when_sync_recent():
    fn = _get_is_healthy()
    recent = (datetime.now(timezone.utc) - timedelta(minutes=2)).isoformat()
    healthy, reason = fn({"succeeded_at": recent})
    assert healthy is True
    assert reason == "ok"


def test_unhealthy_when_sync_stale():
    fn = _get_is_healthy()
    stale = (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat()
    healthy, reason = fn({"succeeded_at": stale})
    assert healthy is False
    assert "ago" in reason


def test_unhealthy_when_failed_at_present():
    fn = _get_is_healthy()
    healthy, reason = fn({"failed_at": "2026-06-07T10:00:00Z"})
    assert healthy is False
    assert "failed_at" in reason


def test_healthy_when_no_sync_info():
    fn = _get_is_healthy()
    healthy, reason = fn({})
    assert healthy is True
