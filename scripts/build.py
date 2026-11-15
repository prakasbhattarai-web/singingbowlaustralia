#!/usr/bin/env python3
"""Build the static site.

- Wraps every guide in src/pages/*.html in the shared layout -> /<slug>/index.html
- Injects the shared nav + footer into index.html (between the NAV/FOOTER markers)
- Regenerates sitemap.xml
- Compiles Tailwind to assets/site.css (needs Node: npx tailwindcss@3.4.17)

Run from the repo root:  python3 scripts/build.py
Commit the generated files; Cloudflare Pages serves the repo as-is (no build step).
"""
import html
import json
import re
import subprocess
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://singingbowlaustralia.com"
NAV = (ROOT / "src/partials/nav.html").read_text()
FOOTER = (ROOT / "src/partials/footer.html").read_text()
COMMUNITY = (ROOT / "src/partials/community.html").read_text()

ORG = {
    "@type": "Organization",
    "@id": f"{SITE}/#org",
    "name": "Singing Bowl Australia",
    "url": f"{SITE}/",
    "logo": f"{SITE}/favicon.svg",
    "parentOrganization": {"@type": "Organization", "name": "Soham Collective", "url": "https://sohamcollective.com/"},
}
AUTHOR = {
    "@type": "Person",
    "@id": f"{SITE}/#prakash",
    "name": "Prakash Bhattarai",
    "url": "https://prakashbhattarai.com/",
    "jobTitle": "Meditation teacher",
}


def load_pages():
    pages = []
    for f in sorted((ROOT / "src/pages").glob("*.html")):
        raw = f.read_text()
        m = re.match(r"<!--META\s*(\{.*?\})\s*META-->\s*", raw, re.S)
        if not m:
            raise SystemExit(f"{f.name}: missing <!--META {{...}} META--> header")
        meta = json.loads(m.group(1))
        meta["body"] = raw[m.end():]
        pages.append(meta)
    return pages


def path_of(p):
    """URL path for a page: guides at /slug/, blog posts at /blog/slug/, the blog index at /blog/."""
    if p.get("type") == "blog":
        return "blog/" + p["slug"]
    return p["slug"]


def card(p, pad="p-5", gap="mt-1"):
    return f'''
        <a href="/{path_of(p)}/" class="group block bg-slate-800 rounded-2xl overflow-hidden hover:ring-1 hover:ring-amber-400/60 transition">
          <img width="640" height="360" src="{p["image"]}" alt="" loading="lazy" class="w-full aspect-[16/9] object-cover">
          <span class="block {pad}"><span class="serif text-2xl text-slate-100 group-hover:text-amber-200">{html.escape(p["card_title"])}</span>
          <span class="block text-sm text-slate-400 {gap}">{html.escape(p["card_text"])}</span></span>
        </a>'''


def guides(pages):
    return [p for p in pages if not p.get("type")]


def posts(pages):
    return sorted([p for p in pages if p.get("type") == "blog"], key=lambda p: p["published"], reverse=True)


def grid(title, items):
    if not items:
        return ""
    return f'''
      <h2 class="serif text-4xl mb-8 mt-4 text-center">{title}</h2>
      <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-14">{"".join(card(p) for p in items)}
      </div>'''


def related_block(page, pages):
    g = [p for p in guides(pages) if p["slug"] != page["slug"]]
    b = [p for p in posts(pages) if p["slug"] != page["slug"]]
    blocks = [grid("More from the Blog", b), grid("Guides", g)] if page.get("type") else [grid("More Guides", g), grid("From the Blog", b)]
    return f'''
  <section class="px-4 sm:px-6 pb-10">
    <div class="max-w-6xl mx-auto">{"".join(blocks)}
    </div>
  </section>'''


def blog_cards(pages):
    return f'<div class="not-prose grid sm:grid-cols-2 gap-6 my-10">{"".join(card(p) for p in posts(pages))}</div>'


def render(page, pages):
    url = f'{SITE}/{path_of(page)}/'
    body = page["body"].replace("<!-- COMMUNITY -->", COMMUNITY).replace("<!-- BLOGCARDS -->", blog_cards(pages))
    crumbs = [{"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"}]
    crumb_html = ""
    if page.get("type") == "blog":
        crumbs.append({"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{SITE}/blog/"})
        crumb_html = '<a href="/blog/" class="hover:text-amber-300">Blog</a> <span aria-hidden="true">›</span> '
    crumbs.append({"@type": "ListItem", "position": len(crumbs) + 1, "name": page["card_title"], "item": url})
    words = len(re.sub(r"<[^>]+>", " ", body).split())
    minutes = max(1, round(words / 220))
    graph = [
        ORG,
        AUTHOR,
        {
            "@type": "CollectionPage" if page.get("type") == "hub" else ("BlogPosting" if page.get("type") == "blog" else "Article"),
            "@id": f"{url}#article",
            "headline": page["h1"],
            "description": page["description"],
            "image": f'{SITE}{page["og_image"]}',
            "datePublished": page["published"],
            "dateModified": page.get("updated", page["published"]),
            "author": {"@id": f"{SITE}/#prakash"},
            "publisher": {"@id": f"{SITE}/#org"},
            "mainEntityOfPage": url,
            "inLanguage": "en",
            "wordCount": words,
        },
        {
            "@type": "BreadcrumbList",
            "itemListElement": crumbs,
        },
    ] + page.get("schema", [])
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, indent=1, ensure_ascii=False)
    published = date.fromisoformat(page["published"]).strftime("%-d %B %Y")
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(page["title"])}</title>
  <meta name="description" content="{html.escape(page["description"])}">
  <link rel="canonical" href="{url}">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <meta name="theme-color" content="#020617">
  <meta name="author" content="Prakash Bhattarai">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="Singing Bowl Australia">
  <meta property="og:locale" content="en_AU">
  <meta property="og:title" content="{html.escape(page["h1"])}">
  <meta property="og:description" content="{html.escape(page["description"])}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{SITE}{page["og_image"]}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="article:published_time" content="{page["published"]}">
  <meta name="twitter:card" content="summary_large_image">
  <script type="application/ld+json">
{ld}
  </script>
  <link rel="preload" href="/fonts/inter.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="/fonts/cormorant.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="/assets/site.css">
</head>
<body class="bg-slate-950 text-slate-100">
{NAV}
  <main>
  <header class="pt-28 pb-10 px-4 sm:px-6">
    <div class="max-w-3xl mx-auto">
      <nav aria-label="Breadcrumb" class="text-sm text-slate-500 mb-6"><a href="/" class="hover:text-amber-300">Home</a> <span aria-hidden="true">›</span> {crumb_html}<span class="text-slate-400">{html.escape(page["card_title"])}</span></nav>
      <p class="text-amber-300 tracking-widest text-xs sm:text-sm mb-4 uppercase">{html.escape(page["kicker"])}</p>
      <h1 class="serif text-4xl sm:text-5xl md:text-6xl font-bold leading-tight mb-6">{html.escape(page["h1"])}</h1>
      <p class="text-lg sm:text-xl text-slate-300 mb-6">{page["lede"]}</p>
      <p class="text-sm text-slate-500">By <a href="/#about" class="text-slate-300 hover:text-amber-300">Prakash Bhattarai</a> · {published} · {minutes} min read</p>
    </div>
  </header>
  <div class="px-4 sm:px-6">
    <img src="{page["image"]}" alt="{html.escape(page["image_alt"])}" width="1100" height="619" fetchpriority="high" class="max-w-5xl w-full mx-auto aspect-[16/9] object-cover rounded-3xl">
  </div>
  <article class="prose-guide max-w-3xl mx-auto px-4 sm:px-6 py-12">
{body}
  </article>
  <aside class="max-w-3xl mx-auto px-4 sm:px-6 pb-4" aria-label="About the author">
    <div class="flex gap-5 items-start rounded-2xl border border-slate-800 p-6">
      <img src="/img/prakash.webp" alt="Prakash Bhattarai" width="72" height="72" loading="lazy" class="w-[72px] h-[72px] rounded-full object-cover flex-none">
      <div>
        <p class="text-amber-200 tracking-widest text-xs mb-1">ABOUT THE AUTHOR</p>
        <p class="text-slate-300 leading-relaxed"><a href="https://prakashbhattarai.com/?utm_source=singingbowlaustralia&amp;utm_medium=referral&amp;utm_campaign=author" class="text-slate-100 font-medium underline decoration-amber-400/60 hover:text-amber-200">Prakash Bhattarai</a> is a meditation teacher in the Canberra region of Australia who helps busy people become more aware and calm. Prakash runs the Meditation for Beginners community and writes free guides at <a href="https://meditationforbeginners.com/?utm_source=singingbowlaustralia&amp;utm_medium=referral&amp;utm_campaign=author" class="text-slate-100 underline decoration-amber-400/60 hover:text-amber-200">meditationforbeginners.com</a>.</p>
      </div>
    </div>
  </aside>
{related_block(page, pages)}
  </main>
{FOOTER}
  <script src="/assets/site.js" defer></script>
</body>
</html>
'''


def build():
    pages = load_pages()
    for p in pages:
        out = ROOT / path_of(p) / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render(p, pages))
        print("built", out.relative_to(ROOT))

    home = (ROOT / "index.html").read_text()
    home = re.sub(r"  <!-- NAV:START -->\n.*?  <!-- NAV:END -->\n", lambda _: f"  <!-- NAV:START -->\n{NAV}  <!-- NAV:END -->\n", home, flags=re.S)
    home = re.sub(r"  <!-- FOOTER:START -->\n.*?  <!-- FOOTER:END -->\n", lambda _: f"  <!-- FOOTER:START -->\n{FOOTER}  <!-- FOOTER:END -->\n", home, flags=re.S)
    cards = "".join(card(p, "p-6", "mt-2") for p in guides(pages))
    blog_home = "".join(card(p, "p-6", "mt-2") for p in posts(pages)[:6])
    home = re.sub(r"  <!-- BLOG:START -->\n.*?  <!-- BLOG:END -->\n", lambda _: f"  <!-- BLOG:START -->{blog_home}\n  <!-- BLOG:END -->\n", home, flags=re.S)
    home = re.sub(r"  <!-- GUIDES:START -->\n.*?  <!-- GUIDES:END -->\n", lambda _: f"  <!-- GUIDES:START -->{cards}\n  <!-- GUIDES:END -->\n", home, flags=re.S)
    (ROOT / "index.html").write_text(home)

    today = date.today().isoformat()
    urls = [(f"{SITE}/", today, "1.0")] + [
        (f'{SITE}/{path_of(p)}/', p.get("updated", p["published"]), "0.8") for p in pages
    ]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"  <url><loc>{u}</loc><lastmod>{d}</lastmod><priority>{pr}</priority></url>" for u, d, pr in urls]
    sm.append("</urlset>\n")
    (ROOT / "sitemap.xml").write_text("\n".join(sm))
    print("built sitemap.xml with", len(urls), "urls")

    subprocess.run(
        ["npx", "-y", "tailwindcss@3.4.17", "-c", "tailwind.config.js", "-i", "src/site.css", "-o", "assets/site.css", "--minify"],
        cwd=ROOT, check=True,
    )


if __name__ == "__main__":
    build()
