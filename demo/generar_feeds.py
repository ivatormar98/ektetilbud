"""DEMO ONLY: invents 60 days of affiliate product feeds for 4 stores, so pipeline.py has history to work with.
Real feeds replace this: download them daily from Adtraction/Awin/Partner-ads into feeds/<YYYY-MM-DD>/<store>.<xml|csv>.
Usage: python demo/generar_feeds.py [end-date YYYY-MM-DD]"""
import csv, datetime as dt, json, random, sys
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).parent
OUT = HERE.parent / "feeds"
DAYS = 60
# store -> feed format, the way each network delivers it (Adtraction = XML, Awin = CSV)
STORES = {"komplett": "xml", "elkjop": "csv", "power": "xml", "netonnet": "csv"}
AWIN_COLS = ["aw_deep_link", "product_name", "merchant_product_id", "merchant_image_url", "merchant_category", "search_price",
             "merchant_name", "currency", "ean", "product_price_old", "in_stock", "brand_name"]


def ean13(n):
    body = f"70{n:010d}"  # 70 = Norway GS1 prefix
    check = (10 - sum(int(d) * (3 if i % 2 else 1) for i, d in enumerate(body)) % 10) % 10
    return body + str(check)


def nok(x):  # shop-style price: 4990, 1299 ...
    return max(49, round(x / 10) * 10 - 1 if x >= 200 else round(x) - 1)


def main():
    end = dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else dt.date.today()
    rnd = random.Random(42)
    products = json.load(open(HERE / "productos_demo.json", encoding="utf-8"))
    plan = []  # (product, ean, store, base, scenario)
    for i, p in enumerate(products):
        stores = rnd.sample(list(STORES), rnd.randint(2, 4))
        scenario = rnd.choices(["real", "inflado", "antes_falso", "normal"], [30, 15, 10, 45])[0]
        for j, s in enumerate(stores):
            # only the first store runs the special scenario, the rest stay normal
            plan.append((p, ean13(i + 1), s, p["price"] * rnd.uniform(0.97, 1.05), scenario if j == 0 else "normal"))

    for d in range(DAYS):
        day = end - dt.timedelta(days=DAYS - 1 - d)
        left = DAYS - 1 - d  # days until the end date
        rows = {s: [] for s in STORES}
        for p, ean, s, base, sc in plan:
            rnd_day = random.Random(f"{ean}{s}{d // 10}")  # price moves a little every 10 days
            price, old = base * rnd_day.uniform(0.96, 1.03), None
            if sc == "real" and left < 3:
                cut = random.Random(ean).uniform(0.15, 0.35)
                old, price = nok(base * 0.96), price * (1 - cut)  # honest store: "before" = its lowest recent price
            elif sc == "inflado" and 3 < left <= 25:
                price = base * 1.25  # raise the price for three weeks ...
            elif sc == "inflado" and left <= 3:
                old = nok(base * 1.25)  # ... then "discount" it back to normal
            elif sc == "antes_falso" and left < 5:
                old = nok(price * 1.4)  # invented "before" price, nothing changed
            rows[s].append({"ean": ean, "name": p["name"], "brand": p["brand"], "cat": p["category"], "img": p["image"],
                            "price": nok(price), "old": old, "url": f"https://www.{s}.no/demo/{ean}",
                            "stock": rnd_day.random() > 0.05})
        if d == DAYS - 1:  # one broken row, to show the pipeline skips it
            rows["elkjop"].append({**rows["elkjop"][0], "ean": "12345", "name": "Fila rota (EAN inválido)"})
        folder = OUT / day.isoformat()
        folder.mkdir(parents=True, exist_ok=True)
        for s, fmt in STORES.items():
            (write_xml if fmt == "xml" else write_csv)(folder / f"{s}.{fmt}", s, rows[s])
    print(f"{DAYS} días x {len(STORES)} tiendas -> {OUT}  ({len(products)} productos, {len(plan)} ofertas por día)")


def write_xml(path, store, rows):
    # Adtraction-style product feed
    tag = lambda k, v: f"<{k}>{escape(str(v))}</{k}>" if v is not None else f"<{k}/>"
    items = ["<product>" + "".join([tag("SKU", r["ean"][-6:]), tag("Name", r["name"]), tag("Category", r["cat"]), tag("Price", r["price"]),
                                    tag("Currency", "NOK"), tag("Instock", "yes" if r["stock"] else "no"), tag("TrackingUrl", r["url"]),
                                    tag("ImageUrl", r["img"]), tag("Brand", r["brand"]), tag("OriginalPrice", r["old"]), tag("Ean", r["ean"])])
             + "</product>" for r in rows]
    path.write_text('<?xml version="1.0" encoding="UTF-8"?>\n<products>\n' + "\n".join(items) + "\n</products>\n", encoding="utf-8")


def write_csv(path, store, rows):
    # Awin-style product feed
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, AWIN_COLS)
        w.writeheader()
        for r in rows:
            w.writerow({"aw_deep_link": r["url"], "product_name": r["name"], "merchant_product_id": r["ean"][-6:], "merchant_image_url": r["img"],
                        "merchant_category": r["cat"], "search_price": f"{r['price']:.2f}", "merchant_name": store.capitalize(), "currency": "NOK",
                        "ean": r["ean"], "product_price_old": f"{r['old']:.2f}" if r["old"] else "", "in_stock": int(r["stock"]), "brand_name": r["brand"]})


if __name__ == "__main__":
    main()
