from fastapi import FastAPI, Request
from utils.odoo import get_ticket_chatter
import os

app = FastAPI()

@app.get("/api/get_ticket_chatter")
async def handler(request: Request):
    api_key = request.headers.get("x-api-key")
    if api_key != os.environ.get("MCP_API_KEY"):
        return {"error": "Invalid API Key"}

    ticket_id = request.query_params.get("ticket_id")
    if not ticket_id:
        return {"error": "Missing ticket_id"}

    try:
        ticket_id = int(ticket_id)
        messages = get_ticket_chatter(ticket_id)
        return {"ticket_id": ticket_id, "count": len(messages), "messages": messages}
    except Exception as e:
        return {"error": str(e)}