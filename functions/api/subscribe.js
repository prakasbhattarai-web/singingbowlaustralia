// Cloudflare Pages Function: POST /api/subscribe
// Adds the visitor to the GetResponse list and tags them by what they asked for.
//
// Environment variables (Pages project → Settings → Variables, mark the key as a secret):
//   GR_API_KEY      GetResponse API key
//   GR_CAMPAIGN_ID  GetResponse list (campaign) id for Singing Bowl Australia

const GR = "https://api.getresponse.com/v3";

// form "kind" → GetResponse tag (GR tag names: letters, numbers, underscore)
const KIND_TAGS = {
  quote: "sba_bowl_quote",
  session: "sba_session",
  sound: "sba_sound_waitlist",
};
const BOWL_TAGS = {
  small: "sba_bowl_small",
  medium: "sba_bowl_medium",
  large: "sba_bowl_large",
  help: "sba_bowl_help_choose",
};
const SESSION_TAGS = {
  online: "sba_session_online",
  inperson: "sba_session_inperson",
  group: "sba_session_group",
};

export async function onRequestPost({ request, env, waitUntil }) {
  let body;
  try {
    const type = request.headers.get("content-type") || "";
    body = type.includes("application/json")
      ? await request.json()
      : Object.fromEntries(await request.formData());
  } catch {
    return json({ ok: false, error: "Bad request" }, 400);
  }

  // Honeypot: real people never fill the hidden "website" field.
  if (body.website) return json({ ok: true });

  const email = String(body.email || "").trim().toLowerCase();
  const name = String(body.name || "").trim().slice(0, 128);
  const kind = String(body.kind || "");
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || email.length > 254) {
    return json({ ok: false, error: "Please enter a valid email." }, 400);
  }
  if (!KIND_TAGS[kind]) return json({ ok: false, error: "Bad request" }, 400);
  if (!env.GR_API_KEY || !env.GR_CAMPAIGN_ID) {
    return json({ ok: false, error: "Sign-up is not set up yet. Please try again later." }, 503);
  }

  const tagNames = [KIND_TAGS[kind]];
  if (kind === "quote" && BOWL_TAGS[body.bowl]) tagNames.push(BOWL_TAGS[body.bowl]);
  if (kind === "session" && SESSION_TAGS[body.session]) tagNames.push(SESSION_TAGS[body.session]);
  if (body.updates) tagNames.push("sba_updates_optin");

  const note = [
    `SBA ${kind}`,
    body.bowl && `bowl=${body.bowl}`,
    body.session && `session=${body.session}`,
    body.location && `where=${String(body.location).slice(0, 60)}`,
    body.message && `msg=${String(body.message).replace(/\s+/g, " ").slice(0, 150)}`,
  ].filter(Boolean).join(" | ").slice(0, 255);

  const headers = {
    "X-Auth-Token": `api-key ${env.GR_API_KEY}`,
    "Content-Type": "application/json",
  };

  try {
    const tags = await Promise.all(tagNames.map((t) => tagId(t, headers)));
    const res = await fetch(`${GR}/contacts`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        email,
        ...(name.length >= 2 ? { name } : {}),
        campaign: { campaignId: env.GR_CAMPAIGN_ID },
        tags: tags.map((tagId) => ({ tagId })),
        ipAddress: request.headers.get("cf-connecting-ip") || undefined,
      }),
    });

    if (res.status === 409) {
      // Already on the list: add the new tags to the existing contact.
      const q = new URLSearchParams({ "query[email]": email, "query[campaignId]": env.GR_CAMPAIGN_ID });
      const found = await (await fetch(`${GR}/contacts?${q}`, { headers })).json();
      const id = Array.isArray(found) && found[0]?.contactId;
      if (id) {
        await fetch(`${GR}/contacts/${id}/tags`, {
          method: "POST",
          headers,
          body: JSON.stringify({ tags: tags.map((tagId) => ({ tagId })) }),
        });
        await addNote(id, note, headers);
      }
      return json({ ok: true });
    }
    if (!res.ok) {
      console.error("GetResponse error", res.status, await res.text());
      return json({ ok: false, error: "Something went wrong. Please try again." }, 502);
    }
    // GetResponse adds new contacts asynchronously and ignores "note" on create,
    // so wait for the contact to exist, then attach the note (bowl, suburb, message).
    waitUntil(noteWhenReady(email, env.GR_CAMPAIGN_ID, note, headers));
    return json({ ok: true });
  } catch (err) {
    console.error(err);
    return json({ ok: false, error: "Something went wrong. Please try again." }, 502);
  }
}

async function findContact(email, campaignId, headers) {
  const q = new URLSearchParams({ "query[email]": email, "query[campaignId]": campaignId });
  const found = await (await fetch(`${GR}/contacts?${q}`, { headers })).json();
  return Array.isArray(found) && found[0]?.contactId;
}

async function noteWhenReady(email, campaignId, note, headers) {
  for (let i = 0; i < 6; i++) {
    await new Promise((r) => setTimeout(r, 4000));
    try {
      const id = await findContact(email, campaignId, headers);
      if (id) return addNote(id, note, headers);
    } catch {}
  }
  console.error("Contact not found in time to add note", email);
}

async function addNote(id, note, headers) {
  const cur = await (await fetch(`${GR}/contacts/${id}?fields=note`, { headers })).json();
  const merged = [note, cur?.note].filter(Boolean).join(" || ").slice(0, 255);
  await fetch(`${GR}/contacts/${id}`, { method: "POST", headers, body: JSON.stringify({ note: merged }) });
}

async function tagId(name, headers) {
  const q = new URLSearchParams({ "query[name]": name });
  const list = await (await fetch(`${GR}/tags?${q}`, { headers })).json();
  const hit = Array.isArray(list) && list.find((t) => t.name === name);
  if (hit) return hit.tagId;
  const created = await (await fetch(`${GR}/tags`, {
    method: "POST",
    headers,
    body: JSON.stringify({ name }),
  })).json();
  return created.tagId;
}

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}
