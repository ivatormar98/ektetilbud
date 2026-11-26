# Prototipo: catálogos de afiliados → chollos reales

Sustituye a los scripts que copiaban Prisjakt y Prisradar. Lee los catálogos que dan las redes de afiliados, guarda el precio de cada producto cada día y publica solo los descuentos que son reales.

## Probarlo con datos de ejemplo

```bash
python demo/generar_feeds.py      # inventa 60 días de catálogos de 4 tiendas (solo demo)
python pipeline.py                # carga los catálogos, calcula y genera salida/index.html
python test_pipeline.py           # comprobación rápida
```

Después abre `salida/index.html` en el navegador.

`python demo/lag_eksempel.py` genera `salida/eksempel.html`. Es la página de ejemplo que se publica para las tiendas: datos inventados, marcada como «Eksempel», con tiendas anónimas y sin fotos ni enlaces. La portada la enlaza mientras no haya datos reales. Nunca toca `precios.db`.

## Archivos

| Archivo | Qué hace |
|---|---|
| `pipeline.py` | Carga los catálogos en `precios.db`, calcula los chollos y los descuentos falsos y genera la página |
| `plantilla.html` | Diseño de la página; el pipeline mete los datos donde pone `/*DATA*/null` |
| `test_pipeline.py` | Prueba un chollo real, un descuento falso y filas inválidas |
| `demo/` | Productos y generador de catálogos inventados. Con catálogos reales no hace falta |

## Con catálogos reales

1. Borra la carpeta `feeds/` de la demo y el archivo `precios.db`.
2. Cada día, descarga los catálogos en `feeds/AAAA-MM-DD/<tienda>.xml` (formato Adtraction) o `<tienda>.csv` (formato Awin).
3. Ejecuta `python pipeline.py`. Los días que ya cargó los salta.

**`precios.db` es el historial de precios: no lo borres.** Ahí está todo el valor del proyecto.

Los nombres de columna se han escrito según la documentación de Adtraction y Awin. Compruébalos con el primer catálogo real; están en `FIELDS`, al principio de `pipeline.py`.

## Publicarlo (GitHub Pages, gratis)

`.github/workflows/diario.yml` se ejecuta cada mañana. Pasa los tests, descarga los catálogos (`descargar_feeds.py`), actualiza el historial y la página (`pipeline.py`), guarda `precios.db` en el repositorio y publica la carpeta `salida/`.

1. Crea un repositorio en GitHub con el contenido de esta carpeta. Antes, borra `precios.db` para que no se mezclen los datos de la demo.
2. En GitHub, ve a Settings → Pages → Source y elige «GitHub Actions».
3. Por cada tienda:
   - añade una línea en `fuentes.json`
   - añade un *secret* en Settings → Secrets → Actions con la URL del catálogo (por ejemplo `FEED_KOMPLETT`); esa URL lleva tu token y no debe ir en el código
   - añade una línea `FEED_...` en el bloque `env` del workflow
4. Pulsa «Run workflow» la primera vez. Después corre solo cada día.
5. Rellena los `[din e-post]`, `[navn…]` y `[dato]` en `salida/om.html` y `salida/personvern.html`.
6. Dominio propio: en Settings → Pages → Custom domain, y un registro CNAME en tu proveedor del `.no`.

## Reglas

- **Chollo real:** precio al menos un 10 % por debajo de la mediana del mejor precio de los últimos 90 días y que sea el más bajo de los últimos 30 días. Hacen falta al menos 14 días de historial.
- **Descuento falso:** el «precio antes» que anuncia la tienda es más alto que el precio más bajo que ella misma cobró en los 30 días previos al inicio de la oferta (regla de *førpris*).
- **Temperatura:** misma fórmula que en Chollos Nórdicos (descuento real, ahorro en coronas y número de tiendas).

Las fotos de la demo salen de la captura anterior. Los catálogos reales traen las fotos de la propia tienda.
