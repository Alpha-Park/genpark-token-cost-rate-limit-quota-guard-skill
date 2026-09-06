"""
MCP Server for genpark-token-cost-rate-limit-quota-guard-skill
Standard JSON-RPC 2.0 protocol over stdio.
"""

import sys
import json
from client import TokenCostQuotaGuardClient

client = TokenCostQuotaGuardClient()

def handle_request(req):
    req_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "check_rate_limit",
                        "description": "Evaluate sliding-window RPM and TPM quota.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "tenant_id": {"type": "string"},
                                "max_rpm": {"type": "integer"},
                                "max_tpm": {"type": "integer"}
                            },
                            "required": ["tenant_id"]
                        }
                    },
                    {
                        "name": "record_usage",
                        "description": "Record LLM token consumption and check spending limits.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "tenant_id": {"type": "string"},
                                "model": {"type": "string"},
                                "prompt_tokens": {"type": "integer"},
                                "completion_tokens": {"type": "integer"}
                            },
                            "required": ["tenant_id", "model", "prompt_tokens", "completion_tokens"]
                        }
                    }
                ]
            }
        }
    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})
        if tool_name == "check_rate_limit":
            res = client.check_rate_limit(args.get("tenant_id", ""), args.get("max_rpm", 60), args.get("max_tpm", 100000))
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}}
        elif tool_name == "record_usage":
            res = client.record_usage(args.get("tenant_id", ""), args.get("model", ""), args.get("prompt_tokens", 0), args.get("completion_tokens", 0))
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}}
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = handle_request(req)
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(e)}}
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
