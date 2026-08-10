import os
import time

import pymysql
from flask import Flask, request, redirect, render_template_string, jsonify, abort

app = Flask(__name__)

DB = dict(
    host=os.environ.get("DB_HOST", "db"),
    port=int(os.environ.get("DB_PORT", 3306)),
    user=os.environ.get("DB_USER", "shortener"),
    password=os.environ.get("DB_PASSWORD", "shortener"),
    database=os.environ.get("DB_NAME", "shortener"),
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True,
)

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
ID_OFFSET = 100_000  # so the first code is 4 chars, not "1"


def encode(n):
    """Base62-encode an integer. n is always >= 1 here."""
    out = []
    while n:
        n, rem = divmod(n, 62)
        out.append(ALPHABET[rem])
    return "".join(reversed(out))


def connect():
    return pymysql.connect(**DB)


SCHEMA = """
CREATE TABLE IF NOT EXISTS links (
    id         BIGINT AUTO_INCREMENT PRIMARY KEY,
    code       VARCHAR(16) UNIQUE,
    long_url   TEXT NOT NULL,
    clicks     INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
)
"""


def init_db(retries=30, delay=2):
    """MySQL is slower to accept connections than Flask is to boot, so retry."""
    for attempt in range(retries):
        try:
            with connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(SCHEMA)
            print("database ready", flush=True)
            return
        except pymysql.err.OperationalError as e:
            print(f"waiting for mysql ({attempt + 1}/{retries}): {e}", flush=True)
            time.sleep(delay)
    raise RuntimeError("could not reach mysql")


FORM = """
<!doctype html>
<title>Shorten a link</title>
<style>
  body { font-family: system-ui, sans-serif; max-width: 40rem; margin: 4rem auto; padding: 0 1rem; }
  input[type=url] { width: 100%; padding: .6rem; font-size: 1rem; }
  button { margin-top: .75rem; padding: .6rem 1.2rem; font-size: 1rem; }
</style>
<h1>Shorten a link</h1>
<form method="post" action="/shorten">
  <input type="url" name="url" placeholder="https://example.com/some/long/path" required autofocus>
  <button type="submit">Shorten</button>
</form>
<p><a href="/stats">See all links</a></p>
"""

STATS = """
<!doctype html>
<title>Links</title>
<style>
  body { font-family: system-ui, sans-serif; max-width: 50rem; margin: 4rem auto; padding: 0 1rem; }
  table { border-collapse: collapse; width: 100%; }
  th, td { text-align: left; padding: .5rem .75rem; border-bottom: 1px solid #ddd; }
  td.url { max-width: 24rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
</style>
<h1>Links</h1>
<table>
  <tr><th>Code</th><th>Destination</th><th>Clicks</th><th>Created</th></tr>
  {% for row in rows %}
  <tr>
    <td><a href="/{{ row.code }}">{{ row.code }}</a></td>
    <td class="url">{{ row.long_url }}</td>
    <td>{{ row.clicks }}</td>
    <td>{{ row.created_at }}</td>
  </tr>
  {% else %}
  <tr><td colspan="4">No links yet.</td></tr>
  {% endfor %}
</table>
<p><a href="/">Shorten another</a></p>
"""


@app.route("/")
def index():
    return render_template_string(FORM)


@app.route("/shorten", methods=["POST"])
def shorten():
    url = (request.form.get("url") or (request.get_json(silent=True) or {}).get("url") or "").strip()
    if not url:
        return jsonify(error="url is required"), 400

    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO links (long_url) VALUES (%s)", (url,))
            new_id = cur.lastrowid
            code = encode(new_id + ID_OFFSET)
            cur.execute("UPDATE links SET code = %s WHERE id = %s", (code, new_id))

    return jsonify(code=code, short_url=request.host_url + code, long_url=url), 201


@app.route("/<code>")
def follow(code):
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT long_url FROM links WHERE code = %s", (code,))
            row = cur.fetchone()
            if row is None:
                abort(404)
            cur.execute("UPDATE links SET clicks = clicks + 1 WHERE code = %s", (code,))

    return redirect(row["long_url"], code=302)


@app.route("/stats")
def stats():
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT code, long_url, clicks, created_at FROM links ORDER BY id DESC"
            )
            rows = cur.fetchall()
    return render_template_string(STATS, rows=rows)


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
