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
  const o = el("button", "go open", "Se prissjekk"); o.type = "button";
  o.setAttribute("aria-label", `Se prissjekk: ${d.name}`); o.onclick = () => openDeal(d);
  o.append(icon("chevron-right")); b.append(o);
  c.append(m, b); return c;
}

// Deal sheet: native modal <dialog>; the browser handles focus, Esc and returning focus to the card.
const sheet = document.getElementById("ficha");
const slug = d => `${d.name}-${d.store}`.toLowerCase().replace(/æ/g, "ae").replace(/ø/g, "o").replace(/å/g, "a")
  .normalize("NFKD").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 90);

// Photo carousel: native scroll snap; the buttons and dots only steer the track (finite: a product has a handful of photos)
function gallery(d) {
  const imgs = d.imgs?.length ? d.imgs : d.img ? [d.img] : [];
  const g = el("section", "gal");
  if (!imgs.length) { const m = media("", d.cat); m.classList.add("big"); g.append(m); return g; }
  g.setAttribute("aria-roledescription", "karusell"); g.setAttribute("aria-label", `Bilder av ${d.name}`);
  const track = el("div", "gal-track"); track.tabIndex = 0; track.setAttribute("role", "group"); track.setAttribute("aria-label", "Bilder");
  imgs.forEach((src, i) => {
    const sl = el("div", "gal-slide"), im = el("img");
    sl.setAttribute("role", "group"); sl.setAttribute("aria-roledescription", "bilde"); sl.setAttribute("aria-label", `${i + 1} av ${imgs.length}`);
    im.src = src; im.alt = i ? "" : d.name; im.loading = i ? "lazy" : "eager"; im.decoding = "async";
    sl.append(im); track.append(sl);
  });
  if (imgs.length < 2) { g.append(track); return g; }
  const nav = el("div", "gal-nav"), prev = el("button"), next = el("button"), dots = el("nav", "gal-dots"), status = el("p", "vh");
  prev.type = next.type = "button"; prev.setAttribute("aria-label", "Forrige bilde"); next.setAttribute("aria-label", "Neste bilde");
  prev.append(icon("chevron-left")); next.append(icon("chevron-right")); nav.append(prev, next);
  dots.setAttribute("aria-label", "Velg bilde"); status.setAttribute("role", "status"); status.setAttribute("aria-live", "polite");
  const marks = imgs.map((_, i) => { const m = el("button"); m.type = "button"; m.setAttribute("aria-label", `Gå til bilde ${i + 1}`); m.onclick = () => go(i); return m; });
  dots.append(...marks);
  let pending = null, settled = 0, frame = 0;
  const at = () => Math.round(track.scrollLeft / track.clientWidth);
  const mark = i => marks.forEach((m, j) => m.setAttribute("aria-current", String(i === j)));
  const go = i => { pending = Math.max(0, Math.min(imgs.length - 1, i)); mark(pending); track.scrollTo({left: pending * track.clientWidth}); };
  prev.onclick = () => go((pending ?? at()) - 1); next.onclick = () => go((pending ?? at()) + 1);
  const settle = () => {
    pending = null; const i = at(); mark(i);
    const focused = document.activeElement;
    prev.disabled = i === 0; next.disabled = i === imgs.length - 1;
    if (focused === prev && prev.disabled) next.focus(); else if (focused === next && next.disabled) prev.focus();  // don't drop focus
    if (i !== settled) { settled = i; status.textContent = `Bilde ${i + 1} av ${imgs.length}`; }
  };
  track.addEventListener("scroll", () => {
    if (pending !== null || frame) return;
    frame = requestAnimationFrame(() => { frame = 0; mark(at()); });
  }, {passive: true});
  if ("onscrollend" in window) track.addEventListener("scrollend", settle);
  else { let t; track.addEventListener("scroll", () => { clearTimeout(t); t = setTimeout(settle, 120); }, {passive: true}); }
  mark(0); prev.disabled = true;
  g.append(nav, track, dots, status); return g;
}

// Price chart: step line of the daily lowest price (feeds: precios.db; hand-picked: our own precios_vistos.csv log), up to a year
const RANGES = [["1 mnd", 30], ["3 mnd", 91], ["6 mnd", 182], ["1 år", 365]], DAY = 864e5;
const shortDate = t => new Date(t).toLocaleDateString("nb-NO", {day: "numeric", month: "short"});
function priceChart(d, low) {
  const pts = (d.series || []).map(([day, v]) => [Date.parse(day), v]);
  const end = pts.length ? pts.at(-1)[0] : Date.now(), span = pts.length ? (end - pts[0][0]) / DAY : 0;
  const refs = d.editor ? [["Vanlig pris", d.ref], ["Laveste 30 dager", low]] : [["Median 90 dager", d.ref]];
  const box = el("section", "f-sec"), head = el("div", "ch-head"), tabs = el("div", "ch-tabs");
  tabs.setAttribute("role", "group"); tabs.setAttribute("aria-label", "Periode");
  head.append(el("h2", null, "Prisutvikling"), tabs);
  const NS = "http://www.w3.org/2000/svg", W = 360, H = 160, L = 50, R = 6, T = 14, B = 20;  // small viewBox so text stays legible when scaled
  const svg = document.createElementNS(NS, "svg"), wrap = el("div", "ch-wrap"), tip = el("div", "ch-tip");
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`); svg.setAttribute("class", "ch"); svg.setAttribute("role", "img"); tip.hidden = true;
  const mk = (tag, attrs) => { const n = document.createElementNS(NS, tag); for (const k in attrs) n.setAttribute(k, attrs[k]); return n; };
  let view = [], x, y;
  const draw = days => {
    tabs.querySelectorAll("button").forEach(b => b.setAttribute("aria-pressed", String(+b.value === days)));
    const from = end - days * DAY, before = pts.filter(p => p[0] < from).at(-1);
    view = [...(before ? [[from, before[1]]] : []), ...pts.filter(p => p[0] >= from)];  // carry the last earlier price to the left edge
    const vals = [...view.map(p => p[1]), ...refs.map(r => r[1])], pad = (Math.max(...vals) - Math.min(...vals) || Math.max(...vals) * .1) * .15;
    const lo = Math.min(...vals) - pad, hi = Math.max(...vals) + pad;
    x = t => L + (t - from) / (end - from) * (W - L - R); y = v => T + (hi - v) / (hi - lo) * (H - T - B);
    svg.replaceChildren();
    [hi - pad, (hi + lo) / 2, lo + pad].forEach(v => {
      svg.append(mk("line", {class: "grid", x1: L, x2: W - R, y1: y(v), y2: y(v)}));
      const t = mk("text", {x: L - 6, y: y(v) + 4, "text-anchor": "end"}); t.textContent = kr(v); svg.append(t);
    });
    refs.forEach(([k, v]) => {
      svg.append(mk("line", {class: "ref", x1: L, x2: W - R, y1: y(v), y2: y(v)}));
      const t = mk("text", {class: "ref-t", x: W - R - 12, y: y(v) - 5, "text-anchor": "end"}); t.textContent = k; svg.append(t);  // clear of the "now" dot
    });
    if (view.length > 1) {
      const line = view.map((p, i) => i ? `H${x(p[0]).toFixed(1)}V${y(p[1]).toFixed(1)}` : `M${x(p[0]).toFixed(1)} ${y(p[1]).toFixed(1)}`).join("");
      svg.append(mk("path", {class: "ar", d: `${line}H${x(end)}V${H - B}H${x(view[0][0])}Z`}), mk("path", {class: "ln", d: `${line}H${x(end)}`}));
    }
    const last = view.at(-1);
    if (last) svg.append(mk("circle", {class: "now", cx: x(end), cy: y(last[1]), r: 5}));
    [[L, "start", shortDate(from)], [W - R, "end", "I dag"]].forEach(([tx, an, s]) => {
      const t = mk("text", {x: tx, y: H - 5, "text-anchor": an}); t.textContent = s; svg.append(t);
    });
    const vs = view.map(p => p[1]);
    svg.setAttribute("aria-label", vs.length ? `Laveste pris siden ${shortDate(from)}: ${kr(Math.min(...vs))} til ${kr(Math.max(...vs))}. Nå ${kr(last[1])}.` : "Ingen priser ennå");
  };
  RANGES.forEach(([label, days], i) => {
    const b = el("button", null, label); b.type = "button"; b.value = days;
    b.disabled = i > 0 && span <= RANGES[i - 1][1];  // only offer a range that shows more than the shorter one
    b.onclick = () => draw(days); tabs.append(b);
  });
  svg.addEventListener("pointermove", e => {  // crosshair + price of that day
    if (view.length < 1) return;
    const r = svg.getBoundingClientRect(), sx = (e.clientX - r.left) / r.width * W;
    if (sx < L || sx > W - R) { tip.hidden = true; svg.querySelector(".xh")?.remove(); return; }
    const t = view[0][0] + (sx - L) / (W - L - R) * (end - view[0][0]), p = view.filter(q => q[0] <= t).at(-1) || view[0];
    let xh = svg.querySelector(".xh"); if (!xh) { xh = mk("line", {class: "xh", y1: T, y2: H - B}); svg.append(xh); }
    xh.setAttribute("x1", sx); xh.setAttribute("x2", sx);
    tip.hidden = false; tip.textContent = `${shortDate(Math.max(t, view[0][0]))}: ${kr(p[1])}`; tip.style.left = `${sx / W * 100}%`;
  });
  svg.addEventListener("pointerleave", () => { tip.hidden = true; svg.querySelector(".xh")?.remove(); });
  wrap.append(svg, tip); box.append(head, wrap);
  if (pts.length < 2) box.append(el("p", "ch-note", "Vi har nettopp begynt å logge prisen på dette produktet. Linjen fylles ut etter hvert som vi sjekker prisen."));
  draw((RANGES.find(([, days]) => days >= span) || RANGES.at(-1))[1]);
  return box;
}

function openDeal(d) {
  const info = el("div", "f-info");
  const h = el("h1", null, d.name); h.id = "f-name";
  const head = el("div"); head.append(h, el("p", "f-meta", `${d.cat} · ${d.editor ? `Hos ${d.store}` : `Billigst hos ${d.store}`}`));
  const pr = el("div", "f-price"); pr.append(el("span", "price", kr(d.price)), el("span", "was", kr(d.ref)), el("span", "tag inline", `−${d.real} %`));
  const low = d.editor ? d.low : Math.min(...d.hist.slice(-31));
  let desc = d.editor
    ? `Vanligvis ${kr(d.ref)}. Nå ${d.real} % billigere${d.price <= low ? ", og den laveste prisen i butikken de siste 30 dagene" : ""}.`
    : `Medianprisen de siste 90 dagene er ${kr(d.ref)}. Nå ${d.real} % lavere, og den laveste prisen den siste måneden.`;
  const off = d.claimed != null && Math.abs(d.claimed - d.real) >= 5;
  if (off) desc += ` Butikken oppgir −${d.claimed} %, men regnet mot vanlig pris er rabatten ${d.real} %.`;
  info.append(head, pr, el("p", "f-desc", desc));
  if (d.note) { const n = el("p", "f-note"); n.append(el("b", null, "Redaksjonen: "), d.note); info.append(n); }
  const chips = el("dl", "f-chips"), chip = (k, v, cls) => { const c = el("div", cls); c.append(el("dt", null, k), el("dd", null, v)); chips.append(c); };
  chip("Ekte rabatt", `−${d.real} %`, "good");
  chip(d.editor ? "Vanlig pris" : "Median 90 dager", kr(d.ref));
  if (d.claimed != null) chip("Butikken oppgir", `−${d.claimed} %`, off ? "bad" : null);
  info.append(chips);
  const hs = priceChart(d, low);
  if (!d.editor && d.stores.length > 1) {
    const st = el("dl", "f-stores"); d.stores.forEach(([s, p]) => st.append(el("dt", null, s), el("dd", null, kr(p)))); hs.append(st);
  }
  info.append(hs, el("p", "f-how", d.editor
    ? "Funnet og sjekket for hånd av redaksjonen: minst 10 % under vanlig pris og ikke høyere enn den laveste prisen i butikken de siste 30 dagene."
    : "Beregnet fra daglige priser: minst 10 % under medianen de siste 90 dagene og den laveste prisen den siste måneden."));
  const act = el("div", "f-act"), ad = !d.editor || d.aff;  // feed links are always affiliate links; hand-picked ones say so in chollos.csv
  if (D.demo) act.append(el("span", "go", "Eksempel – ingen lenke"));
  else {
    const a = el("a", "go primary", `Gå til ${d.store}`); a.href = d.url; a.target = "_blank"; a.rel = ad ? "sponsored noopener" : "noopener";
    a.append(icon("arrow-up-right")); act.append(a);
  }
  const url = `${location.origin}${location.pathname}#${slug(d)}`, sh = el("button", "go share", "Del"); sh.type = "button";
  sh.onclick = async () => {
    try { if (navigator.share) await navigator.share({title: d.name, url}); else { await navigator.clipboard.writeText(url); sh.textContent = "Lenke kopiert"; } }
    catch { /* the user closed the share sheet */ }
  };
  act.append(sh); info.append(act);
  if (ad && !D.demo) info.append(el("p", "ad", "Reklamelenke"));
  const left = el("div", "f-left"); left.append(gallery(d));
  if (d.credit) left.append(el("p", "gal-credit", `Foto: ${d.credit}`));
  document.getElementById("f-body").replaceChildren(left, info);
  sheet.showModal(); icons();
  // focus the main action without scrolling to it (on a phone it sits at the bottom, below the photos)
  (act.querySelector("a") || sheet.querySelector(".x")).focus({preventScroll: true}); sheet.scrollTop = 0;
  history.replaceState(null, "", `#${slug(d)}`);  // shareable link that opens this sheet
}
sheet.addEventListener("close", () => history.replaceState(null, "", location.pathname + location.search));
if (!("closedBy" in HTMLDialogElement.prototype)) {  // Safari: light dismiss without closedby
  const outside = e => { const r = sheet.getBoundingClientRect(); return e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom; };
  let down = false;
  sheet.addEventListener("pointerdown", e => { down = outside(e); });
  sheet.addEventListener("pointerup", e => { if (down && outside(e)) sheet.close(); });
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
const linked = D.deals.find(d => slug(d) === decodeURIComponent(location.hash.slice(1)));
if (linked) openDeal(linked);
