#!/usr/bin/env python3
"""
add_post.py — Add or update a medical blog post.

Creates/updates posts/[slug].html, updates public/posts.json,
and regenerates public/index.html.

Usage:
  python3 scripts/add_post.py \
    --slug 2026-07-27 \
    --title "عنوان مقاله" \
    --summary "خلاصه مقاله..." \
    --date "1405/05/05" \
    --content-file path/to/content.html \
    --journal "NEJM" \
    --study-type "RCT"

All arguments are optional except --slug and --title.
"""

import argparse
import json
import os
import sys

# Resolve paths relative to the project root (one level up from scripts/)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
PUBLIC_DIR = os.path.join(PROJECT_ROOT, "public")
POSTS_DIR = os.path.join(PUBLIC_DIR, "posts")
POSTS_JSON = os.path.join(PUBLIC_DIR, "posts.json")
INDEX_HTML = os.path.join(PUBLIC_DIR, "index.html")


def load_posts():
    """Load existing posts.json, returning a list."""
    if not os.path.exists(POSTS_JSON):
        return []
    with open(POSTS_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        return []
    return data


def save_posts(posts):
    """Write posts list to posts.json."""
    with open(POSTS_JSON, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
        f.write("\n")


def estimate_reading_time(text):
    """Rough reading-time estimate for Persian text (chars / 600 ≈ minutes)."""
    chars = len(text)
    minutes = max(1, round(chars / 600))
    return minutes


def create_post_html(title, content_html, date, journal, study_type, slug):
    """Wrap article content in a minimal HTML shell (used inside post.html via fetch)."""
    reading_time = estimate_reading_time(content_html)
    parts = []
    parts.append(f'<p style="color: var(--color-text-muted); font-size: .85rem; margin-bottom: 1.5rem;">')
    parts.append(f'  ⏱ حدود {reading_time} دقیقه مطالعه')
    parts.append(f'</p>')
    parts.append(content_html)
    return "\n".join(parts)


def generate_index_html(posts):
    """Generate the full public/index.html from posts.json data."""

    # Build cards HTML
    cards_html = ""
    for post in posts:
        slug = post.get("slug", "")
        title = post.get("title", "")
        summary = post.get("summary", "")
        date = post.get("date", "")
        study_type = post.get("study_type", "")
        journal = post.get("journal", "")

        badge_cls = get_badge_class(study_type)
        reading_time = max(1, round(len(summary) / 40))

        # Reading time in chars for summary length
        summary_chars = len(summary)
        read_min = max(1, round(summary_chars / 40))

        cards_html += f'''
      <article class="post-card">
        <a href="post.html?slug={slug}">
          <div class="card-meta">
            <span class="card-date">
              <svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd"/></svg>
              {date}
            </span>
            <span class="card-badge badge-{badge_cls}">{study_type}</span>
          </div>
          <h2 class="card-title">{title}</h2>
          <p class="card-summary">{summary}</p>
          <div class="card-footer">
            <span class="reading-time">
              <svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd"/></svg>
              {read_min} دقیقه مطالعه
            </span>
            <span class="card-arrow" aria-hidden="true">←</span>
          </div>
        </a>
      </article>'''

    if not cards_html.strip():
        cards_html = '''
      <div class="empty-state" id="empty-state">
        <div class="empty-state-icon" aria-hidden="true">📋</div>
        <h2>هنوز مقاله‌ای منتشر نشده است</h2>
        <p>مقالات پزشکی به زودی اضافه خواهند شد.</p>
      </div>'''

    html = f'''<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>digest.medical — دايجست پزشکی</title>
  <meta name="description" content="اخبار و مقالات پزشکی روزانه — مروری بر مهم‌ترین یافته‌های پزشکی">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="style.css">
</head>
<body>

  <!-- ========== HEADER ========== -->
  <header class="site-header">
    <div class="header-content">
      <span class="header-icon" aria-hidden="true">🩺</span>
      <h1 class="site-title">digest<span>.medical</span></h1>
      <p class="site-subtitle">اخبار و مقالات پزشکی روزانه</p>
    </div>
  </header>

  <!-- ========== SEARCH ========== -->
  <div class="search-wrapper">
    <div class="search-bar">
      <span class="search-icon" aria-hidden="true">
        <svg viewBox="0 0 20 20" fill="currentColor" width="18" height="18"><path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd"/></svg>
      </span>
      <input type="search" id="search-input" placeholder="جستجو در مقالات..." aria-label="جستجو">
    </div>
    <div class="search-filters" id="filter-bar">
      <button class="filter-btn active" data-filter="all">همه</button>
      <button class="filter-btn" data-filter="RCT">کارآزمایی بالینی</button>
      <button class="filter-btn" data-filter="Meta-analysis">فراتحلیل</button>
      <button class="filter-btn" data-filter="Systematic Review">مرور نظام‌مند</button>
      <button class="filter-btn" data-filter="Observational">مشاهده‌ای</button>
      <button class="filter-btn" data-filter="Case Report">گزارش مورد</button>
      <button class="filter-btn" data-filter="Clinical Guideline">راهنمای بالینی</button>
    </div>
  </div>

  <!-- ========== MAIN CONTENT ========== -->
  <main>
    <div class="posts-grid" id="posts-grid">
{cards_html}
    </div>
    <div class="no-results" id="no-results">
      نتیجه‌ای برای جستجوی شما یافت نشد.
    </div>
  </main>

  <!-- ========== FOOTER ========== -->
  <footer class="site-footer">
    <p>© <span id="footer-year">2026</span> digest.medical — تمامی حقوق محفوظ است. تألیف: علیرضا</p>
  </footer>

  <!-- ========== CLIENT-SIDE SEARCH & FILTER ========== -->
  <script>
    (function() {{
      'use strict';
      var grid = document.getElementById('posts-grid');
      var searchInput = document.getElementById('search-input');
      var filterBar = document.getElementById('filter-bar');
      var noResults = document.getElementById('no-results');
      var emptyState = document.getElementById('empty-state');

      if (!grid || !searchInput) return;

      var allCards = [];
      var currentFilter = 'all';

      var serverCards = grid.querySelectorAll('.post-card');
      for (var i = 0; i < serverCards.length; i++) {{
        allCards.push({{
          el: serverCards[i],
          title: (serverCards[i].querySelector('.card-title') || {{}}).textContent || '',
          summary: (serverCards[i].querySelector('.card-summary') || {{}}).textContent || '',
          badge: (serverCards[i].querySelector('.card-badge') || {{}}).textContent || ''
        }});
      }}

      if (allCards.length > 0 && emptyState) emptyState.style.display = 'none';

      function applyFilter() {{
        var query = (searchInput.value || '').trim().toLowerCase();
        var visible = 0;
        for (var i = 0; i < allCards.length; i++) {{
          var card = allCards[i];
          var matchesFilter = (currentFilter === 'all') || card.badge.indexOf(currentFilter) !== -1;
          var matchesSearch = !query || card.title.toLowerCase().indexOf(query) !== -1 || card.summary.toLowerCase().indexOf(query) !== -1;
          if (matchesFilter && matchesSearch) {{
            card.el.style.display = '';
            visible++;
          }} else {{
            card.el.style.display = 'none';
          }}
        }}
        if (emptyState) emptyState.style.display = (allCards.length === 0) ? '' : 'none';
        noResults.className = (visible === 0 && allCards.length > 0) ? 'no-results visible' : 'no-results';
      }}

      searchInput.addEventListener('input', applyFilter);

      if (filterBar) {{
        filterBar.addEventListener('click', function(e) {{
          var btn = e.target.closest('.filter-btn');
          if (!btn) return;
          var buttons = filterBar.querySelectorAll('.filter-btn');
          for (var j = 0; j < buttons.length; j++) buttons[j].classList.remove('active');
          btn.classList.add('active');
          currentFilter = btn.getAttribute('data-filter') || 'all';
          applyFilter();
        }});
      }}

      var yearEl = document.getElementById('footer-year');
      if (yearEl) yearEl.textContent = new Date().getFullYear();
    }})();
  </script>

</body>
</html>'''
    return html


def get_badge_class(study_type):
    """Map study type string to CSS badge class."""
    if not study_type:
        return "other"
    st = study_type.lower()
    if "rct" in st or "randomized" in st:
        return "rct"
    if "meta" in st:
        return "meta"
    if "systematic" in st or ("review" in st and "meta" not in st):
        return "sr"
    if "observ" in st or "cohort" in st or "case-control" in st:
        return "obs"
    if "case" in st:
        return "case"
    if "guide" in st or "recommend" in st:
        return "guide"
    return "other"


def main():
    parser = argparse.ArgumentParser(description="Add or update a medical blog post.")
    parser.add_argument("--slug", required=True, help="URL-friendly post identifier (e.g. 2026-07-27)")
    parser.add_argument("--title", required=True, help="Post title in Persian")
    parser.add_argument("--summary", default="", help="Short summary / excerpt (2-3 lines)")
    parser.add_argument("--content-file", default="", help="Path to HTML/Markdown content file")
    parser.add_argument("--date", default="", help="Persian (Jalali) date string")
    parser.add_argument("--journal", default="", help="Journal name (e.g. NEJM, The Lancet)")
    parser.add_argument("--study-type", default="", help="Study type (e.g. RCT, Meta-analysis)")

    args = parser.parse_args()

    slug = args.slug.strip()
    title = args.title.strip()
    summary = args.summary.strip()
    date = args.date.strip()
    journal = args.journal.strip()
    study_type = args.study_type.strip()

    # Ensure directories exist
    os.makedirs(POSTS_DIR, exist_ok=True)

    # Read content file
    content_html = ""
    if args.content_file:
        content_path = args.content_file
        if not os.path.isabs(content_path):
            content_path = os.path.join(PROJECT_ROOT, content_path)
        if os.path.exists(content_path):
            with open(content_path, "r", encoding="utf-8") as f:
                content_html = f.read()
        else:
            print(f"Warning: content file not found: {content_path}", file=sys.stderr)

    # Create the post HTML file
    post_html = create_post_html(title, content_html, date, journal, study_type, slug)
    post_file = os.path.join(POSTS_DIR, f"{slug}.html")
    with open(post_file, "w", encoding="utf-8") as f:
        f.write(post_html)
    print(f"✓ Created post: {post_file}")

    # Update posts.json (idempotent: replace if slug exists)
    posts = load_posts()
    updated = False
    for i, p in enumerate(posts):
        if p.get("slug") == slug:
            posts[i] = {
                "slug": slug,
                "title": title,
                "summary": summary,
                "date": date,
                "journal": journal,
                "study_type": study_type,
            }
            updated = True
            break

    if not updated:
        posts.append({
            "slug": slug,
            "title": title,
            "summary": summary,
            "date": date,
            "journal": journal,
            "study_type": study_type,
        })

    # Sort by slug descending (newest first, assuming date-based slugs)
    posts.sort(key=lambda p: p.get("slug", ""), reverse=True)

    save_posts(posts)
    print(f"✓ Updated {POSTS_JSON} ({len(posts)} posts)")

    # Regenerate index.html
    index_html = generate_index_html(posts)
    with open(INDEX_HTML, "w", encoding="utf-8") as f:
        f.write(index_html)
    print(f"✓ Regenerated {INDEX_HTML}")


if __name__ == "__main__":
    main()
