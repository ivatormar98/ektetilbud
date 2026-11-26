"""Chollos Nórdicos: affiliate product feeds -> SQLite price history -> real discounts -> one static HTML page.

Usage:  python pipeline.py [feeds_dir] [out.html]        defaults: feeds/  salida/index.html   (history in precios.db)
Feeds:  feeds/<YYYY-MM-DD>/<store>.xml  (Adtraction format)  or  <store>.csv  (Awin format). One folder per day.
Run it once a day after downloading the day's feeds; already loaded (day, store) files are skipped."""
import csv, datetime as dt, json, math, re, sqlite3, statistics, sys, xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).parent
MIN_HISTORY = 14   # days of price history needed before we judge a discount
MIN_REAL = 10      # % below the 90-day median to count as a deal
TOLERANCE = 1.01   # "before" price may be 1 % above the 30-day low (rounding) before we call it fake

# shortcut: column names as documented by Adtraction (XML) and Awin (CSV); check them against your first real feed.
FIELDS = {
    "xml": {"ean": "Ean", "name": "Name", "brand": "Brand", "cat": "Category", "img": "ImageUrl", "price": "Price",
            "old": "OriginalPrice", "url": "TrackingUrl", "stock": "Instock", "currency": "Currency"},
    "csv": {"ean": "ean", "name": "product_name", "brand": "brand_name", "cat": "merchant_category", "img": "merchant_image_url",
            "price": "search_price", "old": "product_price_old", "url": "aw_deep_link", "stock": "in_stock", "currency": "currency"},
}

# Store category / product name (Norwegian) -> our category. First match wins.
CATS = [(r"iphone|galaxy [saz]\d|mobiltelefon|nettbrett|lesebrett|pixel \d", "Mobil og nettbrett"),
        (r"robotstøvsuger|støvsuger|mopp|dampvasker", "Rengjøring"),
        (r"smartklokke|pulsklokke|aktivitetsmåler|løpesko|sykkel|ski\b", "Sport og trening"),
        (r"hodetelefon|høyttaler|lydplanke|ørepropp", "Lyd"), (r"^tv$|\btv\b|projektor", "TV"),
        (r"pc-skjerm|skjerm|tastatur|\bmus\b|pekeenhet|skriver|router|ssd|laptop", "Data"),
        (r"playstation|nintendo|konsoll|håndkontroll|lego|spill", "Gaming og leker"),
        (r"espresso|kaffe|mikser|blender|foodprosessor|kjøkken|airfryer|frityr|platetopp|ovn", "Kjøkken"),
        (r"vaskemaskin|tørketrommel|oppvask|kjøleskap|kombiskap|fryser|luftrenser", "Hvitevarer"),
        (r"jakke|sko|bukse|genser", "Klær og sko"), (r"parfyme|tannbørste|barber|hår|hud", "Helse og skjønnhet"),
        (r"julekalender", "Jul")]


STORE_NAMES = {"elkjop": "Elkjøp", "netonnet": "NetOnNet"}  # feed file name -> shown name; others are capitalized


def shop(slug):
    return STORE_NAMES.get(slug, slug.capitalize())


def categorize(cat, name):
    text = f"{cat} {name}".lower()
    return next((c for rx, c in CATS if re.search(rx, text)), "Annet")


def num(v):
    try:
        x = float(str(v).replace(" ", "").replace(",", "."))
        return x if math.isfinite(x) and x > 0 else None
    except ValueError:
        return None


def clean(raw):
    """Validate one feed row (feeds are third-party input). Returns a row dict or None to skip it."""
    ean = re.sub(r"\D", "", raw.get("ean") or "")
    price, name, url = num(raw.get("price")), (raw.get("name") or "").strip()[:300], (raw.get("url") or "").strip()
    if not (8 <= len(ean) <= 14) or not price or not name or not url.startswith("https://"):
        return None
    if (raw.get("currency") or "NOK").strip().upper() != "NOK":
        return None
    old = num(raw.get("old"))
    img = (raw.get("img") or "").strip()
    return {"ean": ean.zfill(13), "name": name, "brand": (raw.get("brand") or "").strip()[:80], "cat": (raw.get("cat") or "").strip()[:120],
            "img": img if img.startswith("https://") else "", "price": price, "old": old if old and old > price else None, "url": url,
            "stock": str(raw.get("stock", "")).strip().lower() in {"yes", "1", "true", "in stock", "instock", "ja"}}


def read_feed(path):
    fmt = path.suffix[1:].lower()
    f2k = {v: k for k, v in FIELDS[fmt].items()}
    if fmt == "csv":
        with open(path, encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                yield {f2k[k]: v for k, v in r.items() if k in f2k}
    else:
        for _, el in ET.iterparse(path):  # streaming: real feeds can be hundreds of MB
            if el.tag == "product":
                yield {f2k[c.tag]: c.text for c in el if c.tag in f2k}
                el.clear()


def connect(path):
    db = sqlite3.connect(path)
    db.executescript("""
      CREATE TABLE IF NOT EXISTS product(ean TEXT PRIMARY KEY, name TEXT, brand TEXT, cat TEXT, img TEXT);
      CREATE TABLE IF NOT EXISTS offer(ean TEXT, store TEXT, day TEXT, price REAL, old REAL, url TEXT, stock INT,
                                       PRIMARY KEY(ean, store, day));
      CREATE TABLE IF NOT EXISTS loaded(day TEXT, store TEXT, PRIMARY KEY(day, store));""")
    return db


def ingest(db, feeds):
    added = skipped = 0
    if not Path(feeds).is_dir():
        return added, skipped
    for day_dir in sorted(p for p in Path(feeds).iterdir() if re.fullmatch(r"\d{4}-\d{2}-\d{2}", p.name)):
        for f in sorted(day_dir.glob("*")):
            store = f.stem.lower()
            # shortcut: a re-downloaded feed for an already loaded day is ignored; delete its `loaded` row to reload it.
            if f.suffix[1:].lower() not in FIELDS or db.execute("SELECT 1 FROM loaded WHERE day=? AND store=?", (day_dir.name, store)).fetchone():
                continue
            for raw in read_feed(f):
                r = clean(raw)
                if not r:
                    skipped += 1
                    continue
                db.execute("""INSERT INTO product VALUES(:ean,:name,:brand,:cat,:img) ON CONFLICT(ean) DO UPDATE SET
                              name=excluded.name, brand=excluded.brand, cat=excluded.cat, img=COALESCE(NULLIF(excluded.img,''), img)""", r)
                db.execute("INSERT OR REPLACE INTO offer VALUES(:ean,:store,:day,:price,:old,:url,:stock)",
                           {**r, "store": store, "day": day_dir.name})
                added += 1
            db.execute("INSERT INTO loaded VALUES(?,?)", (day_dir.name, store))
    db.commit()
    return added, skipped


def shift(day, n):
    return (dt.date.fromisoformat(day) + dt.timedelta(days=n)).isoformat()


def presale_low(db, ean, store, day):
    """Lowest price the store charged in the 30 days before the current sale started (the legal "førpris")."""
    start = day
    for d, old in db.execute("SELECT day, old FROM offer WHERE ean=? AND store=? AND day<=? ORDER BY day DESC", (ean, store, day)):
        if old is None:
            break
        start = d
    return db.execute("SELECT MIN(price) FROM offer WHERE ean=? AND store=? AND day>=? AND day<?",
                      (ean, store, shift(start, -30), start)).fetchone()[0]


def temp(pct, save, stores):
    return round(pct * 3 + math.log2(1 + max(save, 0) / 10) * 9 + min(stores, 30))


def score(db, day=None):
    day = day or db.execute("SELECT MAX(day) FROM offer").fetchone()[0] or dt.date.today().isoformat()  # empty db: empty page
    # shortcut: loads 90 days of daily best prices into memory; fine up to ~100k products, move to SQL window functions beyond that.
    hist = {}
    for ean, d, best in db.execute("""SELECT ean, day, MIN(price) FROM offer WHERE stock=1 AND day>=? AND day<?
                                      GROUP BY ean, day ORDER BY day""", (shift(day, -90), day)):
        hist.setdefault(ean, []).append((d, best))
    today = {}
    for row in db.execute("""SELECT o.ean, o.store, o.price, o.old, o.url, p.name, p.brand, p.cat, p.img
                             FROM offer o JOIN product p USING(ean) WHERE o.day=? AND o.stock=1 ORDER BY o.price""", (day,)):
        today.setdefault(row[0], []).append(dict(zip(["ean", "store", "price", "old", "url", "name", "brand", "cat", "img"], row)))

    deals, fakes, no_history = [], [], 0
    for ean, offers in today.items():
        best, past = offers[0], hist.get(ean, [])
        for o in offers:  # check every advertised "before" price against the store's own 30-day low
            if o["old"]:
                low = presale_low(db, ean, o["store"], day)
                claimed = round((o["old"] - o["price"]) / o["old"] * 100)
                if low and claimed >= MIN_REAL and o["old"] > low * TOLERANCE:
                    fakes.append({"name": o["name"], "img": o["img"], "cat": categorize(o["cat"], o["name"]), "store": shop(o["store"]), "price": o["price"], "old": o["old"],
                                  "claimed": claimed, "low": low, "real": round((low - o["price"]) / low * 100), "url": o["url"]})
        if len(past) < MIN_HISTORY:
            no_history += 1
            continue
        ref = statistics.median(v for _, v in past)
        low30 = min(v for d, v in past if d >= shift(day, -30))
        real = round((ref - best["price"]) / ref * 100)
        if real < MIN_REAL or best["price"] > low30:
            continue
        claimed = round((best["old"] - best["price"]) / best["old"] * 100) if best["old"] else None
        deals.append({"name": best["name"], "brand": best["brand"], "cat": categorize(best["cat"], best["name"]), "img": best["img"],
                      "price": best["price"], "store": shop(best["store"]), "url": best["url"], "real": real, "ref": round(ref),
                      "claimed": claimed, "stores": [[shop(o["store"]), o["price"]] for o in offers],
                      "hist": [v for _, v in past[-60:]] + [best["price"]], "t": temp(real, ref - best["price"], len(offers))})
    deals.sort(key=lambda x: -x["t"])
    fakes.sort(key=lambda x: x["real"] - x["claimed"])
    stores = sorted({shop(o["store"]) for offers in today.values() for o in offers})
    return {"day": day, "deals": deals, "fakes": fakes, "products": len(today), "stores": stores, "no_history": no_history}


def build(data, out):
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text((HERE / "plantilla.html").read_text(encoding="utf-8").replace("/*DATA*/null", blob), encoding="utf-8")


def main():
    feeds = sys.argv[1] if len(sys.argv) > 1 else HERE / "feeds"
    out = sys.argv[2] if len(sys.argv) > 2 else HERE / "salida" / "index.html"
    db = connect(HERE / "precios.db")
    added, skipped = ingest(db, feeds)
    data = score(db)
    build(data, out)
    print(f"cargadas {added} filas nuevas ({skipped} descartadas por inválidas) | día {data['day']}: {data['products']} productos en "
          f"{len(data['stores'])} tiendas -> {len(data['deals'])} chollos reales, {len(data['fakes'])} descuentos falsos, "
          f"{data['no_history']} sin historial suficiente | {out}")


if __name__ == "__main__":
    main()
