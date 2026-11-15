"""Download today's affiliate feeds into feeds/<YYYY-MM-DD>/<store>.<xml|csv>.
Feed URLs carry your publisher token, so they live in environment variables (GitHub secrets), never in the repo.
fuentes.json lists them: [{"tienda": "komplett", "formato": "xml", "env": "FEED_KOMPLETT"}, ...]
Usage: python descargar_feeds.py"""
import datetime as dt, gzip, json, os, shutil, sys, urllib.request
from pathlib import Path

HERE = Path(__file__).parent
MAX_BYTES = 500 * 1024 * 1024  # refuse anything bigger than 500 MB


def download(url, dest):
    tmp = dest.with_suffix(".part")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "chollos-feed/1.0"})
        with urllib.request.urlopen(req, timeout=180) as r, open(tmp, "wb") as w:
            size = 0
            while chunk := r.read(1 << 20):
                size += len(chunk)
                if size > MAX_BYTES:
                    raise ValueError("feed too big")
                w.write(chunk)
        with open(tmp, "rb") as f:
            gz = f.read(2) == b"\x1f\x8b"  # Awin and others often serve gzip
        if gz:
            with gzip.open(tmp) as src, open(dest, "wb") as dst:
                shutil.copyfileobj(src, dst)
            tmp.unlink()
        else:
            tmp.replace(dest)
        return True
    except Exception as e:  # one broken feed must not stop the others
        print(f"FALLO {dest.stem}: {type(e).__name__} {e}", file=sys.stderr)
        tmp.unlink(missing_ok=True)
        return False


def main():
    out = HERE / "feeds" / dt.date.today().isoformat()
    out.mkdir(parents=True, exist_ok=True)
    ok = 0
    for src in json.load(open(HERE / "fuentes.json", encoding="utf-8")):
        url = os.environ.get(src["env"], "").strip()
        if src["formato"] not in ("xml", "csv") or not url.startswith("https://"):
            print(f"saltado {src['tienda']}: falta la variable {src['env']} o el formato no es xml/csv")
            continue
        ok += download(url, out / f"{src['tienda']}.{src['formato']}")
    print(f"{ok} catálogos descargados en {out}")


if __name__ == "__main__":
    main()
