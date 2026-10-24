// Right-click menu: save the page or the selected text to youlytics-OS.
importScripts("grab.js");
const SERVER = "http://127.0.0.1:8765/api/clip";

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({ id: "page", title: "Save page to youlytics", contexts: ["page"] });
  chrome.contextMenus.create({ id: "selection", title: "Save selection to youlytics", contexts: ["selection"] });
});

async function save(tabId, note = "", onlySelection = false) {
  const [{ result }] = await chrome.scripting.executeScript({ target: { tabId }, func: youlyticsGrab });
  if (onlySelection) result.text = "";
  const r = await fetch(SERVER, { method: "POST", headers: { "Content-Type": "application/json" },
                                  body: JSON.stringify({ ...result, note }) });
  if (!r.ok) throw new Error((await r.json().catch(() => ({}))).error || `HTTP ${r.status}`);
  return r.json();
}

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  try {
    await save(tab.id, "", info.menuItemId === "selection");
    chrome.action.setBadgeText({ tabId: tab.id, text: "✓" });
  } catch (e) {
    chrome.action.setBadgeText({ tabId: tab.id, text: "!" });
    console.warn("youlytics clipper:", e.message);
  }
  setTimeout(() => chrome.action.setBadgeText({ tabId: tab.id, text: "" }), 3000);
});

chrome.runtime.onMessage.addListener((msg, _sender, reply) => {
  if (msg.type !== "save") return;
  save(msg.tabId, msg.note).then(r => reply({ ok: true, file: r.file }), e => reply({ ok: false, error: e.message }));
  return true;  // reply later
});
