import json
from unittest.mock import MagicMock, patch, call


@patch("scripts.mqtt_to_bigquery.insert_readings")
def test_on_message_inserts_valid_payload(mock_insert):
    from scripts.mqtt_to_bigquery import on_message

    payload = {
        "id": "reading_1_temperature",
        "line_number": 1,
        "sensor_name": "motor_1a_temperature",
        "sensor_type": "temperature",
        "value": 72.5,
        "unit": "celsius",
        "timestamp": "2026-05-30T10:00:00Z",
        "status": "normal"
    }
    msg = MagicMock()
    msg.payload = json.dumps(payload).encode()

    on_message(None, None, msg)

    mock_insert.assert_called_once_with([payload])


@patch("scripts.mqtt_to_bigquery.insert_readings")
def test_on_message_prints_confirmation(mock_insert, capsys):
    from scripts.mqtt_to_bigquery import on_message

    mock_insert.return_value = None
    payload = {
        "id": "r1", "line_number": 2, "sensor_name": "motor_2b_vibration",
        "sensor_type": "vibration", "value": 9.1, "unit": "mm/s",
        "timestamp": "2026-05-30T10:00:00Z", "status": "critical"
    }
    msg = MagicMock()
    msg.payload = json.dumps(payload).encode()

    on_message(None, None, msg)

    captured = capsys.readouterr()
    assert "motor_2b_vibration" in captured.out
    assert "line 2" in captured.out


@patch("scripts.mqtt_to_bigquery.insert_readings")
def test_on_message_handles_bad_json_gracefully(mock_insert, capsys):
    from scripts.mqtt_to_bigquery import on_message

    msg = MagicMock()
    msg.payload = b"not valid json"

    on_message(None, None, msg)

    mock_insert.assert_not_called()
    captured = capsys.readouterr()
    assert "error" in captured.out


def test_on_connect_subscribes_to_topic(capsys):
    from scripts.mqtt_to_bigquery import on_connect, TOPIC_PREFIX

    mock_client = MagicMock()
    on_connect(mock_client, None, None, 0)

    mock_client.subscribe.assert_called_once_with(f"{TOPIC_PREFIX}/#")
    captured = capsys.readouterr()
    assert "subscribing" in captured.out
