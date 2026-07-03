#!/usr/bin/env python3
"""
Site builder for leomohan.net — regenerates the data-driven pages from data/*.json.

  python3 build.py        (or double-click build.command)

Regenerates: index.html, the 9 genre pages, newreleases.html + book detail
pages, news.html, articles.html, previousarticles.html, and sitemap.xml.
All other pages (about, certifications, travel, etc.) are never touched.

To add a new book:
  1. Copy the cover image into assets/images/
  2. Add an entry in data/books.json under its genre
     (and data/newreleases.json + a body file in data/releases/ if it
      should appear on the New Releases page with its own detail page)
  3. Run this script, then commit & push
"""
import os, re, json, html, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
BASE = "https://www.leomohan.net"
TODAY = datetime.date.today()
LION_IMG = "assets/images/animated-image-of-lion-majestically-walking-about-1256x1256.jpg"

def load(name):
    return json.load(open(os.path.join(DATA, name), encoding="utf-8"))

def esc(s):
    return html.escape(s, quote=True)

def dims(src):
    m = re.search(r"-(\d+)x(\d+)\.\w+$", src)
    return (m.group(1), m.group(2)) if m else (None, None)

def img_tag(src, alt, lazy=True, cls=""):
    w, h = dims(src)
    a = f'<img src="{src}" alt="{esc(alt)}"'
    if cls: a += f' class="{cls}"'
    if w: a += f' width="{w}" height="{h}"'
    if lazy: a += ' loading="lazy"'
    return a + ">"

# ---------------------------------------------------------------- shared nav / footer
BOOK_CATS = [
    ("business.html", "Business"), ("fiction.html", "Fiction"),
    ("general.html", "General"), ("humor.html", "Humor"),
    ("philosophy.html", "Philosophy"), ("spiritual.html", "Spiritual"),
    ("technology.html", "Technology"), ("syngress.html", "Syngress"),
    ("storybooks.html", "Storybooks"), ("tamil.html", "Tamil Works"),
]
STORES = [
    ("https://www.smashwords.com/profile/view/MohanKrishnamurthy", "Smashwords"),
    ("https://www.amazon.com/author/mohankrishnamurthy", "Amazon"),
    ("https://www.goodreads.com/mohankrishnamurthy", "Goodreads"),
    ("https://www.everand.com/author/870315188/Mohan-Krishnamurthy", "Everand"),
    ("https://fable.co/author/mohan-krishnamurthy", "Fable"),
    ("https://www.kobo.com/ww/en/search?query=mohan+krishnamurthy", "Rakuten Kobo"),
    ("https://www.thalia.de/shop/home/mehr-von-suche/ANY/sp/suche.html?mehrVon=mohan+krishnamurthy", "Thalia"),
    ("https://shop.vivlio.com/author/mohan-krishnamurthy/1402656", "Vivlio"),
    ("https://www.barnesandnoble.com/s/%22Mohan%20Krishnamurthy%22?Ntk=P_key_Contributor_List&amp;Ns=P_Sales_Rank&amp;Ntx=mode+matchall", "Barnes &amp; Noble"),
    ("https://bookshop.org/beta-search?keywords=Mohan+Krishnamurthy", "Bookshop"),
]

def dropdown(label, parent_href, items, page):
    lis = []
    for h, t in items:
        attrs = ' target="_blank" rel="noopener"' if h.startswith("http") else ""
        if h == page:
            attrs += ' aria-current="page"'
        lis.append(f'<li><a href="{h}"{attrs}>{t}</a></li>')
    return (f'<li class="has-dropdown"><a href="{parent_href}">{label}</a>'
            f'<ul class="dropdown">{"".join(lis)}</ul></li>')

def nav_html(page, latest_article_url):
    books = dropdown("Books", "books.html",
                     [("newreleases.html", "New Releases")] + BOOK_CATS, page)
    articles = dropdown("Articles", "articles.html",
                        [(latest_article_url, "Latest Article"),
                         ("previousarticles.html", "Earlier Articles"),
                         ("news.html", "In the News")], page)
    about = dropdown("About", "aboutme.html",
                     [("aboutme.html", "About Me"), ("certifications.html", "Certifications"),
                      ("inspiration.html", "Inspiration"), ("travel.html", "Travel"),
                      ("gallery.html", "Gallery"), ("youtube.html", "YT Channel"),
                      ("podcasts.html", "Podcasts"), ("index.html#contact", "Contact")], page)
    stores = dropdown("Book Stores", "books.html", STORES, page)
    return f'''<header class="site-header">
  <div class="container nav-bar">
    <a class="brand" href="index.html">Mohan&nbsp;Krishnamurthy</a>
    <input type="checkbox" id="nav-toggle" class="nav-toggle" aria-hidden="true">
    <label for="nav-toggle" class="nav-toggle-label" aria-label="Toggle navigation"><span></span><span></span><span></span></label>
    <nav aria-label="Main navigation">
      <ul class="nav-menu">
        <li><a href="index.html#bestsellers">Best Sellers</a></li>
        {books}
        {articles}
        {about}
        <li><a href="https://labs.leomohan.net/index.html" target="_blank" rel="noopener">Labs</a></li>{stores}
      </ul>
    </nav>
  </div>
</header>'''

SOCIALS = [
    ("https://www.facebook.com/mohan.madwachar", "Facebook",
     "M13.5 9H15V6.5h-1.5c-1.93 0-3.5 1.57-3.5 3.5v1.5H8V14h2v8h2.5v-8H15l.5-2.5h-3V10c0-.55.45-1 1-1z"),
    ("https://x.com/madwachar", "X (Twitter)",
     "M17.7 3H21l-7.3 8.3L22.3 22h-6.4l-5-6.5L5 22H1.7l7.8-8.9L1.5 3H8l4.5 6L17.7 3zm-1.1 17h1.8L7 4.8H5.1L16.6 20z"),
    ("https://www.instagram.com/mohanmadwachar/", "Instagram",
     "M12 8.8A3.2 3.2 0 1 0 12 15.2 3.2 3.2 0 0 0 12 8.8zM12 7a5 5 0 1 1 0 10 5 5 0 0 1 0-10zm6.4-.9a1.3 1.3 0 1 1-2.6 0 1.3 1.3 0 0 1 2.6 0zM12 4.5c-2 0-2.3 0-3.1.05a4.2 4.2 0 0 0-3 1.2 4.2 4.2 0 0 0-1.2 3C4.6 9.6 4.5 9.9 4.5 12s0 2.3.06 3.1a4.2 4.2 0 0 0 1.2 3 4.2 4.2 0 0 0 3 1.2c.8.05 1.1.06 3.1.06s2.3 0 3.1-.06a4.2 4.2 0 0 0 3-1.2 4.2 4.2 0 0 0 1.2-3c.05-.8.06-1.1.06-3.1s0-2.3-.06-3.1a4.2 4.2 0 0 0-1.2-3 4.2 4.2 0 0 0-3-1.2C14.3 4.6 14 4.5 12 4.5z"),
    ("https://linkedin.com/in/leomohan", "LinkedIn",
     "M6.94 5a2 2 0 1 1-4-.02 2 2 0 0 1 4 .02zM7 8.48H3V21h4V8.48zm6.32 0H9.34V21h3.94v-6.57c0-3.66 4.77-4 4.77 0V21H22v-7.93c0-6.17-7.06-5.94-8.72-2.91l.04-1.68z"),
    ("https://www.youtube.com/leomohan", "YouTube",
     "M21.6 7.2a2.5 2.5 0 0 0-1.76-1.77C18.25 5 12 5 12 5s-6.25 0-7.84.43A2.5 2.5 0 0 0 2.4 7.2 26 26 0 0 0 2 12a26 26 0 0 0 .4 4.8 2.5 2.5 0 0 0 1.76 1.77C5.75 19 12 19 12 19s6.25 0 7.84-.43a2.5 2.5 0 0 0 1.76-1.77A26 26 0 0 0 22 12a26 26 0 0 0-.4-4.8zM10 15V9l5.2 3z"),
]

def footer_html():
    soc = "".join(
        f'<a href="{u}" target="_blank" rel="noopener" aria-label="{n}">'
        f'<svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor" aria-hidden="true"><path d="{p}"/></svg></a>'
        for u, n, p in SOCIALS)
    return f'''<footer class="site-footer">
  <div class="container">
    <ul class="footer-links">
      <li><a href="index.html">Home</a></li>
      <li><a href="books.html">Books</a></li>
      <li><a href="articles.html">Articles</a></li>
      <li><a href="aboutme.html">About Me</a></li>
      <li><a href="index.html#contact">Contact</a></li>
    </ul>
    <div class="social-row">{soc}</div>
    <p class="copyright">&copy; {TODAY.year} Mohan Krishnamurthy. All rights reserved.</p>
  </div>
</footer>'''

def page(fname, title, desc, body, og_image, jsonld, latest_article_url):
    ld = ""
    if jsonld:
        ld = ('\n  <script type="application/ld+json">'
              + json.dumps(jsonld, ensure_ascii=False) + "</script>")
    doc = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{esc(desc)}">
  <link rel="canonical" href="{BASE}/{fname if fname != "index.html" else ""}">
  <link rel="shortcut icon" href="assets/images/favicon-1.ico" type="image/x-icon">
  <link rel="stylesheet" href="assets/css/style.css">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Mohan Krishnamurthy">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(desc)}">
  <meta property="og:url" content="{BASE}/{fname}">
  <meta property="og:image" content="{BASE}/{og_image}">
  <meta name="twitter:card" content="summary_large_image">{ld}
</head>
<body>
{nav_html(fname, latest_article_url)}
<main id="main">
{body}
</main>
{footer_html()}
</body>
</html>
'''
    open(os.path.join(ROOT, fname), "w", encoding="utf-8").write(doc)
    print("built", fname)

GENERIC_ALT = {
    "business": "Business book cover by Mohan Krishnamurthy",
    "fiction": "Fiction book cover by Mohan Krishnamurthy",
    "general": "General interest book cover by Mohan Krishnamurthy",
    "humor": "Humor book cover by Mohan Krishnamurthy",
    "philosophy": "Philosophy book cover by Mohan Krishnamurthy",
    "spiritual": "Spiritual book cover by Mohan Krishnamurthy",
    "storybooks": "Illustrated storybook cover by Mohan Krishnamurthy",
    "tamil": "Tamil book cover by Mohan Krishnamurthy",
    "technology": "Technology book cover by Mohan Krishnamurthy",
}

def build_genre_pages(latest_article_url):
    data = load("books.json")
    for genre, g in data.items():
        cards = []
        for b in g["books"]:
            alt = b["title"] + " — book cover" if b["title"] else GENERIC_ALT[genre]
            caption = f'<figcaption>{esc(b["title"])}</figcaption>' if b["title"] else ""
            if caption:
                cards.append(
                    f'<a class="book-card" href="{b["link"]}" target="_blank" rel="noopener">'
                    f'<figure style="margin:0">{img_tag(b["cover"], alt)}{caption}</figure></a>')
            else:
                cards.append(
                    f'<a class="book-card" href="{b["link"]}" target="_blank" rel="noopener">'
                    f'{img_tag(b["cover"], alt)}</a>')
        lang_attr = f' lang="{g["heading_lang"]}"' if g.get("heading_lang") else ""
        body = f'''<section class="page-hero">
  <div class="container">
    <h1{lang_attr}>{g["heading"]}</h1>
    <p class="lead">{g["intro"]}</p>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="book-grid">
      {"".join(cards)}
    </div>
    <p class="center mt-2"><a class="btn" href="https://www.amazon.com/author/mohankrishnamurthy" target="_blank" rel="noopener">Browse All on Amazon</a></p>
  </div>
</section>'''
        og = g["books"][0]["cover"] if g["books"] else LION_IMG
        ld = {"@context": "https://schema.org", "@type": "CollectionPage",
              "name": g["page_title"], "url": f"{BASE}/{genre}.html",
              "author": {"@type": "Person", "name": "Mohan Krishnamurthy"}}
        titled = [b for b in g["books"] if b["title"]]
        if titled:
            ld["mainEntity"] = {"@type": "ItemList", "itemListElement": [
                {"@type": "ListItem", "position": n + 1,
                 "item": {"@type": "Book", "name": b["title"],
                          "author": {"@type": "Person", "name": "Mohan Krishnamurthy"},
                          "image": f"{BASE}/{b['cover']}", "url": b["link"]}}
                for n, b in enumerate(titled)]}
        page(f"{genre}.html", g["page_title"], g["meta_description"], body, og, ld, latest_article_url)

def teaser_of(body_html):
    for p in re.findall(r'<p[^>]*>(.*?)</p>', body_html, flags=re.S):
        txt = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', p))).strip()
        if len(txt) > 30:
            return (txt[:150].rsplit(' ', 1)[0] + '…') if len(txt) > 150 else txt
    return ""

def build_releases(latest_article_url):
    nr = load("newreleases.json")
    cards = []
    for r in nr["releases"]:
        title, cover = r["title"], r["cover"]
        if r.get("slug"):
            fname = r["slug"] + ".html"
            body_html = open(os.path.join(DATA, "releases", r["slug"] + ".html"), encoding="utf-8").read().strip()
            teaser = teaser_of(body_html)
            ld = {"@context": "https://schema.org", "@type": "Book",
                  "name": title, "author": {"@type": "Person", "name": "Mohan Krishnamurthy"},
                  "image": f"{BASE}/{cover}", "url": f"{BASE}/{fname}",
                  "genre": r["genre"], "description": teaser}
            try:
                d = datetime.datetime.strptime(r["date"], "%B %Y")
                ld["datePublished"] = d.strftime("%Y-%m")
            except ValueError:
                pass
            if "author/mohankrishnamurthy" not in r["buy_link"]:
                ld["sameAs"] = r["buy_link"]
            detail = f'''<section class="page-hero">
  <div class="container">
    <h1>{esc(title)}</h1>
    <p class="chip">{r["genre"]} &middot; {r["date"]}</p>
  </div>
</section>
<section class="section">
  <div class="container book-detail">
    <div class="book-detail-cover">
      <img src="{cover}" alt="{esc(title)} — book cover">
    </div>
    <div class="book-detail-body prose">
      {body_html}
      <a class="btn" href="{r["buy_link"]}" target="_blank" rel="noopener">{r["buy_label"]}</a>
    </div>
  </div>
</section>
<section class="section section--alt">
  <div class="container center">
    <p class="lead">Explore more <a href="newreleases.html">new releases</a> or browse <a href="books.html">all books by category</a>.</p>
  </div>
</section>'''
            desc = f"{title} by Mohan Krishnamurthy — {teaser}"[:158]
            page(fname, f"{title} — Mohan Krishnamurthy", desc, detail, cover, ld, latest_article_url)
            datechip = f'<p class="date">{r["date"]}</p>' if r["date"] else ""
            cards.append(f'''<div class="feature-card">
      <a href="{fname}">{img_tag(cover, title + " — book cover")}</a>
      <div class="feature-body">
        {datechip}
        <h3 class="h6">{esc(title)}</h3>
        <p>{esc(teaser)}</p>
        <a class="btn btn-small" href="{fname}">Read More</a>
      </div>
    </div>''')
        else:
            cards.append(f'''<div class="feature-card">
      <a href="{r["buy_link"]}" target="_blank" rel="noopener">{img_tag(cover, title + " — book cover")}</a>
      <div class="feature-body">
        <h3 class="h6">{esc(title)}</h3>
        <p>{r["genre"]}.</p>
        <a class="btn btn-small" href="{r["buy_link"]}" target="_blank" rel="noopener">{r["buy_label"]}</a>
      </div>
    </div>''')

    fc = nr["free_callout"]
    body = f'''<section class="page-hero">
  <div class="container">
    <h1>New Releases &amp; Book News</h1>
    <p class="chip">Updated {TODAY.strftime("%B %-d, %Y")}</p>
    <p class="lead">The latest books from Mohan Krishnamurthy &mdash; fiction, business and technology &mdash; each with the story behind it.</p>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="article-highlight">
      <h2 class="h4">Free on Kindle</h2>
      <p><a href="{fc["page"]}">{fc["title"]}</a> &mdash; <a href="{fc["link"]}" target="_blank" rel="noopener">{fc["text"]}</a>.</p>
    </div>
    <div class="feature-grid cols-3 mt-2">
      {"".join(cards)}
    </div>
  </div>
</section>
<section class="section section--alt" id="mailing-list">
  <div class="container">
    <div class="subscribe">
      <h2 class="h4">News About New Books</h2>
      <p>Sign up for news, free books, new book launches and more! You can unsubscribe anytime.</p>
      <form class="subscribe-form" action="https://assets.mailerlite.com/jsonp/1538678/forms/155011195784398292/subscribe" method="post" target="_blank">
        <input aria-label="email" aria-required="true" type="email" name="fields[email]" placeholder="Your email address" autocomplete="email" required>
        <input type="hidden" name="ml-submit" value="1">
        <button class="btn" type="submit">Subscribe</button>
      </form>
      <p class="fine-print">Powered by MailerLite. You can unsubscribe anytime.</p>
    </div>
  </div>
</section>'''
    og = nr["releases"][0]["cover"] if nr["releases"] else LION_IMG
    page("newreleases.html", "New Releases & Book News — Mohan Krishnamurthy",
         "The latest books by Mohan Krishnamurthy — fiction, business and technology — with full descriptions and buy links.",
         body, og, None, latest_article_url)
    return [r["slug"] + ".html" for r in nr["releases"] if r.get("slug")]

def build_news(latest_article_url):
    n = load("news.json")
    press_cards = "".join(f'''<figure class="press-card">
      {img_tag(p["image"], "Press clipping: " + p["title"])}
      <figcaption>{esc(p["title"])}</figcaption>
    </figure>''' for p in n["press"])
    pdf_items = "".join(
        f'<li><a href="{p["file"]}" target="_blank" rel="noopener">{esc(p["title"])}</a> <span class="isbn">(PDF)</span></li>'
        for p in n["pdfs"])
    body = f'''<section class="page-hero">
  <div class="container">
    <h1>In the News</h1>
    <p class="lead">Press interviews, industry commentary and media coverage featuring Mohan Krishnamurthy &mdash; on cybersecurity, the Indian technology industry and the working world.</p>
  </div>
</section>
<section class="section">
  <div class="container">
    <h2 class="section-title">Featured Coverage</h2>
    <div class="press-grid">{press_cards}</div>
  </div>
</section>
<section class="section section--alt">
  <div class="container">
    <h2 class="section-title">More Coverage</h2>
    <ul class="pdf-list">{pdf_items}</ul>
  </div>
</section>'''
    og = n["press"][0]["image"] if n["press"] else LION_IMG
    page("news.html", "In the News — Press & Media Coverage of Mohan Krishnamurthy",
         "Press interviews and media coverage featuring Mohan Krishnamurthy: cybersecurity commentary, industry analysis and news features from print and online media.",
         body, og, None, latest_article_url)

def build_articles(latest_article_url):
    a = load("articles.json")
    stamp = TODAY.strftime("%B %-d, %Y")
    body = f'''<section class="page-hero">
  <div class="container">
    <h1>Articles</h1>
    <p class="chip">Article list updated {stamp}</p>
    <p class="lead">Essays and opinion pieces on leadership, cybersecurity, the corporate world and life &mdash; published on LinkedIn and other platforms.</p>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="article-highlight">
      <h2 class="h4">Latest Article</h2>
      <p><a href="{a["latest"]["url"]}" target="_blank" rel="noopener">{esc(a["latest"]["title"])}</a> &mdash; the newest piece, on LinkedIn.</p>
    </div>
    <p class="mt-2">Looking for more? Browse the <a href="previousarticles.html">full article archive</a> or see <a href="news.html">press coverage</a>.</p>
  </div>
</section>'''
    page("articles.html", "Articles by Mohan Krishnamurthy",
         "Articles by Mohan Krishnamurthy on leadership, cybersecurity, the corporate world and life — published on LinkedIn and other platforms.",
         body, LION_IMG, None, latest_article_url)

    items = "".join(
        f'<li><a href="{x["url"]}" target="_blank" rel="noopener">{esc(x["title"])}</a></li>'
        for x in a["archive"])
    body = f'''<section class="page-hero">
  <div class="container">
    <h1>Article Archive</h1>
    <p class="chip">Archive updated {stamp}</p>
    <p class="lead">Earlier articles published on LinkedIn &amp; other platforms.</p>
  </div>
</section>
<section class="section">
  <div class="container">
    <ul class="article-list">{items}</ul>
  </div>
</section>'''
    page("previousarticles.html", "Article Archive — Mohan Krishnamurthy",
         "Archive of articles by Mohan Krishnamurthy: leadership lessons, cybersecurity commentary, COVID-19 industry analysis and more.",
         body, LION_IMG, None, latest_article_url)

def build_index(latest_article_url):
    f = load("featured.json")
    hero = f["hero_book"]
    recent_cards = "".join(f'''<div class="feature-card">
      <a href="{b["link"]}" target="_blank" rel="noopener">{img_tag(b["cover"], b["title"] + " — book cover")}</a>
      <div class="feature-body"><h3 class="h6">{esc(b["title"])}</h3></div>
    </div>''' for b in f["recent_launches"])
    seller_cards = "".join(f'''<article class="seller-card">
      <a href="{b["link"]}" target="_blank" rel="noopener">{img_tag(b["cover"], b["title"] + " — book cover")}</a>
      <div class="seller-body">
        <h3 class="h5">{esc(b["title"])}</h3>
        <p>{esc(b["description"])}</p>
        <a class="btn" href="{b["link"]}" target="_blank" rel="noopener">Buy Now</a>
      </div>
    </article>''' for b in f["best_sellers"])

    person = {
        "@context": "https://schema.org", "@type": "Person",
        "name": "Mohan Krishnamurthy",
        "alternateName": ["Leo Mohan", "Mohan K. Madwachar"],
        "url": f"{BASE}/",
        "jobTitle": "Author, Speaker, Trainer & Cybersecurity Professional",
        "email": "mailto:leomohan@yahoo.com",
        "sameAs": [
            "https://linkedin.com/in/leomohan",
            "https://www.amazon.com/author/mohankrishnamurthy",
            "https://www.goodreads.com/mohankrishnamurthy",
            "https://www.smashwords.com/profile/view/MohanKrishnamurthy",
            "https://www.everand.com/author/870315188/Mohan-Krishnamurthy",
            "https://fable.co/author/mohan-krishnamurthy",
            "https://www.facebook.com/mohan.madwachar",
            "https://x.com/madwachar",
            "https://www.instagram.com/mohanmadwachar/",
            "https://www.youtube.com/leomohan",
        ],
    }
    website = {"@context": "https://schema.org", "@type": "WebSite",
               "name": "Mohan Krishnamurthy", "url": f"{BASE}/"}
    books_ld = {"@context": "https://schema.org", "@type": "ItemList",
                "name": "Best Sellers by Mohan Krishnamurthy",
                "itemListElement": [
                    {"@type": "ListItem", "position": i + 1,
                     "item": {"@type": "Book", "name": b["title"],
                              "author": {"@type": "Person", "name": "Mohan Krishnamurthy"},
                              "image": f"{BASE}/{b['cover']}", "url": b["link"]}}
                    for i, b in enumerate(f["best_sellers"])]}

    body = f'''<section class="hero">
  <div class="container hero-grid">
    <div class="hero-text">
      <h1>Hi, I&rsquo;m Mohan.<br>Techie by Day; Storyteller by Night!</h1>
      <p class="lead">Mohan Krishnamurthy (Leo Mohan) is a writer, speaker, trainer, and cybersecurity professional &mdash; the author of books in English and Tamil spanning technology, fiction, business, humor, philosophy and spirituality.</p>
      <div class="btn-row">
        <a class="btn" href="https://www.linkedin.com/in/leomohan" target="_blank" rel="noopener">LinkedIn</a>
        <a class="btn btn-outline" href="mailto:leomohan@yahoo.com?subject=Connect%20From%20Website">eMail</a>
      </div>
    </div>
    <div class="hero-img">
      <a href="{hero["link"]}" target="_blank" rel="noopener">{img_tag(hero["cover"], hero["title"] + " — book cover", lazy=False)}</a>
    </div>
  </div>
</section>
<section class="section section--alt" id="recent">
  <div class="container">
    <h2 class="section-title">Recent Launches</h2>
    <p class="section-sub">A healthy mix of tech &amp; fiction!</p>
    <div class="feature-grid cols-4">
      {recent_cards}
    </div>
  </div>
</section>
<section class="section" id="bestsellers">
  <div class="container">
    <h2 class="section-title">Best Sellers</h2>
    <div class="seller-list">
      {seller_cards}
    </div>
  </div>
</section>
<section class="section section--alt" id="contact">
  <div class="container contact-grid">
    <div class="contact-img">{img_tag(LION_IMG, "Illustration of a lion walking across a stack of books")}</div>
    <div>
      <h2 class="section-title">Contact Me</h2>
      <p class="lead">Write to me, and let&rsquo;s exchange some great ideas over a coffee!</p>
      <div class="btn-row">
        <a class="btn" href="mailto:leomohan@yahoo.com?subject=Connect%20From%20Website">leomohan@yahoo.com</a>
        <a class="btn btn-outline" href="https://www.linkedin.com/in/leomohan" target="_blank" rel="noopener">Message on LinkedIn</a>
      </div>
    </div>
  </div>
</section>'''
    page("index.html",
         "Mohan Krishnamurthy — Author, Speaker & Cybersecurity Professional",
         "Official website of Mohan Krishnamurthy (Leo Mohan), author of books in English and Tamil across technology, fiction, business, humor and spirituality. Explore his books, articles, podcasts and videos.",
         body, hero["cover"], [person, website, books_ld], latest_article_url)

def build_sitemap(detail_pages):
    static_pages = ["index.html", "articles.html", "travel.html", "books.html",
        "inspiration.html", "business.html", "general.html", "philosophy.html",
        "spiritual.html", "technology.html", "fiction.html", "humor.html",
        "previousarticles.html", "youtube.html", "syngress.html", "storybooks.html",
        "tamil.html", "certifications.html", "gallery.html", "promos.html",
        "podcasts.html", "newreleases.html", "aboutme.html", "news.html"]
    lastmod = TODAY.isoformat()
    urls = "".join(
        f"\t<url>\n\t\t<loc>{BASE}/{p}</loc>\n\t\t<lastmod>{lastmod}</lastmod>\n\t</url>\n"
        for p in static_pages + detail_pages)
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>')
    print("built sitemap.xml", f"({len(static_pages) + len(detail_pages)} urls)")

def main():
    latest_article_url = load("articles.json")["latest"]["url"]
    build_index(latest_article_url)
    build_genre_pages(latest_article_url)
    detail_pages = build_releases(latest_article_url)
    build_news(latest_article_url)
    build_articles(latest_article_url)
    build_sitemap(detail_pages)
    print("\nDone. Review changes, then commit & push.")

if __name__ == "__main__":
    main()
