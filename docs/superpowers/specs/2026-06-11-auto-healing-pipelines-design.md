---
title: Auto-Healing Pipelines
date: 2026-06-11
status: approved
---

# Auto-Healing Pipelines

## Summary

When a human approves a `pipeline_fix` action in the HITL dashboard, the `ActionAgent` now calls the Fivetran REST API to attempt an automated repair (unpause if needed, then force-sync), then sends a confirmation email with the repair outcome. No changes to detection, forensics, orchestrator, or HITL flow.

---

## Scope

**In scope:**
- New `_repair_connector(connector_id, connector_status) -> tuple[bool, str]` function in `action_agent.py`
- Updated `_execute_action` branch for `pipeline_fix` / `investigate_pipeline_failure`
- Updated `_compose_email_body` to render repair outcome
- Unit tests for `_repair_connector`

**Out of scope:**
- Bypassing HITL — repair only runs after human approval
- Changes to `PipelineHealthAgent`, `PipelineForensicsAgent`, or orchestrator
- Fivetran MCP integration (uses REST API directly, consistent with `pipeline_health.py`)

---

## Data Flow

```
[human approves pipeline_fix in dashboard]
         |
ActionAgent._poll_once() picks up approved row
         |
_execute_action(row)
         |
_repair_connector(connector_id, connector_status)
  |- if paused: PATCH /v1/connectors/{id}  {"paused": false}
  +- POST /v1/connectors/{id}/force
         |
_send_email(recipient, subject, body)   <- always, outcome-aware
```

---

## `_repair_connector` Function

**Signature:** `_repair_connector(connector_id: str, connector_status: dict) -> tuple[bool, str]`

**Unpause step:**
- If `connector_status.get("paused")` is truthy, calls `PATCH /v1/connectors/{connector_id}` with `{"paused": false}`.
- On failure: returns `(False, "unpause failed: <error>")` immediately — skip force-sync.

**Force-sync step:**
- Calls `POST /v1/connectors/{connector_id}/force`.
- On failure: returns `(False, "sync trigger failed: <error>")`.

**Success return values:**
- Unpaused + synced: `(True, "repair triggered: unpaused + sync forced")`
- Sync only: `(True, "repair triggered: sync forced")`

**Auth:** requires two new module-level variables in `action_agent.py` — `_FIVETRAN_API_KEY = os.getenv("FIVETRAN_API_KEY")` and `_FIVETRAN_API_SECRET = os.getenv("FIVETRAN_API_SECRET")`. Same 10s timeout as `pipeline_health.py`. Uses `requests` (already imported).

**Connector ID resolution** (in `_execute_action`):
```
payload["connector_id"]
  ?? payload["connector_status"]["id"]
  ?? FIVETRAN_CONNECTOR_ID env var
```

---

## `_execute_action` Changes

The `pipeline_action_types` branch becomes:

1. Resolve `connector_id` from payload using the priority chain above.
2. Call `_repair_connector(connector_id, connector_status)` → `(success, repair_msg)`.
3. Inject `repair_result` and `repair_success` keys into payload.
4. Set email subject: `[Pipeline Repaired]` if success, `[Pipeline Repair Failed]` otherwise.
5. Call `_compose_email_body` (now renders repair section) then `_send_email`.

Email is always sent regardless of repair outcome.

---

## Email Changes

`_compose_email_body` for `pipeline_fix` / `investigate_pipeline_failure` gains a **Repair Attempt** section:

```
Repair Attempt:
  Status: Successful   (or: Failed)
  Detail: repair triggered: unpaused + sync forced
```

Rendered using `payload["repair_result"]` and `payload["repair_success"]`. If these keys are absent (legacy rows without repair), the section is omitted gracefully.

---

## Error Handling

| Scenario | Behaviour |
|---|---|
| Unpause API call fails | Return `(False, "unpause failed: ...")`, skip force-sync, email sent with failure detail |
| Force-sync API call fails | Return `(False, "sync trigger failed: ...")`, email sent with failure detail |
| Both calls succeed | Return `(True, ...)`, email sent with success detail |
| `connector_id` cannot be resolved | Return `(False, "no connector_id available")`, email sent |

The existing `execution_failed` BigQuery status is set by `_poll_once` if `_execute_action` raises — `_repair_connector` does not raise, it returns `(False, ...)` so the action always progresses to `executed` status even on repair failure.

---

## Testing

New unit tests in `tests/unit/test_action_agent.py`:

- `test_repair_connector_success_sync_only` — connector not paused, force-sync succeeds → `(True, "repair triggered: sync forced")`
- `test_repair_connector_success_unpause_and_sync` — connector paused, both calls succeed → `(True, "repair triggered: unpaused + sync forced")`
- `test_repair_connector_unpause_fails` — connector paused, PATCH fails → `(False, "unpause failed: ...")`, POST not called
- `test_repair_connector_sync_fails` — connector not paused, POST fails → `(False, "sync trigger failed: ...")`
- `test_execute_action_pipeline_fix_sends_email_on_success` — end-to-end mock: approved `pipeline_fix` row → repair succeeds → email sent with `[Pipeline Repaired]` subject
- `test_execute_action_pipeline_fix_sends_email_on_failure` — repair fails → email still sent with `[Pipeline Repair Failed]` subject

All tests mock `requests.patch`, `requests.post`, and `smtplib.SMTP_SSL`.

---

## Difficulty

Low-to-medium. The Fivetran API calls are already proven in `scripts/unpause_connector.py` and `scripts/trigger_sync.py`. Total new code is approximately 40-50 lines (function + `_execute_action` changes + email section). No new dependencies, no schema changes, no new files.
