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
    mock_bq.query.return_value.result.return_value = None

    action_id = agent.write_pending_action(
        action_type="maintenance_email",
        payload={"subject": "Motor 2B alert"},
        proposed_by="investigator",
        bq_client=mock_bq,
    )

    assert mock_bq.query.called
    sql = mock_bq.query.call_args[0][0]
    assert "INSERT INTO" in sql
    assert "approved_actions" in sql

    params = {p.name: p.value for p in mock_bq.query.call_args[1]["job_config"].query_parameters}
    assert params["action_type"] == "maintenance_email"
    assert params["proposed_by"] == "investigator"
    assert params["action_id"] == action_id


def test_write_pending_raises_on_bq_error(agent):
    mock_bq = MagicMock()
    mock_bq.query.return_value.result.side_effect = Exception("insert failed")

    with pytest.raises(Exception, match="insert failed"):
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
