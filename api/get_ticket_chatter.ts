import type { VercelRequest, VercelResponse } from "@vercel/node";
import { getTicketChatter } from "../utils/odoo.js";

export default async function handler(req: VercelRequest, res: VercelResponse) {
  const apiKey = req.headers["x-api-key"];
  if (apiKey !== process.env.MCP_API_KEY) {
    return res.status(401).json({ error: "Invalid API Key" });
  }

  const ticket_id = parseInt(req.query.ticket_id as string);

  if (!ticket_id) {
    return res.status(400).json({ error: "Missing ticket_id" });
  }

  try {
    const messages = await getTicketChatter(ticket_id);
    return res.status(200).json({
      ticket_id,
      count: messages.length,
      messages
    });
  } catch (err: any) {
    return res.status(500).json({ error: err.message });
  }
}