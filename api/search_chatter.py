from fastapi import FastAPI, Request
from utils.odoo import search_chatter
import os

app = FastAPI()

@app.get("/api/search_chatter")
async def handler(request: Request):
    api_key = request.headers.get("x-api-key")
    if api_key != os.environ.get("MCP_API_KEY"):
        return {"error": "Invalid API Key"}
    
    ticket_id = request.query_params.get("ticket_id")
    query = request.query_params.get("query")

    if not ticket_id or not query:
        return {"error": "Missing ticket_id or query"}

    try:
        results = search_chatter(int(ticket_id), query)
        return {"results": results}
    except Exception as e:
        return {"error": str(e)}