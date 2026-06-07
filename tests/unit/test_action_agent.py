import json
import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def agent():
    with patch.dict("os.environ", {"GCP_PROJECT_ID": "p", "BIGQUERY_DATASET": "d"}):
        from backend.agents.action_agent import ActionAgent
        return ActionAgent()


def test_write_pending_inserts_correct_row(agent):
    mock_bq = MagicMock()
    mock_bq.insert_rows_json.return_value = []

    action_id = agent.write_pending_action(
        action_type="maintenance_email",
        payload={"subject": "Motor 2B alert"},
        proposed_by="investigator",
        bq_client=mock_bq,
    )

    assert mock_bq.insert_rows_json.called
    row = mock_bq.insert_rows_json.call_args[0][1][0]
    assert row["action_type"] == "maintenance_email"
    assert row["status"] == "pending"
    assert row["proposed_by"] == "investigator"
    assert action_id == row["action_id"]


def test_write_pending_raises_on_bq_error(agent):
    mock_bq = MagicMock()
    mock_bq.insert_rows_json.return_value = [{"error": "insert failed"}]

    with pytest.raises(RuntimeError, match="BQ write failed"):
        agent.write_pending_action(
            action_type="maintenance_email",
            payload={"subject": "test"},
            proposed_by="investigator",
            bq_client=mock_bq,
        )


def test_poll_once_executes_approved_row(agent):
    mock_bq = MagicMock()
    mock_bq.query.return_value.result.side_effect = [
        [{"action_id": "xyz-789", "action_type": "maintenance_email",
          "payload": json.dumps({"subject": "Alert"}), "status": "approved",
          "proposed_by": "investigator", "approved_by": "xavier",
          "created_at": "2026-06-07T10:00:00+00:00", "executed_at": None}],
        [],
    ]
    executed = agent._poll_once(bq_client=mock_bq)
    assert "xyz-789" in executed
    update_sql = mock_bq.query.call_args_list[1][0][0]
    assert "executed" in update_sql


def test_poll_once_returns_empty_when_no_approved(agent):
    mock_bq = MagicMock()
    mock_bq.query.return_value.result.return_value = []
    assert agent._poll_once(bq_client=mock_bq) == []
