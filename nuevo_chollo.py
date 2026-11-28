"""Add a hand-picked deal to chollos.csv: asks for the data, shows the verdict with the site's rules, saves it and can publish it.
Usage: python nuevo_chollo.py        (Enter on an optional field leaves it empty)"""
import csv, datetime as dt, subprocess, sys
from pathlib import Path
import pipeline as p

CSV = p.HERE / "chollos.csv"
ASK = [("fecha", "Fecha (AAAA-MM-DD, Enter = hoy)"), ("producto", "Producto"), ("tienda", "Tienda (p. ej. Elkjøp)"),
       ("enlace", "Enlace al producto (https://...)"), ("precio", "Precio de hoy (kr)"),
       ("minimo_30d", "Precio más bajo en esa tienda los últimos 30 días (kr)"),
       ("precio_normal", "Precio normal, el más habitual los últimos meses (kr, Enter = el mínimo de 30 días)"),
       ("precio_antes", "Precio anterior que anuncia la tienda, si anuncia rebaja (kr, opcional)"),
       ("categoria", "Categoría (Enter = automática)"), ("imagen", "URL de la imagen (opcional)"),
       ("afiliado", "¿Es un enlace de afiliado? (si/no)"), ("hasta", "Visible hasta (AAAA-MM-DD, Enter = 2 días)"),
       ("minimo_antes_oferta", "Precio más bajo en esa tienda en los 30 días ANTES de empezar la oferta (kr, opcional; solo si lo has visto)")]


def main():
    row = {k: input(f"{q}: ").strip() for k, q in ASK}
    row["fecha"] = row["fecha"] or dt.date.today().isoformat()
    try:
        e = p.editor_entry(row)
    except ValueError as x:
        sys.exit(f"\nNo se guarda: {x}")
    print(f"\nRebaja real: −{e['real']} % (de {e['ref']} kr a {e['price']:g} kr). Mínimo de 30 días: {e['low']:g} kr.")
    if e["claimed"] is not None:
        print(f"La tienda anuncia −{e['claimed']} % desde {e['old']:g} kr" + (" → DESCUENTO FALSO: ese precio anterior es más alto que el mínimo de los 30 días antes de la oferta." if e["fake"] else "."))
    print("Saldrá como chollo." if e["deal"] else "Saldrá solo en la tabla de descuentos falsos.")
    if input("\n¿Guardar? (s/n): ").strip().lower() != "s":
        return
    new = not CSV.exists() or CSV.stat().st_size == 0
    with open(CSV, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=p.EDITOR_COLS)
        if new:
            w.writeheader()
        w.writerow(row)
    print("Guardado en chollos.csv.")
    if input("¿Publicar ahora? (s/n): ").strip().lower() == "s":
        for cmd in (["git", "add", "chollos.csv"], ["git", "commit", "-m", f"Chollo: {e['name'][:60]}"], ["git", "push"]):
            subprocess.run(cmd, cwd=p.HERE, check=True)
        print("Subido. La web se actualiza sola en uno o dos minutos.")


if __name__ == "__main__":
    main()
