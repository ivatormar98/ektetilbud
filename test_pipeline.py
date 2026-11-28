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


def test_build_keeps_data_inside_script():
    import json
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "i.html"
        p.build({"name": "</script><script>alert(1)</script>"}, out)
        html = out.read_text(encoding="utf-8")
        assert "alert(1)</script>" not in html, "data must not be able to close the script block"
        blob = html.split('id="data">')[1].split("</script>")[0]
        assert json.loads(blob)["name"].startswith("</script>"), "data must round-trip intact"


def test_editor_deals():
    import datetime as dt
    rows = [
        # real deal: 20 % below normal, at the 30-day low; store claims −50 % from an inflated price -> deal + fake
        ["2026-12-01", "Robotstøvsuger X", "Elkjøp", "https://e.no/x", "800", "800", "1000", "1600", "", "", "si", "", "1000"],
        # not cheaper than the 30-day low, honest claim -> rejected
        ["2026-12-01", "Kaffemaskin Y", "Power", "https://p.no/y", "900", "850", "1000", "", "", "", "", ""],
        # only a fake claim (price equals the low, nothing to save) -> fake only
        ["2026-12-01", "Hodetelefon Z", "Komplett", "https://k.no/z", "500", "500", "", "800", "", "", "", "", "500"],
        # claimed before-price but no pre-sale low known -> deal with a warning, never called fake
        ["2026-12-01", "Nettbrett W", "Komplett", "https://k.no/w", "1890", "1890", "2570", "3790", "", "", "", ""],
        # expired
        ["2026-11-01", "Gammel", "Power", "https://p.no/g", "500", "800", "", "", "", "", "", ""],
        # bad link
        ["2026-12-01", "Uten lenke", "Power", "http://p.no", "500", "800", "", "", "", "", "", ""],
    ]
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "c.csv"
        with open(f, "w", newline="", encoding="utf-8") as h:
            w = csv.writer(h); w.writerow(p.EDITOR_COLS); w.writerows(rows)
        deals, fakes, errors = p.editor(f, dt.date(2026, 12, 2))
    assert [d["name"] for d in deals] == ["Robotstøvsuger X", "Nettbrett W"], deals
    d = deals[0]
    assert d["real"] == 20 and d["claimed"] == 50 and d["aff"] and d["editor"] and d["cat"] == "Rengjøring"
    assert sorted(x["name"] for x in fakes) == ["Hodetelefon Z", "Robotstøvsuger X"], fakes
    assert len(errors) == 2 and "línea 3" in errors[0] and "línea 7" in errors[1], errors


def test_editor_images():
    folder = p.HERE / "salida" / "img" / "_test"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "1.webp").write_bytes(b"x")
    try:
        urls, missing = p.editor_images({"imagen": "", "imagenes": "_test/1.webp | https://cdn.example/a.jpg | _test/nope.webp | _test/../../pipeline.py | ../x.png"})
        assert urls == ["/img/_test/1.webp", "https://cdn.example/a.jpg"], urls
        assert missing == ["_test/nope.webp", "_test/../../pipeline.py", "../x.png"], missing
    finally:
        (folder / "1.webp").unlink(); folder.rmdir()


if __name__ == "__main__":
    test_editor_images()
    test_editor_deals()
    test_build_keeps_data_inside_script()
    test_clean_rejects_bad_rows()
    test_end_to_end()
    print("ok")
