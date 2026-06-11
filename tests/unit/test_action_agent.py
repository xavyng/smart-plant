import sys
import json
import pytest
from unittest.mock import MagicMock, patch

# google-cloud-bigquery is not installed in the local dev environment;
# stub it so action_agent can be imported in tests.
_bq_mock = MagicMock()

def _scalar_param(name, type_, value):
    m = MagicMock()
    m.name = name
    m.value = value
    return m

def _query_job_config(**kwargs):
    m = MagicMock()
    m.query_parameters = kwargs.get("query_parameters", [])
    return m

_bq_mock.ScalarQueryParameter.side_effect = _scalar_param
_bq_mock.QueryJobConfig.side_effect = _query_job_config
sys.modules.setdefault("google.cloud.bigquery", _bq_mock)
sys.modules.setdefault("google.cloud", MagicMock(bigquery=_bq_mock))


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


@patch("backend.agents.action_agent._send_email")
def test_poll_once_executes_approved_row(mock_send, agent):
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


# _repair_connector tests

def test_repair_connector_success_sync_only():
    from backend.agents.action_agent import _repair_connector
    with patch("requests.post") as mock_post:
        mock_post.return_value.raise_for_status.return_value = None
        success, msg = _repair_connector("conn123", {"paused": False})
    assert success is True
    assert msg == "repair triggered: sync forced"
    assert "/force" in mock_post.call_args[0][0]


def test_repair_connector_success_unpause_and_sync():
    from backend.agents.action_agent import _repair_connector
    with patch("requests.patch") as mock_patch, patch("requests.post") as mock_post:
        mock_patch.return_value.raise_for_status.return_value = None
        mock_post.return_value.raise_for_status.return_value = None
        success, msg = _repair_connector("conn123", {"paused": True})
    assert success is True
    assert msg == "repair triggered: unpaused + sync forced"
    mock_patch.assert_called_once()
    mock_post.assert_called_once()


def test_repair_connector_unpause_fails():
    from backend.agents.action_agent import _repair_connector
    with patch("requests.patch") as mock_patch, patch("requests.post") as mock_post:
        mock_patch.return_value.raise_for_status.side_effect = Exception("403 Forbidden")
        success, msg = _repair_connector("conn123", {"paused": True})
    assert success is False
    assert "unpause failed" in msg
    mock_post.assert_not_called()


def test_repair_connector_sync_fails():
    from backend.agents.action_agent import _repair_connector
    with patch("requests.post") as mock_post:
        mock_post.return_value.raise_for_status.side_effect = Exception("503 Service Unavailable")
        success, msg = _repair_connector("conn123", {"paused": False})
    assert success is False
    assert "sync trigger failed" in msg


# _execute_action integration tests

@patch("backend.agents.action_agent._send_email")
@patch("requests.post")
def test_execute_action_pipeline_fix_sends_email_on_success(mock_post, mock_email):
    from backend.agents.action_agent import _execute_action
    mock_post.return_value.raise_for_status.return_value = None
    row = {
        "action_id": "abc-123",
        "action_type": "pipeline_fix",
        "payload": json.dumps({
            "subject": "Pipeline failure",
            "connector_id": "conn456",
            "connector_status": {"paused": False, "id": "conn456"},
            "reason": "sync stale",
        }),
    }
    _execute_action(row)
    mock_email.assert_called_once()
    subject = mock_email.call_args[0][1]
    assert "[Pipeline Repaired]" in subject


@patch("backend.agents.action_agent._send_email")
@patch("requests.post")
def test_execute_action_pipeline_fix_sends_email_on_failure(mock_post, mock_email):
    from backend.agents.action_agent import _execute_action
    mock_post.return_value.raise_for_status.side_effect = Exception("503")
    row = {
        "action_id": "abc-456",
        "action_type": "pipeline_fix",
        "payload": json.dumps({
            "subject": "Pipeline failure",
            "connector_id": "conn456",
            "connector_status": {"paused": False, "id": "conn456"},
            "reason": "sync stale",
        }),
    }
    _execute_action(row)
    mock_email.assert_called_once()
    subject = mock_email.call_args[0][1]
    assert "[Pipeline Repair Failed]" in subject
