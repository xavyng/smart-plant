from unittest.mock import MagicMock, patch


def _make_agent():
    with patch("backend.agents.investigator.genai.Client"):
        from backend.agents.investigator import InvestigatorAgent
        return InvestigatorAgent()


def test_format_readings_empty():
    agent = _make_agent()
    result = agent._format_readings([])
    assert result == "No readings available."


def test_format_readings_includes_sensor_fields():
    agent = _make_agent()
    readings = [{"line_number": 2, "sensor_name": "motor_2b_vibration",
                 "sensor_type": "vibration", "value": 9.1,
                 "unit": "mm/s", "status": "critical"}]
    result = agent._format_readings(readings)
    assert "Line 2" in result
    assert "motor_2b_vibration" in result
    assert "9.1" in result
    assert "critical" in result


def test_build_prompt_contains_readings():
    agent = _make_agent()
    readings = [{"line_number": 1, "sensor_name": "motor_1a_temperature",
                 "sensor_type": "temperature", "value": 72.0,
                 "unit": "celsius", "status": "normal"}]
    prompt = agent._build_prompt(readings)
    assert "plant manager" in prompt
    assert "motor_1a_temperature" in prompt


def test_build_prompt_with_no_readings():
    agent = _make_agent()
    prompt = agent._build_prompt([])
    assert "No readings available" in prompt


@patch("backend.agents.investigator.query_recent_readings")
def test_investigate_calls_gemini_and_returns_finding(mock_query):
    readings = [
        {"line_number": 2, "sensor_name": "motor_2b_vibration",
         "sensor_type": "vibration", "value": 9.1,
         "unit": "mm/s", "status": "critical"}
    ]
    mock_query.return_value = readings
    with patch("backend.agents.investigator.genai.Client") as MockClient, \
         patch("backend.agents.orchestrator.handle_event"):
        mock_response = MagicMock()
        mock_response.text = "Line 2 vibration is critical. Bearing failure likely."
        MockClient.return_value.models.generate_content.return_value = mock_response

        from backend.agents.investigator import InvestigatorAgent
        agent = InvestigatorAgent()
        result = agent.investigate()

    assert result["diagnosis"] == "Line 2 vibration is critical. Bearing failure likely."
    assert result["source"] == "investigator"
    mock_query.assert_called_once_with(minutes=15)
