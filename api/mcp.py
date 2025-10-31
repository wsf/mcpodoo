
from fastapi import FastAPI, Request
from pydantic import BaseModel, Field
import os, json
from pathlib import Path
from utils.odoo import get_ticket_chatter, search_chatter, post_message

app = FastAPI()

class RunInput(BaseModel):
    tool: str = Field(..., description="Tool name (get_ticket_chatter | search_chatter | post_message)")
    args: dict = Field(default_factory=dict, description="Arguments for the tool")

def check_api_key(request: Request):
    key = request.headers.get("x-api-key")
    if key != os.environ.get("MCP_API_KEY"):
        return False
    return True

@app.get("/api/mcp/meta")
async def mcp_meta(request: Request):
    if not check_api_key(request):
        return {"error": "Invalid API Key"}
    mcp_path = Path(__file__).resolve().parents[1] / "mcp.json"
    try:
        return json.loads(mcp_path.read_text())
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/mcp/run")
async def mcp_run(request: Request, payload: RunInput):
    if not check_api_key(request):
        return {"error": "Invalid API Key"}

    try:
        tool = payload.tool
        args = payload.args or {}

        if tool == "get_ticket_chatter":
            ticket_id = int(args.get("ticket_id"))
            limit = int(args.get("limit", 50))
            data = get_ticket_chatter(ticket_id, limit)
            return {"ok": True, "tool": tool, "data": data}

        elif tool == "search_chatter":
            ticket_id = int(args.get("ticket_id"))
            query = str(args.get("query") or "")
            data = search_chatter(ticket_id, query)
            return {"ok": True, "tool": tool, "data": data}

        elif tool == "post_message":
            ticket_id = int(args.get("ticket_id"))
            body = str(args.get("body") or "")
            result = post_message(ticket_id, body)
            return {"ok": True, "tool": tool, "result": result}

        else:
            return {"error": f"Unknown tool: {tool}"}
    except Exception as e:
        return {"error": str(e)}
