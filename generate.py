#!/usr/bin/env python3
"""
Generatore di smart link pages per i singoli JjMart.
Crea un file HTML per ogni release Spotify; ognuno è autosufficiente
(nessuna risorsa esterna oltre alla copertina servita da i.scdn.co).
"""
import os, re, json, html

# --- Dati delle release (in ordine logico alfabetico) -----------------------
RELEASES = [
    # filename, title, spotify_url, cover_url
    ("agnese",   "Agnese",                 "https://open.spotify.com/album/7j1IMvwVMCRPwGd5GWJdMz",
        "https://i.scdn.co/image/ab67616d0000b273e3de1bb5d3189dbf39e5fdbb"),
    ("albachiara", "Albachiara",           "https://open.spotify.com/album/1bWusTfIghikR5ToJjzxxa",
        "https://i.scdn.co/image/ab67616d0000b273e396e5ab5766edfa463e06b6"),
    ("benedetta", "Benedetta",             "https://open.spotify.com/album/3BuZvQXSuKgbVunkN5kLSf",
        "https://i.scdn.co/image/ab67616d0000b273d8f67f9985dbdcfdca4ed172"),
    ("chiara",   "Chiara",                 "https://open.spotify.com/album/3PwgNSUMhaObSx0KN1K2jZ",
        "https://i.scdn.co/image/ab67616d0000b273fad705106787b34c7c36d330"),
    ("chico",    "Chico",                  "https://open.spotify.com/album/2teHkJSKwuss7esRHgOUlb",
        "https://i.scdn.co/image/ab67616d0000b273e89845b87772c45ce095b6b9"),
    ("da-te-a-me", "Da te a me",           "https://open.spotify.com/album/5r03F8X71qsL7d5qoA7bOh",
        "https://i.scdn.co/image/ab67616d0000b273087d74b02db6fb13ba3a2789"),
    ("falena",   "Falena",                 "https://open.spotify.com/track/5ijPQq7hW89R04wZTGiwDu",
        "https://i.scdn.co/image/ab67616d0000b2730f03bf3f7c40f47e6faf12bb"),
    ("lisa-e-l-antica-teiera", "Lisa e l'antica teiera",
        "https://open.spotify.com/album/5c2fIN7lIEUS3FRGPI9feS",
        "https://i.scdn.co/image/ab67616d0000b2731b1ec564b9278ed1362d1b22"),
    ("nemoriel", "Nemoriel",               "https://open.spotify.com/album/0D6oATVoeGgydSVaVU2XGX",
        "https://i.scdn.co/image/ab67616d0000b27327838a9cd4525694882faa51"),
    ("penelope", "Penelope",               "https://open.spotify.com/album/7hxPpVXkL301LD2LTyiFTR",
        "https://i.scdn.co/image/ab67616d0000b273f796eeb83ef41eb68e8eb5f7"),
    ("selene",   "Selene",                 "https://open.spotify.com/album/0fxzNzAcVEpmw1XEPx6ep0",
        "https://i.scdn.co/image/ab67616d0000b2732dec1f3db6e8bb1a74036569"),
    ("vera",     "Vera",                   "https://open.spotify.com/album/4v9mlW2ZiBmRVUaxiJzm6z",
        "https://i.scdn.co/image/ab67616d0000b273762620fd51efb27b2184fe1b"),
    ("virginia", "Virginia",               "https://open.spotify.com/album/4eaiVauKXTCEDdMGqrTB4R",
        "https://i.scdn.co/image/ab67616d0000b27369c0b1b739c198795bd04723"),
]

ARTIST = "JjMart"
ARTIST_URL = "https://open.spotify.com/artist/72PTEJIL6geBp5jBxrMkZA"

# Link social presi dalla pagina snd.click di riferimento
SOCIALS = [
    ("Instagram", "https://www.instagram.com/jjmart_prod",
     "M7.75 2h8.5A5.75 5.75 0 0 1 22 7.75v8.5A5.75 5.75 0 0 1 16.25 22h-8.5A5.75 5.75 0 0 1 2 16.25v-8.5A5.75 5.75 0 0 1 7.75 2zm0 1.5A4.25 4.25 0 0 0 3.5 7.75v8.5a4.25 4.25 0 0 0 4.25 4.25h8.5a4.25 4.25 0 0 0 4.25-4.25v-8.5A4.25 4.25 0 0 0 16.25 3.5h-8.5zM12 7a5 5 0 1 1 0 10 5 5 0 0 1 0-10zm0 1.5a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7zM17.5 6.25a.75.75 0 1 1 0 1.5.75.75 0 0 1 0-1.5z"),
    ("Facebook", "https://www.facebook.com/Jjmartprod",
     "M13.5 22v-8h2.7l.4-3.1h-3.1V8.9c0-.9.25-1.5 1.55-1.5h1.65V4.6c-.3 0-1.25-.1-2.35-.1-2.3 0-3.9 1.4-3.9 4v2.4H8v3.1h2.45V22h3.05z"),
    ("TikTok", "https://www.tiktok.com/@jjmart_prod",
     "M16.5 2c.2 1.6 1.1 3.1 2.5 4 .8.5 1.7.8 2.7.9v3.2c-1.7 0-3.3-.5-4.7-1.4v6.6c0 3.7-3 6.7-6.7 6.7S3.6 19 3.6 15.3s3-6.7 6.7-6.7c.4 0 .8 0 1.2.1v3.3c-.4-.1-.8-.2-1.2-.2-1.8 0-3.3 1.5-3.3 3.4s1.5 3.4 3.3 3.4 3.4-1.5 3.4-3.4V2h3z"),
    ("YouTube", "https://youtube.com/@jjmartproduction",
     "M23 12s0-3.4-.4-5c-.2-.9-.9-1.6-1.8-1.8C19.2 4.8 12 4.8 12 4.8s-7.2 0-8.8.4c-.9.2-1.6.9-1.8 1.8C1 8.6 1 12 1 12s0 3.4.4 5c.2.9.9 1.6 1.8 1.8 1.6.4 8.8.4 8.8.4s7.2 0 8.8-.4c.9-.2 1.6-.9 1.8-1.8.4-1.6.4-5 .4-5zM9.75 15.5v-7l6 3.5-6 3.5z"),
    ("SoundCloud", "https://soundcloud.com/jjmartprod",
     "M2 16.5c0-1.4.5-2.6 1.4-3.5v6.9C2.5 19 2 17.9 2 16.5zm2.5-4.3c.4-.2.9-.3 1.4-.3v8.2H4.5v-7.9zM7 11.6c.4 0 .9.1 1.3.2v8.3H7v-8.5zm2.4.4c.4.1.8.3 1.2.5v7.6H9.4V12zm2.3 1c.4.3.8.6 1.1 1v6.7h-1.1V13zm2.2 1.6c.3.4.5.9.6 1.4h4.1c1.8 0 3.3 1.4 3.3 3.2s-1.5 3.2-3.3 3.2h-4.8v-7.8z"),
]

PAGE_TEMPLATE = """<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,shrink-to-fit=no">
<title>{TITLE} — {ARTIST}</title>
<meta name="description" content="Ascolta &quot;{TITLE}&quot; di {ARTIST} su Spotify.">
<link rel="icon" href="{COVER}">

<!-- Open Graph / Twitter -->
<meta property="og:type" content="music.song">
<meta property="og:title" content="{TITLE} — {ARTIST}">
<meta property="og:description" content="Ascolta &quot;{TITLE}&quot; di {ARTIST} su Spotify.">
<meta property="og:image" content="{COVER}">
<meta property="og:url" content="{SPOTIFY}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{TITLE} — {ARTIST}">
<meta name="twitter:description" content="Ascolta &quot;{TITLE}&quot; di {ARTIST} su Spotify.">
<meta name="twitter:image" content="{COVER}">

<style>
  *,*::before,*::after{{box-sizing:border-box}}
  html,body{{margin:0;padding:0;min-height:100%;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Oxygen,Ubuntu,sans-serif;color:#fff;background:#0a0a0a}}
  /* sfondo: copertina sfocata + gradiente scuro */
  body::before{{content:"";position:fixed;inset:0;background:url("{COVER}") center/cover no-repeat;filter:blur(60px) saturate(140%) brightness(.55);transform:scale(1.2);z-index:-2}}
  body::after{{content:"";position:fixed;inset:0;background:radial-gradient(ellipse at top,rgba(0,0,0,.2),rgba(0,0,0,.85) 70%);z-index:-1}}
  main{{max-width:520px;margin:0 auto;padding:48px 24px 32px;text-align:center;display:flex;flex-direction:column;min-height:100vh}}
  .cover-wrap{{position:relative;width:min(360px,80vw);margin:0 auto 28px;aspect-ratio:1/1}}
  .cover{{width:100%;height:100%;border-radius:12px;box-shadow:0 30px 60px -10px rgba(0,0,0,.7),0 0 0 1px rgba(255,255,255,.05);display:block}}
  .cover-wrap::after{{content:"";position:absolute;left:6%;right:6%;bottom:-16px;height:30px;background:url("{COVER}") center/cover no-repeat;filter:blur(12px) saturate(120%);opacity:.6;border-radius:50%;z-index:-1}}
  .artist{{font-size:14px;letter-spacing:.18em;text-transform:uppercase;color:rgba(255,255,255,.7);margin:0 0 8px}}
  .artist a{{color:inherit;text-decoration:none}}
  .artist a:hover{{color:#fff}}
  h1{{font-size:28px;font-weight:600;letter-spacing:-.01em;margin:0 0 6px;line-height:1.2}}
  .tag{{font-size:13px;color:rgba(255,255,255,.55);margin:0 0 28px;letter-spacing:.04em}}
  .cta{{display:inline-flex;align-items:center;justify-content:center;gap:10px;background:#1db954;color:#fff;font-weight:600;font-size:15px;letter-spacing:.02em;text-decoration:none;padding:16px 28px;border-radius:999px;min-width:260px;transition:transform .15s ease,background .15s ease,box-shadow .15s ease;box-shadow:0 8px 24px -8px rgba(29,185,84,.6)}}
  .cta:hover{{background:#1ed760;transform:translateY(-1px);box-shadow:0 12px 28px -8px rgba(29,185,84,.8)}}
  .cta:active{{transform:translateY(0)}}
  .cta svg{{width:20px;height:20px;flex:none;fill:currentColor}}
  .socials{{margin-top:auto;padding-top:48px;display:flex;justify-content:center;gap:18px;flex-wrap:wrap}}
  .socials a{{display:inline-flex;align-items:center;justify-content:center;width:42px;height:42px;border-radius:50%;background:rgba(255,255,255,.08);color:rgba(255,255,255,.85);transition:background .15s ease,color .15s ease,transform .15s ease;text-decoration:none}}
  .socials a:hover{{background:rgba(255,255,255,.18);color:#fff;transform:translateY(-2px)}}
  .socials svg{{width:20px;height:20px;fill:currentColor}}
  footer{{margin-top:32px;font-size:12px;color:rgba(255,255,255,.4);letter-spacing:.05em}}
  footer a{{color:inherit;text-decoration:none;border-bottom:1px dotted rgba(255,255,255,.25)}}
  @media (max-width:480px){{
    main{{padding:32px 18px 24px}}
    h1{{font-size:24px}}
    .cta{{min-width:0;width:100%}}
  }}
</style>
</head>
<body>
  <main>
    <div class="cover-wrap">
      <img class="cover" src="{COVER}" alt="Copertina di {TITLE}" width="640" height="640" loading="eager">
    </div>

    <p class="artist"><a href="{ARTIST_URL}" target="_blank" rel="noopener">{ARTIST}</a></p>
    <h1>{TITLE}</h1>
    <p class="tag">Singolo · 2026</p>

    <div>
      <a class="cta" href="{SPOTIFY}" target="_blank" rel="noopener">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 0a12 12 0 1 0 0 24 12 12 0 0 0 0-24zm5.5 17.3a.75.75 0 0 1-1 .25c-2.8-1.7-6.3-2.1-10.4-1.1a.75.75 0 0 1-.35-1.46c4.5-1.1 8.4-.65 11.5 1.3.35.2.45.7.25 1.02zm1.5-3.3a.94.94 0 0 1-1.3.3c-3.2-2-8.1-2.55-11.9-1.4a.94.94 0 1 1-.55-1.8c4.35-1.32 9.8-.7 13.5 1.55.45.27.6.85.25 1.35zm.13-3.4C15.3 8.2 8.7 8 5 9.1a1.13 1.13 0 1 1-.66-2.16C8.6 5.7 15.9 5.95 20.3 8.5a1.13 1.13 0 0 1-1.17 1.93z"/></svg>
        Ascolta su Spotify
      </a>
    </div>

    <div class="socials">
{SOCIAL_BLOCK}
    </div>

    <footer>
      © 2026 {ARTIST} · <a href="index.html">tutte le uscite</a>
    </footer>
  </main>
</body>
</html>
"""

INDEX_TEMPLATE = """<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,shrink-to-fit=no">
<title>{ARTIST} — Tutte le uscite</title>
<meta name="description" content="Tutte le release di {ARTIST}.">
<link rel="icon" href="{FIRST_COVER}">
<meta property="og:type" content="music.musician">
<meta property="og:title" content="{ARTIST} — Tutte le uscite">
<meta property="og:image" content="{FIRST_COVER}">
<style>
  *,*::before,*::after{{box-sizing:border-box}}
  html,body{{margin:0;padding:0;min-height:100%;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Oxygen,Ubuntu,sans-serif;color:#fff;background:#0a0a0a}}
  body::before{{content:"";position:fixed;inset:0;background:linear-gradient(135deg,#1a1a1a 0%,#0a0a0a 50%,#151515 100%);z-index:-1}}
  header{{max-width:1100px;margin:0 auto;padding:60px 24px 24px;text-align:center}}
  header h1{{font-size:34px;margin:0 0 8px;font-weight:700;letter-spacing:-.02em}}
  header p{{margin:0;color:rgba(255,255,255,.55);font-size:14px;letter-spacing:.08em;text-transform:uppercase}}
  .grid{{max-width:1100px;margin:0 auto;padding:24px 24px 60px;display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:20px}}
  .card{{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.06);border-radius:12px;padding:14px;text-decoration:none;color:inherit;transition:background .15s ease,transform .15s ease,border-color .15s ease}}
  .card:hover{{background:rgba(255,255,255,.08);border-color:rgba(255,255,255,.15);transform:translateY(-3px)}}
  .card img{{width:100%;aspect-ratio:1/1;border-radius:8px;display:block;box-shadow:0 8px 20px -8px rgba(0,0,0,.6)}}
  .card .name{{font-size:15px;font-weight:600;margin:12px 4px 2px;line-height:1.3}}
  .card .meta{{font-size:12px;color:rgba(255,255,255,.5);margin:0 4px}}
  footer{{text-align:center;padding:30px 24px;font-size:12px;color:rgba(255,255,255,.35)}}
</style>
</head>
<body>
  <header>
    <h1>{ARTIST}</h1>
    <p>Singoli · 2026</p>
  </header>
  <div class="grid">
{CARDS}
  </div>
  <footer>© 2026 {ARTIST}</footer>
</body>
</html>
"""

def social_block():
    parts = []
    for name, url, path in SOCIALS:
        parts.append(
            f'      <a href="{url}" target="_blank" rel="noopener" aria-label="{name}" title="{name}">'
            f'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="{path}"/></svg></a>'
        )
    return "\n".join(parts)

def main():
    out = os.path.join(os.path.dirname(__file__), "site")
    os.makedirs(out, exist_ok=True)
    sb = social_block()

    for slug, title, spotify, cover in RELEASES:
        page = PAGE_TEMPLATE.format(
            TITLE=html.escape(title),
            ARTIST=html.escape(ARTIST),
            ARTIST_URL=ARTIST_URL,
            SPOTIFY=spotify,
            COVER=cover,
            SOCIAL_BLOCK=sb,
        )
        path = os.path.join(out, f"{slug}.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(page)
        print(f"wrote {path}")

    # index
    cards = []
    for slug, title, spotify, cover in RELEASES:
        cards.append(
            f'    <a class="card" href="{slug}.html">\n'
            f'      <img src="{cover}" alt="{html.escape(title)}" loading="lazy">\n'
            f'      <div class="name">{html.escape(title)}</div>\n'
            f'      <div class="meta">Singolo · 2026</div>\n'
            f'    </a>'
        )
    idx = INDEX_TEMPLATE.format(
        ARTIST=html.escape(ARTIST),
        FIRST_COVER=RELEASES[0][3],
        CARDS="\n".join(cards),
    )
    idx_path = os.path.join(out, "index.html")
    with open(idx_path, "w", encoding="utf-8") as f:
        f.write(idx)
    print(f"wrote {idx_path}")

if __name__ == "__main__":
    main()
