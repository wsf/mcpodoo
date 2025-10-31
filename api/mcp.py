
from fastapi import FastAPI, Request
from pydantic import BaseModel
import os, json, xmlrpc.client, datetime
from pathlib import Path

app = FastAPI()

def _ok(req: Request):
    return req.headers.get("x-api-key") == os.environ.get("MCP_API_KEY")

def _odoo_env():
    url = os.environ.get("ODOO_URL")
    db = os.environ.get("ODOO_DB")
    user = os.environ.get("ODOO_USER")
    pwd = os.environ.get("ODOO_PASS")
    if not all([url, db, user, pwd]):
        raise Exception("Faltan ODOO_URL/DB/USER/PASS")
    return url, db, user, pwd

class Run(BaseModel):
    tool: str
    args: dict = {}

@app.get("/")
def health():
    return {"status": "ok", "service": "odoo-helpdesk-mcp"}

@app.get("/api/mcp/meta")
def meta(request: Request):
    if not _ok(request):
        return {"error": "Invalid API Key"}
    p = Path(__file__).resolve().parents[1] / "mcp.json"
    try:
        return json.loads(p.read_text())
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/mcp/run")
def run(request: Request, body: Run):
    if not _ok(request):
        return {"error": "Invalid API Key"}
    try:
        t = body.tool
        a = body.args or {}
        if t == "add":
            return {"ok": True, "data": int(a.get("a")) + int(a.get("b"))}

        if t == "odoo_search":
            url, db, user, pwd = _odoo_env()
            common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
            uid = common.authenticate(db, user, pwd, {})
            models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
            data = models.execute_kw(db, uid, pwd, a["model"], "search_read", [a.get("domain", [])], {"fields": a.get("fields", [])})
            return {"ok": True, "data": data}

        if t == "crear_solicitud_mantenimiento":
            url, db, user, pwd = _odoo_env()
            common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
            uid = common.authenticate(db, user, pwd, {})
            models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
            request_date = a.get("request_date") or datetime.date.today().isoformat()
            payload = {
                "name": a["name"],
                "description": a.get("description", ""),
                "request_date": request_date,
                "maintenance_type": "corrective",
                "company_id": 1,
                "maintenance_team_id": 2
            }
            try:
                new_id = models.execute_kw(db, uid, pwd, "maintenance.request", "create", [payload])
                return {"ok": True, "data": {"id": new_id, **payload}}
            except Exception as e:
                return {"ok": False, "error": str(e)}

        if t == "mantenimiento_con_compras":
            url, db, user, pwd = _odoo_env()
            common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
            uid = common.authenticate(db, user, pwd, {})
            models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
            solicitudes = models.execute_kw(
                db, uid, pwd, "maintenance.request", "search_read",
                [[["stage_id.name", "not in", ["Repaired", "Scrap"]]]],
                {"fields": ["id", "name", "request_date"]}
            )
            ids = [s["id"] for s in solicitudes] or [0]
            compras = models.execute_kw(
                db, uid, pwd, "purchase.order", "search_read",
                [[["maintenance_request_id", "in", ids]]],
                {"fields": ["name", "date_order", "amount_total", "maintenance_request_id"]}
            )
            out = []
            for s in solicitudes:
                ligadas = [c for c in compras if c.get("maintenance_request_id") and c["maintenance_request_id"][0] == s["id"]]
                out.append({"solicitud": s, "compras": ligadas})
            return {"ok": True, "data": out}

        return {"error": f"Unknown tool: {t}"}
    except Exception as e:
        return {"error": str(e)}
