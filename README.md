
# odoo-helpdesk-mcp

MCP Server (HTTP) para consultar y operar el chatter de `helpdesk.ticket` en Odoo.
Listo para desplegar en **Vercel**.

## Endpoints principales

- `GET /api/mcp/meta`  -> devuelve `mcp.json` (tools, schemas, metadata)
- `POST /api/mcp/run`  -> ejecuta una tool con `{"tool": "...", "args": {...}}`
- `GET /`              -> health + listado de tools

**Header obligatorio**: `x-api-key: <MCP_API_KEY>`

## Tools
- `get_ticket_chatter` { ticket_id:int, limit?:int }
- `search_chatter` { ticket_id:int, query:str }
- `post_message` { ticket_id:int, body:str }

## Variables de entorno (Vercel)
- `ODOO_URL`  (e.g. https://tu-odoo.com)
- `ODOO_DB`
- `ODOO_USER` (ID de usuario en Odoo)
- `ODOO_PASS`
- `MCP_API_KEY`

## Pruebas

### Meta
curl -H "x-api-key: $MCP_API_KEY" https://<app>.vercel.app/api/mcp/meta

### Run (get_ticket_chatter)
curl -X POST https://<app>.vercel.app/api/mcp/run           -H "x-api-key: $MCP_API_KEY" -H "Content-Type: application/json"           -d '{"tool":"get_ticket_chatter","args":{"ticket_id":45,"limit":50}}'
