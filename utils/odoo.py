
import os
import xmlrpc.client

ODOO_URL = os.environ.get("ODOO_URL")
ODOO_DB = os.environ.get("ODOO_DB")
ODOO_USER = os.environ.get("ODOO_USER")
ODOO_PASS = os.environ.get("ODOO_PASS")

common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
object = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

def auth():
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASS, {})
    if not uid:
        raise Exception("Odoo authentication failed. Check ODOO_* env vars and credentials.")
    return uid

def get_ticket_chatter(ticket_id: int, limit: int = 50):
    uid = auth()
    domain = [["res_id", "=", ticket_id], ["model", "=", "helpdesk.ticket"]]
    fields = ["id", "body", "author_id", "date", "message_type"]
    messages = object.execute_kw(
        ODOO_DB, uid, ODOO_PASS,
        "mail.message", "search_read",
        [domain], {"fields": fields, "limit": limit, "order": "date asc"}
    )
    return messages

def search_chatter(ticket_id: int, query: str):
    uid = auth()
    domain = [
        ["res_id", "=", ticket_id],
        ["model", "=", "helpdesk.ticket"],
        ["body", "ilike", query]
    ]
    messages = object.execute_kw(
        ODOO_DB, uid, ODOO_PASS,
        "mail.message", "search_read",
        [domain], {"fields": ["id", "body", "date", "author_id"], "order": "date asc"}
    )
    return messages

def post_message(ticket_id: int, body: str):
    uid = auth()
    result = object.execute_kw(
        ODOO_DB, uid, ODOO_PASS,
        "helpdesk.ticket", "message_post",
        [ticket_id], {"body": body}
    )
    return result
