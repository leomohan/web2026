# How to Update leomohan.net

The site is plain HTML, but the pages that change often are **generated from
JSON files** in the `data/` folder. Edit the JSON, run the build, push.

## The routine (every update)

1. Edit the relevant file in `data/` (see below)
2. **Double-click `build.command`** (or run `python3 build.py` in Terminal)
3. In GitHub Desktop: review the changes, commit, push

That's it. The build regenerates only the data-driven pages — it never touches
About Me, Certifications, Inspiration, Travel, Gallery, YouTube, Podcasts,
Promos, Syngress, or the Books hub.

## Adding a new book to a genre page

1. Copy the cover image into `assets/images/`
   (JPEG, ideally under 250 KB and no wider than 1000px)
2. In `data/books.json`, find the genre (e.g. `"fiction"`) and add to its
   `"books"` list:

```json
{
  "title": "My New Novel",
  "cover": "assets/images/my-new-novel.jpg",
  "link": "https://www.amazon.in/dp/B0XXXXXXXX",
  "description": ""
}
```

3. Build, commit, push.

Title is optional but recommended — when present, it appears under the cover
(good for readers and for Google). New books go at the start of the list to
appear first.

## Announcing a new release (with its own page)

1. Copy the cover into `assets/images/`
2. Write the book description as a small HTML snippet in
   `data/releases/<slug>.html` — use `<p>...</p>` per paragraph
   (copy an existing file in that folder as a template).
   The slug becomes the page URL: `<slug>.html`
3. Add an entry at the TOP of `"releases"` in `data/newreleases.json`:

```json
{
  "slug": "my-new-novel",
  "title": "My New Novel",
  "genre": "Fiction",
  "date": "July 2026",
  "cover": "assets/images/my-new-novel.jpg",
  "buy_link": "https://www.amazon.in/dp/B0XXXXXXXX",
  "buy_label": "Buy on Amazon"
}
```

4. Also add it to its genre in `data/books.json` (step above)
5. Build, commit, push.

## New LinkedIn article

In `data/articles.json`: move the current `"latest"` entry to the top of
`"archive"`, then set `"latest"` to the new article's title and URL.
Build, commit, push. (The nav's "Latest Article" link updates automatically.)

## Press coverage / news

In `data/news.json`:
- Clipping image → copy to `assets/images/`, add under `"press"`
- PDF → copy to `assets/docs/` with a descriptive filename, add under `"pdfs"`

## Changing the homepage

`data/featured.json` controls the hero book, the four Recent Launches, and
the Best Sellers (title, cover, link, description each). Swap entries as
books rise and fall.

## Things the build does for you

- Unique titles, descriptions, canonical and social-preview tags on every page
- Book schema (JSON-LD) for Google and AI assistants
- "Updated <today>" freshness stamps on New Releases and Articles
- sitemap.xml regenerated with today's date

## Don't forget

- `llms.txt` — when you add a notable book, add a line there too (plain text)
- New covers should be compressed (Preview.app: Tools → Adjust Size, then
  export at ~80% quality)
- For anything bigger than a data update, open Claude Code in this folder
  and describe what you want.
