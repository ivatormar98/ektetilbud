# Plan: Chollos Nórdicos como proyecto personal

Objetivo: lanzarlo casi sin gastar y, si la gente lo usa, hacerlo crecer. Si no, te queda una herramienta útil para ti.

## 1. De dónde salen las ofertas

| Fuente | Qué da | Cómo conseguirla | Cuándo |
|---|---|---|---|
| **Adtraction** | Catálogo diario por tienda: precio, foto, EAN, enlace que cobra comisión. Komplett está aquí | Alta como sitio (necesitas la web publicada) y solicitar cada tienda | Semana 1 |
| **Partner-ads, Awin, Tradedoubler, Addrevenue** | Lo mismo, con otras tiendas | Igual; en cada red, mira qué tiendas noruegas tiene | Semanas 1–3 |
| **Tu propio historial** (`pipeline.py`) | Descuento real y descuentos falsos | Automático en cuanto entran catálogos | Desde el primer catálogo; sirve a partir de 14 días y la detección de falsos a partir de 30 |
| **Usuarios** | Cupones, tiendas sin afiliación, ofertas en tienda física | Formulario «enviar oferta» y votos | Fase 3, solo si hay uso |
| **Boletines y páginas de campaña de las tiendas** | Ofertas de Black Week, rebajas de enero | Seleccionarlas a mano | Puntual |
| **Prisjakt y Prisradar** | — | Solo para uso personal, o pidiendo licencia | No usar para publicar |

## 2. Lanzamiento

### Fase 0 · Esta semana: la base (coste ≈ 0)

- Traducir la página al noruego (bokmål). El público es noruego.
- Elegir un nombre y registrar un dominio `.no`, que los particulares pueden registrar (≈ 100–200 NOK/año).
- Alojamiento gratis en GitHub Pages o Cloudflare Pages. Un GitHub Action diario (gratis) descarga los catálogos, ejecuta `pipeline.py` y publica `salida/index.html`.
- Páginas mínimas: quién eres, política de privacidad y aviso de que los enlaces son de afiliado (*annonselenker*).
- Medir visitas con analítica sin cookies (GoatCounter o Plausible) para no necesitar banner de cookies.

### Fase 1 · Semanas 1–3: catálogos reales

- Darte de alta como sitio en Adtraction, Partner-ads y Awin con la web ya publicada. Las redes rechazan webs vacías, así que publica antes algo de contenido (la lista de descuentos falsos y una guía de cómo funciona *førpris*).
- Pedir 5–10 tiendas. Además de electrónica, mete hogar, deporte y belleza, que pagan más comisión.
- Empezar a guardar precios cuanto antes: el historial es lo que te diferencia y no se puede recuperar hacia atrás.
- Cobrar: las redes pagan a particulares, pero son ingresos que tributan. Cuando empiecen a entrar, registra un *enkeltpersonforetak* (ENK), gratis en Brønnøysund. El IVA (MVA) solo es obligatorio a partir de 50 000 NOK en 12 meses. Confírmalo con Skatteetaten.

### Fase 2 · Meses 1–2: primeros usuarios

- **Alertas automáticas** en un canal de Telegram o Discord para cada oferta de más de 160°, generadas desde el mismo pipeline.
- **Boletín semanal «Ukens falske tilbud»** (MailerLite o Buttondown, gratis hasta unos 1 000 suscriptores). Es el gancho más compartible.
- **Dónde moverlo:** hilos de ofertas de Diskusjon.no, r/norge (respetando sus normas sobre autopromoción), grupos de Facebook de ahorro, amigos y compañeros.
- **Calendario:**
  - Black Week (27 de noviembre) llega demasiado pronto para tener 30 días de historial, pero si empiezas a guardar precios ya, tendrás los precios de antes de la campaña.
  - Las rebajas de después de Navidad y enero (*mellomjulssalg*, *januarsalg*) son el primer gran momento realista para lanzarlo.

### Fase 3 · Meses 3–6: comunidad (solo si hay uso)

- Formulario «enviar oferta», votos que suben o bajan la temperatura y comentarios.
- Necesita un pequeño backend con capa gratuita (Supabase o Cloudflare D1) y tiempo de moderación.

## 3. Cómo saber si funciona (revisión a los 90 días)

| Señal | Objetivo |
|---|---|
| Visitas | ≥ 1 000 por semana |
| Suscriptores (boletín + Telegram) | ≥ 300 |
| Clics hacia tiendas | ≥ 20 % de las visitas |
| Comisiones | Las primeras confirmadas, para calcular cuánto ganas por clic |

- **Si se cumple:** más tiendas, comunidad y plantearse dedicarle más horas.
- **Si no:** se queda como herramienta personal, que cuesta casi nada mantener.

## 4. Costes a nivel personal

| Concepto | Coste |
|---|---|
| Dominio `.no` | ≈ 150 NOK/año |
| Alojamiento y ejecución diaria (GitHub Pages / Actions) | 0 |
| Boletín y analítica | 0 en las capas gratuitas |
| Registro ENK | 0 |
| **Total** | **< 500 NOK/año** |
| Tu tiempo | ≈ 5–10 h/semana los primeros meses |

## 5. Riesgos y cómo evitarlos

- **Catálogos sin «precio antes»:** no importa; el pipeline calcula el descuento real con su propio historial.
- **Redes que rechazan el alta:** publica contenido útil primero y vuelve a pedirla.
- **Fotos:** usa solo las del catálogo, que la tienda te da para promocionarla.
- **Tiendas molestas por salir en «descuentos falsos»:** muestra los datos con un tono neutro («su precio más bajo en 30 días fue X») y sin adjetivos.
