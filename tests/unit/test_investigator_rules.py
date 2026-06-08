from unittest.mock import patch, MagicMock


def _get_has_anomaly():
    with patch.dict("os.environ", {"GCP_PROJECT_ID": "p", "BIGQUERY_DATASET": "d",
                                    "VERTEX_AI_PROJECT": "p"}):
        with patch("vertexai.init"), patch("backend.agents.investigator.GenerativeModel"):
            from backend.agents.investigator import has_anomaly
            return has_anomaly


def test_has_anomaly_false_for_all_normal():
    has_anomaly = _get_has_anomaly()
    assert has_anomaly([{"status": "normal"}, {"status": "normal"}]) is False


def test_has_anomaly_true_for_warning():
    has_anomaly = _get_has_anomaly()
    assert has_anomaly([{"status": "normal"}, {"status": "warning"}]) is True


def test_has_anomaly_true_for_critical():
    has_anomaly = _get_has_anomaly()
    assert has_anomaly([{"status": "critical"}]) is True


def test_has_anomaly_false_for_empty():
    has_anomaly = _get_has_anomaly()
    assert has_anomaly([]) is False


@patch("backend.agents.investigator.query_recent_readings")
def test_investigate_returns_none_when_all_normal(mock_query):
    mock_query.return_value = [{"status": "normal"}]
    with patch.dict("os.environ", {"GCP_PROJECT_ID": "p", "BIGQUERY_DATASET": "d",
                                    "VERTEX_AI_PROJECT": "p"}):
        with patch("vertexai.init"), patch("backend.agents.investigator.GenerativeModel") as MockModel:
            from backend.agents.investigator import InvestigatorAgent
            agent = InvestigatorAgent()
            result = agent.investigate()
    assert result is None
    MockModel.return_value.generate_content.assert_not_called()
