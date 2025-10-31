from fastapi import FastAPI, Request
from utils.odoo import post_message
import os

app = FastAPI()

@app.post("/api/post_message")
async def handler(request: Request):
    api_key = request.headers.get("x-api-key")
    if api_key != os.environ.get("MCP_API_KEY"):
        return {"error": "Invalid API Key"}

    data = await request.json()
    ticket_id = data.get("ticket_id")
    body = data.get("body")

    if not ticket_id or not body:
        return {"error": "Missing fields"}

    try:
        result = post_message(int(ticket_id), body)
        return {"status": "posted", "result": result}
    except Exception as e:
        return {"error": str(e)}