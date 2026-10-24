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
   UI.nav(current)                    the shared top bar (Dashboard, Planner, Brain, Recos, Review) with a skip link
   UI.say(message)                    tell screen-reader users what just changed
   UI.markdown(text, {onTask, skipTitle})  plain Markdown to HTML (headings, lists, - [ ] tasks, tables); onTask(line, text, done) makes tasks tickable
*/
(function () {
  const UI = {};

  const MARK = '<svg viewBox="0 0 88 88" aria-hidden="true"><rect width="88" height="88" rx="18" fill="#1F3B70"/><path d="M26 24 L44 48 M62 24 L36 68" stroke="#fff" stroke-width="9" stroke-linecap="round" fill="none"/><circle cx="62" cy="24" r="6" fill="#D9962B"/></svg>';
  const PAGES = [["Dashboard", "/"], ["Planner", "/app/planner"], ["Brain", "/app/brain"], ["Recos", "/recos"], ["Review", "/app/review"]];

  UI.nav = current => {
    const main = document.querySelector("main");
    const header = main && main.querySelector(".ui-header");
    const target = header || main;
    if (target) { target.id = target.id || "content"; target.tabIndex = -1; }
    const nav = document.createElement("nav");
    nav.className = "ui-nav"; nav.setAttribute("aria-label", "youlytics-OS");
    const skip = Object.assign(document.createElement("a"), { className: "ui-skip", href: `#${target ? target.id : "main"}`, textContent: "Skip to content" });
    document.body.prepend(skip);
    nav.innerHTML = `<a class="brand" href="/">${MARK}<span>youlytics-OS</span></a>` +
      PAGES.map(([name, href]) => `<a class="tab" href="${href}"${name === current ? ' aria-current="page"' : ""}>${name}</a>`).join("");
    header ? header.before(nav) : (main || document.body).prepend(nav);
    return nav;
  };

  UI.say = msg => {
    let el = document.querySelector("#ui-say");
    if (!el) { el = Object.assign(document.createElement("div"), { id: "ui-say", className: "sr-only" }); el.setAttribute("aria-live", "polite"); document.body.append(el); }
    el.textContent = ""; setTimeout(() => { el.textContent = msg; }, 50);
  };

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

  UI.commentBox = ({ value = "", placeholder = "What should change?", label, onInput } = {}) => {
    const ta = document.createElement("textarea");
    ta.className = "ui-comment"; ta.value = value; ta.placeholder = placeholder;
    ta.setAttribute("aria-label", label || placeholder);
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
      <div class="ui-verdicts" role="group" aria-label="Verdict for ${UI.esc(title)}">
        <button class="ui-btn approve" type="button" data-v="approve">Approve</button>
        <button class="ui-btn change" type="button" data-v="change">Change</button>
        <button class="ui-btn skip" type="button" data-v="skip">Skip</button>
      </div>`;
    const box = UI.commentBox({ value: comment, onInput: v => { state.comment = v; onChange && onChange({ ...state }); } });
    box.setAttribute("aria-label", `What should change in ${title}`);
    card.querySelectorAll("pre").forEach(pre => { pre.tabIndex = 0; pre.setAttribute("aria-label", `Text of ${title}`); });
    card.append(box);
    const paint = () => {
      card.querySelectorAll("[data-v]").forEach(b => b.setAttribute("aria-pressed", String(b.dataset.v === state.verdict)));
      box.hidden = state.verdict !== "change" && !state.comment;
      card.classList.toggle("is-done", state.verdict === "skip");
    };
    card.querySelectorAll("[data-v]").forEach(b => b.addEventListener("click", () => {
      state.verdict = state.verdict === b.dataset.v ? "" : b.dataset.v;
      paint(); onChange && onChange({ ...state });
      UI.say(state.verdict ? `${title}: ${state.verdict}` : `${title}: no verdict`);
      if (state.verdict === "change") box.focus();
    }));
    paint();
    return card;
  };

  UI.cart = ({ count, label = "picked", button = "Copy for Claude", onCopy, onClear }) => {
    let bar = document.querySelector(".ui-cart");
    if (!bar) {
      bar = document.createElement("section"); bar.className = "ui-cart"; bar.setAttribute("aria-label", "Copy back to Claude");
      document.body.append(bar);
    }
    if (bar.dataset.count !== String(count)) { if (count) UI.say(`${count} ${label}`); bar.dataset.count = count; }
    bar.hidden = !count;
    bar.innerHTML = `<span><b>${count}</b> ${UI.esc(label)}</span>
      <button class="ui-btn highlight" type="button" data-copy>${UI.esc(button)}</button>
      ${onClear ? '<button class="ui-btn quiet" type="button" data-clear>Clear</button>' : ""}`;
    bar.querySelector("[data-copy]").onclick = onCopy;
    if (onClear) bar.querySelector("[data-clear]").onclick = onClear;
    return bar;
  };

  UI.markdown = (text, { onTask, skipTitle } = {}) => {
    const inline = s => UI.esc(s)
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
      .replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (m, label, href) => /^(https?:|\/|#)/.test(href.replace(/&amp;/g, "&")) ? `<a href="${href}">${label}</a>` : label);
    const lines = String(text || "").split("\n"), out = [];
    let list = null, tag = null, i = 0;
    const close = () => { if (list) { out.push(`</${tag}>`); list = tag = null; } };
    const open = (t, cls = "") => { if (list !== t + cls) { close(); out.push(`<${t}${cls ? ` class="${cls}"` : ""}>`); list = t + cls; tag = t; } };
    for (; i < lines.length; i++) {
      const l = lines[i], t = l.trim();
      let m;
      if (!t) { close(); continue; }
      if (skipTitle && !out.length && !list && /^# /.test(t)) continue;  // the page already shows a title
      if ((m = /^(#{1,3}) (.*)$/.exec(t))) { close(); const h = Math.min(m[1].length + 1, 3); out.push(`<h${h}>${inline(m[2])}</h${h}>`); continue; }
      if ((m = /^- \[( |x|X)\](?: (.*))?$/.exec(t))) {
        if (!(m[2] || "").trim()) continue;
        open("ul", "tasks");
        const done = m[1] !== " ";
        out.push(`<li><label class="task${done ? " done" : ""}"><input type="checkbox" ${done ? "checked" : ""} ${onTask ? "" : "disabled"} data-line="${i}" data-text="${UI.esc(m[2].trim())}"><span>${inline(m[2])}</span></label></li>`);
        continue;
      }
      if ((m = /^[-*] (.*)$/.exec(t))) { if (m[1].trim()) { open("ul"); out.push(`<li>${inline(m[1])}</li>`); } continue; }
      if ((m = /^\d+\. (.*)$/.exec(t))) { open("ol"); out.push(`<li>${inline(m[1])}</li>`); continue; }
      if (t.startsWith("|")) {
        close();
        const rows = [];
        for (; i < lines.length && lines[i].trim().startsWith("|"); i++) rows.push(lines[i].trim().replace(/^\||\|$/g, "").split("|").map(c => c.trim()));
        i--;
        const body = rows.slice(rows[1] && rows[1].every(c => /^:?-+:?$/.test(c)) ? 2 : 1);
        out.push(`<div class="ui-scroll"><table class="ui-table"><thead><tr>${rows[0].map(c => `<th scope="col">${inline(c)}</th>`).join("")}</tr></thead><tbody>${
          body.map(r => `<tr>${r.map(c => `<td>${inline(c)}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`);
        continue;
      }
      close(); out.push(`<p>${inline(t)}</p>`);
    }
    close();
    const el = document.createElement("div");
    el.className = "ui-md"; el.innerHTML = out.join("");
    if (onTask) el.querySelectorAll("input[data-line]").forEach(cb => cb.addEventListener("change", () => onTask(Number(cb.dataset.line), cb.dataset.text, cb.checked)));
    return el;
  };

  UI.copyBack = (intro, lines, outro) => [intro, "", ...lines, "", outro].filter(x => x !== undefined).join("\n").trim();

  window.UI = UI;
})();
