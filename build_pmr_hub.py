from pathlib import Path
import re
import html
import json
import sys
from datetime import datetime

EXCLUDE = {
    "index.html",
    "about.html",
    "template.html",
}

CATEGORY_KEYWORDS = {
    "Musculoskeletal": [
        "oa", "osteoarthritis", "knee", "acl", "pcl", "shoulder", "rotator", "low back", "lbp",
        "spondy", "spine", "orthosis", "brace", "gait", "ankle", "hip", "tkr", "thr", "pain"
    ],
    "Neurologic Rehabilitation": [
        "stroke", "spasticity", "parkinson", "ssep", "emg", "ncv", "tms", "brain", "cord",
        "neuropathy", "radiculopathy", "plexus", "bpi", "cerebral", "sci"
    ],
    "Pediatric Rehabilitation": [
        "pediatric", "paediatric", "children", "child", "cp", "cerebral palsy", "down", "milestone",
        "congenital", "development", "speech", "cleft"
    ],
    "Cardiopulmonary Rehabilitation": [
        "cardiac", "cabg", "heart", "pulmonary", "copd", "ventilator", "imt", "respiratory",
        "dyspnea", "6mwt", "vo2", "exercise test", "chd"
    ],
    "Amputation and Prosthetics": [
        "amputation", "prosthesis", "prosthetic", "transtibial", "transfemoral", "stump", "residual limb"
    ],
    "Modalities and Therapeutic Exercise": [
        "laser", "lllt", "hilt", "eswt", "ultrasound", "diathermy", "tens", "nmes",
        "electrical", "biofeedback", "exercise", "strength", "stretching", "cryotherapy", "heat"
    ],
    "Geriatrics and General PM&R": [
        "geriatric", "sarcopenia", "frailty", "portfolio", "exam", "board", "rehabilitation"
    ],
}

STYLE_CSS = '\n:root {\n  --bg: #eef4f1;\n  --panel: #f8fbf8;\n  --panel-2: #ffffff;\n  --text: #17221f;\n  --muted: #5d6b66;\n  --line: #d8e3dd;\n  --brand: #4f7f73;\n  --brand-2: #6c9d8e;\n  --accent: #d9b56f;\n  --danger: #9c5148;\n  --shadow: 0 14px 35px rgba(22, 40, 34, 0.08);\n  --radius: 22px;\n}\n\n[data-theme="dark"] {\n  --bg: #101816;\n  --panel: #17231f;\n  --panel-2: #1d2b26;\n  --text: #edf6f2;\n  --muted: #a9b9b2;\n  --line: #2e433b;\n  --brand: #8bbcaf;\n  --brand-2: #a8d1c5;\n  --accent: #d7bc7d;\n  --danger: #e08c82;\n  --shadow: 0 14px 35px rgba(0, 0, 0, 0.25);\n}\n\n* {\n  box-sizing: border-box;\n}\n\nhtml {\n  scroll-behavior: smooth;\n}\n\nbody {\n  margin: 0;\n  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;\n  background:\n    radial-gradient(circle at top left, rgba(108, 157, 142, 0.20), transparent 34rem),\n    radial-gradient(circle at bottom right, rgba(217, 181, 111, 0.15), transparent 28rem),\n    var(--bg);\n  color: var(--text);\n  line-height: 1.55;\n}\n\na {\n  color: inherit;\n}\n\n.site-header {\n  position: sticky;\n  top: 0;\n  z-index: 20;\n  backdrop-filter: blur(16px);\n  background: color-mix(in srgb, var(--bg) 84%, transparent);\n  border-bottom: 1px solid var(--line);\n}\n\n.nav {\n  max-width: 1180px;\n  margin: 0 auto;\n  padding: 14px 22px;\n  display: flex;\n  align-items: center;\n  gap: 16px;\n}\n\n.brand {\n  display: flex;\n  align-items: center;\n  gap: 10px;\n  font-weight: 800;\n  letter-spacing: -0.03em;\n  text-decoration: none;\n}\n\n.logo {\n  width: 38px;\n  height: 38px;\n  border-radius: 12px;\n  display: grid;\n  place-items: center;\n  background: linear-gradient(135deg, var(--brand), var(--accent));\n  color: white;\n  font-weight: 900;\n}\n\n.nav-links {\n  margin-left: auto;\n  display: flex;\n  gap: 10px;\n  align-items: center;\n}\n\n.nav-links a,\n.icon-button,\n.primary-button,\n.secondary-button {\n  border: 1px solid var(--line);\n  background: var(--panel);\n  color: var(--text);\n  text-decoration: none;\n  padding: 9px 13px;\n  border-radius: 999px;\n  font-weight: 650;\n  cursor: pointer;\n  transition: transform 140ms ease, border-color 140ms ease, background 140ms ease;\n}\n\n.nav-links a:hover,\n.icon-button:hover,\n.primary-button:hover,\n.secondary-button:hover {\n  transform: translateY(-1px);\n  border-color: var(--brand);\n}\n\n.primary-button {\n  background: var(--brand);\n  color: white;\n  border-color: transparent;\n}\n\n.secondary-button {\n  background: transparent;\n}\n\n.container {\n  max-width: 1180px;\n  margin: 0 auto;\n  padding: 34px 22px 60px;\n}\n\n.hero {\n  display: grid;\n  grid-template-columns: 1.35fr 0.65fr;\n  gap: 22px;\n  align-items: stretch;\n  margin-top: 12px;\n}\n\n.hero-card,\n.panel {\n  background: color-mix(in srgb, var(--panel) 94%, transparent);\n  border: 1px solid var(--line);\n  border-radius: var(--radius);\n  box-shadow: var(--shadow);\n}\n\n.hero-card {\n  padding: 36px;\n  overflow: hidden;\n  position: relative;\n}\n\n.hero-card:after {\n  content: "";\n  position: absolute;\n  inset: auto -60px -120px auto;\n  width: 270px;\n  height: 270px;\n  background: color-mix(in srgb, var(--brand) 20%, transparent);\n  border-radius: 50%;\n}\n\n.kicker {\n  color: var(--brand);\n  font-weight: 800;\n  text-transform: uppercase;\n  letter-spacing: 0.08em;\n  font-size: 0.82rem;\n}\n\nh1 {\n  margin: 12px 0 12px;\n  font-size: clamp(2.1rem, 4.8vw, 4.25rem);\n  line-height: 0.98;\n  letter-spacing: -0.06em;\n}\n\nh2 {\n  margin: 0 0 16px;\n  letter-spacing: -0.035em;\n}\n\np {\n  color: var(--muted);\n  margin: 0 0 14px;\n}\n\n.hero-actions {\n  display: flex;\n  flex-wrap: wrap;\n  gap: 10px;\n  margin-top: 24px;\n}\n\n.stats-panel {\n  padding: 26px;\n  display: grid;\n  gap: 14px;\n}\n\n.stat {\n  padding: 18px;\n  border: 1px solid var(--line);\n  border-radius: 18px;\n  background: var(--panel-2);\n}\n\n.stat-value {\n  font-size: 2rem;\n  font-weight: 850;\n  letter-spacing: -0.05em;\n}\n\n.stat-label {\n  color: var(--muted);\n  font-weight: 650;\n  font-size: 0.92rem;\n}\n\n.toolbar {\n  margin: 24px 0 18px;\n  display: grid;\n  grid-template-columns: 1fr auto auto;\n  gap: 12px;\n  align-items: center;\n}\n\n.search {\n  width: 100%;\n  border: 1px solid var(--line);\n  background: var(--panel);\n  color: var(--text);\n  border-radius: 16px;\n  padding: 14px 16px;\n  font-size: 1rem;\n  outline: none;\n}\n\n.search:focus {\n  border-color: var(--brand);\n  box-shadow: 0 0 0 4px color-mix(in srgb, var(--brand) 18%, transparent);\n}\n\n.category-tabs {\n  display: flex;\n  gap: 8px;\n  overflow-x: auto;\n  padding: 4px 0 14px;\n}\n\n.tab {\n  white-space: nowrap;\n  border: 1px solid var(--line);\n  color: var(--text);\n  background: var(--panel);\n  padding: 9px 13px;\n  border-radius: 999px;\n  cursor: pointer;\n  font-weight: 650;\n}\n\n.tab.active {\n  color: white;\n  background: var(--brand);\n  border-color: var(--brand);\n}\n\n.grid {\n  display: grid;\n  grid-template-columns: repeat(3, minmax(0, 1fr));\n  gap: 16px;\n}\n\n.topic-card {\n  display: flex;\n  flex-direction: column;\n  gap: 12px;\n  min-height: 220px;\n  padding: 20px;\n  border: 1px solid var(--line);\n  border-radius: 20px;\n  background: var(--panel);\n  box-shadow: 0 10px 24px rgba(22, 40, 34, 0.05);\n}\n\n.topic-card h3 {\n  margin: 0;\n  line-height: 1.18;\n  letter-spacing: -0.025em;\n}\n\n.badge {\n  align-self: flex-start;\n  border-radius: 999px;\n  padding: 6px 10px;\n  background: color-mix(in srgb, var(--brand) 14%, transparent);\n  color: var(--brand);\n  font-weight: 750;\n  font-size: 0.8rem;\n}\n\n.card-footer {\n  margin-top: auto;\n  display: flex;\n  gap: 8px;\n  align-items: center;\n  justify-content: space-between;\n}\n\n.open-link {\n  display: inline-flex;\n  align-items: center;\n  justify-content: center;\n  border-radius: 999px;\n  padding: 9px 12px;\n  background: var(--brand);\n  color: white;\n  text-decoration: none;\n  font-weight: 750;\n}\n\n.file-path {\n  color: var(--muted);\n  font-size: 0.82rem;\n  overflow-wrap: anywhere;\n}\n\n.empty {\n  padding: 34px;\n  text-align: center;\n  border: 1px dashed var(--line);\n  border-radius: var(--radius);\n  color: var(--muted);\n  background: color-mix(in srgb, var(--panel) 80%, transparent);\n}\n\n.about-layout {\n  display: grid;\n  grid-template-columns: 0.75fr 1.25fr;\n  gap: 22px;\n}\n\n.list {\n  display: grid;\n  gap: 10px;\n  margin: 0;\n  padding: 0;\n  list-style: none;\n}\n\n.list li {\n  padding: 12px 14px;\n  border: 1px solid var(--line);\n  background: var(--panel-2);\n  border-radius: 14px;\n}\n\ncode {\n  background: color-mix(in srgb, var(--brand) 14%, transparent);\n  padding: 2px 6px;\n  border-radius: 7px;\n}\n\n.footer {\n  max-width: 1180px;\n  margin: 0 auto;\n  padding: 0 22px 34px;\n  color: var(--muted);\n  font-size: 0.92rem;\n}\n\n@media (max-width: 900px) {\n  .hero,\n  .about-layout {\n    grid-template-columns: 1fr;\n  }\n\n  .grid {\n    grid-template-columns: repeat(2, minmax(0, 1fr));\n  }\n\n  .toolbar {\n    grid-template-columns: 1fr;\n  }\n\n  .nav {\n    flex-wrap: wrap;\n  }\n\n  .nav-links {\n    width: 100%;\n    margin-left: 0;\n  }\n}\n\n@media (max-width: 620px) {\n  .grid {\n    grid-template-columns: 1fr;\n  }\n\n  .hero-card {\n    padding: 26px;\n  }\n}\n\n@media print {\n  .site-header,\n  .toolbar,\n  .category-tabs,\n  .hero-actions {\n    display: none;\n  }\n\n  body {\n    background: white;\n    color: black;\n  }\n\n  .topic-card,\n  .hero-card,\n  .panel {\n    box-shadow: none;\n    break-inside: avoid;\n  }\n}\n'
APP_JS = '\nconst topics = Array.isArray(window.PMR_TOPICS) ? window.PMR_TOPICS : [];\nlet activeCategory = "All";\nlet query = "";\n\nconst $ = (id) => document.getElementById(id);\n\nfunction normalize(str) {\n  return String(str || "").toLowerCase();\n}\n\nfunction groupedCategories() {\n  const counts = new Map();\n  topics.forEach(t => counts.set(t.category || "Other Topics", (counts.get(t.category || "Other Topics") || 0) + 1));\n  return [["All", topics.length], ...Array.from(counts.entries()).sort((a, b) => a[0].localeCompare(b[0]))];\n}\n\nfunction filteredTopics() {\n  return topics.filter(t => {\n    const matchesCategory = activeCategory === "All" || t.category === activeCategory;\n    const haystack = normalize(`${t.title} ${t.category} ${t.description} ${t.file}`);\n    const matchesSearch = !query || haystack.includes(normalize(query));\n    return matchesCategory && matchesSearch;\n  });\n}\n\nfunction renderStats() {\n  const topicCountEls = document.querySelectorAll("#topicCount");\n  const categoryCountEls = document.querySelectorAll("#categoryCount");\n  const lastUpdatedEls = document.querySelectorAll("#lastUpdated");\n\n  const categories = new Set(topics.map(t => t.category || "Other Topics"));\n  const last = topics.map(t => t.updated).filter(Boolean).sort().pop();\n\n  topicCountEls.forEach(el => el.textContent = topics.length);\n  categoryCountEls.forEach(el => el.textContent = categories.size);\n  lastUpdatedEls.forEach(el => el.textContent = last || "-");\n}\n\nfunction renderTabs() {\n  const el = $("categoryTabs");\n  if (!el) return;\n  el.innerHTML = "";\n  groupedCategories().forEach(([category, count]) => {\n    const btn = document.createElement("button");\n    btn.className = "tab" + (category === activeCategory ? " active" : "");\n    btn.textContent = `${category} (${count})`;\n    btn.addEventListener("click", () => {\n      activeCategory = category;\n      renderTabs();\n      renderGrid();\n    });\n    el.appendChild(btn);\n  });\n}\n\nfunction renderGrid() {\n  const el = $("topicGrid");\n  const empty = $("emptyState");\n  if (!el) return;\n\n  const list = filteredTopics();\n  el.innerHTML = "";\n\n  if (empty) empty.style.display = list.length ? "none" : "block";\n\n  list.forEach(t => {\n    const card = document.createElement("article");\n    card.className = "topic-card";\n    card.innerHTML = `\n      <span class="badge">${escapeHtml(t.category || "Other Topics")}</span>\n      <h3>${escapeHtml(t.title)}</h3>\n      <p>${escapeHtml(t.description || "")}</p>\n      <div class="file-path">${escapeHtml(t.file)}</div>\n      <div class="card-footer">\n        <small>${escapeHtml(t.updated || "")}</small>\n        <a class="open-link" href="${encodeURI(t.file)}">Open</a>\n      </div>\n    `;\n    el.appendChild(card);\n  });\n}\n\nfunction escapeHtml(value) {\n  return String(value || "")\n    .replaceAll("&", "&amp;")\n    .replaceAll("<", "&lt;")\n    .replaceAll(">", "&gt;")\n    .replaceAll(\'"\', "&quot;")\n    .replaceAll("\'", "&#039;");\n}\n\nfunction setupSearch() {\n  const input = $("searchInput");\n  if (!input) return;\n  input.addEventListener("input", (e) => {\n    query = e.target.value;\n    renderGrid();\n  });\n}\n\nfunction setupRandom() {\n  const btn = $("randomBtn");\n  if (!btn) return;\n  btn.addEventListener("click", () => {\n    const list = filteredTopics();\n    if (!list.length) return;\n    const topic = list[Math.floor(Math.random() * list.length)];\n    window.location.href = topic.file;\n  });\n}\n\nfunction setupTheme() {\n  const btn = $("themeBtn");\n  const saved = localStorage.getItem("pmr-hub-theme");\n  if (saved === "dark" || saved === "light") {\n    document.documentElement.dataset.theme = saved;\n  } else {\n    document.documentElement.dataset.theme = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";\n  }\n\n  function updateLabel() {\n    if (btn) btn.textContent = document.documentElement.dataset.theme === "dark" ? "Light mode" : "Night mode";\n  }\n\n  updateLabel();\n\n  if (btn) {\n    btn.addEventListener("click", () => {\n      const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";\n      document.documentElement.dataset.theme = next;\n      localStorage.setItem("pmr-hub-theme", next);\n      updateLabel();\n    });\n  }\n}\n\nfunction setupPrint() {\n  const btn = $("printBtn");\n  if (btn) btn.addEventListener("click", () => window.print());\n}\n\nrenderStats();\nrenderTabs();\nrenderGrid();\nsetupSearch();\nsetupRandom();\nsetupTheme();\nsetupPrint();\n'
INDEX_HTML = '<!doctype html>\n<html lang="en" data-theme="light">\n<head>\n  <meta charset="utf-8">\n  <meta name="viewport" content="width=device-width, initial-scale=1">\n  <title>PM&R Study Hub by Fahrin</title>\n  <link rel="stylesheet" href="assets/style.css">\n  <script defer src="assets/topics.js"></script>\n  <script defer src="assets/app.js"></script>\n</head>\n<body>\n  <header class="site-header">\n    <nav class="nav">\n      <a class="brand" href="index.html">\n        <span class="logo">PM</span>\n        <span>PM&R Study Hub</span>\n      </a>\n      <div class="nav-links">\n        <a href="index.html">Index</a>\n        <a href="about.html">About</a>\n        <button class="icon-button" id="themeBtn" type="button">Night mode</button>\n      </div>\n    </nav>\n  </header>\n\n  <main class="container">\n    <section class="hero">\n      <div class="hero-card">\n        <div class="kicker">Offline revision library</div>\n        <h1>PM&R Study Hub by Fahrin</h1>\n        <p>\n          A local index for your Physical Medicine and Rehabilitation national board exam HTML notes.\n          Search, filter by topic category, open files offline, and keep everything inside one study folder.\n        </p>\n        <div class="hero-actions">\n          <a class="primary-button" href="#topics">Browse topics</a>\n          <button class="secondary-button" id="randomBtn" type="button">Random topic</button>\n          <button class="secondary-button" id="printBtn" type="button">Print index</button>\n        </div>\n      </div>\n\n      <aside class="stats-panel panel" aria-label="Library summary">\n        <div class="stat">\n          <div class="stat-value" id="topicCount">0</div>\n          <div class="stat-label">HTML topic files</div>\n        </div>\n        <div class="stat">\n          <div class="stat-value" id="categoryCount">0</div>\n          <div class="stat-label">Detected categories</div>\n        </div>\n        <div class="stat">\n          <div class="stat-value" id="lastUpdated">-</div>\n          <div class="stat-label">Latest file update</div>\n        </div>\n      </aside>\n    </section>\n\n    <section id="topics">\n      <div class="toolbar">\n        <input class="search" id="searchInput" type="search" placeholder="Search topics, file names, or categories..." autocomplete="off">\n        <a class="secondary-button" href="about.html">How to update</a>\n      </div>\n\n      <div class="category-tabs" id="categoryTabs" aria-label="Topic categories"></div>\n\n      <div class="empty" id="emptyState" style="display: none;">\n        No matching topic found. Try another keyword or rebuild the index after adding files.\n      </div>\n\n      <div class="grid" id="topicGrid"></div>\n    </section>\n  </main>\n\n  <footer class="footer">\n    Built for offline PM&R board exam revision. Keep this file in the same folder as your topic HTML files.\n  </footer>\n</body>\n</html>\n'
ABOUT_HTML = '<!doctype html>\n<html lang="en" data-theme="light">\n<head>\n  <meta charset="utf-8">\n  <meta name="viewport" content="width=device-width, initial-scale=1">\n  <title>About - PM&R Study Hub by Fahrin</title>\n  <link rel="stylesheet" href="assets/style.css">\n  <script defer src="assets/topics.js"></script>\n  <script defer src="assets/app.js"></script>\n</head>\n<body>\n  <header class="site-header">\n    <nav class="nav">\n      <a class="brand" href="index.html">\n        <span class="logo">PM</span>\n        <span>PM&R Study Hub</span>\n      </a>\n      <div class="nav-links">\n        <a href="index.html">Index</a>\n        <a href="about.html">About</a>\n        <button class="icon-button" id="themeBtn" type="button">Night mode</button>\n      </div>\n    </nav>\n  </header>\n\n  <main class="container">\n    <section class="hero-card">\n      <div class="kicker">About this offline hub</div>\n      <h1>How this study hub works</h1>\n      <p>\n        This is a lightweight offline webpage. It does not need an internet connection and it does not upload your files.\n        The index is generated from the HTML files inside your study folder.\n      </p>\n    </section>\n\n    <section class="about-layout" style="margin-top: 22px;">\n      <aside class="panel" style="padding: 24px;">\n        <h2>Current library</h2>\n        <ul class="list">\n          <li><strong id="topicCount">0</strong> topic files detected</li>\n          <li><strong id="categoryCount">0</strong> categories detected</li>\n          <li>Last update: <strong id="lastUpdated">-</strong></li>\n        </ul>\n      </aside>\n\n      <article class="panel" style="padding: 28px;">\n        <h2>How to update the index</h2>\n        <p>\n          Place all your PM&R HTML topic files in:\n          <code>C:\\Users\\Fahri\\Documents\\School Work\\PM&R\\SEM 8</code>\n        </p>\n\n        <ul class="list">\n          <li>Copy <code>build_pmr_hub.py</code> into that folder.</li>\n          <li>Double click <code>run_build_hub.bat</code>, or run <code>python build_pmr_hub.py</code> from Command Prompt.</li>\n          <li>The script will create or refresh <code>index.html</code>, <code>about.html</code>, and the <code>assets</code> folder.</li>\n          <li>Open <code>index.html</code> in your browser. You can pin or bookmark it.</li>\n          <li>Whenever you add, rename, or delete topic HTML files, run the builder again.</li>\n        </ul>\n\n        <h2 style="margin-top: 26px;">Suggested folder structure</h2>\n        <p>You can keep all files in one folder, or organize them into subfolders. Both approaches work.</p>\n        <ul class="list">\n          <li><code>SEM 8\\Stroke\\stroke_revision.html</code></li>\n          <li><code>SEM 8\\Cardiac Rehab\\cabg_rehab.html</code></li>\n          <li><code>SEM 8\\Musculoskeletal\\knee_acl_oa.html</code></li>\n          <li><code>SEM 8\\index.html</code></li>\n        </ul>\n\n        <h2 style="margin-top: 26px;">Important note</h2>\n        <p>\n          A normal offline browser cannot automatically scan a Windows folder by itself for security reasons.\n          That is why this hub uses a local Python builder script to create the topic list.\n        </p>\n      </article>\n    </section>\n  </main>\n\n  <footer class="footer">\n    PM&R Study Hub by Fahrin.\n  </footer>\n</body>\n</html>\n'

def clean_text(value: str) -> str:
    value = re.sub(r"\s+", " ", value or "").strip()
    return value

def read_title(path: Path) -> str:
    try:
        txt = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return path.stem.replace("_", " ").replace("-", " ").title()

    patterns = [
        r"<title[^>]*>(.*?)</title>",
        r"<h1[^>]*>(.*?)</h1>",
        r"<h2[^>]*>(.*?)</h2>",
    ]

    for pat in patterns:
        m = re.search(pat, txt, flags=re.I | re.S)
        if m:
            raw = re.sub(r"<[^>]+>", "", m.group(1))
            title = html.unescape(clean_text(raw))
            if title:
                return title

    return path.stem.replace("_", " ").replace("-", " ").title()

def infer_category(title: str, rel_path: str) -> str:
    haystack = f"{title} {rel_path}".lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(k.lower() in haystack for k in keywords):
            return category
    return "Other Topics"

def short_description(title: str, category: str) -> str:
    return f"{category} revision file for PM&R national board preparation."

def scan_files(root: Path):
    topics = []
    for path in sorted(root.rglob("*.html")):
        if path.name.startswith("."):
            continue
        if path.name.lower() in EXCLUDE:
            continue
        lower_parts = [p.lower() for p in path.parts]
        if "assets" in lower_parts:
            continue

        rel = path.relative_to(root).as_posix()
        title = read_title(path)
        category = infer_category(title, rel)
        topics.append({
            "title": title,
            "file": rel,
            "category": category,
            "description": short_description(title, category),
            "updated": datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d"),
        })
    return topics

def write_site(root: Path, topics):
    assets = root / "assets"
    assets.mkdir(exist_ok=True)

    (assets / "topics.js").write_text(
        "window.PMR_TOPICS = " + json.dumps(topics, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8"
    )
    (assets / "style.css").write_text(STYLE_CSS, encoding="utf-8")
    (assets / "app.js").write_text(APP_JS, encoding="utf-8")
    (root / "index.html").write_text(INDEX_HTML, encoding="utf-8")
    (root / "about.html").write_text(ABOUT_HTML, encoding="utf-8")

def main():
    root = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else Path.cwd()
    root = root.resolve()

    if not root.exists():
        print(f"Folder not found: {root}")
        raise SystemExit(1)

    topics = scan_files(root)
    write_site(root, topics)

    print("PM&R Study Hub created successfully.")
    print(f"Folder: {root}")
    print(f"HTML topic files indexed: {len(topics)}")
    print("Open index.html in your browser.")

if __name__ == "__main__":
    main()
