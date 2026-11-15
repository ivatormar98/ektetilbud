"""Self-check for pipeline.py: python test_pipeline.py  (no test framework needed)"""
import csv, datetime as dt, tempfile
from pathlib import Path
import pipeline as p

COLS = list(p.FIELDS["csv"].values())


def write_day(root, day, rows):
    d = Path(root) / day
    d.mkdir(parents=True, exist_ok=True)
    with open(d / "tienda.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(COLS)
        for ean, price, old in rows:  # ean, name, brand, cat, img, price, old, url, stock, currency
            w.writerow([ean, f"Producto {ean[-1]}", "Marca", "TV", "https://img/x.jpg", price, old or "", f"https://shop/{ean}", "1", "NOK"])


def test_end_to_end():
    A, B = "7000000000017", "7000000000024"
    start = dt.date(2026, 10, 1)
    with tempfile.TemporaryDirectory() as tmp:
        for i in range(40):
            # A: 1000 kr, raised to 1250 on day 20, "discounted" back to 1000 (before 1250) on days 38-39 -> fake
            a = (1000, None) if i < 20 else (1250, None) if i < 38 else (1000, 1250)
            # B: 2000 kr for 39 days, then 1500 (before 2000) on the last day -> real 25 % deal, honest "before"
            b = (2000, None) if i < 39 else (1500, 2000)
            write_day(tmp, (start + dt.timedelta(days=i)).isoformat(), [(A, *a), (B, *b), ("12", 10, None)])
        db = p.connect(":memory:")
        added, skipped = p.ingest(db, tmp)
        assert (added, skipped) == (80, 40), (added, skipped)
        assert p.ingest(db, tmp) == (0, 0), "second run must skip loaded days"
        r = p.score(db)
        assert [d["name"] for d in r["deals"]] == ["Producto 4"], r["deals"]
        assert r["deals"][0]["real"] == 25 and r["deals"][0]["claimed"] == 25
        assert [(f["name"], f["claimed"], f["low"], f["real"]) for f in r["fakes"]] == [("Producto 7", 20, 1000, 0)], r["fakes"]


def test_clean_rejects_bad_rows():
    ok = {"ean": "7000000000017", "name": "X", "price": "1 299,00", "url": "https://a", "currency": "NOK", "stock": "yes"}
    assert p.clean(ok)["price"] == 1299
    for bad in ({"ean": "12"}, {"price": "0"}, {"url": "javascript:alert(1)"}, {"currency": "SEK"}, {"name": ""}):
        assert p.clean({**ok, **bad}) is None, bad
    assert p.clean({**ok, "old": "999"})["old"] is None, "a 'before' price below the price is ignored"
    assert p.clean({**ok, "img": "http://insecure"})["img"] == ""


if __name__ == "__main__":
    test_clean_rejects_bad_rows()
    test_end_to_end()
    print("ok")
