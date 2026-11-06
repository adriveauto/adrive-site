#!/usr/bin/env python3
"""Build the ADrive static site.

Usage: pip install markdown && python3 build.py

Reads templates/home.html and content/posts/*.md, writes:
  index.html, blog/index.html, blog/<slug>/index.html, sitemap.xml, robots.txt
Generated files are committed, so Vercel serves them as plain static files.
"""
import datetime as dt
import html
import json
import pathlib
import re

import markdown

ROOT = pathlib.Path(__file__).parent
SITE = "https://adrive-site.vercel.app"  # change here when a custom domain is added
BUY = "https://ailabofficial.gumroad.com/l/starter-kit"
OG_IMAGE = "/assets/img/gumroad_cover_2560x1440.png"
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;700;800;900'
         '&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap">')


def head(title, description, path, og_type="website"):
    url = SITE + path
    t, d = html.escape(title), html.escape(description)
    return f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{t}</title>
<meta name="description" content="{d}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}{OG_IMAGE}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
{FONTS}
<link rel="stylesheet" href="/assets/site.css">"""


HEADER = f"""<header class="top">
  <div class="wrap">
    <a class="logo" href="/" aria-label="ADrive home">
      <span class="logo-mark" aria-hidden="true"><i style="background:var(--stop)"></i><i style="background:var(--wait)"></i><i style="background:var(--go)"></i></span>
      ADrive <small>STARTER KIT</small>
    </a>
    <nav aria-label="Main">
      <a href="/#kit">What you get</a><a href="/#price">Pricing</a><a href="/blog/">Guides</a><a href="/#faq">FAQ</a>
    </nav>
    <a class="btn btn-primary" href="{BUY}?utm_source=site&amp;utm_medium=header" target="_blank" rel="noopener">Start for $19</a>
  </div>
</header>"""

FOOTER = """<footer>
  <div class="wrap">
    <p><b style="color:var(--ink)">ADrive</b> · <a href="/blog/">Guides</a> · Instagram <a href="https://www.instagram.com/adrive.ad0/" rel="noopener">@adrive.ad0</a></p>
    <p>The chat screens and numbers on this site are examples that show how the product works. Ad spend is paid directly to Meta and is not included. Ad results depend on your product and market and are not guaranteed. Claude is a service of Anthropic. ADrive is not affiliated with Anthropic or Meta.</p>
    <p>All content is owned by ADrive. Copying, sharing, distributing or reselling without written permission is prohibited. © 2026 ADrive</p>
  </div>
</footer>"""


def parse_post(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        raise SystemExit(f"{path}: missing front matter")
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"')
    for key in ("title", "slug", "description", "date"):
        if not meta.get(key):
            raise SystemExit(f"{path}: front matter needs '{key}'")
    if meta.get("status", "published") != "published":
        return None
    body = markdown.markdown(m.group(2), extensions=["tables", "fenced_code"])
    body = body.replace("<li>[ ] ", "<li>☐ ").replace("<li>[x] ", "<li>☑ ")
    meta["html"] = body
    return meta


def cta_box(slug):
    return f"""<div class="cta-box">
  <b>Want Claude to do this math and build the ad for you?</b>
  <p>The ADrive Starter Kit is one file you attach to free Claude. It works out your break-even numbers, writes 3 compliant ad copies, and builds your Meta campaign turned off until you choose to start. $19, one time.</p>
  <a class="btn btn-primary" href="{BUY}?utm_source=blog&amp;utm_medium={slug}" target="_blank" rel="noopener">Get the Starter Kit · $19</a>
</div>"""


def render_post(p):
    path = f"/blog/{p['slug']}/"
    ld = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"],
          "description": p["description"], "datePublished": p["date"],
          "dateModified": p.get("updated", p["date"]), "mainEntityOfPage": SITE + path,
          "image": SITE + OG_IMAGE, "author": {"@type": "Organization", "name": "ADrive"},
          "publisher": {"@type": "Organization", "name": "ADrive"}}
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{head(p.get('seo_title', p['title']), p['description'], path, 'article')}
<script type="application/ld+json">{json.dumps(ld)}</script>
</head>
<body>
{HEADER}
<main class="wrap">
  <article class="article">
    <p class="crumbs"><a href="/blog/">Guides</a> · <span class="post-meta">{p['date']}</span></p>
    <h1>{html.escape(p['title'])}</h1>
    {p['html']}
    {cta_box(p['slug'])}
  </article>
</main>
{FOOTER}
</body>
</html>
"""


def post_cards(posts):
    return "\n".join(
        f"""<a class="post-card" href="/blog/{p['slug']}/"><span class="post-meta">{p['date']}</span><h2>{html.escape(p['title'])}</h2><p>{html.escape(p['description'])}</p></a>"""
        for p in posts)


def main():
    posts = [p for p in (parse_post(f) for f in sorted((ROOT / "content/posts").glob("*.md"))) if p]
    posts.sort(key=lambda p: p["date"], reverse=True)

    for p in posts:
        out = ROOT / "blog" / p["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_post(p), encoding="utf-8")

    blog_index = f"""<!DOCTYPE html>
<html lang="en">
<head>
{head('Instagram & Meta Ads Guides for Small Store Owners | ADrive', 'Plain-English guides on running Instagram and Facebook ads for small online stores: budgets, break-even ROAS, ad copy rules and more.', '/blog/')}
</head>
<body>
{HEADER}
<main class="wrap" style="padding-block:56px 72px">
  <div class="sec-head"><p class="eyebrow">GUIDES</p><h2>Instagram ads, explained for small store owners</h2><p class="lead">One practical guide at a time. No jargon, real numbers, things you can do today.</p></div>
  <div class="post-list">
{post_cards(posts)}
  </div>
</main>
{FOOTER}
</body>
</html>
"""
    (ROOT / "blog").mkdir(exist_ok=True)
    (ROOT / "blog/index.html").write_text(blog_index, encoding="utf-8")

    latest = ""
    if posts:
        latest = f"""<section style="padding-top:0">
    <div class="wrap">
      <div class="sec-head"><p class="eyebrow">FREE GUIDES</p><h2>Learn the numbers before you spend</h2></div>
      <div class="post-list">
{post_cards(posts[:3])}
      </div>
    </div>
  </section>"""
    home = (ROOT / "templates/home.html").read_text(encoding="utf-8")
    home = (home.replace("{{HEAD}}", head("ADrive Starter Kit · Launch your first Instagram ad with free Claude",
                                           "A $19 one-time kit: attach one file to free Claude and launch your own Meta ads, with break-even math and a compliance check.", "/"))
            .replace("{{HEADER}}", HEADER).replace("{{FOOTER}}", FOOTER).replace("{{LATEST}}", latest)
            .replace("{{SITE}}", SITE).replace("{{BUY}}", BUY))
    (ROOT / "index.html").write_text(home, encoding="utf-8")

    today = dt.date.today().isoformat()
    urls = [(SITE + "/", today), (SITE + "/blog/", posts[0]["date"] if posts else today)]
    urls += [(f"{SITE}/blog/{p['slug']}/", p.get("updated", p["date"])) for p in posts]
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sitemap += [f"  <url><loc>{u}</loc><lastmod>{d}</lastmod></url>" for u, d in urls]
    sitemap.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(sitemap) + "\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    print(f"Built home, blog index and {len(posts)} post(s).")


if __name__ == "__main__":
    main()
