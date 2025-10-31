
from mcp.server.fastmcp import FastMCP
import os, xmlrpc.client, datetime

mcp = FastMCP("Demo")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Suma dos números"""
    return a + b

def _odoo_env():
    url = os.environ.get("ODOO_URL", "http://localhost:1869")
    db = os.environ.get("ODOO_DB", "uai")
    username = os.environ.get("ODOO_USER", "demo")
    password = os.environ.get("ODOO_PASS", "demo")
    return url, db, username, password

@mcp.tool()
def odoo_search(model: str, domain: list, fields: list) -> list:
    url, db, username, password = _odoo_env()
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(db, username, password, {})
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
    result = models.execute_kw(
        db, uid, password,
        model, 'search_read',
        [domain],
        {'fields': fields}
    )
    return result

@mcp.tool()
def crear_solicitud_mantenimiento(name: str, description: str = "", request_date: str = None) -> dict:
    url, db, username, password = _odoo_env()
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(db, username, password, {})
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
    if not request_date:
        request_date = datetime.date.today().isoformat()
    payload = {
        "name": name,
        "description": description,
        "request_date": request_date,
        "maintenance_type": "corrective",
        "company_id": 1,
        "maintenance_team_id": 2
    }
    try:
        solicitud_id = models.execute_kw(
            db, uid, password,
            "maintenance.request", "create",
            [payload]
        )
        return {"success": True, "id": solicitud_id, "name": name, "description": description, "request_date": request_date}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
def mantenimiento_con_compras():
    url, db, username, password = _odoo_env()
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(db, username, password, {})
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
    solicitudes = models.execute_kw(
        db, uid, password,
        "maintenance.request", "search_read",
        [[["stage_id.name", "not in", ["Repaired", "Scrap"]]]],
        {"fields": ["id", "name", "request_date"]}
    )
    solicitud_ids = [s["id"] for s in solicitudes] or [0]
    compras = models.execute_kw(
        db, uid, password,
        "purchase.order", "search_read",
        [[["maintenance_request_id", "in", solicitud_ids]]],
        {"fields": ["name", "date_order", "amount_total", "maintenance_request_id"]}
    )
    resultado = []
    for solicitud in solicitudes:
        compras_relacionadas = [
            c for c in compras if c.get("maintenance_request_id") and c["maintenance_request_id"][0] == solicitud["id"]
        ]
        resultado.append({
            "solicitud": solicitud,
            "compras": compras_relacionadas
        })
    return resultado

@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    return f"¡Hola, {name}!"

@mcp.resource("comando1://{name}")
def get_comando1(name: str) -> str:
    return f"¡Comando 1, {name}!"

if __name__ == "__main__":
    mcp.run()
