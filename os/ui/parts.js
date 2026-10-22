/* youlytics UI parts (ARMS A3). Plain script, no build step: <script src="/ui/parts.js"></script>
   Every local app builds from these so nothing is rebuilt from scratch.

   UI.esc(text)                       escape text for HTML
   UI.toast(message)                  short message at the top of the page
   UI.copy(text)                      copy to the clipboard, with a toast
   UI.store(key, fallback)            {get, set} on localStorage that never throws
   UI.save(url, data)                 POST JSON to the local server (the file is the record)
   UI.commentBox({value, placeholder, onInput})
   UI.reviewCard({title, tag, meta, body, facts, verdict, comment, onChange})
   UI.cart({count, label, onCopy, onClear})   bottom bar with the copy-back button
   UI.copyBack(intro, lines, outro)   the text that goes back to Claude
*/
(function () {
  const UI = {};

  UI.esc = t => String(t ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);

  UI.toast = msg => {
    let el = document.querySelector(".ui-toast");
    if (!el) { el = document.createElement("div"); el.className = "ui-toast"; el.setAttribute("role", "status"); document.body.append(el); }
    el.textContent = msg; el.classList.add("on");
    clearTimeout(el._t); el._t = setTimeout(() => el.classList.remove("on"), 2200);
  };

  UI.copy = async text => {
    try { await navigator.clipboard.writeText(text); }
    catch {
      const ta = Object.assign(document.createElement("textarea"), { value: text });
      document.body.append(ta); ta.select(); document.execCommand("copy"); ta.remove();
    }
    UI.toast("Copied. Paste it into Claude Code.");
  };

  UI.store = (key, fallback) => ({
    get() { try { const v = localStorage.getItem(key); return v ? JSON.parse(v) : fallback; } catch { return fallback; } },
    set(v) { try { localStorage.setItem(key, JSON.stringify(v)); } catch { /* private window: keep going */ } },
  });

  UI.save = async (url, data) => {
    const r = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) });
    if (!r.ok) UI.toast("Could not save. Is os/server.py running?");
    return r.ok;
  };

  UI.commentBox = ({ value = "", placeholder = "What should change?", onInput } = {}) => {
    const ta = document.createElement("textarea");
    ta.className = "ui-comment"; ta.value = value; ta.placeholder = placeholder;
    if (onInput) ta.addEventListener("input", () => onInput(ta.value));
    return ta;
  };

  UI.reviewCard = ({ title, tag, meta, body, facts, verdict = "", comment = "", onChange }) => {
    const card = document.createElement("article");
    card.className = "ui-card ui-review";
    const state = { verdict, comment };
    const factsHtml = facts ? `<dl class="ui-facts">${Object.entries(facts).map(([k, v]) => `<dt>${UI.esc(k)}</dt><dd>${UI.esc(v)}</dd>`).join("")}</dl>` : "";
    card.innerHTML = `
      <div class="ui-row">${tag ? `<span class="ui-tag ${UI.esc(tag)}">${UI.esc(tag)}</span>` : ""}<h3>${UI.esc(title)}</h3></div>
      ${meta ? `<p class="ui-sub">${UI.esc(meta)}</p>` : ""}
      ${body || ""}${factsHtml}
      <div class="ui-verdicts" role="group" aria-label="Verdict">
        <button class="ui-btn approve" type="button" data-v="approve">Approve</button>
        <button class="ui-btn change" type="button" data-v="change">Change</button>
        <button class="ui-btn skip" type="button" data-v="skip">Skip</button>
      </div>`;
    const box = UI.commentBox({ value: comment, onInput: v => { state.comment = v; onChange && onChange({ ...state }); } });
    card.append(box);
    const paint = () => {
      card.querySelectorAll("[data-v]").forEach(b => b.setAttribute("aria-pressed", String(b.dataset.v === state.verdict)));
      box.hidden = state.verdict !== "change" && !state.comment;
      card.classList.toggle("is-done", state.verdict === "skip");
    };
    card.querySelectorAll("[data-v]").forEach(b => b.addEventListener("click", () => {
      state.verdict = state.verdict === b.dataset.v ? "" : b.dataset.v;
      paint(); onChange && onChange({ ...state });
      if (state.verdict === "change") box.focus();
    }));
    paint();
    return card;
  };

  UI.cart = ({ count, label = "picked", button = "Copy for Claude", onCopy, onClear }) => {
    let bar = document.querySelector(".ui-cart");
    if (!bar) { bar = document.createElement("div"); bar.className = "ui-cart"; document.body.append(bar); }
    bar.hidden = !count;
    bar.innerHTML = `<span><b>${count}</b> ${UI.esc(label)}</span>
      <button class="ui-btn highlight" type="button" data-copy>${UI.esc(button)}</button>
      ${onClear ? '<button class="ui-btn quiet" type="button" data-clear>Clear</button>' : ""}`;
    bar.querySelector("[data-copy]").onclick = onCopy;
    if (onClear) bar.querySelector("[data-clear]").onclick = onClear;
    return bar;
  };

  UI.copyBack = (intro, lines, outro) => [intro, "", ...lines, "", outro].filter(x => x !== undefined).join("\n").trim();

  window.UI = UI;
})();
