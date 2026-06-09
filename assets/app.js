
const topics = Array.isArray(window.PMR_TOPICS) ? window.PMR_TOPICS : [];
let activeCategory = "All";
let query = "";

const $ = (id) => document.getElementById(id);

function normalize(str) {
  return String(str || "").toLowerCase();
}

function groupedCategories() {
  const counts = new Map();
  topics.forEach(t => counts.set(t.category || "Other Topics", (counts.get(t.category || "Other Topics") || 0) + 1));
  return [["All", topics.length], ...Array.from(counts.entries()).sort((a, b) => a[0].localeCompare(b[0]))];
}

function filteredTopics() {
  return topics.filter(t => {
    const matchesCategory = activeCategory === "All" || t.category === activeCategory;
    const haystack = normalize(`${t.title} ${t.category} ${t.description} ${t.file}`);
    const matchesSearch = !query || haystack.includes(normalize(query));
    return matchesCategory && matchesSearch;
  });
}

function renderStats() {
  const topicCountEls = document.querySelectorAll("#topicCount");
  const categoryCountEls = document.querySelectorAll("#categoryCount");
  const lastUpdatedEls = document.querySelectorAll("#lastUpdated");

  const categories = new Set(topics.map(t => t.category || "Other Topics"));
  const last = topics.map(t => t.updated).filter(Boolean).sort().pop();

  topicCountEls.forEach(el => el.textContent = topics.length);
  categoryCountEls.forEach(el => el.textContent = categories.size);
  lastUpdatedEls.forEach(el => el.textContent = last || "-");
}

function renderTabs() {
  const el = $("categoryTabs");
  if (!el) return;
  el.innerHTML = "";
  groupedCategories().forEach(([category, count]) => {
    const btn = document.createElement("button");
    btn.className = "tab" + (category === activeCategory ? " active" : "");
    btn.textContent = `${category} (${count})`;
    btn.addEventListener("click", () => {
      activeCategory = category;
      renderTabs();
      renderGrid();
    });
    el.appendChild(btn);
  });
}

function renderGrid() {
  const el = $("topicGrid");
  const empty = $("emptyState");
  if (!el) return;

  const list = filteredTopics();
  el.innerHTML = "";

  if (empty) empty.style.display = list.length ? "none" : "block";

  list.forEach(t => {
    const card = document.createElement("article");
    card.className = "topic-card";
    card.innerHTML = `
      <span class="badge">${escapeHtml(t.category || "Other Topics")}</span>
      <h3>${escapeHtml(t.title)}</h3>
      <p>${escapeHtml(t.description || "")}</p>
      <div class="file-path">${escapeHtml(t.file)}</div>
      <div class="card-footer">
        <small>${escapeHtml(t.updated || "")}</small>
        <a class="open-link" href="${encodeURI(t.file)}">Open</a>
      </div>
    `;
    el.appendChild(card);
  });
}

function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function setupSearch() {
  const input = $("searchInput");
  if (!input) return;
  input.addEventListener("input", (e) => {
    query = e.target.value;
    renderGrid();
  });
}

function setupRandom() {
  const btn = $("randomBtn");
  if (!btn) return;
  btn.addEventListener("click", () => {
    const list = filteredTopics();
    if (!list.length) return;
    const topic = list[Math.floor(Math.random() * list.length)];
    window.location.href = topic.file;
  });
}

function setupTheme() {
  const btn = $("themeBtn");
  const saved = localStorage.getItem("pmr-hub-theme");
  if (saved === "dark" || saved === "light") {
    document.documentElement.dataset.theme = saved;
  } else {
    document.documentElement.dataset.theme = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  function updateLabel() {
    if (btn) btn.textContent = document.documentElement.dataset.theme === "dark" ? "Light mode" : "Night mode";
  }

  updateLabel();

  if (btn) {
    btn.addEventListener("click", () => {
      const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
      document.documentElement.dataset.theme = next;
      localStorage.setItem("pmr-hub-theme", next);
      updateLabel();
    });
  }
}

function setupPrint() {
  const btn = $("printBtn");
  if (btn) btn.addEventListener("click", () => window.print());
}

renderStats();
renderTabs();
renderGrid();
setupSearch();
setupRandom();
setupTheme();
setupPrint();
