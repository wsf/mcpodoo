import os, ssl, xmlrpc.client, datetime
from mcp.server.fastmcp import FastMCP

def _make_transport(url: str, allow_insecure: bool):
    if url.startswith("https://") and allow_insecure:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        class TLSNoVerifyTransport(xmlrpc.client.SafeTransport):
            def make_connection(self, host):
                conn = super().make_connection(host)
                conn._context = ctx
                return conn
        return TLSNoVerifyTransport()
    return None

def _odoo_env():
    url = os.environ.get("ODOO_URL", "https://mi-odoo.com")
    db = os.environ.get("ODOO_DB", "")
    user = os.environ.get("ODOO_USER", "")
    pwd = os.environ.get("ODOO_PASS", "")
    allow_insecure = os.environ.get("ODOO_ALLOW_INSECURE_SSL", "false").lower() in ("1","true","yes")
    if not all([url, db, user, pwd]):
        raise RuntimeError("Faltan ODOO_URL, ODOO_DB, ODOO_USER, ODOO_PASS")
    return url, db, user, pwd, allow_insecure

mcp = FastMCP(os.environ.get("MCP_SERVER_NAME", "odoo-helpdesk-mcp"))

@mcp.tool()
def add(a: int, b: int) -> int:
    """Suma dos números"""
    return a + b

@mcp.tool()
def odoo_search(model: str, domain: list, fields: list) -> list:
    url, db, user, pwd, allow_insecure = _odoo_env()
    transport = _make_transport(url, allow_insecure)
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common", transport=transport)
    uid = common.authenticate(db, user, pwd, {})
    if not uid:
        raise RuntimeError("Autenticación Odoo fallida")
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object", transport=transport)
    return models.execute_kw(db, uid, pwd, model, "search_read", [domain], {"fields": fields})

@mcp.tool()
def crear_solicitud_mantenimiento(name: str, description: str = "", request_date: str | None = None) -> dict:
    url, db, user, pwd, allow_insecure = _odoo_env()
    transport = _make_transport(url, allow_insecure)
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common", transport=transport)
    uid = common.authenticate(db, user, pwd, {})
    if not uid:
        raise RuntimeError("Autenticación Odoo fallida")
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object", transport=transport)
    if not request_date:
        request_date = datetime.date.today().isoformat()
    payload = {
        "name": name,
        "description": description,
        "request_date": request_date,
        "maintenance_type": "corrective",
        "company_id": 1,
        "maintenance_team_id": 2,
    }
    try:
        rec_id = models.execute_kw(db, uid, pwd, "maintenance.request", "create", [payload])
        return {"success": True, "id": rec_id, **payload}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
def mantenimiento_con_compras():
    url, db, user, pwd, allow_insecure = _odoo_env()
    transport = _make_transport(url, allow_insecure)
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common", transport=transport)
    uid = common.authenticate(db, user, pwd, {})
    if not uid:
        raise RuntimeError("Autenticación Odoo fallida")
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object", transport=transport)

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
    return out

@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    return f"¡Hola, {name}!"

@mcp.resource("comando1://{name}")
def get_comando1(name: str) -> str:
    return f"¡Comando 1, {name}!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8765))
    mcp.run(host="0.0.0.0", port=port)