import xmlrpc from "xmlrpc";

const ODOO_URL = process.env.ODOO_URL!;
const ODOO_DB = process.env.ODOO_DB!;
const ODOO_USER = process.env.ODOO_USER!;
const ODOO_PASS = process.env.ODOO_PASS!;

const common = xmlrpc.createClient({ url: `${ODOO_URL}/xmlrpc/2/common` });
const object = xmlrpc.createClient({ url: `${ODOO_URL}/xmlrpc/2/object` });

async function auth(): Promise<number> {
  return new Promise((resolve, reject) => {
    common.methodCall(
      "authenticate",
      [ODOO_DB, ODOO_USER, ODOO_PASS, {}],
      (err: any, uid: number) => {
        if (err) return reject(err);
        resolve(uid);
      }
    );
  });
}

export async function getTicketChatter(ticket_id: number, limit = 50) {
  const uid = await auth();
  const domain = [["res_id", "=", ticket_id], ["model", "=", "helpdesk.ticket"]];
  const fields = ["id", "body", "author_id", "date", "message_type"];

  return new Promise((resolve, reject) => {
    object.methodCall(
      "execute_kw",
      [
        ODOO_DB,
        uid,
        ODOO_PASS,
        "mail.message",
        "search_read",
        [domain],
        { fields, limit, order: "date asc" }
      ],
      (err: any, messages: any[]) => {
        if (err) return reject(err);
        resolve(messages);
      }
    );
  });
}