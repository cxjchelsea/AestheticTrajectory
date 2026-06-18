"""Optional local stdio MCP server exposing read-only internal tool names.

This is a thin protocol shell for V4-D debugging. Tool execution still happens
through the FastAPI observation service in production paths.
"""

from __future__ import annotations

import json
import sys

TOOL_CATALOG = [
    {
        "name": "list_reports",
        "description": "List recent aesthetic analysis reports for a user.",
        "inputSchema": {"type": "object", "properties": {"userId": {"type": "string"}}, "required": ["userId"]},
    },
    {
        "name": "get_report",
        "description": "Fetch one report by id.",
        "inputSchema": {
            "type": "object",
            "properties": {"reportId": {"type": "string"}},
            "required": ["reportId"],
        },
    },
    {
        "name": "get_timeline_summary",
        "description": "Get timeline summary for week or month.",
        "inputSchema": {
            "type": "object",
            "properties": {"userId": {"type": "string"}, "period": {"type": "string"}},
            "required": ["userId"],
        },
    },
    {
        "name": "list_external_context",
        "description": "List user-confirmed external context items.",
        "inputSchema": {"type": "object", "properties": {"userId": {"type": "string"}}, "required": ["userId"]},
    },
]


def _response(request_id, result) -> dict:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _error(request_id, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": message}}


def handle_message(message: dict) -> dict:
    request_id = message.get("id")
    method = message.get("method")
    if method == "initialize":
        return _response(
            request_id,
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "aesthetic-internal-tools", "version": "0.1.0"},
            },
        )
    if method == "tools/list":
        return _response(request_id, {"tools": TOOL_CATALOG})
    if method == "tools/call":
        params = message.get("params") or {}
        tool_name = params.get("name")
        return _response(
            request_id,
            {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(
                            {
                                "toolName": tool_name,
                                "note": "stdio MCP shell only; call FastAPI observation service for execution.",
                                "arguments": params.get("arguments") or {},
                            },
                            ensure_ascii=False,
                        ),
                    }
                ]
            },
        )
    return _error(request_id, f"Unsupported method: {method}")


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        message = json.loads(line)
        sys.stdout.write(json.dumps(handle_message(message), ensure_ascii=False) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
