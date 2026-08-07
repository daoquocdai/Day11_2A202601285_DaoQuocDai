"""
Assignment 11 — Audit Log starter (TODO).

Records every interaction for forensics. Never blocks by itself —
other layers catch attacks; this layer makes them reviewable.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone


class AuditLogPlugin:
    """Framework-agnostic audit logger (wire into ADK callbacks or your pipeline)."""

    def __init__(self):
        self.name = "audit_log"
        self.logs: list[dict] = []
        self._open: dict[str, dict] = {}

    def record_input(self, *, user_id: str, text: str, request_id: str | None = None) -> str:
        """Store input + start timestamp keyed by request_id/user_id."""
        req_id = request_id or f"REQ-{user_id}-{len(self.logs)+1:04d}"
        self._open[req_id] = {
            "text": text,
            "start_time": datetime.now(timezone.utc).timestamp(),
        }
        return req_id

    def record_output(
        self,
        *,
        user_id: str,
        text: str,
        blocked: bool = False,
        layer: str | None = None,
        request_id: str | None = None,
        reviewer_decision: str | None = None,
    ):
        """Store output, layer decision, latency; append to self.logs."""
        req_id = request_id or f"REQ-{user_id}-{len(self.logs)+1:04d}"
        open_data = self._open.pop(req_id, {})
        start = open_data.get("start_time", datetime.now(timezone.utc).timestamp())
        input_text = open_data.get("text", "")
        latency = round((datetime.now(timezone.utc).timestamp() - start) * 1000, 2)
        entry = {
            "request_id": req_id,
            "user_id": user_id,
            "timestamp": utc_now_iso(),
            "input": input_text,
            "response_preview": text[:300] if text else "",
            "blocked": blocked,
            "layer": layer,
            "reviewer_decision": reviewer_decision or ("BLOCKED" if blocked else "APPROVED"),
            "latency_ms": latency,
        }
        self.logs.append(entry)

    def export_json(self, filepath: str = "outputs/audit_log.json"):
        """Write logs to disk (JSON array)."""
        from pathlib import Path
        p = Path(filepath)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.logs, ensure_ascii=False, indent=2), encoding="utf-8")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
