// Runs inside the page (via chrome.scripting) and returns what the clipper saves.
// Shared by the popup and the right-click menu.
function youlyticsGrab() {
  const meta = n => document.querySelector(`meta[name="${n}"], meta[property="${n}"]`)?.content || "";
  const main = document.querySelector("article") || document.querySelector("main") || document.body;
  return {
    url: location.href,
    title: meta("og:title") || document.title,
    site: meta("og:site_name") || location.hostname,
    description: meta("description") || meta("og:description"),
    selection: String(getSelection() || "").trim().slice(0, 20000),
    text: (main?.innerText || "").replace(/\n{3,}/g, "\n\n").trim().slice(0, 60000),
  };
}
