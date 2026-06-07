import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient


@pytest.fixture
def client_and_bq():
    mock_bq = MagicMock()
    with patch.dict("os.environ", {"GCP_PROJECT_ID": "test-proj", "BIGQUERY_DATASET": "test_ds"}):
        from backend.api.main import app
        from backend.api.dependencies import get_bq_client
        app.dependency_overrides[get_bq_client] = lambda: mock_bq
        yield TestClient(app), mock_bq
        app.dependency_overrides.clear()


def test_pending_returns_empty_list(client_and_bq):
    client, mock_bq = client_and_bq
    mock_bq.query.return_value.result.return_value = []
    response = client.get("/api/v1/actions/pending")
    assert response.status_code == 200
    assert response.json() == []


def test_pending_returns_rows(client_and_bq):
    client, mock_bq = client_and_bq
    mock_bq.query.return_value.result.return_value = [{
        "action_id": "abc-123", "action_type": "maintenance_email",
        "payload": '{"subject": "Alert"}', "status": "pending",
        "proposed_by": "investigator", "approved_by": None,
        "created_at": "2026-06-07T10:00:00+00:00", "executed_at": None,
    }]
    response = client.get("/api/v1/actions/pending")
    assert response.status_code == 200
    assert response.json()[0]["action_id"] == "abc-123"


def test_approve_returns_approved(client_and_bq):
    client, mock_bq = client_and_bq
    mock_bq.query.return_value.result.side_effect = [
        [{"status": "pending"}],
        [],
    ]
    response = client.post(
        "/api/v1/actions/abc-123/approve",
        json={"decision": "approve", "approved_by": "xavier"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "approved"


def test_reject_returns_rejected(client_and_bq):
    client, mock_bq = client_and_bq
    mock_bq.query.return_value.result.side_effect = [
        [{"status": "pending"}],
        [],
    ]
    response = client.post(
        "/api/v1/actions/abc-123/approve",
        json={"decision": "reject", "approved_by": "xavier"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "rejected"


def test_approve_nonexistent_returns_404(client_and_bq):
    client, mock_bq = client_and_bq
    mock_bq.query.return_value.result.return_value = []
    response = client.post(
        "/api/v1/actions/ghost/approve",
        json={"decision": "approve", "approved_by": "xavier"},
    )
    assert response.status_code == 404


def test_approve_executed_returns_409(client_and_bq):
    client, mock_bq = client_and_bq
    mock_bq.query.return_value.result.return_value = [{"status": "executed"}]
    response = client.post(
        "/api/v1/actions/abc-123/approve",
        json={"decision": "approve", "approved_by": "xavier"},
    )
    assert response.status_code == 409
