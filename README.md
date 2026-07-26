# Medical Digest — دايجست پزشکی

A static blog for daily medical digest posts, built for Persian (Farsi) readers.
Deployed on Cloudflare Pages.

## Structure

```
medical-digest/
├── public/                 # Static site root (served by Cloudflare Pages)
│   ├── index.html          # Main page — card grid of all posts
│   ├── post.html           # Individual post viewer
│   ├── style.css           # Dark medical theme
│   ├── posts.json          # Post metadata (JSON array)
│   └── posts/              # Individual post HTML files
│       └── .gitkeep
├── scripts/
│   ├── add_post.py         # Add/update a post and rebuild index
│   └── build_index.py      # Rebuild index.html from posts.json
└── README.md
```

## Adding a Post

```bash
python3 scripts/add_post.py \
  --slug 2026-07-27 \
  --title "نتایج جدید آزمایشی" \
  --summary "خلاصه‌ای کوتاه از مقاله..." \
  --date "1405/05/05" \
  --content-file content.html \
  --journal "NEJM" \
  --study-type "RCT"
```

The content file should contain the article body (HTML fragments are fine).
The script is idempotent — running it twice with the same slug updates in place.

## Rebuilding the Index

```bash
python3 scripts/build_index.py
```

Reads `public/posts.json` and regenerates `public/index.html`.

## Deployment (Cloudflare Pages)

1. Push this repository to GitHub/GitLab.
2. In Cloudflare Pages, create a new project.
3. Set the **build command** to `python3 scripts/build_index.py` (or leave empty if using pre-built HTML).
4. Set the **output directory** to `public`.
5. Deploy — Cloudflare will serve everything under `public/`.

## Design

- Dark theme (`#0f172a` background, `#1e293b` cards)
- Teal accent (`#0d9488`)
- RTL (right-to-left) Persian layout
- Vazirmatn font from Google Fonts
- Responsive: 3-column → 2-column → 1-column
- Print-friendly post pages
- Client-side search and filter on the main page
- Progressive enhancement (works without JavaScript)

## License

All rights reserved. © Alireza
