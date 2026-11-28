// Page logic for index.html and eksempel.html; data comes from the JSON block the pipeline fills in
const D = JSON.parse(document.getElementById("data").textContent);
const ICON = {"Mobil og nettbrett": "smartphone", "Rengjøring": "spray-can", "Sport og trening": "dumbbell", "Lyd": "headphones", "TV": "tv",
  "Data": "monitor", "Gaming og leker": "gamepad-2", "Kjøkken": "chef-hat", "Hvitevarer": "washing-machine", "Klær og sko": "shirt",
  "Helse og skjønnhet": "droplets", "Jul": "gift", "Annet": "package"};
const kr = n => Math.round(n).toLocaleString("nb-NO") + " kr";
const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
const icon = name => { const i = el("i"); i.dataset.lucide = name; return i; };
const icons = () => window.lucide && lucide.createIcons();  // page still works if the icon script is blocked
let cat = "Alle", sort = "t";
document.getElementById("demo").hidden = !D.demo;

document.getElementById("sub").textContent =
  new Date(D.day).toLocaleDateString("nb-NO", {day: "numeric", month: "long", year: "numeric"}) + (D.products
    ? ` · ${D.products} produkter i ${D.stores.length} butikker · ${D.deals.length} ekte tilbud · ${D.fakes.length} falske rabatter`
    : D.deals.length ? ` · ${D.deals.length} ekte tilbud` : "");

function media(img, category) {
  const m = el("div", "media");
  if (img) { const i = el("img"); i.src = img; i.alt = ""; i.loading = "lazy"; m.append(i); }
  else { m.classList.add("noimg"); m.append(icon(ICON[category] || "package")); }
  return m;
}

function spark(h) {
  const NS = "http://www.w3.org/2000/svg", svg = document.createElementNS(NS, "svg");
  svg.setAttribute("class", "spark"); svg.setAttribute("viewBox", "0 0 100 36"); svg.setAttribute("preserveAspectRatio", "none");
  svg.setAttribute("role", "img"); svg.setAttribute("aria-label", "Laveste pris de siste dagene");
  const lo = Math.min(...h), hi = Math.max(...h), y = v => 32 - (hi === lo ? 14 : (v - lo) / (hi - lo) * 28);
  const pts = h.map((v, i) => [(i / (h.length - 1) * 98 + 1).toFixed(1), y(v).toFixed(1)]);
  const area = document.createElementNS(NS, "path"); area.setAttribute("class", "area");
  area.setAttribute("d", `M${pts[0][0]} 36 L${pts.map(p => p.join(" ")).join(" L")} L${pts.at(-1)[0]} 36Z`);
  const line = document.createElementNS(NS, "polyline"); line.setAttribute("points", pts.map(p => p.join(",")).join(" "));
  const dot = document.createElementNS(NS, "circle"); dot.setAttribute("cx", pts.at(-1)[0]); dot.setAttribute("cy", pts.at(-1)[1]); dot.setAttribute("r", 2.5);
  svg.append(area, line, dot); return svg;
}

function card(d) {
  const c = el("article", "card"), m = media(d.img, d.cat);
  m.append(el("span", "tag", `−${d.real} %`), el("span", "temp" + (d.t >= 160 ? " hot" : ""), `${d.t}°`));
  const b = el("div", "body"), pr = el("div", "prices");
  pr.append(el("span", "price", kr(d.price)), el("span", "was", kr(d.ref)));
  b.append(el("span", "cat", d.cat), el("div", "name", d.name), pr, el("div", "where", d.editor
    ? `Hos ${d.store} · valgt av redaksjonen`
    : `Billigst hos ${d.store} · ${d.stores.length} ${d.stores.length === 1 ? "butikk" : "butikker"}`));
  if (d.claimed != null && Math.abs(d.claimed - d.real) >= 5) b.append(el("div", "warn", `Butikken oppgir −${d.claimed} %`));
  if (d.editor) b.append(el("div", "stores", `Laveste pris siste 30 dager: ${kr(d.low)}`));
  else b.append(spark(d.hist), el("div", "stores", d.stores.map(([s, p]) => `${s} ${kr(p)}`).join(" · ")));
  if (D.demo) b.append(el("span", "go", "Eksempel – ingen lenke"));
  else {
    const ad = !d.editor || d.aff;  // feed links are always affiliate links; hand-picked ones say so in chollos.csv
    const a = el("a", "go", `Se hos ${d.store}`); a.href = d.url; a.target = "_blank"; a.rel = ad ? "sponsored noopener" : "noopener";
    a.append(icon("arrow-up-right")); b.append(a);
    if (ad) b.append(el("div", "ad", "Reklamelenke"));
  }
  c.append(m, b); return c;
}

function render() {
  const g = document.getElementById("grid"); g.replaceChildren();
  const list = D.deals.filter(d => cat === "Alle" || d.cat === cat)
    .sort((a, b) => sort === "price" ? a.price - b.price : b[sort] - a[sort]);
  list.forEach(d => g.append(card(d)));
  if (!list.length && D.products) g.append(el("p", null, "Ingen ekte tilbud i denne kategorien i dag."));
  if (!list.length && !D.products) {
    const p = el("p", null, "Vi har nettopp startet og samler priser fra nettbutikkene hver dag. De første ekte tilbudene dukker opp her så snart vi har nok prishistorikk. ");
    const a = el("a", null, "Se et eksempel på hvordan siden vil se ut"); a.href = "/eksempel";
    p.append(a, "."); g.append(p);
  }
  icons();
}

const bar = document.getElementById("bar");
["Alle", ...new Set(D.deals.map(d => d.cat))].forEach(c => {
  const b = el("button", "chip", c); b.setAttribute("aria-pressed", c === cat);
  b.onclick = () => { cat = c; bar.querySelectorAll(".chip").forEach(x => x.setAttribute("aria-pressed", x === b)); render(); };
  bar.append(b);
});
const s = el("select"); s.setAttribute("aria-label", "Sorter");
[["t", "Hetest"], ["real", "Størst ekte rabatt"], ["price", "Lavest pris"]].forEach(([v, t]) => { const o = el("option", null, t); o.value = v; s.append(o); });
s.onchange = () => { sort = s.value; render(); };
bar.append(s);
bar.hidden = !D.deals.length;  // no filters to show before the first deals

const fb = document.getElementById("fakes");
D.fakes.forEach(f => {
  const tr = el("tr"), ti = el("td"), tp = el("td"), real = el("td");
  ti.append(media(f.img, f.cat));
  tp.append(el("div", null, f.name), el("div", "mute", `Nå ${kr(f.price)}`));
  real.append(el("div", "num", f.real > 0 ? `−${f.real} %` : f.real === 0 ? "0 %" : `+${-f.real} %, dyrere`),
              el("div", "mute", `Laveste pris var ${kr(f.low)}`));
  const claim = el("td"); claim.append(el("div", "claim", `−${f.claimed} %`), el("div", "mute", `Før ${kr(f.old)}`));
  tr.append(ti, tp, el("td", null, f.store), claim, real);
  fb.append(tr);
});
if (!D.fakes.length) { const tr = el("tr"), td = el("td", "mute", "Ingen i dag."); td.colSpan = 5; tr.append(td); fb.append(tr); }
render();
