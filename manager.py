#!/usr/bin/env python
"""
Site Manager for leomohan.net — local web app to update the site's JSON data.

  python manager.py        (or double-click manager.command)
  → http://localhost:5050

Features:
  1. Add a Book  — compresses the cover, saves it to assets/images/,
                   and adds the entry to data/books.json under its genre.
  2. Compress Images — batch-compress up to 10 images for the website.
  3. Rebuild Site — runs build.py so the HTML pages pick up your changes.

Nothing here touches the internet; it edits files in this folder only.
Review changes in GitHub Desktop and push when happy.
"""
import io, json, os, re, subprocess, sys, tempfile, time, zipfile

from flask import (Flask, flash, redirect, render_template_string, request,
                   send_file, url_for)
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
BOOKS_JSON = os.path.join(ROOT, "data", "books.json")
IMAGES_DIR = os.path.join(ROOT, "assets", "images")
MAX_EDGE = 1000
JPEG_QUALITY = 82
MAX_BATCH = 10

app = Flask(__name__)
app.secret_key = "local-site-manager"
_downloads = {}  # token -> zip path

GENRE_LABELS = {
    "business": "Business", "fiction": "Fiction", "general": "General",
    "humor": "Humor", "philosophy": "Philosophy", "spiritual": "Spiritual",
    "storybooks": "Storybooks", "tamil": "Tamil Works", "technology": "Technology",
}


def load_books():
    with open(BOOKS_JSON, encoding="utf-8") as f:
        return json.load(f)


def save_books(data):
    with open(BOOKS_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def slugify(text):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:60] or "book"


def compress_image(stream, dest_path):
    """Resize to MAX_EDGE and save as JPEG. Returns (width, height, bytes)."""
    img = Image.open(stream)
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[-1])
        img = bg
    elif img.mode != "RGB":
        img = img.convert("RGB")
    w, h = img.size
    if max(w, h) > MAX_EDGE:
        if w >= h:
            img = img.resize((MAX_EDGE, round(h * MAX_EDGE / w)), Image.LANCZOS)
        else:
            img = img.resize((round(w * MAX_EDGE / h), MAX_EDGE), Image.LANCZOS)
    img.save(dest_path, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
    return img.size + (os.path.getsize(dest_path),)


def unique_path(directory, base, ext=".jpg"):
    p = os.path.join(directory, base + ext)
    n = 2
    while os.path.exists(p):
        p = os.path.join(directory, f"{base}-{n}{ext}")
        n += 1
    return p


PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Site Manager — leomohan.net</title>
<style>
:root {
  --ivory:#FBF5E8; --savanna:#EDE0C4; --mane:#3D1F05; --amber:#C8860A;
  --tawny:#D4973E; --fur-pale:#F5E3B0; --muzzle:#FAF6EE;
  --font-head:"Palatino Linotype",Palatino,Georgia,serif;
  --font-body:"Avenir Next","Segoe UI",Helvetica,Arial,sans-serif;
  --shadow:0 2px 10px rgba(61,31,5,.10); --radius:10px;
}
*{box-sizing:border-box}
body{margin:0;font-family:var(--font-body);background:var(--ivory);color:var(--mane);line-height:1.6}
header{background:var(--muzzle);border-bottom:3px solid var(--amber);padding:1rem 1.5rem;box-shadow:var(--shadow);
  display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:.5rem}
header .brand{font-family:var(--font-head);font-size:1.3rem;font-weight:700}
header .note{font-size:.85rem;color:var(--amber);font-weight:600}
main{max-width:980px;margin:0 auto;padding:2rem 1.25rem}
h1,h2{font-family:var(--font-head)}
h1{font-size:1.9rem;margin:.2em 0 .1em}
h1::after{content:"";display:block;width:70px;height:4px;background:var(--amber);border-radius:2px;margin-top:.3em}
.sub{margin:.5em 0 2em}
.card{background:var(--muzzle);border:1px solid var(--fur-pale);border-top:4px solid var(--amber);
  border-radius:var(--radius);box-shadow:var(--shadow);padding:1.5rem;margin-bottom:2rem}
label{display:block;font-weight:600;margin:.9rem 0 .3rem}
input[type=text],input[type=url],select,textarea{width:100%;padding:.6rem .8rem;font:inherit;color:var(--mane);
  background:#fff;border:2px solid var(--savanna);border-radius:8px}
input:focus,select:focus,textarea:focus{outline:none;border-color:var(--amber)}
input[type=file]{margin-top:.3rem;font:inherit}
.btn{display:inline-block;margin-top:1.2rem;padding:.65rem 1.6rem;background:var(--amber);color:var(--ivory);
  font-weight:700;font-size:1rem;border:2px solid var(--amber);border-radius:999px;cursor:pointer}
.btn:hover{background:var(--tawny);border-color:var(--tawny);color:var(--mane)}
.btn.secondary{background:transparent;color:var(--mane);border-color:var(--mane)}
.btn.secondary:hover{background:var(--mane);color:var(--ivory)}
.flash{background:var(--fur-pale);border-left:5px solid var(--amber);border-radius:var(--radius);
  padding:1rem 1.25rem;margin-bottom:1.5rem;white-space:pre-wrap;font-size:.95rem}
.counts{display:flex;flex-wrap:wrap;gap:.5rem;margin:.6rem 0 0}
.chip{background:var(--fur-pale);border-radius:999px;padding:.2rem .8rem;font-size:.85rem;font-weight:600}
table{border-collapse:collapse;width:100%;margin-top:1rem}
td,th{text-align:left;padding:.5rem .6rem;border-bottom:1px solid var(--savanna);font-size:.95rem}
.hint{font-size:.85rem;color:#7a5a2f;margin-top:.3rem}
footer{text-align:center;color:#7a5a2f;font-size:.85rem;padding:2rem}
</style>
</head>
<body>
<header>
  <span class="brand">🦁 Site Manager</span>
  <span class="note">local only — edits data/books.json &amp; assets/images/</span>
</header>
<main>
<h1>leomohan.net Site Manager</h1>
<p class="sub">Add books, compress images, rebuild the site — then review &amp; push in GitHub Desktop.</p>

{% with messages = get_flashed_messages() %}
  {% for m in messages %}<div class="flash">{{ m }}</div>{% endfor %}
{% endwith %}

<div class="card">
  <h2>1 &middot; Add a Book</h2>
  <form method="post" action="{{ url_for('add_book') }}" enctype="multipart/form-data">
    <label for="title">Title</label>
    <input type="text" id="title" name="title" required placeholder="e.g. The Blank Book">
    <label for="genre">Genre</label>
    <select id="genre" name="genre" required>
      {% for key, label in genres.items() %}
      <option value="{{ key }}">{{ label }} ({{ counts[key] }} books)</option>
      {% endfor %}
    </select>
    <label for="link">Link to bookstore</label>
    <input type="url" id="link" name="link" required placeholder="https://www.amazon.in/dp/...">
    <label for="description">Description <span style="font-weight:400">(optional)</span></label>
    <textarea id="description" name="description" rows="3" placeholder="One or two sentences about the book"></textarea>
    <label for="cover">Cover image</label>
    <input type="file" id="cover" name="cover" accept="image/*" required>
    <p class="hint">The cover is resized to max {{ max_edge }}px, saved as an optimized JPEG in assets/images/, and the book is added at the top of its genre page.</p>
    <button class="btn" type="submit">Add Book</button>
  </form>
</div>

<div class="card">
  <h2>2 &middot; Compress Images</h2>
  <form method="post" action="{{ url_for('compress') }}" enctype="multipart/form-data">
    <label for="images">Select up to {{ max_batch }} images</label>
    <input type="file" id="images" name="images" accept="image/*" multiple required>
    <p class="hint">Each image is resized to max {{ max_edge }}px and saved as an optimized JPEG (quality {{ quality }}) — the same recipe used across the website. Transparent areas become white. You get a ZIP back.</p>
    <button class="btn" type="submit">Compress &amp; Download ZIP</button>
  </form>
</div>

<div class="card">
  <h2>3 &middot; Rebuild Site</h2>
  <p>Regenerates the home page, genre pages, new releases, news, articles and sitemap from the JSON files.</p>
  <form method="post" action="{{ url_for('rebuild') }}">
    <button class="btn secondary" type="submit">Run build.py</button>
  </form>
</div>

{% if results %}
<div class="card">
  <h2>Compression Results</h2>
  <table>
    <tr><th>File</th><th>Before</th><th>After</th><th>Saved</th></tr>
    {% for r in results %}
    <tr><td>{{ r.name }}</td><td>{{ r.before }}</td><td>{{ r.after }}</td><td>{{ r.saved }}</td></tr>
    {% endfor %}
  </table>
  <a class="btn" href="{{ url_for('download', token=token) }}">Download ZIP</a>
</div>
{% endif %}

</main>
<footer>Site Manager runs only on your Mac. Remember: rebuild &rarr; review in GitHub Desktop &rarr; push.</footer>
</body>
</html>"""


def fmt_size(n):
    return f"{n/1024:.0f} KB" if n < 1024 * 1024 else f"{n/1024/1024:.1f} MB"


@app.route("/")
def index():
    books = load_books()
    counts = {g: len(v["books"]) for g, v in books.items()}
    return render_template_string(PAGE, genres=GENRE_LABELS, counts=counts,
                                  max_edge=MAX_EDGE, quality=JPEG_QUALITY,
                                  max_batch=MAX_BATCH, results=None, token=None)


@app.route("/add-book", methods=["POST"])
def add_book():
    title = request.form.get("title", "").strip()
    genre = request.form.get("genre", "").strip()
    link = request.form.get("link", "").strip()
    description = request.form.get("description", "").strip()
    cover = request.files.get("cover")
    books = load_books()
    if not (title and link and cover and cover.filename and genre in books):
        flash("Missing field — title, genre, link and cover are all required.")
        return redirect(url_for("index"))

    dest = unique_path(IMAGES_DIR, "cover-" + slugify(title))
    try:
        w, h, size = compress_image(cover.stream, dest)
    except Exception as e:
        flash(f"Could not read that image ({e}). Try a JPEG or PNG.")
        return redirect(url_for("index"))

    rel = "assets/images/" + os.path.basename(dest)
    entry = {"title": title, "cover": rel, "link": link, "description": description}
    books[genre]["books"].insert(0, entry)
    save_books(books)
    flash(f"Added “{title}” to {GENRE_LABELS[genre]}.\n"
          f"Cover saved as {rel} ({w}×{h}, {fmt_size(size)}).\n"
          f"Now click “Run build.py”, then review & push in GitHub Desktop.")
    return redirect(url_for("index"))


@app.route("/compress", methods=["POST"])
def compress():
    files = request.files.getlist("images")[:MAX_BATCH]
    files = [f for f in files if f and f.filename]
    if not files:
        flash("No images selected.")
        return redirect(url_for("index"))

    tmpdir = tempfile.mkdtemp(prefix="sitemgr-")
    results = []
    for f in files:
        data = f.read()
        before = len(data)
        base = re.sub(r"\.[A-Za-z]+$", "", os.path.basename(f.filename))
        dest = unique_path(tmpdir, slugify(base) or "image")
        try:
            compress_image(io.BytesIO(data), dest)
        except Exception:
            continue
        after = os.path.getsize(dest)
        results.append(dict(name=os.path.basename(dest), before=fmt_size(before),
                            after=fmt_size(after),
                            saved=f"{max(0, 100 - round(after*100/before))}%"))
    if not results:
        flash("None of the selected files could be read as images.")
        return redirect(url_for("index"))

    zpath = os.path.join(tmpdir, "compressed-images.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for r in results:
            z.write(os.path.join(tmpdir, r["name"]), r["name"])
    token = str(int(time.time() * 1000))
    _downloads[token] = zpath

    books = load_books()
    counts = {g: len(v["books"]) for g, v in books.items()}
    return render_template_string(PAGE, genres=GENRE_LABELS, counts=counts,
                                  max_edge=MAX_EDGE, quality=JPEG_QUALITY,
                                  max_batch=MAX_BATCH, results=results, token=token)


@app.route("/download/<token>")
def download(token):
    zpath = _downloads.get(token)
    if not zpath or not os.path.exists(zpath):
        flash("That download has expired — compress again.")
        return redirect(url_for("index"))
    return send_file(zpath, as_attachment=True, download_name="compressed-images.zip")


@app.route("/rebuild", methods=["POST"])
def rebuild():
    proc = subprocess.run([sys.executable, os.path.join(ROOT, "build.py")],
                          capture_output=True, text=True, cwd=ROOT)
    out = (proc.stdout + proc.stderr).strip()
    flash(("Build OK!\n" if proc.returncode == 0 else "Build FAILED:\n") + out)
    return redirect(url_for("index"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    print(f"Site Manager → http://localhost:{port}")
    app.run(port=port, debug=False)
