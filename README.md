
# odoo-helpdesk-mcp (Vercel)

MCP server listo para Vercel. Usa env vars ODOO_* y MCP_API_KEY.

## Variables de entorno
- ODOO_URL (https://tu-odoo.com)
- ODOO_DB
- ODOO_USER
- ODOO_PASS
- MCP_API_KEY

## Endpoints
- GET /           -> health
- GET /api/mcp/meta   -> metadata (x-api-key)
- POST /api/mcp/run   -> ejecutar tools (x-api-key)

## Ejemplos
curl https://<app>.vercel.app/api/mcp/meta -H "x-api-key: $MCP_API_KEY"

curl -X POST https://<app>.vercel.app/api/mcp/run       -H "x-api-key: $MCP_API_KEY" -H "Content-Type: application/json"       -d '{"tool":"add","args":{"a":2,"b":3}}'
