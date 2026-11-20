// Anchor Point — website inquiry form → Telegram.
// A small Cloudflare Worker: the website form posts here, and the Worker forwards the inquiry
// to a Telegram chat through a bot. The bot token never appears in the website's code.
//
// Secrets (set with `wrangler secret put <NAME>`, never commit them):
//   TELEGRAM_BOT_TOKEN   token from @BotFather
//   TELEGRAM_CHAT_ID     the person or group that receives inquiries
const ALLOWED = ['https://anchorpointengineers.com', 'https://www.anchorpointengineers.com'];
const clean = (v, max) => String(v || '').replace(/\s+\n/g, '\n').trim().slice(0, max);

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || '';
    const cors = {
      'Access-Control-Allow-Origin': ALLOWED.includes(origin) ? origin : ALLOWED[0],
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Accept, Content-Type',
      'Vary': 'Origin',
    };
    const reply = (status, body) => new Response(JSON.stringify(body), { status, headers: { ...cors, 'Content-Type': 'application/json' } });

    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors });
    if (request.method !== 'POST') return reply(405, { ok: false, error: 'method' });
    if (!ALLOWED.includes(origin)) return reply(403, { ok: false, error: 'origin' });

    let form;
    try { form = await request.formData(); } catch { return reply(400, { ok: false, error: 'body' }); }
    if (clean(form.get('website'), 10)) return reply(200, { ok: true }); // honeypot: pretend success, send nothing

    const name = clean(form.get('name'), 120);
    const contact = clean(form.get('contact'), 160);
    const organization = clean(form.get('organization'), 160);
    const message = clean(form.get('message'), 3000);
    if (name.length < 2 || contact.length < 2 || message.length < 2) return reply(422, { ok: false, error: 'fields' });

    // Plain text on purpose: no parse_mode, so visitor text can never break the message.
    const lines = ['New project inquiry — Anchor Point website', '', `Name: ${name}`, `Contact: ${contact}`];
    if (organization) lines.push(`Organization: ${organization}`);
    lines.push('', message);

    const res = await fetch(`https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/sendMessage`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ chat_id: env.TELEGRAM_CHAT_ID, text: lines.join('\n'), disable_web_page_preview: true }),
    });
    if (!res.ok) {
      // Log Telegram's reason (never the token) so a failed delivery can be diagnosed with `wrangler tail`.
      console.log('telegram', res.status, (await res.text()).slice(0, 200));
      return reply(502, { ok: false, error: 'delivery' });
    }
    // The site shows "could not send" — never a false success
    return reply(200, { ok: true });
  },
};
