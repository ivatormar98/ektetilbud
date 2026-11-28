# Prototipo: catálogos de afiliados → chollos reales

Sustituye a los scripts que copiaban Prisjakt y Prisradar. Lee los catálogos que dan las redes de afiliados, guarda el precio de cada producto cada día y publica solo los descuentos que son reales.

## Probarlo con datos de ejemplo

```bash
python demo/generar_feeds.py      # inventa 60 días de catálogos de 4 tiendas (solo demo)
python pipeline.py                # carga los catálogos, calcula y genera salida/index.html
python test_pipeline.py           # comprobación rápida
```

Después ejecuta `python serve.py` y abre http://localhost:8772. Sirve las mismas URLs limpias que GitHub Pages (`/om` en vez de `om.html`); abrir el archivo directamente ya no funciona.

`python demo/lag_eksempel.py` genera `salida/eksempel.html`. Es la página de ejemplo que se publica para las tiendas: datos inventados, marcada como «Eksempel», con tiendas anónimas y sin fotos ni enlaces. La portada la enlaza mientras no haya datos reales. Nunca toca `precios.db`.

## Publicar chollos a mano

Mientras no haya catálogos conectados, la portada se llena con chollos que eliges tú. Cada uno pasa por las mismas reglas que el motor automático: el precio tiene que estar al menos un 10 % por debajo del precio normal y no por encima del mínimo de esa tienda en los últimos 30 días. Si la tienda anuncia un precio anterior más alto que ese mínimo, sale también en «Rabatter som ikke er ekte».

- **Desde el ordenador:** `python nuevo_chollo.py`. Te pregunta los datos, te enseña el veredicto, lo guarda en `chollos.csv` y, si quieres, lo publica.
- **Desde el móvil:** edita `chollos.csv` en GitHub (botón del lápiz), añade una línea y pulsa «Commit changes». La web se actualiza sola en uno o dos minutos. Las líneas que no cumplen las reglas no salen; el motivo aparece en el registro de la ejecución en Actions.

Columnas: `fecha` (AAAA-MM-DD), `producto`, `tienda`, `enlace` (https), `precio`, `minimo_30d` (precio más bajo en esa tienda los últimos 30 días; míralo en el historial de precios), `precio_normal` (opcional, el precio habitual; por defecto el mínimo de 30 días), `precio_antes` (opcional, el precio anterior que anuncia la tienda), `categoria` (opcional), `imagen` (opcional, https), `afiliado` (`si` si el enlace es de afiliado: sale con la etiqueta «Reklamelenke»), `hasta` (opcional; por defecto el chollo se ve 2 días). `minimo_antes_oferta` (opcional): el precio más bajo de esa tienda en los 30 días *antes* de empezar la oferta, que es la førpris legal. Solo con este dato se marca un precio anterior como descuento falso; sin él la tarjeta muestra «Butikken oppgir −X %» sin acusar a nadie.

Apunta solo lo que hayas comprobado tú: eres responsable de lo que publicas como redacción.

## Fotos

La ficha de cada chollo tiene un carrusel. Sube las fotos a `salida/img/<carpeta-del-chollo>/` (por ejemplo `salida/img/sonos-beam/1.webp`, `2.webp`…): desde el ordenador, o en GitHub con «Add file → Upload files». Luego pon en la columna `imagenes` de `chollos.csv` los archivos separados por `|`: `sonos-beam/1.webp|sonos-beam/2.webp`. También valen URLs `https://` (las fotos que traen los catálogos de afiliado). La columna `nota` añade una frase tuya en noruego a la ficha.

Pon en la carpeta un `credito.txt`: la primera línea sale bajo el carrusel como «Foto: …» y la segunda guarda el enlace a la fuente. Usa solo fotos que puedas publicar: las de la sala de prensa de la marca, las del catálogo de afiliado o fotos propias. No copies las de la tienda si no eres su afiliado. Al publicar, `fotos.py` reduce cada foto a 1600 px como máximo; los originales del repositorio no cambian. Sin fotos, la ficha muestra el icono de la categoría.

## Historial de precios

La ficha dibuja el precio más bajo de cada día, hasta un año atrás, con vistas de 1 mes, 3 meses, 6 meses y 1 año. Los chollos automáticos usan `precios.db`. Los manuales usan nuestro propio registro, `precios_vistos.csv` (`fecha,producto,tienda,precio`): `nuevo_chollo.py` añade una línea cada vez que guardas un chollo, y puedes añadir más a mano cada vez que vuelvas a mirar un precio. El producto y la tienda tienen que escribirse igual que en `chollos.csv`. No copies series de precios de otras webs.

## Modo claro y oscuro

La web sigue el modo del sistema. El botón sol/luna del menú lo cambia y la elección se guarda en el navegador (localStorage, sin cookies). `salida/tema.js` la aplica antes de pintar la página.

## Archivos

| Archivo | Qué hace |
|---|---|
| `pipeline.py` | Carga los catálogos en `precios.db`, calcula los chollos y los descuentos falsos y genera la página |
| `plantilla.html` | Diseño de la página; el pipeline mete los datos donde pone `/*DATA*/null` (un bloque JSON, sin código) |
| `salida/app.js`, `salida/lucide.min.js` | Lógica de la página e iconos, servidos desde la propia web: la política CSP solo permite scripts propios. GoatCounter (`salida/count.js`, copia del script oficial) envía a `https://ivatormar.goatcounter.com`, permitido en `connect-src`. Para no contar tus propias visitas, abre https://ektetilbud.no/#toggle-goatcounter una vez en cada navegador |
| `salida/robots.txt`, `salida/sitemap.xml`, `salida/og.png`, `salida/favicon.svg` | SEO y vista previa al compartir. Si añades una página nueva, añádela al sitemap y copia las etiquetas `og:` del `<head>` |
| `salida/fonts.css`, `salida/fonts/` | Fuentes servidas desde la propia web (sin Google Fonts, que enviaba la IP del visitante a Google) |
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
5. Contacto: kontakt@ektetilbud.no, reenviado con ImprovMX (plan gratuito, solo recibe). Registros MX y SPF en Norgesdomene.
6. Dominio propio: en Settings → Pages → Custom domain, y un registro CNAME en tu proveedor del `.no`.

## Reglas

- **Chollo real:** precio al menos un 10 % por debajo de la mediana del mejor precio de los últimos 90 días y que sea el más bajo de los últimos 30 días. Hacen falta al menos 14 días de historial.
- **Descuento falso:** el «precio antes» que anuncia la tienda es más alto que el precio más bajo que ella misma cobró en los 30 días previos al inicio de la oferta (regla de *førpris*).
- **Temperatura:** misma fórmula que en Chollos Nórdicos (descuento real, ahorro en coronas y número de tiendas).

Las fotos de la demo salen de la captura anterior. Los catálogos reales traen las fotos de la propia tienda.
