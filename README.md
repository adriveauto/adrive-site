# adrive-site

US sales page + SEO blog for the ADrive Starter Kit. Plain static files, served by Vercel (no build step on Vercel).

## Add a blog post
1. Create `content/posts/YYYY-MM-DD-<slug>.md` with front matter:
   ```
   ---
   title: Human headline
   seo_title: Title shown in Google (optional)
   slug: url-slug
   description: 140-160 character meta description
   date: YYYY-MM-DD
   target_keyword: main keyword
   ---
   ```
   Don't add an H1 or a buy box; the template adds both.
2. `pip install markdown && python3 build.py`
3. Commit everything (including generated `index.html`, `blog/`, `sitemap.xml`) and push. Vercel deploys automatically.

## Settings
`build.py`: `SITE` (change when a custom domain is added) and `BUY` (Gumroad link).
