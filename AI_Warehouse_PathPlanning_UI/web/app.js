// Warehouse Robot Route Planner - frontend.
// Draws the grid on a <canvas>, lets the user edit it, and calls the Python backend
// (server.py) for the actual search and replanning. All AI logic lives in Python.

const CELL_COLORS = {
  ".": "#faf9f5", S: "#faf9f5", G: "#faf9f5",
  C: "#f6c177", "#": "#5b4a3f", R: "#e06c75", T: "#8e44ad",
};
const ALGO_COLORS = { "BFS": "#1f77b4", "DFS": "#7d7d7d", "Greedy Best-First": "#ff7f0e", "A*": "#2ca02c" };
const TOOLS = [
  { sym: ".", name: "Open (1)" }, { sym: "C", name: "Crowded (4)" },
  { sym: "#", name: "Shelf" }, { sym: "R", name: "Restricted" },
  { sym: "S", name: "Start" }, { sym: "G", name: "Goal" },
  { sym: "T", name: "Trolley" },
];

const $ = (sel) => document.querySelector(sel);
const canvas = $("#grid");
const ctx = canvas.getContext("2d");

const state = {
  grid: [], tool: "#", tab: "search", presets: [], algorithms: [],
  search: null, selected: null, cell: 32,
  view: { overlays: [], explored: null, robot: null, ghosts: new Set(), arrow: null },
};
let animToken = 0;

// ------------------------------------------------------------------ utilities
const key = (r, c) => `${r},${c}`;
const sleep = (ms) => new Promise((res) => setTimeout(res, ms));
const fmt = (p) => `(${p[0]}, ${p[1]})`;
function delay(id) {
  const s = Number($(id).value);
  return Math.round(700 / (s * s * 0.6 + 1));
}
function stopAnim() { animToken++; }
function resetView() {
  state.view = { overlays: [], explored: null, robot: null, ghosts: new Set(), arrow: null };
}
function banner(text, kind = "info") {
  const b = $("#banner");
  if (!text) { b.classList.add("hidden"); return; }
  b.textContent = text;
  b.className = `banner ${kind}`;
}
async function api(path, body) {
  const res = await fetch(path, body ? {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
  } : undefined);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
  return data;
}
const layoutStrings = () => state.grid.map((row) => row.join(""));

// -------------------------------------------------------------------- drawing
function draw() {
  const g = state.grid;
  if (!g.length) return;
  const rows = g.length, cols = g[0].length;
  const avail = canvas.parentElement.clientWidth - 4;
  const cell = Math.max(18, Math.min(52, Math.floor(avail / cols)));
  state.cell = cell;
  const dpr = window.devicePixelRatio || 1;
  canvas.width = cols * cell * dpr;
  canvas.height = rows * cell * dpr;
  canvas.style.width = `${cols * cell}px`;
  canvas.style.height = `${rows * cell}px`;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, cols * cell, rows * cell);
  const v = state.view;

  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const ch = g[r][c];
      const ghost = ch === "T" && v.ghosts.has(key(r, c));
      ctx.fillStyle = ghost ? CELL_COLORS["."] : CELL_COLORS[ch];
      ctx.fillRect(c * cell, r * cell, cell, cell);
      if (ghost) {                       // trolley the robot does not know about yet
        ctx.save();
        ctx.globalAlpha = 0.28;
        ctx.fillStyle = CELL_COLORS.T;
        ctx.fillRect(c * cell + 3, r * cell + 3, cell - 6, cell - 6);
        ctx.restore();
        ctx.setLineDash([4, 3]);
        ctx.strokeStyle = CELL_COLORS.T;
        ctx.strokeRect(c * cell + 3.5, r * cell + 3.5, cell - 7, cell - 7);
        ctx.setLineDash([]);
      }
      const label = { C: "C", R: "R", T: ghost ? "?" : "T" }[ch];
      if (label) {
        ctx.fillStyle = ch === "C" ? "#8a5a00" : ghost ? CELL_COLORS.T : "#fff";
        ctx.font = `${ch === "T" ? "bold " : ""}${Math.round(cell * 0.36)}px Segoe UI, sans-serif`;
        ctx.textAlign = "center"; ctx.textBaseline = "middle";
        ctx.fillText(label, c * cell + cell / 2, r * cell + cell / 2 + 1);
      }
    }
  }
  ctx.strokeStyle = "rgba(0,0,0,.12)";
  ctx.lineWidth = 1;
  for (let r = 0; r <= rows; r++) line(0, r * cell, cols * cell, r * cell);
  for (let c = 0; c <= cols; c++) line(c * cell, 0, c * cell, rows * cell);

  if (v.explored) {
    ctx.fillStyle = "rgba(60,60,60,.35)";
    for (const [r, c] of v.explored) {
      ctx.beginPath();
      ctx.arc(c * cell + cell / 2, r * cell + cell / 2, Math.max(2.5, cell * 0.11), 0, Math.PI * 2);
      ctx.fill();
    }
  }
  for (const o of v.overlays) drawPath(o);

  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      if (g[r][c] === "S") marker(r, c, "#27ae60", "S");
      if (g[r][c] === "G") marker(r, c, "#2980b9", "G");
    }
  }
  if (v.arrow) arrow(v.arrow.from, v.arrow.to);
  if (v.robot) {
    const [r, c] = v.robot;
    ctx.beginPath();
    ctx.arc(c * cell + cell / 2, r * cell + cell / 2, cell * 0.34, 0, Math.PI * 2);
    ctx.fillStyle = "#f1c40f"; ctx.fill();
    ctx.lineWidth = 2; ctx.strokeStyle = "#222"; ctx.stroke();
    ctx.beginPath();                    // robot "eye"
    ctx.arc(c * cell + cell / 2, r * cell + cell / 2, cell * 0.1, 0, Math.PI * 2);
    ctx.fillStyle = "#222"; ctx.fill();
  }
}
function line(x1, y1, x2, y2) { ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke(); }
function drawPath({ path, color, width = 4, offset = 0, dash = null, alpha = 0.95 }) {
  if (!path || path.length < 2) return;
  const cell = state.cell;
  ctx.save();
  ctx.globalAlpha = alpha;
  ctx.strokeStyle = color;
  ctx.lineWidth = width;
  ctx.lineCap = "round"; ctx.lineJoin = "round";
  if (dash) ctx.setLineDash(dash);
  ctx.beginPath();
  path.forEach(([r, c], i) => {
    const x = c * cell + cell / 2 + offset * cell, y = r * cell + cell / 2 + offset * cell;
    i ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
  });
  ctx.stroke();
  ctx.restore();
}
function marker(r, c, color, text) {
  const cell = state.cell, pad = cell * 0.14;
  ctx.fillStyle = color;
  ctx.fillRect(c * cell + pad, r * cell + pad, cell - 2 * pad, cell - 2 * pad);
  ctx.lineWidth = 1.5; ctx.strokeStyle = "#111";
  ctx.strokeRect(c * cell + pad, r * cell + pad, cell - 2 * pad, cell - 2 * pad);
  ctx.fillStyle = "#fff";
  ctx.font = `bold ${Math.round(cell * 0.4)}px Segoe UI, sans-serif`;
  ctx.textAlign = "center"; ctx.textBaseline = "middle";
  ctx.fillText(text, c * cell + cell / 2, r * cell + cell / 2 + 1);
}
function arrow(from, to) {
  const cell = state.cell;
  const x1 = from[1] * cell + cell / 2, y1 = from[0] * cell + cell / 2;
  const x2 = to[1] * cell + cell / 2, y2 = to[0] * cell + cell / 2;
  const ang = Math.atan2(y2 - y1, x2 - x1), h = cell * 0.28;
  ctx.strokeStyle = "#d62828"; ctx.fillStyle = "#d62828"; ctx.lineWidth = 3;
  line(x1, y1, x2 - Math.cos(ang) * h, y2 - Math.sin(ang) * h);
  ctx.beginPath();
  ctx.moveTo(x2, y2);
  ctx.lineTo(x2 - h * Math.cos(ang - 0.5), y2 - h * Math.sin(ang - 0.5));
  ctx.lineTo(x2 - h * Math.cos(ang + 0.5), y2 - h * Math.sin(ang + 0.5));
  ctx.closePath(); ctx.fill();
}

function setLegend(lines = []) {
  const cells = [
    ["#faf9f5", "Open (cost 1)"], ["#f6c177", "Crowded (cost 4)"], ["#5b4a3f", "Shelf"],
    ["#e06c75", "Restricted"], ["#8e44ad", "Trolley"],
  ];
  const el = $("#legend");
  el.innerHTML = "";
  for (const [color, text] of cells) {
    el.insertAdjacentHTML("beforeend",
      `<span><i class="swatch" style="background:${color}"></i>${text}</span>`);
  }
  for (const [color, text, dashed] of lines) {
    el.insertAdjacentHTML("beforeend",
      `<span><svg width="26" height="8"><line x1="1" y1="4" x2="25" y2="4" stroke="${color}" stroke-width="4" stroke-linecap="round" ${dashed ? 'stroke-dasharray="5 4"' : ""}/></svg>${text}</span>`);
  }
}

// -------------------------------------------------------------------- editing
function setGrid(layout) {
  stopAnim();
  state.grid = layout.map((row) => row.split(""));
  $("#rows").value = layout.length;
  $("#cols").value = layout[0].length;
  clearResults();
}
function clearResults() {
  stopAnim();
  resetView();
  state.search = null; state.selected = null;
  ["#searchTable", "#verdict", "#searchNote", "#replanCards", "#replanLog"].forEach((s) => $(s).classList.add("hidden"));
  banner("");
  setLegend();
  draw();
}
function cellFromEvent(e) {
  const rect = canvas.getBoundingClientRect();
  const c = Math.floor((e.clientX - rect.left) / state.cell);
  const r = Math.floor((e.clientY - rect.top) / state.cell);
  if (r < 0 || c < 0 || r >= state.grid.length || c >= state.grid[0].length) return null;
  return [r, c];
}
function paint(r, c) {
  const g = state.grid, tool = state.tool, cur = g[r][c];
  if (cur === tool) return false;
  if (tool === "S" || tool === "G") {
    for (const row of g) for (let i = 0; i < row.length; i++) if (row[i] === tool) row[i] = ".";
  } else if (cur === "S" || cur === "G") {
    return false;                       // never paint over start / goal
  }
  g[r][c] = tool;
  return true;
}
let painting = false;
canvas.addEventListener("pointerdown", (e) => {
  const p = cellFromEvent(e);
  if (!p) return;
  painting = true;
  canvas.setPointerCapture(e.pointerId);
  if (paint(...p)) clearResults();
});
canvas.addEventListener("pointermove", (e) => {
  if (!painting) return;
  const p = cellFromEvent(e);
  if (p && paint(...p)) clearResults();
});
canvas.addEventListener("pointerup", () => { painting = false; });

function buildPalette() {
  const el = $("#palette");
  TOOLS.forEach((t, i) => {
    const b = document.createElement("button");
    const txt = { S: "S", G: "G", C: "C", R: "R", T: "T" }[t.sym] || "";
    const bg = t.sym === "S" ? "#27ae60" : t.sym === "G" ? "#2980b9" : CELL_COLORS[t.sym];
    b.innerHTML = `<i class="swatch" style="background:${bg};color:${t.sym === "C" ? "#8a5a00" : "#fff"}">${txt}</i>${t.name}<kbd>${i + 1}</kbd>`;
    b.onclick = () => selectTool(t.sym);
    b.dataset.sym = t.sym;
    el.appendChild(b);
  });
  selectTool("#");
}
function selectTool(sym) {
  state.tool = sym;
  document.querySelectorAll("#palette button").forEach((b) => b.classList.toggle("active", b.dataset.sym === sym));
}
document.addEventListener("keydown", (e) => {
  if (e.target.tagName === "INPUT" || e.target.tagName === "SELECT") return;
  const i = Number(e.key) - 1;
  if (i >= 0 && i < TOOLS.length) selectTool(TOOLS[i].sym);
});

// ---------------------------------------------------------- tab 1: algorithms
function buildAlgoChecks() {
  const el = $("#algoChecks");
  for (const name of state.algorithms) {
    el.insertAdjacentHTML("beforeend",
      `<label><input type="checkbox" value="${name}" checked><span class="dot" style="background:${ALGO_COLORS[name]}"></span>${name}</label>`);
  }
}
async function runSearch() {
  const algorithms = [...document.querySelectorAll("#algoChecks input:checked")].map((i) => i.value);
  if (!algorithms.length) return banner("Select at least one algorithm.", "warn");
  const btn = $("#runSearch");
  btn.disabled = true;
  clearResults();
  try {
    const data = await api("/api/search", { layout: layoutStrings(), algorithms });
    state.search = data;
    renderSearchTable();
    showAllRoutes();
    $("#searchNote").textContent = data.note;
    $("#searchNote").classList.toggle("hidden", !data.note);
    if (algorithms.length > 1) {
      $("#verdict").innerHTML = `<b>Shortest vs. cheapest:</b> ${data.verdict}`;
      $("#verdict").classList.remove("hidden");
    }
    const none = data.results.every((r) => !r.found);
    banner(none ? "No route exists from S to G on this map." : "", none ? "error" : "info");
  } catch (err) {
    banner(err.message, "error");
  } finally {
    btn.disabled = false;
  }
}
function renderSearchTable() {
  const res = state.search.results, found = res.filter((r) => r.found);
  const min = (k) => Math.min(...found.map((r) => r[k]));
  const best = found.length ? { moves: min("moves"), cost: min("cost"), nodes_expanded: min("nodes_expanded"), time_ms: min("time_ms") } : {};
  const td = (r, k, v) => `<td class="${r.found && r[k] === best[k] ? "best" : ""}">${v}</td>`;
  const body = $("#searchTable tbody");
  body.innerHTML = "";
  res.forEach((r, i) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td><span class="dot" style="background:${ALGO_COLORS[r.algorithm]}"></span></td>
      <td>${r.algorithm}</td><td>${r.found ? "Yes" : "No"}</td>
      ${td(r, "moves", r.found ? r.moves : "–")}${td(r, "cost", r.found ? r.cost : "–")}
      ${td(r, "nodes_expanded", r.nodes_expanded)}${td(r, "time_ms", r.time_ms.toFixed(3))}
      <td><button class="play" title="Animate this search">▶</button></td>`;
    tr.onclick = (e) => {
      if (e.target.closest(".play")) animateSearch(i);
      else if (state.selected === i) showAllRoutes();
      else showOne(i);
    };
    body.appendChild(tr);
  });
  $("#searchTable").classList.remove("hidden");
}
function markRow(i) {
  document.querySelectorAll("#searchTable tbody tr").forEach((tr, j) => tr.classList.toggle("selected", j === i));
}
function showAllRoutes() {
  stopAnim(); resetView();
  state.selected = null; markRow(-1);
  const res = state.search.results.filter((r) => r.found);
  const offsets = [-0.18, -0.06, 0.06, 0.18];
  res.forEach((r, i) => state.view.overlays.push({
    path: r.path, color: ALGO_COLORS[r.algorithm], width: 3.5,
    offset: res.length > 1 ? offsets[i % 4] : 0,
  }));
  setLegend(res.map((r) => [ALGO_COLORS[r.algorithm], `${r.algorithm}: ${r.moves} moves, cost ${r.cost}`]));
  draw();
}
function showOne(i) {
  stopAnim(); resetView();
  state.selected = i; markRow(i);
  const r = state.search.results[i];
  state.view.explored = r.explored;
  if (r.found) state.view.overlays.push({ path: r.path, color: ALGO_COLORS[r.algorithm], width: 5 });
  setLegend([[ALGO_COLORS[r.algorithm], r.found ? `${r.algorithm} route (grey dots = expanded nodes)` : `${r.algorithm}: no route`]]);
  draw();
}
async function animateSearch(i) {
  stopAnim(); resetView();
  const tok = animToken;
  state.selected = i; markRow(i);
  const r = state.search.results[i];
  setLegend([[ALGO_COLORS[r.algorithm], `${r.algorithm} (grey dots = expanded nodes)`]]);
  for (let k = 1; k <= r.explored.length; k++) {
    if (tok !== animToken) return;
    state.view.explored = r.explored.slice(0, k);
    banner(`${r.algorithm}: expanding node ${k} of ${r.explored.length}  ${fmt(r.explored[k - 1])}`, "info");
    draw();
    await sleep(delay("#speedSearch"));
  }
  if (!r.found) return banner(`${r.algorithm}: no route found`, "error");
  for (let k = 2; k <= r.path.length; k++) {
    if (tok !== animToken) return;
    state.view.overlays = [{ path: r.path.slice(0, k), color: ALGO_COLORS[r.algorithm], width: 5 }];
    draw();
    await sleep(delay("#speedSearch") * 0.6);
  }
  banner(`${r.algorithm}: ${r.moves} moves, cost ${r.cost}, ${r.nodes_expanded} nodes expanded`, "info");
}

// --------------------------------------------------------- tab 2: replanning
async function runReplan() {
  const btn = $("#runReplan");
  btn.disabled = true;
  clearResults();
  try {
    const rep = await api("/api/replan", { layout: layoutStrings(), auto_trolley: $("#autoTrolley").checked });
    state.grid = rep.layout.map((row) => row.split(""));
    await animateReplan(rep);
  } catch (err) {
    banner(err.message, "error");
  } finally {
    btn.disabled = false;
  }
}
function logLine(text) {
  const li = document.createElement("li");
  li.textContent = text;
  if (/FAILED|no alternative/i.test(text)) li.className = "bad";
  else if (/Goal reached/i.test(text)) li.className = "good";
  $("#replanLog").appendChild(li);
  $("#replanLog").classList.remove("hidden");
}
async function animateReplan(rep) {
  stopAnim(); resetView();
  const tok = animToken, v = state.view;
  $("#replanLog").innerHTML = "";
  rep.trolleys.forEach(([r, c]) => v.ghosts.add(key(r, c)));
  setLegend([["#2ca02c", "original A* plan"], ["#e67e22", "revised A* plan"], ["#23201c", "route driven"],
    ["#2ca02c", "abandoned plan", true]]);
  if (!rep.trolleys.length) banner("No trolley on the map, so the robot just follows its A* plan.", "warn");
  else if (rep.auto_placed) banner(`Trolley auto-placed on the A* route at ${fmt(rep.auto_placed)}. The robot does not know about it.`, "info");
  else banner(`${rep.trolleys.length} trolley(s) on the map. The robot does not know about them.`, "info");

  const logs = [...rep.log];
  logLine(logs.shift());
  let planIdx = 0;
  const abandoned = [];
  const detAt = {};
  rep.detection_steps.forEach((step, k) => (detAt[step] = detAt[step] || []).push(k));
  const wait = () => sleep(delay("#speedReplan"));

  for (let idx = 0; idx < rep.executed_path.length; idx++) {
    if (tok !== animToken) return;
    v.robot = rep.executed_path[idx];
    const plan = rep.plans[planIdx].path;
    v.overlays = [
      ...abandoned.map((p) => ({ path: p, color: "#2ca02c", width: 2.5, dash: [6, 5], alpha: 0.45 })),
      { path: plan, color: planIdx ? "#e67e22" : "#2ca02c", width: 4, alpha: 0.8 },
      { path: rep.executed_path.slice(0, idx + 1), color: "#23201c", width: 3, offset: 0.12 },
    ];
    draw();
    await wait();
    for (const k of detAt[idx] || []) {
      if (tok !== animToken) return;
      const d = rep.detections[k];
      v.ghosts.delete(key(...d.blocked));
      v.arrow = { from: d.robot, to: d.blocked };
      banner(`Trolley detected at ${fmt(d.blocked)}. Robot stops at ${fmt(d.robot)} and updates its map.`, "warn");
      logLine(logs.shift());
      draw();
      await sleep(delay("#speedReplan") * 7);
      if (tok !== animToken) return;
      abandoned.push(plan);
      planIdx++;
      const next = rep.plans[planIdx].path;
      v.arrow = null;
      logLine(logs.shift());
      if (next) {
        banner(`Replanned with A* from ${fmt(d.robot)}: new route of ${next.length - 1} moves.`, "info");
        v.overlays = [
          ...abandoned.map((p) => ({ path: p, color: "#2ca02c", width: 2.5, dash: [6, 5], alpha: 0.45 })),
          { path: next, color: "#e67e22", width: 4 },
          { path: rep.executed_path.slice(0, idx + 1), color: "#23201c", width: 3, offset: 0.12 },
        ];
        draw();
        await sleep(delay("#speedReplan") * 6);
      }
    }
  }
  if (tok !== animToken) return;
  logs.forEach(logLine);
  banner(rep.goal_reached ? `Goal reached: ${rep.moves} moves, cost ${rep.total_cost}, ${rep.replans} replan(s).`
    : "No alternative route. Replanning failed and the robot stopped safely.",
  rep.goal_reached ? "info" : "error");
  const cards = [
    ["Goal reached", rep.goal_reached ? "Yes" : "No"], ["Path length (moves)", rep.moves],
    ["Total path cost", rep.total_cost], ["Nodes expanded", rep.nodes_expanded],
    ["Execution time (ms)", rep.time_ms.toFixed(3)], ["Replans", rep.replans],
  ];
  $("#replanCards").innerHTML = cards.map(([k, val]) => `<div class="card"><span>${k}</span><b>${val}</b></div>`).join("");
  $("#replanCards").classList.remove("hidden");
}

// ---------------------------------------------------------------- page setup
function switchTab(tab) {
  state.tab = tab;
  document.querySelectorAll(".tab").forEach((b) => b.classList.toggle("active", b.dataset.tab === tab));
  document.querySelectorAll("[data-panel]").forEach((p) => p.classList.toggle("hidden", p.dataset.panel !== tab));
  clearResults();
}
document.querySelectorAll(".tab").forEach((b) => (b.onclick = () => switchTab(b.dataset.tab)));
$("#runSearch").onclick = runSearch;
$("#runReplan").onclick = runReplan;
$("#preset").onchange = (e) => setGrid(state.presets.find((p) => p.id === e.target.value).layout);
$("#blank").onclick = () => {
  const rows = Math.min(40, Math.max(3, Number($("#rows").value) || 9));
  const cols = Math.min(40, Math.max(3, Number($("#cols").value) || 15));
  const g = Array.from({ length: rows }, () => ".".repeat(cols).split(""));
  g[0][0] = "S"; g[rows - 1][cols - 1] = "G";
  setGrid(g.map((r) => r.join("")));
};
window.addEventListener("resize", draw);

(async function init() {
  buildPalette();
  try {
    const data = await api("/api/layouts");
    state.presets = data.presets;
    state.algorithms = data.algorithms;
    $("#preset").innerHTML = data.presets.map((p) => `<option value="${p.id}">${p.name}</option>`).join("");
    buildAlgoChecks();
    setGrid(data.presets[0].layout);
  } catch (err) {
    banner("Cannot reach the Python backend. Start it with:  python server.py", "error");
  }
})();
