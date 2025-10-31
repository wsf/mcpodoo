
from fastapi import FastAPI
import json
from pathlib import Path

app = FastAPI()

@app.get("/")
def root():
    mcp_path = Path(__file__).resolve().parents[1] / "mcp.json"
    meta = {}
    try:
        meta = json.loads(mcp_path.read_text())
    except Exception:
        meta = {"name": "odoo-helpdesk-mcp"}
    return {"status": "ok", "mcp": meta.get("name"), "tools": [t["name"] for t in meta.get("tools", [])]}
