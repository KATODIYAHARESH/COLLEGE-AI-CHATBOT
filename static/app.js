const chatEl = document.getElementById("chat");
const qEl = document.getElementById("q");
const askBtn = document.getElementById("askBtn");

function esc(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function addMsg(cls, html) {
  const div = document.createElement("div");
  div.className = "msg " + cls;
  div.innerHTML = html;
  chatEl.appendChild(div);
  chatEl.scrollTop = chatEl.scrollHeight;
}

async function ask(question) {
  question = question.trim();
  if (!question) return;
  addMsg("user", "You: " + esc(question));
  askBtn.disabled = true;
  try {
    const res = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const d = await res.json();
    let html = esc(d.answer);
    if (d.sources && d.sources.length) {
      html += '<div class="sources">Sources: ' +
        d.sources.map((s) => `${esc(s.source)} (${s.score})`).join(", ") + "</div>";
    }
    addMsg("bot", html);
  } catch (e) {
    addMsg("bot", "Error: " + e.message);
  } finally {
    askBtn.disabled = false;
  }
}

askBtn.addEventListener("click", () => { ask(qEl.value); qEl.value = ""; });
qEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter") { ask(qEl.value); qEl.value = ""; }
});
document.querySelectorAll(".sample").forEach((b) => {
  b.addEventListener("click", () => { qEl.value = b.textContent; ask(b.textContent); });
});
