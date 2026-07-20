/* ============================================================
   CopilotLens Dashboard — app.js
   Fetches data from /api/data and renders all dashboard panels
   ============================================================ */

const API_URL = window.location.protocol.startsWith("http") ? "/api/data" : "http://localhost:8765/api/data";
let scoreRingChart = null;
let distChart = null;
let dashboardData = null;

// ── Bootstrap ──────────────────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", () => {
  loadData();
  // Auto-refresh every 30 seconds
  setInterval(loadData, 30000);
});

async function loadData() {
  try {
    const res = await fetch(API_URL);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    dashboardData = await res.json();

    if (dashboardData.status === "loading") {
      setStatus("loading");
      document.getElementById("score-interpretation").textContent = "⏳ Analyzing repository in background...";
      setTimeout(loadData, 2000);
      return;
    }

    setStatus("connected");
    renderAll(dashboardData);
    const lastEl = document.getElementById("last-updated");
    if (lastEl) {
      lastEl.textContent = "Updated: " + new Date().toLocaleTimeString();
    }
  } catch (e) {
    setStatus("error");
    console.error("Failed to load data:", e);
    showError();
  }
}

function setStatus(state) {
  const dot = document.getElementById("status-dot");
  const text = document.getElementById("status-text");
  dot.className = "status-dot " + (state === "loading" ? "connecting" : state);
  text.textContent = state === "connected" ? "Live" : state === "loading" ? "Analyzing..." : state === "error" ? "Error" : "Connecting...";
}

function showError() {
  document.getElementById("score-interpretation").textContent =
    "⚠️ Cannot connect to MCP server. Is it running? python run_dashboard.py --repo demo_project";
}

// ── Tab Switching ──────────────────────────────────────────────────────────────

function switchTab(name, btn) {
  document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
  document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
  document.getElementById("tab-" + name).classList.add("active");
  btn.classList.add("active");
}

// ── Render All ────────────────────────────────────────────────────────────────

function safeRun(fn, name) {
  try { fn(); } catch(err) { console.warn(`Render error in ${name}:`, err); }
}

function renderAll(data) {
  safeRun(() => renderHero(data), "hero");
  safeRun(() => renderHotspots(data.hotspots || []), "hotspots");
  safeRun(() => renderHealth(data.health || {}), "health");
  safeRun(() => renderDeadCode(data.dead_code || []), "deadcode");
  safeRun(() => renderDependencies(data.dependency_graph || {}), "dependencies");
  safeRun(() => renderCoChange(data.co_change_pairs || []), "cochange");
  safeRun(() => renderBlastRadius(data.blast_radius || []), "blastradius");
}

// ── Hero Section ──────────────────────────────────────────────────────────────

function renderHero(data) {
  const health = data.health || {};
  const git = data.repo_summary || {};

  const avg = health.avg_score || 0;
  const grade = health.grade || "?";
  const dist = health.distribution || {};

  document.getElementById("avg-score").textContent = avg;
  document.getElementById("score-grade").textContent = grade;
  document.getElementById("repo-path").textContent = shortenPath(data.repo_path || "");
  document.getElementById("score-interpretation").textContent =
    health.worst_files?.length
      ? `${health.total_files} files scored. ${dist.critical || 0} critical, ${dist.poor || 0} poor.`
      : "Analysis complete.";

  document.getElementById("total-files").textContent = health.total_files || 0;
  document.getElementById("total-commits").textContent =
    git.total_commits != null ? git.total_commits.toLocaleString() : "—";
  document.getElementById("contributors").textContent =
    git.active_contributors_90d?.length || "—";
  document.getElementById("critical-count").textContent = dist.critical || 0;

  if (typeof Chart !== "undefined") {
    safeRun(() => renderScoreRing(avg, grade), "scoreRing");
    safeRun(() => renderDistChart(dist), "distChart");
  }
}

function renderScoreRing(score, grade) {
  const canvas = document.getElementById("scoreRing");
  const ctx = canvas.getContext("2d");

  const color = score >= 80 ? "#10B981" : score >= 65 ? "#3B82F6" : score >= 50 ? "#F59E0B" : "#EF4444";
  const track = "rgba(255,255,255,0.06)";

  if (scoreRingChart) scoreRingChart.destroy();

  scoreRingChart = new Chart(ctx, {
    type: "doughnut",
    data: {
      datasets: [{
        data: [score, 100 - score],
        backgroundColor: [color, track],
        borderWidth: 0,
        borderRadius: 4,
      }]
    },
    options: {
      cutout: "75%",
      events: [],   // no mouse/scroll capture
      plugins: { legend: { display: false }, tooltip: { enabled: false } },
      animation: { duration: 800, easing: "easeInOutQuart" }
    }
  });
}

function renderDistChart(dist) {
  const canvas = document.getElementById("distributionChart");
  const ctx = canvas.getContext("2d");

  const labels = ["Critical\n(<30)", "Poor\n(30-49)", "Fair\n(50-69)", "Good\n(70-84)", "Excellent\n(85+)"];
  const values = [dist.critical || 0, dist.poor || 0, dist.fair || 0, dist.good || 0, dist.excellent || 0];
  const colors = ["#EF4444", "#F97316", "#F59E0B", "#3B82F6", "#10B981"];

  if (distChart) distChart.destroy();

  const maxVal = Math.max(...values, 1);
  // Tight Y-axis: just a bit above the tallest bar
  const yMax = Math.ceil(maxVal * 1.25);

  distChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: colors.map(c => c + "44"),
        borderColor: colors,
        borderWidth: 2,
        borderRadius: 6,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      // Disable ALL mouse/wheel/touch events — prevents scroll hijacking
      events: [],
      plugins: {
        legend: { display: false },
        tooltip: { enabled: false }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { color: "#545B6E", font: { size: 11, family: "Inter" } }
        },
        y: {
          min: 0,
          max: yMax,
          grid: { color: "rgba(255,255,255,0.04)" },
          ticks: {
            color: "#545B6E",
            font: { size: 10 },
            precision: 0,
            maxTicksLimit: 5
          }
        }
      },
      animation: { duration: 600, easing: "easeInOutQuart" }
    }
  });
}

// ── Hotspots ──────────────────────────────────────────────────────────────────

function renderHotspots(hotspots) {
  const container = document.getElementById("hotspot-list");
  if (!hotspots.length) {
    container.innerHTML = emptyState("No git history found. Make sure the repo has commits.");
    return;
  }

  container.innerHTML = hotspots.map((h, i) => `
    <div class="hotspot-item">
      <div class="hotspot-rank">#${i + 1}</div>
      <div class="hotspot-info">
        <div class="hotspot-path" title="${h.path}">${h.path}</div>
        <div class="hotspot-meta">
          <span>Last: ${h.last_changed || "unknown"}</span>
          <span>Authors: ${(h.authors || []).slice(0,2).join(", ") || "unknown"}</span>
          <span>Churn: ${h.churn || 0} lines</span>
        </div>
      </div>
      <div class="hotspot-churn">
        <span class="churn-count">${h.commit_count || 0}</span>
        <span class="churn-label">commits</span>
      </div>
      <div class="risk-badge risk-${h.risk_level || "LOW"}">${h.risk_level || "LOW"}</div>
    </div>
  `).join("");
}

// ── Health Grid ───────────────────────────────────────────────────────────────

function renderHealth(health) {
  const container = document.getElementById("health-grid");
  const worst = health.worst_files || [];
  const best = health.best_files || [];
  const all = [...worst, ...best];

  if (!all.length) {
    container.innerHTML = emptyState("No source files found to score.");
    return;
  }

  // Show worst then best
  const files = worst.length ? worst : all;
  container.innerHTML = files.map(f => {
    const score = f.score || 0;
    const grade = f.grade || "?";
    const barColor = score >= 80 ? "#10B981" : score >= 65 ? "#3B82F6" : score >= 50 ? "#F59E0B" : "#EF4444";
    const markers = f.markers || [];
    const badMarkers = markers.filter(m => m.impact < 0).slice(0, 3);
    const goodMarkers = markers.filter(m => m.impact > 0).slice(0, 2);

    return `
      <div class="health-item">
        <div class="health-item-top">
          <div class="health-path" title="${f.path}">${f.path}</div>
          <div class="health-score-badge grade-${grade}">${score} ${grade}</div>
        </div>
        <div class="health-bar-bg">
          <div class="health-bar-fill" style="width:${score}%; background:${barColor}"></div>
        </div>
        <div class="health-markers">
          ${badMarkers.map(m => `<span class="marker-chip" title="${m.desc}">${markerIcon(m.id)}</span>`).join("")}
          ${goodMarkers.map(m => `<span class="marker-chip good" title="${m.desc}">${markerIcon(m.id)}</span>`).join("")}
        </div>
      </div>
    `;
  }).join("");
}

function markerIcon(id) {
  const icons = {
    file_too_large: "📄 Too large",
    very_large_file: "📄 Large",
    long_functions: "📏 Long fns",
    deeply_nested: "📦 Deep nesting",
    too_many_todos: "⚠️ TODOs",
    no_comments: "📝 No docs",
    high_complexity: "🔀 Complex",
    magic_numbers: "🔢 Magic nums",
    good_comment_ratio: "✅ Documented",
    short_file: "✅ Concise",
    has_tests: "✅ Tests",
    consistent_style: "✅ Style"
  };
  return icons[id] || id;
}

// ── Dead Code ─────────────────────────────────────────────────────────────────

function renderDeadCode(dead) {
  const container = document.getElementById("dead-code-list");
  if (!dead.length) {
    container.innerHTML = emptyState("✅ No dead code candidates detected! Or repo has no git history.");
    return;
  }

  container.innerHTML = dead.map(d => `
    <div class="dead-code-item">
      <div>
        <div class="dead-symbol">${d.symbol}</div>
        <div class="dead-location">${d.defined_in}${d.line ? ` : ${d.line}` : ""}</div>
      </div>
      <span class="dead-type-badge">${d.type || "symbol"}</span>
      <span class="confidence-${d.confidence}">${d.confidence}</span>
    </div>
  `).join("");
}

// ── Dependencies ──────────────────────────────────────────────────────────────

function renderDependencies(graph) {
  const statsRow = document.getElementById("dep-stats-row");
  const grid = document.getElementById("dep-grid");

  const nodes = graph.nodes || [];
  const edges = graph.edges || [];
  const circular = graph.circular || [];
  const orphans = graph.orphans || [];
  const hubs = nodes.filter(n => n.is_hub);

  statsRow.innerHTML = `
    <div class="dep-stat-card">
      <span class="dep-stat-value" style="color:#7C3AED">${nodes.length}</span>
      <span class="dep-stat-label">Tracked Files</span>
    </div>
    <div class="dep-stat-card">
      <span class="dep-stat-value" style="color:#06B6D4">${edges.length}</span>
      <span class="dep-stat-label">Dependencies</span>
    </div>
    <div class="dep-stat-card">
      <span class="dep-stat-value" style="color:${circular.length ? '#EF4444' : '#10B981'}">${circular.length}</span>
      <span class="dep-stat-label">Circular Chains</span>
    </div>
    <div class="dep-stat-card">
      <span class="dep-stat-value" style="color:#F59E0B">${orphans.length}</span>
      <span class="dep-stat-label">Orphan Files</span>
    </div>
  `;

  grid.innerHTML = `
    <div class="dep-section">
      <div class="dep-section-title">🔗 Hub Files <span style="color:var(--text-muted);font-weight:400;font-size:11px">(imported by 5+ others)</span></div>
      <div class="dep-file-list">
        ${hubs.length
          ? hubs.slice(0, 10).map(n => `
            <div class="dep-file-item">
              <span class="dep-file-path" title="${n.id}">${n.id}</span>
              <span class="dep-badge hub">${n.imported_by_count} imports</span>
            </div>`).join("")
          : "<div class='empty-state' style='padding:16px'>No hub files — good coupling!</div>"}
      </div>
    </div>

    <div class="dep-section">
      <div class="dep-section-title">🔄 Circular Dependencies</div>
      <div class="dep-file-list">
        ${circular.length
          ? circular.slice(0, 8).map(chain => `
            <div class="dep-file-item">
              <span class="dep-file-path" title="${chain.join(' → ')}">${chain.slice(0,2).join(" → ")}${chain.length > 2 ? " …" : ""}</span>
              <span class="dep-badge circular">circular</span>
            </div>`).join("")
          : "<div class='empty-state' style='padding:16px'>✅ No circular dependencies!</div>"}
      </div>
    </div>

    <div class="dep-section">
      <div class="dep-section-title">🌿 Orphan Files <span style="color:var(--text-muted);font-weight:400;font-size:11px">(no references)</span></div>
      <div class="dep-file-list">
        ${orphans.length
          ? orphans.slice(0, 8).map(f => `
            <div class="dep-file-item">
              <span class="dep-file-path" title="${f}">${f}</span>
              <span class="dep-badge orphan">orphan</span>
            </div>`).join("")
          : "<div class='empty-state' style='padding:16px'>✅ No orphan files!</div>"}
      </div>
    </div>

    <div class="dep-section">
      <div class="dep-section-title">📊 Top Imported Files</div>
      <div class="dep-file-list">
        ${nodes.slice(0, 8).map(n => `
          <div class="dep-file-item">
            <span class="dep-file-path" title="${n.id}">${n.id}</span>
            <span style="font-size:11px;color:var(--text-secondary);flex-shrink:0">↑${n.imported_by_count} ↓${n.imports_count}</span>
          </div>`).join("")}
      </div>
    </div>
  `;
}

// ── Utility ───────────────────────────────────────────────────────────────────

function shortenPath(path) {
  if (!path) return "—";
  const parts = path.replace(/\\/g, "/").split("/");
  if (parts.length <= 3) return path;
  return "…/" + parts.slice(-2).join("/");
}

function emptyState(msg) {
  return `<div class="empty-state">${msg}</div>`;
}

// ── Copilot Prompt Copy ────────────────────────────────────────────────────────

function copyPrompt(btn) {
  const prompt = btn.dataset.prompt;
  if (navigator.clipboard) {
    navigator.clipboard.writeText(prompt).catch(() => fallbackCopy(prompt));
  } else {
    fallbackCopy(prompt);
  }
  showToast();
}

function fallbackCopy(text) {
  const ta = document.createElement("textarea");
  ta.value = text;
  ta.style.position = "fixed";
  ta.style.opacity = "0";
  document.body.appendChild(ta);
  ta.select();
  document.execCommand("copy");
  document.body.removeChild(ta);
}

function showToast() {
  const toast = document.getElementById("copied-toast");
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 2500);
}

// ── Co-Change Pairs ────────────────────────────────────────────────────────────

function renderCoChange(pairs) {
  const container = document.getElementById("cochange-list");
  if (!pairs || !pairs.length) {
    container.innerHTML = emptyState("No co-change pairs found. Need more git history (run git fetch --unshallow).");
    return;
  }
  container.innerHTML = pairs.map(p => `
    <div class="cochange-item">
      <div class="cochange-files">
        <div class="cochange-file-a" title="${p.file_a}">${p.file_a}</div>
        <div class="cochange-arrow">&#8597; always together</div>
        <div class="cochange-file-b" title="${p.file_b}">${p.file_b}</div>
      </div>
      <div class="cochange-count">
        <span class="cochange-num">${p.co_change_count}</span>
        <span class="cochange-label">co-changes</span>
      </div>
      <span class="coupling-${p.coupling_strength}">${p.coupling_strength}</span>
    </div>
  `).join("");
}

// ── Blast Radius ───────────────────────────────────────────────────────────────

function renderBlastRadius(items) {
  const container = document.getElementById("blastradius-list");
  if (!items || !items.length) {
    container.innerHTML = emptyState("Calculating blast radius sets...");
    return;
  }
  container.innerHTML = items.map(b => {
    const target = (b.targets || [])[0] || "Unknown File";
    const bd = b.blast_radius_breakdown || {};
    const dependents = bd.direct_dependents || [];
    const coChanges = bd.co_change_partners || [];
    const tests = bd.associated_tests || [];
    const savings = b.token_savings || {};

    return `
      <div class="blast-card">
        <div class="blast-card-header">
          <span class="blast-target-title">🎯 ${target}</span>
          <span class="savings-chip">⚡ ${savings.token_reduction_multiplier || "Token Savings"} (${savings.reduction_percentage || "95%"})</span>
        </div>
        <div class="blast-grid">
          <div class="blast-subbox">
            <div class="blast-subbox-title">🔗 Direct Dependents (${dependents.length})</div>
            <div class="blast-subbox-list">
              ${dependents.length ? dependents.map(f => `<div>${f.split('/').pop()}</div>`).join('') : '<div style="color:var(--text-muted)">None</div>'}
            </div>
          </div>
          <div class="blast-subbox">
            <div class="blast-subbox-title">🔄 Co-Change Files (${coChanges.length})</div>
            <div class="blast-subbox-list">
              ${coChanges.length ? coChanges.map(f => `<div>${f.split('/').pop()}</div>`).join('') : '<div style="color:var(--text-muted)">None</div>'}
            </div>
          </div>
          <div class="blast-subbox">
            <div class="blast-subbox-title">🧪 Associated Tests (${tests.length})</div>
            <div class="blast-subbox-list">
              ${tests.length ? tests.map(f => `<div>${f.split('/').pop()}</div>`).join('') : '<div style="color:var(--text-muted)">None</div>'}
            </div>
          </div>
        </div>
        <div class="blast-summary-bar">
          💡 ${savings.summary || `Minimal Review Set: ${b.total_files_in_review_set || 1} files instead of ${b.total_repo_files || 200} full repository files.`}
        </div>
      </div>
    `;
  }).join("");
}

