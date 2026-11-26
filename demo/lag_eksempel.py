"""Builds salida/eksempel.html: the page filled with the invented demo feeds, so brands can see the idea before real data exists.
Clearly marked as an example (banner), anonymous store names, no product photos, no links.
Usage: python demo/generar_feeds.py && python demo/lag_eksempel.py     (reads feeds/, which locally only holds demo feeds)"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pipeline as p

db = p.connect(":memory:")  # never touches precios.db, the real history
p.ingest(db, p.HERE / "feeds")
data = p.score(db)
names = {s: f"Butikk {chr(65 + i)}" for i, s in enumerate(data["stores"])}
for d in data["deals"]:
    d.update(store=names[d["store"]], img="", url="#", stores=[[names[s], price] for s, price in d["stores"]])
for f in data["fakes"]:
    f.update(store=names[f["store"]], img="", url="#")
data.update(stores=sorted(names.values()), demo=True)
assert data["deals"] and not any(d["img"] or d["url"] != "#" for d in data["deals"] + data["fakes"])
p.build(data, p.HERE / "salida" / "eksempel.html")
print(f"eksempel.html: {len(data['deals'])} tilbud, {len(data['fakes'])} falske rabatter, butikker {data['stores']}")
