from unittest.mock import MagicMock, patch
import pytest


@patch("backend.tools.bigquery_tool._get_client")
def test_insert_readings_calls_insert_rows_json(mock_get_client):
    mock_client = MagicMock()
    mock_client.insert_rows_json.return_value = []
    mock_get_client.return_value = mock_client

    from backend.tools.bigquery_tool import insert_readings
    rows = [{"id": "test1", "line_number": 1, "sensor_name": "motor_1a_temperature",
             "sensor_type": "temperature", "value": 72.0, "unit": "celsius",
             "timestamp": "2026-05-30T10:00:00Z", "status": "normal"}]
    insert_readings(rows)

    mock_client.insert_rows_json.assert_called_once()
    call_args = mock_client.insert_rows_json.call_args
    assert call_args[0][1] == rows


@patch("backend.tools.bigquery_tool._get_client")
def test_insert_readings_prints_on_error(mock_get_client, capsys):
    mock_client = MagicMock()
    mock_client.insert_rows_json.return_value = [{"errors": ["something failed"]}]
    mock_get_client.return_value = mock_client

    from backend.tools.bigquery_tool import insert_readings
    insert_readings([{"id": "bad"}])

    captured = capsys.readouterr()
    assert "bigquery insert errors" in captured.out


@patch("backend.tools.bigquery_tool._get_client")
def test_query_recent_readings_returns_list_of_dicts(mock_get_client):
    mock_client = MagicMock()
    mock_row = {"id": "r1", "line_number": 2, "sensor_name": "motor_2b_vibration",
                "sensor_type": "vibration", "value": 9.1, "unit": "mm/s",
                "timestamp": "2026-05-30T10:00:00Z", "status": "critical"}
    mock_client.query.return_value.result.return_value = [mock_row]
    mock_get_client.return_value = mock_client

    from backend.tools.bigquery_tool import query_recent_readings
    result = query_recent_readings(minutes=10)

    assert isinstance(result, list)
    assert result[0]["sensor_name"] == "motor_2b_vibration"


@patch("backend.tools.bigquery_tool._get_client")
def test_query_recent_readings_uses_parameterized_query(mock_get_client):
    mock_client = MagicMock()
    mock_client.query.return_value.result.return_value = []
    mock_get_client.return_value = mock_client

    from backend.tools.bigquery_tool import query_recent_readings
    query_recent_readings(minutes=15)

    call_kwargs = mock_client.query.call_args[1]
    params = call_kwargs["job_config"].query_parameters
    assert any(p.value == 15 for p in params)
