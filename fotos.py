"""Shrink the carousel photos in salida/img/ before publishing: max 1600 px on the long side, re-encoded in the same format
(same file name, so chollos.csv keeps working). Run by the workflow on the copy it publishes; safe to run locally too."""
from pathlib import Path
from PIL import Image, ImageOps

MAX, LIMIT = 1600, 300_000  # px on the long side; files under this many bytes that already fit are left alone
SAVE = {".jpg": ("JPEG", {"quality": 82, "optimize": True, "progressive": True}), ".jpeg": ("JPEG", {"quality": 82, "optimize": True, "progressive": True}),
        ".png": ("PNG", {"optimize": True}), ".webp": ("WEBP", {"quality": 80, "method": 6})}


def shrink(path):
    fmt, opts = SAVE[path.suffix.lower()]
    with Image.open(path) as im:
        if max(im.size) <= MAX and path.stat().st_size <= LIMIT:
            return False
        im = ImageOps.exif_transpose(im)  # phone photos: apply the rotation before EXIF is dropped
        im.thumbnail((MAX, MAX))
        if fmt == "JPEG" and im.mode not in ("RGB", "L"):
            im = im.convert("RGB")
        im.save(path, fmt, **opts)
    return True


def main(root=Path(__file__).parent / "salida" / "img"):
    files = [f for f in root.rglob("*") if f.suffix.lower() in SAVE]
    done = sum(shrink(f) for f in files)
    print(f"fotos: {done} de {len(files)} reducidas")


if __name__ == "__main__":
    main()
