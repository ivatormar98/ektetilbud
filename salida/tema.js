// Light/dark override. Loaded blocking in <head> (CSP forbids inline scripts) so the stored choice applies before first paint.
// No stored value = follow the system; the button stores only a choice that differs from the system (two-state toggle).
(() => {
  const meta = document.querySelector('meta[name="color-scheme"]');
  const read = () => { try { return localStorage.getItem("color-scheme"); } catch { return null; } };
  meta.content = read() ?? "light dark";
  const system = () => matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  addEventListener("storage", e => { if (e.key === "color-scheme") meta.content = e.newValue ?? "light dark"; });  // other tabs
  document.addEventListener("click", e => {
    if (!e.target.closest("[data-tema]")) return;
    const shown = meta.content === "light dark" ? system() : meta.content, target = shown === "dark" ? "light" : "dark";
    try { target === system() ? localStorage.removeItem("color-scheme") : localStorage.setItem("color-scheme", target); } catch { /* blocked storage: still switch */ }
    meta.content = target === system() ? "light dark" : target;
  });
})();
