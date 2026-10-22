const $ = s => document.querySelector(s);
let tab;
chrome.tabs.query({ active: true, currentWindow: true }).then(([t]) => { tab = t; $("#title").textContent = t.title; });
$("#save").addEventListener("click", () => {
  $("#save").disabled = true;
  $("#status").className = ""; $("#status").textContent = "Saving…";
  chrome.runtime.sendMessage({ type: "save", tabId: tab.id, note: $("#note").value }, r => {
    $("#save").disabled = false;
    if (r?.ok) { $("#status").textContent = `Saved: ${r.file}`; setTimeout(() => window.close(), 1500); }
    else { $("#status").className = "bad"; $("#status").textContent = `Not saved: ${r?.error || "is os/server.py running?"}`; }
  });
});
