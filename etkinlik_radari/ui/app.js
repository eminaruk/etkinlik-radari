"use strict";
/* Etkinlik Radarı — UI. Talks to Python through window.pywebview.api.* */

const ICONS = {
  radar: '<path d="M19.07 4.93A10 10 0 0 0 6.99 3.34"/><path d="M4 6h.01"/><path d="M2.29 9.62A10 10 0 1 0 21.31 8.35"/><path d="M16.24 7.76A6 6 0 1 0 8.23 16.67"/><path d="M12 18h.01"/><path d="M17.99 11.66A6 6 0 0 1 15.77 16.67"/><circle cx="12" cy="12" r="2"/><path d="m13.41 10.59 5.66-5.66"/>',
  compass: '<circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/>',
  calendar: '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
  bookmark: '<path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16z"/>',
  news: '<path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"/><path d="M18 14h-8M15 18h-5M10 6h8v4h-8V6Z"/>',
  db: '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14a9 3 0 0 0 18 0V5"/><path d="M3 12a9 3 0 0 0 18 0"/>',
  user: '<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
  refresh: '<path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/><path d="M16 16h5v5"/>',
  moon: '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>',
  sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/>',
  search: '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
  grid: '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/>',
  list: '<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',
  x: '<path d="M18 6 6 18M6 6l12 12"/>',
  sparkles: '<path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z"/>',
  left: '<path d="m15 18-6-6 6-6"/>',
  right: '<path d="m9 18 6-6-6-6"/>',
  up: '<path d="M7 10v12"/><path d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2a3.13 3.13 0 0 1 3 3.88Z"/>',
  down: '<path d="M17 14V2"/><path d="M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8A2 2 0 0 1 6.5 2H20a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2.76a2 2 0 0 0-1.79 1.11L12 22a3.13 3.13 0 0 1-3-3.88Z"/>',
  ext: '<path d="M15 3h6v6M10 14 21 3M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>',
  pin: '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
  clock: '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
  users: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
  check: '<path d="M20 6 9 17l-5-5"/>',
  globe: '<circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20M2 12h20"/>',
  download: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m7 10 5 5 5-5M12 15V3"/>',
  cpu: '<rect width="16" height="16" x="4" y="4" rx="2"/><rect width="6" height="6" x="9" y="9" rx="1"/><path d="M15 2v2M15 20v2M2 15h2M2 9h2M20 15h2M20 9h2M9 2v2M9 20v2"/>',
  rocket: '<path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"/><path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/>',
  trending: '<path d="M22 7 13.5 15.5 8.5 10.5 2 17"/><path d="M16 7h6v6"/>',
  card: '<rect width="20" height="14" x="2" y="5" rx="2"/><path d="M2 10h20"/>',
  bitcoin: '<path d="M11.767 19.089c4.924.868 6.14-6.025 1.216-6.894m-1.216 6.894L5.86 18.047m5.908 1.042-.347 1.97m1.563-8.864c4.924.869 6.14-6.025 1.215-6.893m-1.215 6.893-3.94-.694m5.155-6.2L8.29 4.26m5.908 1.042.348-1.97M7.48 20.364l3.126-17.727"/>',
  code: '<path d="m16 18 6-6-6-6"/><path d="m8 6-6 6 6 6"/>',
  shield: '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/>',
  layers: '<path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/><path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/>',
  megaphone: '<path d="m3 11 18-5v12L3 14v-3z"/><path d="M11.6 16.8a3 3 0 1 1-5.8-1.6"/>',
  atom: '<circle cx="12" cy="12" r="1"/><path d="M20.2 20.2c2.04-2.03.02-7.36-4.5-11.9-4.54-4.52-9.87-6.54-11.9-4.5-2.04 2.03-.02 7.36 4.5 11.9 4.54 4.52 9.87 6.54 11.9 4.5Z"/><path d="M15.7 15.7c4.52-4.54 6.54-9.87 4.5-11.9-2.03-2.04-7.36-.02-11.9 4.5-4.52 4.54-6.54 9.87-4.5 11.9 2.03 2.04 7.36.02 11.9-4.5Z"/>',
  heart: '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/><path d="M3.22 12H9.5l.5-1 2 4.5 2-7 1.5 3.5h5.27"/>',
  leaf: '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>',
  cap: '<path d="M21.42 10.922a1 1 0 0 0-.019-1.838L12.83 5.18a2 2 0 0 0-1.66 0L2.6 9.08a1 1 0 0 0 0 1.832l8.57 3.908a2 2 0 0 0 1.66 0z"/><path d="M22 10v6"/><path d="M6 12.5V16a6 3 0 0 0 12 0v-3.5"/>',
  zap: '<path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"/>',
  presentation: '<path d="M2 3h20"/><path d="M21 3v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V3"/><path d="m7 21 5-5 5 5"/>',
  wrench: '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>',
  video: '<path d="m16 13 5.223 3.482a.5.5 0 0 0 .777-.416V7.87a.5.5 0 0 0-.752-.432L16 10.5"/><rect x="2" y="6" width="14" height="12" rx="2"/>',
  mic: '<path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><path d="M12 19v3"/>',
  earth: '<path d="M21.54 15H17a2 2 0 0 0-2 2v4.54"/><path d="M7 3.34V5a3 3 0 0 0 3 3a2 2 0 0 1 2 2c0 1.1.9 2 2 2a2 2 0 0 0 2-2c0-1.1.9-2 2-2h3.17"/><path d="M11 21.95V18a2 2 0 0 0-2-2a2 2 0 0 1-2-2v-1a2 2 0 0 0-2-2H2.05"/><circle cx="12" cy="12" r="10"/>',
  eyeoff: '<path d="M10.733 5.076a10.744 10.744 0 0 1 11.205 6.575 1 1 0 0 1 0 .696 10.747 10.747 0 0 1-1.444 2.49"/><path d="M14.084 14.158a3 3 0 0 1-4.242-4.242"/><path d="M17.479 17.499a10.75 10.75 0 0 1-15.417-5.151 1 1 0 0 1 0-.696 10.75 10.75 0 0 1 4.446-5.143"/><path d="m2 2 20 20"/>',
  percent: '<path d="M19 5 5 19"/><circle cx="6.5" cy="6.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/>',
  trophy: '<path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6M18 9h1.5a2.5 2.5 0 0 0 0-5H18M4 22h16M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22M18 2H6v7a6 6 0 0 0 12 0V2Z"/>',
  music: '<path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/>',
  ticket: '<path d="M2 9a3 3 0 0 1 0 6v2a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-2a3 3 0 0 1 0-6V7a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2Z"/><path d="M13 5v2M13 17v2M13 11v2"/>',
  palette: '<circle cx="13.5" cy="6.5" r=".5" fill="currentColor"/><circle cx="17.5" cy="10.5" r=".5" fill="currentColor"/><circle cx="8.5" cy="7.5" r=".5" fill="currentColor"/><circle cx="6.5" cy="12.5" r=".5" fill="currentColor"/><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2z"/>',
  film: '<rect width="18" height="18" x="3" y="3" rx="2"/><path d="M7 3v18M3 7.5h4M3 12h18M3 16.5h4M17 3v18M17 7.5h4M17 16.5h4"/>',
  book: '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>',
  smile: '<circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2M9 9h.01M15 9h.01"/>',
  image: '<rect width="18" height="18" x="3" y="3" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/>',
  tent: '<path d="M3.5 21 14 3M20.5 21 10 3M15.5 21 12 15l-3.5 6M2 21h20"/>',
  languages: '<path d="m5 8 6 6M4 14l6-6 2-3M2 5h12M7 2h1M22 22l-5-10-5 10M14 18h6"/>',
  briefcase: '<path d="M16 20V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/><rect width="20" height="14" x="2" y="6" rx="2"/>',
  mail: '<rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
  linkedin: '<path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/><rect width="4" height="12" x="2" y="9"/><circle cx="4" cy="4" r="2"/>',
  twitter: '<path d="M4 4h4.5L20 20h-4.5zM20 4l-6.6 7.2M4 20l6.6-7.2"/>',
  info: '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>',
  github: '<path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"/><path d="M9 18c-4.51 2-5-2-7-2"/>',
};

const icon = (n, cls = "i") => `<svg class="${cls}" viewBox="0 0 24 24">${ICONS[n] || ""}</svg>`;
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
let api;

// ---------- language ----------
const LANG = () => (S.boot?.settings.lang === "en" ? "en" : "tr");
const LOC = () => (LANG() === "en" ? "en-GB" : "tr-TR");
/** Translated UI string; {0}, {1}… are filled from the remaining arguments. */
function t(key, ...args) {
  let s = I18N[LANG()][key] ?? I18N.tr[key] ?? key;
  if (typeof s === "string") args.forEach((a, i) => (s = s.replaceAll(`{${i}}`, a)));
  return s;
}
const num = (n) => Number(n).toLocaleString(LOC());
function applyI18n() {
  document.documentElement.lang = LANG();
  $$("[data-i18n]").forEach((el) => (el.textContent = t(el.dataset.i18n)));
  $$("[data-i18n-ph]").forEach((el) => (el.placeholder = t(el.dataset.i18nPh)));
  $$("[data-i18n-title]").forEach((el) => (el.title = t(el.dataset.i18nTitle)));
  $("#lang-btn span").textContent = LANG() === "en" ? "TR" : "EN";
  $("#sort").innerHTML = ["score", "date", "imp", "new"].filter((v) => v !== "score" || personal())
    .map((v) => `<option value="${v}">${t("sort_" + v)}</option>`).join("");
  $("#sort").value = S.f.sort;
}

// ---------- state ----------
const S = {
  boot: null, events: [], byId: {}, learned: [], news: [],
  f: { q: "", time: "all", sort: "score", domain: "all", cats: new Set(), region: "all", kind: "all", src: "all", free: false, past: false, hidden: false },
  layout: "grid", shown: 60, view: "discover",
  cal: { y: new Date().getFullYear(), m: new Date().getMonth(), sel: null },
  savedTab: "save", newsSrc: "all",
};
/** "For you" mode ranks by fit; "all events" mode is a plain chronological list without scores. */
const personal = () => S.boot?.settings.personalize !== false;
const META = () => S.boot.meta;
const catMeta = (id) => META().categories.find((c) => c.id === id);
const kindMeta = (id) => META().kinds.find((k) => k.id === id) || META().kinds[0];
const regionMeta = (id) => META().regions.find((r) => r.id === id);
const srcLabel = (id) => META().source_labels[id] || id;
const TINTS = {
  ai: "purple", startup: "orange", invest: "green", fintech: "cyan", crypto: "yellow", dev: "blue", security: "red", product: "magenta",
  growth: "orange", deeptech: "cyan", health: "red", climate: "green", research: "purple",
  music: "magenta", stage: "red", art: "yellow", film: "blue", lit: "green", family: "cyan",
};
const tint = (cat) => `--tint:var(--c-${TINTS[cat] || "blue"})`;
const flag = (cc) => (cc ? `<img class="flag" src="flags/${cc}.svg" alt="${cc.toUpperCase()}" onerror="this.remove()">` : "");
/** Icon for a meta item: "flag:tr", "flag:us+ca" or a lucide icon name. */
function iconFor(m) {
  if (!m) return "";
  if (m.icon.startsWith("flag:")) return `<span class="flags">${m.icon.slice(5).split("+").map(flag).join("")}</span>`;
  return icon(m.icon);
}
const locIcon = (e) => (e.online ? icon("globe") : e.cc ? flag(e.cc) : icon("pin"));

// ---------- dates ----------
const monthShort = (i) => new Date(2020, i, 1).toLocaleDateString(LOC(), { month: "short" }).replace(".", "");
const isDateOnly = (s) => s && s.length === 10;
function parseD(s) {
  if (!s) return null;
  if (isDateOnly(s)) { const [y, m, d] = s.split("-").map(Number); return new Date(y, m - 1, d); }
  return new Date(s);
}
function endOf(e) {
  const d = parseD(e.end || e.start);
  if (d && isDateOnly(e.end || e.start)) d.setHours(23, 59, 59);
  return d;
}
const now = () => new Date();
const isPast = (e) => endOf(e) < now();
const isLive = (e) => parseD(e.start) <= now() && endOf(e) >= now();
const sameDay = (a, b) => a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate();
const dayKey = (d) => `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`;
function fmtDay(s, withTime = true) {
  const d = parseD(s);
  const time = withTime && !isDateOnly(s) ? " · " + d.toLocaleTimeString(LOC(), { hour: "2-digit", minute: "2-digit" }) : "";
  return `${d.getDate()} ${monthShort(d.getMonth())} ${d.getFullYear()}, ${d.toLocaleDateString(LOC(), { weekday: "short" })}${time}`;
}
function fmtRange(e, withTime = true) {
  const s = parseD(e.start), en = e.end ? parseD(e.end) : null;
  if (!en || sameDay(s, en)) return fmtDay(e.start, withTime);
  if (s.getMonth() === en.getMonth() && s.getFullYear() === en.getFullYear())
    return `${s.getDate()}–${en.getDate()} ${monthShort(s.getMonth())} ${s.getFullYear()}`;
  const sy = s.getFullYear() !== en.getFullYear() ? ` ${s.getFullYear()}` : "";
  return `${s.getDate()} ${monthShort(s.getMonth())}${sy} – ${en.getDate()} ${monthShort(en.getMonth())} ${en.getFullYear()}`;
}
function relTime(iso) {
  if (!iso) return "";
  const diff = (new Date(iso) - now()) / 1000;
  const rtf = new Intl.RelativeTimeFormat(LANG(), { numeric: "auto" });
  const units = [["day", 86400], ["hour", 3600], ["minute", 60]];
  for (const [u, sec] of units) if (Math.abs(diff) >= sec || u === "minute") return rtf.format(Math.round(diff / sec), u);
}
function daysUntil(e) { return Math.ceil((parseD(e.start) - now()) / 86400000); }

// ---------- filtering ----------
function locText(e) {
  if (e.online) return "Online";
  // venues often already contain the city ("MEO Arena, Lisbon"), so skip repeated parts
  const parts = [];
  for (const p of [e.venue, e.city, e.country]) {
    if (p && !parts.join(", ").toLocaleLowerCase("tr").includes(p.toLocaleLowerCase("tr"))) parts.push(p);
  }
  return parts.join(", ") || regionMeta(e.region)?.label || "";
}
function passes(e, { ignoreTime = false, ignorePast = false } = {}) {
  const f = S.f;
  // hiding is part of personalization; the plain list shows everything
  if (personal() && !f.hidden && e.state.includes("dislike")) return false;
  if (!ignorePast && !f.past && isPast(e)) return false;
  if (f.domain !== "all" && e.domain !== f.domain) return false;
  if (f.cats.size && !e.categories.some((c) => f.cats.has(c))) return false;
  if (f.region !== "all" && e.region !== f.region) return false;
  if (f.kind !== "all" && e.kind !== f.kind) return false;
  if (f.src !== "all" && e.source !== f.src && !e.also.some((a) => a.source === f.src)) return false;
  if (f.free && e.is_free !== true) return false;
  if (!ignoreTime && f.time !== "all") {
    const lim = { week: 7, month: 30, q: 90 }[f.time];
    if (parseD(e.start) > new Date(Date.now() + lim * 86400000)) return false;
  }
  if (f.q) {
    const hay = (e.title + " " + e.city + " " + e.country + " " + e.organizer + " " + e.venue + " " + (e.description || "").slice(0, 300) + " " + e.categories.map((c) => catMeta(c)?.label).join(" ")).toLocaleLowerCase("tr");
    if (!f.q.toLocaleLowerCase("tr").split(/\s+/).every((w) => hay.includes(w))) return false;
  }
  return true;
}
/** Chronological key: events already running (exhibitions, open hackathons) sort by their closing date, so a
 * show that opened months ago doesn't sit above everything happening this week. */
function dateKey(e) {
  const s = parseD(e.start);
  return s < now() && e.end ? endOf(e) : s;
}
function sorted(list) {
  const by = {
    score: (a, b) => b.score - a.score || parseD(a.start) - parseD(b.start),
    date: (a, b) => dateKey(a) - dateKey(b),
    imp: (a, b) => b.imp - a.imp || parseD(a.start) - parseD(b.start),
    new: (a, b) => (b.first_seen || "").localeCompare(a.first_seen || "") || parseD(a.start) - parseD(b.start),
  }[S.f.sort] || ((a, b) => parseD(a.start) - parseD(b.start));
  return [...list].sort(by);
}

// ---------- components ----------
function ring(score) {
  if (!personal()) return "";
  const r = 17, c = 2 * Math.PI * r, col = score >= 75 ? "var(--good)" : score >= 55 ? "var(--accent)" : "var(--faint)";
  return `<div class="ring" title="${esc(t("fit_title", score))}"><svg viewBox="0 0 42 42"><circle class="bg" cx="21" cy="21" r="${r}"/><circle cx="21" cy="21" r="${r}" stroke="${col}" stroke-dasharray="${(c * score) / 100} ${c}" stroke-linecap="round"/></svg><span>${score}</span></div>`;
}
function coverHTML(e, cls = "cover", badge = true) {
  // placeholder (tinted dot grid + category mark) sits underneath; a real image, when it loads, covers it
  const cat = e.categories[0];
  const mark = (cat && catMeta(cat)) || kindMeta(e.kind);
  const d = parseD(e.start);
  return `<div class="${cls}" style="${tint(cat)}">
    <div class="ph-mark"><span class="ph-icon">${icon(mark.icon)}</span><small>${esc(mark.label)}</small></div>
    ${e.image ? `<img src="${esc(e.image)}" loading="lazy" referrerpolicy="no-referrer" onerror="this.remove()">` : ""}
    ${badge ? `<div class="date-badge"><b>${d.getDate()}</b><small>${monthShort(d.getMonth()).toLocaleUpperCase(LOC())}</small></div>` : ""}
    ${badge && isLive(e) ? `<span class="live-badge">${t("live")}</span>` : badge && e.extra?.sold_out ? `<span class="live-badge sold">${t("sold_out")}</span>` : ""}
  </div>`;
}
function actionBtns(e) {
  const on = (a) => (e.state.includes(a) ? " on" : "");
  return `<button class="icon-btn like${on("like")}" data-act="like" title="${esc(t("act_like"))}">${icon("up")}</button>
    <button class="icon-btn dislike${on("dislike")}" data-act="dislike" title="${esc(t("act_dislike"))}">${icon("down")}</button>
    <button class="icon-btn save${on("save")}" data-act="save" title="${esc(t("act_save"))}">${icon("bookmark")}</button>
    <span class="grow"></span>
    <button class="icon-btn" data-act="open" title="${esc(t("act_open"))}">${icon("ext")}</button>`;
}
function extraLine(e) {
  const x = e.extra || {};
  if (x.prize) return `<div class="meta-line">${icon("trophy")}<span>${esc(t("prize_line", x.prize))}${e.guest_count ? ` · ${t("signups", num(e.guest_count))}` : ""}</span></div>`;
  if (x.performances) return `<div class="meta-line">${icon("calendar")}<span>${t("performances", x.performances)}${x.venues ? ` · ${t("in_venues", x.venues)}` : ""}</span></div>`;
  if (e.guest_count && e.source === "luma") return `<div class="meta-line">${icon("users")}<span>${t("attendees", e.guest_count)}${e.is_free ? " · " + t("free") : ""}</span></div>`;
  if (x.next_deadline) return `<div class="meta-line">${icon("clock")}<span>${esc(t("deadline", x.next_deadline.date))}</span></div>`;
  return "";
}
function cardHTML(e) {
  const kind = kindMeta(e.kind);
  const cats = e.categories.slice(0, 3).map(catMeta).filter(Boolean).map((c) => `<span class="tag">${icon(c.icon)}${esc(c.label)}</span>`).join("");
  const reasons = personal() && e.reasons.length ? `<div class="reasons">${e.reasons.map((r) => `<span class="reason">${esc(r)}</span>`).join("")}</div>` : "";
  return `<article class="card${personal() && e.state.includes("dislike") ? " disliked" : ""}" data-id="${esc(e.id)}">
    ${coverHTML(e)}
    <div class="content">
      <div class="top"><h3>${esc(e.title)}</h3>${ring(e.score)}</div>
      <div class="meta-line">${icon("clock")}<span>${fmtRange(e)}</span></div>
      <div class="meta-line">${locIcon(e)}<span>${esc(locText(e))}</span></div>
      ${extraLine(e)}
      <div class="tags"><span class="tag srcname">${esc(srcLabel(e.source))}${e.also.length ? ` +${e.also.length}` : ""}</span><span class="tag kind">${icon(kind.icon)}${esc(kind.label)}</span>${cats}</div>
      ${reasons}
    </div>
    <div class="actions">${actionBtns(e)}</div>
  </article>`;
}
function featHTML(e) {
  return `<div class="feat" data-id="${esc(e.id)}">${coverHTML(e, "cover", false)}${ring(e.score)}
    <div class="body"><b>${esc(e.title)}</b><small>${icon("clock")}${fmtRange(e, false)}</small><small>${locIcon(e)}${esc(locText(e))}</small></div></div>`;
}

// ---------- discover ----------
function renderDiscover() {
  const list = sorted(S.events.filter((e) => passes(e)));
  const grid = $("#grid");
  grid.className = "grid" + (S.layout === "list" ? " list" : "");
  $$("#mode-seg button").forEach((b) => b.classList.toggle("on", b.dataset.v === (personal() ? "personal" : "all")));
  $("#f-hidden-wrap").style.display = personal() ? "" : "none";
  const anyFilter = S.f.q || S.f.cats.size || S.f.region !== "all" || S.f.kind !== "all" || S.f.src !== "all" || S.f.free || S.f.time !== "all";
  $("#result-title").textContent = anyFilter ? t("results_filtered") : t("results_all");
  $("#result-count").textContent = t("n_events", num(list.length));
  if (!S.events.length) {
    grid.innerHTML = `<div class="empty loading-screen" style="grid-column:1/-1"><div class="spin">${icon("refresh")}</div><b>${t("loading_title")}</b>${t("loading_sub")}</div>`;
  } else if (!list.length) {
    grid.innerHTML = `<div class="empty" style="grid-column:1/-1"><b>${t("no_results")}</b>${t("no_results_sub")}</div>`;
  } else {
    grid.innerHTML = list.slice(0, S.shown).map(cardHTML).join("");
  }
  $("#more-wrap").style.display = list.length > S.shown ? "" : "none";
  $("#more-btn").textContent = t("more", num(list.length - S.shown));

  // featured: upcoming 60 days — best blend of fit and importance, or importance alone in the plain list
  const lim = Date.now() + 60 * 86400000;
  const rank = personal() ? (e) => e.score * 0.65 + e.imp * 0.35 : (e) => e.imp;
  const pool = S.events.filter((e) => passes(e, { ignoreTime: true }) && !isPast(e) && parseD(e.start) <= lim && !(personal() && e.state.includes("dislike")))
    .sort((a, b) => rank(b) - rank(a) || parseD(a.start) - parseD(b.start));
  // with both areas shown, alternate them so tech flagships don't crowd out culture
  const feat = [];
  if (S.f.domain === "all") {
    const lanes = META().domains.map((d) => pool.filter((e) => e.domain === d.id));
    for (let i = 0; feat.length < 4 && lanes.some((l) => l[i]); i++) lanes.forEach((l) => l[i] && feat.length < 4 && feat.push(l[i]));
  } else feat.push(...pool.slice(0, 4));
  $("#featured-title").textContent = t(personal() ? "featured_personal" : "featured_all");
  $("#featured-sub").textContent = t(personal() ? "featured_personal_sub" : "featured_all_sub");
  $("#featured-wrap").style.display = feat.length && !S.f.q ? "" : "none";
  $("#featured").innerHTML = feat.map(featHTML).join("");
  updateCounts();
}
function updateCounts() {
  $("#cnt-discover").textContent = S.events.filter((e) => !isPast(e) && (S.f.domain === "all" || e.domain === S.f.domain) && !(personal() && e.state.includes("dislike"))).length || "";
  $("#cnt-saved").textContent = S.events.filter((e) => e.state.includes("save")).length || "";
}
function buildFilters() {
  const inDomain = (x) => S.f.domain === "all" || x.domain === S.f.domain;
  const upcoming = S.events.filter((e) => !isPast(e) && inDomain(e));
  const counts = {}, kinds = {};
  upcoming.forEach((e) => { e.categories.forEach((c) => (counts[c] = (counts[c] || 0) + 1)); kinds[e.kind] = (kinds[e.kind] || 0) + 1; });
  $("#domain-seg").innerHTML = `<button data-v="all" class="${S.f.domain === "all" ? "on" : ""}">${icon("layers")} ${t("domain_all")}</button>` +
    META().domains.map((d) => `<button data-v="${d.id}" class="${S.f.domain === d.id ? "on" : ""}">${icon(d.icon)} ${esc(d.label)}</button>`).join("");
  $("#cat-chips").innerHTML = META().categories.filter(inDomain).map((c) =>
    `<button class="chip${S.f.cats.has(c.id) ? " on" : ""}" data-cat="${c.id}">${icon(c.icon)}${esc(c.label)} <span class="n">${num(counts[c.id] || 0)}</span></button>`).join("");
  $("#region-seg").innerHTML = `<button data-v="all" class="${S.f.region === "all" ? "on" : ""}">${t("anywhere")}</button>` +
    META().regions.map((r) => `<button data-v="${r.id}" class="${S.f.region === r.id ? "on" : ""}">${iconFor(r)} ${esc(r.label)}</button>`).join("");
  $("#kind-sel").innerHTML = `<option value="all">${t("kind_all")}</option>` + META().kinds.filter((k) => kinds[k.id] || S.f.kind === k.id)
    .map((k) => `<option value="${k.id}">${esc(k.label)} (${num(kinds[k.id] || 0)})</option>`).join("");
  $("#kind-sel").value = S.f.kind;
  const srcs = [...new Set(S.events.filter(inDomain).map((e) => e.source))].sort();
  $("#src-sel").innerHTML = `<option value="all">${t("src_all")}</option>` + srcs.map((s) => `<option value="${s}">${esc(srcLabel(s))}</option>`).join("");
  $("#src-sel").value = srcs.includes(S.f.src) ? S.f.src : "all";
}
/** Discover opens on the areas chosen in the profile; both (or none) means everything. */
function defaultDomain() {
  const d = S.boot.settings.domains || [];
  return d.length === 1 ? d[0] : "all";
}

// ---------- interactions ----------
let rescoreTimer;
async function act(id, action) {
  const e = S.byId[id];
  if (!e) return;
  if (action === "open") return api.open_url(e.url);
  const on = !e.state.includes(action);
  e.state = e.state.filter((a) => a !== action && !(on && ((action === "like" && a === "dislike") || (action === "dislike" && a === "like"))));
  if (on) e.state.push(action);
  await api.interact(id, action, on);
  refreshCardsFor(id);
  if (action === "dislike" && on) toast(t("t_hidden"), t("t_undo"), () => act(id, "dislike"));
  else if (action === "like" && on) toast(t("t_liked"));
  else if (action === "save" && on) toast(t("t_saved"));
  else if (action === "attended" && on) toast(t("t_attended"));
  updateCounts();
  clearTimeout(rescoreTimer);
  rescoreTimer = setTimeout(rescore, 700);
}
function refreshCardsFor(id) {
  const e = S.byId[id];
  $$(`.card[data-id="${CSS.escape(id)}"]`).forEach((el) => {
    if (personal() && e.state.includes("dislike") && !S.f.hidden && el.closest("#grid")) {
      el.style.transition = "opacity .25s, transform .25s"; el.style.opacity = 0; el.style.transform = "scale(.96)";
      setTimeout(() => el.remove(), 250);
    } else el.outerHTML = cardHTML(e);
  });
  if ($("#drawer").classList.contains("open") && $("#drawer").dataset.id === id) openDrawer(id);
  if (S.view === "saved") renderSaved();
}
/** Re-score after an interaction without reordering what the user is looking at. */
async function rescore() {
  await loadEvents();
  $$("#grid .card, #saved-grid .card").forEach((el) => { const e = S.byId[el.dataset.id]; if (e) el.outerHTML = cardHTML(e); });
  if (S.view === "profile") renderLearned();
}
async function loadEvents() {
  const r = await api.get_events();
  S.events = r.events; S.learned = r.learned;
  S.byId = {};
  S.events.forEach((e) => (S.byId[e.id] = e));
}

// ---------- drawer ----------
function gcalUrl(e) {
  const f = (s, end) => {
    if (isDateOnly(s)) { const d = parseD(s); if (end) d.setDate(d.getDate() + 1); return `${d.getFullYear()}${String(d.getMonth() + 1).padStart(2, "0")}${String(d.getDate()).padStart(2, "0")}`; }
    return s.replace(/[-:]/g, "");
  };
  const p = new URLSearchParams({ action: "TEMPLATE", text: e.title, dates: `${f(e.start)}/${f(e.end || e.start, true)}`, details: `${(e.description || "").slice(0, 600)}\n\n${e.url}`, location: locText(e) });
  return "https://calendar.google.com/calendar/render?" + p;
}
function openDrawer(id) {
  const e = S.byId[id];
  if (!e) return;
  const d = $("#drawer");
  d.dataset.id = id;
  const kind = kindMeta(e.kind), x = e.extra || {};
  const info = [
    [t("d_date"), fmtRange(e)],
    [t("d_location"), locText(e)],
    e.organizer && [t("d_organizer"), e.organizer],
    [t("d_kind"), kind.label],
    e.guest_count && [e.source === "devpost" ? t("d_registered") : t("d_attendees"), num(e.guest_count)],
    e.is_free != null && [t("d_price"), e.is_free ? t("free") : t("paid")],
    x.prize && [t("d_prize"), x.prize],
    x.time_left && [t("d_time_left"), x.time_left],
    x.next_deadline && [t("d_next_deadline"), `${x.next_deadline.label}: ${x.next_deadline.date}`],
    x.spots_remaining != null && [t("d_spots"), x.spots_remaining],
    !isPast(e) && [t("d_days_left"), isLive(e) ? t("d_live_now") : t("d_days", daysUntil(e))],
  ].filter(Boolean);
  const dates = x.dates?.length > 1 ? `<div class="dates"><small>${t("d_dates")}</small><div class="date-list">${x.dates.map((s) => `<span class="chip">${esc(fmtDay(s))}</span>`).join("")}${x.performances > x.dates.length ? `<span class="chip ghost">${t("d_more_dates", x.performances - x.dates.length)}</span>` : ""}</div></div>` : "";
  const on = (a) => e.state.includes(a);
  const scoreBox = personal()
    ? `<div class="score-box">${ring(e.score)}<div><b>${t("d_fit", e.score)}</b> · ${t("d_importance", e.imp)}<div class="reasons" style="margin-top:6px">${e.reasons.map((r) => `<span class="reason">${esc(r)}</span>`).join("") || `<span class="muted" style="font-size:12px;color:var(--muted)">${t("d_fit_hint")}</span>`}</div></div></div>`
    : `<div class="score-box plain"><b>${t("d_importance_only", e.imp)}</b></div>`;
  d.innerHTML = `<button class="icon-btn close" data-close>${icon("x")}</button>
    ${coverHTML(e)}
    <div class="inner">
      <div class="tags"><span class="tag srcname">${esc(srcLabel(e.source))}</span>${e.categories.map(catMeta).filter(Boolean).map((c) => `<span class="tag">${icon(c.icon)}${esc(c.label)}</span>`).join("")}</div>
      <h2>${esc(e.title)}</h2>
      ${scoreBox}
      <div class="btn-row">
        <button class="btn primary" data-dact="open">${icon("ext")}${t("d_open")}</button>
        <button class="btn" data-dact="gcal">${icon("calendar")}${t("d_gcal")}</button>
        <button class="btn" data-dact="ics">${icon("download")}.ics</button>
      </div>
      <div class="btn-row">
        <button class="btn${on("like") ? " primary" : ""}" data-dact="like">${icon("up")}${t("d_like")}</button>
        <button class="btn${on("dislike") ? " primary" : ""}" data-dact="dislike">${icon("down")}${t("d_dislike")}</button>
        <button class="btn${on("save") ? " primary" : ""}" data-dact="save">${icon("bookmark")}${on("save") ? t("d_saved") : t("d_save")}</button>
        <button class="btn${on("attended") ? " primary" : ""}" data-dact="attended">${icon("check")}${t("d_attended")}</button>
      </div>
      <div class="info-grid">${info.map(([k, v]) => `<div class="info"><small>${esc(k)}</small><div>${esc(v)}</div></div>`).join("")}</div>
      ${dates}
      ${e.description ? `<div class="desc">${esc(e.description)}</div>` : ""}
      ${e.also.length ? `<div><small style="color:var(--faint)">${t("d_also")}</small><div class="btn-row" style="margin-top:6px">${e.also.map((a) => `<button class="btn small" data-url="${esc(a.url)}">${esc(srcLabel(a.source))} ${icon("ext")}</button>`).join("")}</div></div>` : ""}
    </div>`;
  d.classList.add("open");
  $("#scrim").classList.add("open");
}
function closeDrawer() { $("#drawer").classList.remove("open"); $("#scrim").classList.remove("open"); }

// ---------- calendar ----------
function renderCalendar() {
  const { y, m } = S.cal;
  const first = new Date(y, m, 1);
  $("#cal-title").textContent = first.toLocaleDateString(LOC(), { month: "long", year: "numeric" });
  $("#cal-top-wrap").style.display = personal() ? "" : "none";
  const onlySaved = $("#cal-saved").checked, top = personal() && $("#cal-top").checked;
  const byDay = {};
  S.events.forEach((e) => {
    if (!passes(e, { ignoreTime: true, ignorePast: true })) return;
    if (onlySaved && !["save", "like", "attended"].some((a) => e.state.includes(a))) return;
    if (top && e.score < 60 && !e.state.includes("save")) return;
    (byDay[dayKey(parseD(e.start))] ||= []).push(e);
  });
  Object.values(byDay).forEach((l) => l.sort(personal() ? (a, b) => b.score - a.score : (a, b) => b.imp - a.imp));
  const start = new Date(first); start.setDate(1 - ((first.getDay() + 6) % 7));
  // Monday-first weekday names in the UI language (2024-01-01 was a Monday)
  let html = [...Array(7)].map((_, i) => `<div class="dow">${new Date(2024, 0, 1 + i).toLocaleDateString(LOC(), { weekday: "short" })}</div>`).join("");
  const sel = S.cal.sel || new Date();
  for (let i = 0; i < 42; i++) {
    const d = new Date(start); d.setDate(start.getDate() + i);
    const evs = byDay[dayKey(d)] || [];
    html += `<div class="day${d.getMonth() !== m ? " out" : ""}${sameDay(d, new Date()) ? " today" : ""}${sameDay(d, sel) ? " sel" : ""}" data-day="${d.toISOString()}">
      <span class="num">${d.getDate()}</span>
      ${evs.slice(0, 3).map((e) => `<div class="ev${personal() && e.score >= 75 ? " hot" : ""}" title="${esc(e.title)}">${esc(e.title)}</div>`).join("")}
      ${evs.length > 3 ? `<span class="plus">${t("cal_more", evs.length - 3)}</span>` : ""}</div>`;
  }
  $("#cal").innerHTML = html;
  const list = byDay[dayKey(sel)] || [];
  $("#day-panel").innerHTML = `<h3>${sel.toLocaleDateString(LOC(), { weekday: "long", day: "numeric", month: "long" })}</h3>` +
    (list.length ? list.slice(0, 80).map(miniHTML).join("") : `<div class="empty" style="padding:30px 10px">${t("cal_empty")}</div>`);
}
function miniHTML(e) {
  const mark = (e.categories[0] && catMeta(e.categories[0])) || kindMeta(e.kind);
  return `<div class="mini" data-id="${esc(e.id)}"><div class="thumb" style="${tint(e.categories[0])};${e.image ? `background-image:url('${esc(e.image)}')` : ""}">${e.image ? "" : icon(mark.icon)}</div>
    <div style="flex:1;min-width:0"><b>${esc(e.title)}</b><small>${esc(locText(e))} · ${esc(srcLabel(e.source))}</small></div>${ring(e.score)}</div>`;
}

// ---------- saved ----------
function renderSaved() {
  const list = S.events.filter((e) => e.state.includes(S.savedTab)).sort((a, b) => parseD(a.start) - parseD(b.start));
  $("#saved-grid").innerHTML = list.length ? list.map(cardHTML).join("")
    : `<div class="empty" style="grid-column:1/-1"><b>${t("saved_empty")}</b>${t("saved_empty_sub")}</div>`;
}

// ---------- news ----------
const NEWS_SOURCES = {
  swipeline: ["Swipeline", "orange", "tr"], webrazzi: ["Webrazzi", "red", "tr"], endeavor: ["Endeavor TR", "purple", "tr"],
  techcrunch: ["TechCrunch", "green", "global"], techmeme: ["Techmeme", "blue", "global"], crunchbase: ["Crunchbase News", "cyan", "global"],
};
const nsrc = (n) => NEWS_SOURCES[n.source] || [n.source, "blue", "global"];
const srcDot = (n) => `<span class="src-dot" style="--sc:var(--c-${nsrc(n)[1]})">${esc(n.outlet ? `${nsrc(n)[0]} · ${n.outlet}` : nsrc(n)[0])} <time>${relTime(n.published)}</time></span>`;
function newsImg(n, cls = "img") {
  return n.image ? `<div class="${cls}" style="background-image:url('${esc(n.image)}')"></div>`
    : `<div class="${cls} ph" style="--sc:var(--c-${nsrc(n)[1]})"><span>${esc(nsrc(n)[0])}</span></div>`;
}
function dayLabel(iso) {
  const d = new Date(iso), td = new Date();
  const diff = Math.round((new Date(td.getFullYear(), td.getMonth(), td.getDate()) - new Date(d.getFullYear(), d.getMonth(), d.getDate())) / 86400000);
  return diff === 0 ? t("today") : diff === 1 ? t("yesterday") : d.toLocaleDateString(LOC(), { day: "numeric", month: "long", weekday: "long" });
}
async function renderNews(reload = false) {
  if (reload || !S.news.length) S.news = await api.get_news();
  const scope = S.newsScope || "all";
  const inScope = S.news.filter((n) => scope === "all" || nsrc(n)[2] === scope);
  const counts = (k) => inScope.filter((n) => n.source === k).length;
  $("#news-chips").innerHTML = `<div class="news-top"><div class="seg" id="news-scope">
      ${[["all", t("news_all")], ["tr", t("news_tr")], ["global", t("news_global")]].map(([k, v]) => `<button data-scope="${k}" class="${scope === k ? "on" : ""}">${k === "tr" ? flag("tr") : k === "global" ? icon("earth") : ""} ${v}</button>`).join("")}</div>
      <div class="chips">${[["all", t("news_all_src")], ...Object.entries(NEWS_SOURCES).filter(([, v]) => scope === "all" || v[2] === scope).map(([k, v]) => [k, v[0]])]
        .map(([k, v]) => `<button class="chip${S.newsSrc === k ? " on" : ""}" data-news="${k}">${esc(v)} <span class="n">${k === "all" ? inScope.length : counts(k)}</span></button>`).join("")}</div></div>`;
  const list = inScope.filter((n) => S.newsSrc === "all" || n.source === S.newsSrc)
    .sort((a, b) => (b.published || "").localeCompare(a.published || ""));
  if (!list.length) { $("#news-list").innerHTML = `<div class="empty"><b>${t("news_empty")}</b>${t("news_empty_sub")}</div>`; return; }
  // lead: newest story with a picture, plus the next three as a side column
  const withImg = list.filter((n) => n.image);
  const lead = withImg[0] || list[0];
  const side = list.filter((n) => n !== lead).slice(0, 3);
  const rest = list.filter((n) => n !== lead && !side.includes(n));
  let html = `<div class="news-lead">
    <div class="lead-main" data-url="${esc(lead.url)}" style="${lead.image ? `background-image:url('${esc(lead.image)}')` : ""}">
      <div class="body">${srcDot(lead)}<h2>${esc(lead.title)}</h2><p>${esc(lead.summary)}</p></div></div>
    <div class="lead-side">${side.map((n) => `<div class="lead-item" data-url="${esc(n.url)}">${newsImg(n)}<div>${srcDot(n)}<b>${esc(n.title)}</b></div></div>`).join("")}</div>
  </div>`;
  let day = null;
  for (const n of rest) {
    const lbl = n.published ? dayLabel(n.published) : t("undated");
    if (lbl !== day) { html += `${day ? "</div>" : ""}<div class="day-head">${esc(lbl)}</div><div class="news-grid">`; day = lbl; }
    html += `<article class="ncard" data-url="${esc(n.url)}">${newsImg(n)}<div class="body">${srcDot(n)}<b>${esc(n.title)}</b>
      ${n.summary ? `<p>${esc(n.summary)}</p>` : ""}${n.byline ? `<span class="byline">${esc(n.byline)}</span>` : ""}</div></article>`;
  }
  $("#news-list").innerHTML = html + (day ? "</div>" : "");
}

// ---------- sources ----------
async function renderSources(reload = true) {
  if (reload) S.boot.sources = await api.sources();
  const srcs = S.boot.sources;
  const ok = srcs.filter((s) => s.status === "events").length;
  // the "Slush / Web Summit" card covers two sites
  $("#src-summary").textContent = t("src_summary", srcs.length + 1, ok + 1, num(S.events.length));
  const pill = { events: t("pill_events"), news: t("pill_news"), blocked: t("pill_blocked") };
  const card = (s) => {
    const r = s.run;
    return `<div class="src" data-src="${s.id}">
      <div class="row"><h3>${esc(s.label)}</h3><span class="pill ${s.status}">${pill[s.status]}</span></div>
      <p>${esc(s.note)}</p>
      <div class="stats">
        <div><b>${r ? num(r.count) : "—"}</b>${s.status === "events" ? t("src_events") : t("src_news_all")}</div>
        <div><b>${r ? t("sec", r.duration) : "—"}</b>${t("src_duration")}</div>
        <div><b>${r ? relTime(r.last_run) : "—"}</b>${t("src_last")}</div>
      </div>
      ${r && r.error ? `<div class="err">${esc(r.error)}</div>` : ""}
      <div class="row">
        ${s.status === "events" ? `<label class="toggle"><input type="checkbox" data-enable="${s.id}" ${s.enabled ? "checked" : ""}><span class="sw"></span>${t("src_enabled")}</label>` : ""}
        <span style="flex:1"></span>
        <button class="btn small" data-refresh-src="${s.status === "events" ? s.id : "news"}">${icon("refresh")}${t("src_refresh")}</button>
        <button class="btn small ghost" data-url="${esc(s.home)}">${icon("ext")}${t("src_site")}</button>
      </div></div>`;
  };
  const groups = [["culture", (s) => s.status === "events" && s.domain === "culture"], ["tech", (s) => s.status === "events" && s.domain === "tech"],
    ["mixed", (s) => s.status === "events" && s.domain === "mixed"], ["news", (s) => s.status !== "events"]];
  $("#src-groups").innerHTML = groups.map(([g, fn]) => {
    const list = srcs.filter(fn);
    return list.length ? `<h2 class="group-head">${t("src_group_" + g)} <span class="n">${list.length}</span></h2><div class="src-grid">${list.map(card).join("")}</div>` : "";
  }).join("");
}

// ---------- profile ----------
const LEVELS = () => [[-1, t("lv_no")], [0, t("lv_neutral")], [1, t("lv_some")], [2, t("lv_very")]];
function levelRows(container, items, values, onChange) {
  container.innerHTML = items.map((it) => `<div class="level-row"><span class="lbl">${iconFor(it)} ${esc(it.label)}</span>
    <div class="levels" data-key="${it.id}">${LEVELS().map(([v, l]) => `<button data-v="${v}" class="${(values[it.id] || 0) === v ? "on" : ""}">${l}</button>`).join("")}</div></div>`).join("");
  container.onclick = (ev) => {
    const b = ev.target.closest(".levels button");
    if (!b) return;
    const key = b.parentElement.dataset.key, v = Number(b.dataset.v);
    values[key] = v;
    $$("button", b.parentElement).forEach((x) => x.classList.toggle("on", x === b));
    onChange();
  };
}
/** Category level rows split by area, limited to the areas the user follows. */
function categoryRows(container, values, domains, onChange) {
  const doms = META().domains.filter((d) => !domains.length || domains.includes(d.id));
  container.innerHTML = doms.map((d) => `<h3 class="w-h">${icon(d.icon)} ${esc(d.label)}</h3><div data-dom="${d.id}"></div>`).join("");
  doms.forEach((d) => levelRows($(`[data-dom="${d.id}"]`, container), META().categories.filter((c) => c.domain === d.id), values, onChange));
}
let profileTimer;
function profileChanged() {
  clearTimeout(profileTimer);
  profileTimer = setTimeout(async () => {
    await api.save_settings({ profile: S.boot.settings.profile });
    await loadEvents();
    toast(t("t_profile_saved"));
  }, 500);
}
function domainChecks(box, selected, onChange) {
  box.innerHTML = META().domains.map((d) => `<label class="check"><input type="checkbox" data-dom="${d.id}" ${selected.includes(d.id) ? "checked" : ""}><span class="box">${icon("check")}</span>${icon(d.icon)} ${esc(d.label)}</label>`).join("");
  box.onchange = (ev) => {
    const id = ev.target.dataset.dom;
    if (!id) return;
    const set = new Set(selected);
    ev.target.checked ? set.add(id) : set.delete(id);
    if (!set.size) { ev.target.checked = true; return; }  // at least one area
    selected.splice(0, selected.length, ...META().domains.map((d) => d.id).filter((x) => set.has(x)));
    onChange();
  };
}
function renderProfile() {
  const st = S.boot.settings, p = st.profile;
  $$("#prof-lang button").forEach((b) => b.classList.toggle("on", b.dataset.v === LANG()));
  $$("#prof-mode button").forEach((b) => b.classList.toggle("on", b.dataset.v === (personal() ? "personal" : "all")));
  st.domains = st.domains?.length ? st.domains : META().domains.map((d) => d.id);
  domainChecks($("#prof-domains"), st.domains, async () => {
    S.boot.settings = await api.save_settings({ domains: st.domains });
    S.f.domain = defaultDomain(); S.f.cats.clear();
    buildFilters(); renderProfile(); toast(t("t_saved_next").split("—")[0].trim());
  });
  categoryRows($("#prof-cats"), p.interests, st.domains, profileChanged);
  levelRows($("#prof-kinds"), META().kinds.filter((k) => st.domains.includes(k.domain) || st.domains.length === 2), p.kinds, profileChanged);
  levelRows($("#prof-regions"), META().regions, p.regions, profileChanged);
  tagInput($("#luma-tags"), $("#luma-suggest"), st.luma_slugs, LUMA_SUGGEST, settingSaver("luma_slugs", "luma"));
  tagInput($("#eb-tags"), $("#eb-suggest"), st.eventbrite_places, EB_SUGGEST, settingSaver("eventbrite_places", "eventbrite"));
  tagInput($("#fc-tags"), $("#fc-suggest"), st.foundercal_cities, FC_SUGGEST, settingSaver("foundercal_cities", "foundercal"));
  renderLearned();
}
/** About & Help tab: the app, its developer (contact + social links) and a short user guide. */
function renderAbout() {
  const a = S.boot.about, L = a.links || {};
  const social = [["x", "twitter", t("about_x"), "@" + (L.x || "").split("/").filter(Boolean).pop()],
    ["linkedin", "linkedin", t("about_linkedin"), "in/" + (L.linkedin || "").split("/").filter(Boolean).pop()],
    ["github", "github", t("about_github"), (L.github || "").replace(/^https?:\/\//, "")]]
    .filter(([k]) => L[k]).map(([k, ic, label, handle]) => `<button class="social ${k}" data-url="${esc(L[k])}">
      <span class="s-icon">${icon(ic)}</span><span><b>${esc(label)}</b><small>${esc(handle)}</small></span>${icon("ext", "i go")}</button>`).join("");
  const initials = a.author.split(/\s+/).filter(Boolean).map((w) => w[0]).filter((_, i, arr) => i === 0 || i === arr.length - 1).join("");
  const mail = `mailto:${a.email}?subject=${encodeURIComponent(`Etkinlik Radarı ${S.boot.version}`)}`;
  $("#about-left").innerHTML = `
    <div class="panel about-app">
      <div class="about-row"><div class="brand-logo big">${icon("radar")}</div>
        <div><h2>Etkinlik Radarı</h2><small>${t("about_version", S.boot.version)} · ${t("about_license")}</small></div></div>
      <p>${esc(t("about_desc", S.boot.sources.length + 1))}</p>
    </div>
    <div class="panel dev-card">
      <small class="eyebrow">${t("about_dev")}</small>
      <div class="dev-head"><div class="avatar">${esc(initials)}</div>
        <div><h2>${esc(a.author)}</h2><small>${t("about_role")}</small></div></div>
      <div class="contact-row" data-url="${esc(mail)}">${icon("mail")}<span><small>${t("about_contact")}</small><b>${esc(a.email)}</b></span>
        <button class="btn small primary">${t("about_mail")}</button></div>
      <small class="eyebrow">${t("about_follow")}</small>
      <div class="socials">${social}</div>
    </div>
    <div class="panel">
      <h2>${t("about_support")}</h2><p>${t("about_support_d")}</p>
      <div class="btn-row">
        <button class="btn small" data-url="${esc(L.github ? L.github.replace(/\/$/, "") + "/issues" : mail)}">${icon("shield")}${t("about_bug")}</button>
        <button class="btn small ghost" id="open-data">${icon("db")}${t("about_open_data")}</button>
      </div>
      <div class="info wide" style="margin-top:12px"><small>${t("about_data")}</small><div><code>${esc(S.boot.data_dir)}</code></div></div>
      <p class="hint">${t("about_notices")}</p>
    </div>`;
  $("#about-right").innerHTML = `
    <div class="panel">
      <h2>${t("help_start")}</h2>
      <div class="feature-list">${t("help_steps").map(([ic, tt, d], i) => `<div class="feature"><span class="ph-icon">${icon(ic)}</span>
        <div><b>${i + 1}. ${esc(tt)}</b><p>${esc(d)}</p></div></div>`).join("")}</div>
    </div>
    <div class="panel">
      <h2>${t("help_faq")}</h2>
      <div class="faq">${t("faq").map(([q, ans], i) => `<details${i === 0 ? " open" : ""}><summary>${icon("right", "i chev")}${esc(q)}</summary><p>${esc(ans)}</p></details>`).join("")}</div>
    </div>
    <div class="panel"><h2>${t("help_keys")}</h2><p>${t("help_keys_d")}</p></div>`;
  $("#open-data").onclick = () => api.open_data_dir();
}
function tagInput(box, sug, vals, suggestions, onChange = () => {}) {
  const changed = () => { render(); onChange(); };
  const render = () => {
    box.innerHTML = vals.map((v) => `<span class="chip on">${esc(v)}<button data-rm="${esc(v)}">${icon("x")}</button></span>`).join("") + `<input placeholder="${esc(t("tag_ph"))}">`;
    sug.innerHTML = suggestions.filter((s) => !vals.includes(s)).map((s) => `<button class="chip" data-add="${s}">+ ${s}</button>`).join("");
    $("input", box).onkeydown = (ev) => {
      const v = ev.target.value.trim().toLowerCase().replace(/\s+/g, "-");
      if (ev.key === "Enter" && v && !vals.includes(v)) { vals.push(v); changed(); }
    };
  };
  box.onclick = (ev) => { const b = ev.target.closest("[data-rm]"); if (b) { vals.splice(vals.indexOf(b.dataset.rm), 1); changed(); } };
  sug.onclick = (ev) => { const b = ev.target.closest("[data-add]"); if (b) { vals.push(b.dataset.add); changed(); } };
  render();
}
function settingSaver(key, source) {
  return async () => {
    await api.save_settings({ [key]: S.boot.settings[key] });
    toast(t("t_saved_next"), t("t_refresh_now"), () => startRefresh([source]));
  };
}
function renderLearned() {
  const rows = S.learned.filter((r) => r.type !== "src").slice(0, 16);
  if (!rows.length) { $("#learned").innerHTML = `<div class="empty" style="padding:20px">${t("prof_learned_empty")}</div>`; return; }
  const max = Math.max(...rows.map((r) => Math.abs(r.weight)));
  $("#learned").innerHTML = rows.map((r) => `<div class="bar-row"><span class="lbl" title="${t("type_" + r.type)}">${esc(r.label)}</span>
    <div class="bar"><div class="${r.weight > 0 ? "pos" : "neg"}" style="width:${(Math.abs(r.weight) / max) * 50}%"></div></div><span style="color:var(--faint)">${r.weight > 0 ? "+" : ""}${r.weight}</span></div>`).join("");
}
async function setLang(lang) {
  if (lang === LANG()) return;
  await api.save_settings({ lang, lang_chosen: true });
  S.boot = await api.bootstrap();  // category, kind and source texts come from Python in the new language
  if (W.draft) W.draft.lang = lang;
  applyI18n();
  setTheme(W.draft?.theme || S.boot.settings.theme);
  setRefreshMeta();
  await loadEvents();
  buildFilters();
  if ($("#setup").classList.contains("open")) renderWizard();
  renderCurrent();
}
async function setPersonal(on) {
  S.boot.settings = await api.save_settings({ personalize: on });
  if (!on && S.f.sort === "score") S.f.sort = "date";
  if (on && S.f.sort === "date") S.f.sort = "score";
  applyI18n();
  S.shown = 60;
  renderCurrent();
}

// ---------- setup wizard (first run, or Profile › "Open setup wizard") ----------
const LUMA_SUGGEST = ["tech", "ai", "crypto", "arts", "istanbul", "london", "berlin", "paris", "amsterdam", "sf", "nyc", "seattle", "boston", "dubai", "singapore", "lisbon", "barcelona", "climate"];
const FC_SUGGEST = ["istanbul", "london", "berlin", "sf", "nyc", "paris", "amsterdam", "lisbon", "munich", "zurich", "barcelona", "vienna", "singapore", "copenhagen"];
const EB_SUGGEST = ["turkey--istanbul", "turkey--ankara", "united-kingdom--london", "ny--new-york", "germany--berlin", "france--paris", "netherlands--amsterdam", "spain--barcelona", "ca--los-angeles", "united-arab-emirates--dubai", "italy--milano", "portugal--lisboa"];
const REFRESH_HOURS = [0, 3, 6, 12, 24];
const refreshLabel = (h) => t("refresh_opts")[REFRESH_HOURS.indexOf(h)] || "";
const themeLabel = (v) => ({ dark: t("theme_dark_l"), light: t("theme_light_l"), system: t("theme_system") })[v];
const W = { step: 0, draft: null, firstRun: true, accepted: false, installed: false, prevTheme: null };
const levelSummary = (items, vals) => {
  const pick = (v) => items.filter((it) => (vals[it.id] || 0) === v).map((it) => it.label);
  return [[2, t("lv_very")], [1, t("lv_some")], [-1, t("lv_no")]].map(([v, l]) => (pick(v).length ? `<div><b>${l}:</b> ${esc(pick(v).join(", "))}</div>` : "")).join("") || `<div>${t("w9_all_neutral")}</div>`;
};
const draftDomains = () => (W.draft.domains?.length ? W.draft.domains : ["tech", "culture"]);
const WIZARD_STEPS = [
  {
    id: "welcome",
    render: (b) => {
      b.innerHTML = `<h3 class="w-h">${icon("languages")} ${t("w1_lang")}</h3>
        <div class="seg" id="w-lang"><button data-v="tr" class="${LANG() === "tr" ? "on" : ""}">Türkçe</button><button data-v="en" class="${LANG() === "en" ? "on" : ""}">English</button></div>
        <div class="feature-list" style="margin-top:18px">
        ${[["radar", t("w1_f1", S.boot.sources.length + 1), t("w1_f1d")], ["sparkles", t("w1_f2"), t("w1_f2d")],
           ["palette", t("w1_f3"), t("w1_f3d")], ["calendar", t("w1_f4"), t("w1_f4d")]]
          .map(([i, tt, d]) => `<div class="feature"><span class="ph-icon">${icon(i)}</span><div><b>${tt}</b><p>${d}</p></div></div>`).join("")}
        </div><p class="hint">${t("w1_hint")}</p>`;
      $("#w-lang").onclick = (e) => { const x = e.target.closest("button[data-v]"); if (x) setLang(x.dataset.v); };
    },
  },
  {
    id: "terms",
    canNext: () => W.accepted,
    render: (b) => {
      b.innerHTML = `<div class="terms"><p>${t("w2_p")}</p><ul>${["w2_l1", "w2_l2", "w2_l3", "w2_l4"].map((k) => `<li>${t(k)}</li>`).join("")}</ul></div>
        <label class="check"><input type="checkbox" id="w-accept" ${W.accepted ? "checked" : ""}><span class="box">${icon("check")}</span>${t("w2_accept")}</label>`;
      $("#w-accept").onchange = (e) => { W.accepted = e.target.checked; wizardButtons(); };
    },
  },
  {
    id: "areas",
    canNext: () => draftDomains().length > 0,
    render: (b) => {
      const doms = draftDomains();
      const desc = { tech: t("w3_tech_d"), culture: t("w3_culture_d") };
      b.innerHTML = `<h3 class="w-h">${t("w3_domains")}</h3><div class="w-sources">${META().domains.map((d) => `<label class="w-src">
          <input type="checkbox" data-wdom="${d.id}" ${doms.includes(d.id) ? "checked" : ""}><span class="box">${icon("check")}</span>
          <div><b>${icon(d.icon)} ${esc(d.label)}</b><p>${desc[d.id]}</p></div></label>`).join("")}</div>
        <h3 class="w-h">${t("w3_mode")}</h3><div class="w-sources">
          ${[["personal", "sparkles", t("mode_personal"), t("w3_personal_d")], ["all", "list", t("mode_all"), t("w3_all_d")]].map(([v, ic, l, d]) => `<label class="w-src">
            <input type="radio" name="w-mode" value="${v}" ${(W.draft.personalize !== false) === (v === "personal") ? "checked" : ""}><span class="box round">${icon("check")}</span>
            <div><b>${icon(ic)} ${l}</b><p>${d}</p></div></label>`).join("")}</div>
        <p class="hint">${t("w3_hint")}</p>`;
      b.onchange = (e) => {
        if (e.target.name === "w-mode") { W.draft.personalize = e.target.value === "personal"; renderRail(); return; }
        const id = e.target.dataset.wdom;
        if (!id) return;
        const set = new Set(draftDomains());
        e.target.checked ? set.add(id) : set.delete(id);
        if (!set.size) { e.target.checked = true; return; }
        W.draft.domains = META().domains.map((d) => d.id).filter((x) => set.has(x));
      };
    },
  },
  {
    id: "interests", skip: () => W.draft.personalize === false,
    render: (b) => categoryRows(b, W.draft.profile.interests, draftDomains(), () => {}),
  },
  {
    id: "location", skip: () => W.draft.personalize === false,
    render: (b) => {
      b.innerHTML = `<h3 class="w-h">${t("w5_location")}</h3><div id="w-r"></div><h3 class="w-h">${t("w5_kind")}</h3><div id="w-k"></div>`;
      levelRows($("#w-r"), META().regions, W.draft.profile.regions, () => {});
      const doms = draftDomains();
      levelRows($("#w-k"), META().kinds.filter((k) => doms.length === 2 || doms.includes(k.domain)), W.draft.profile.kinds, () => {});
    },
  },
  {
    id: "sources",
    render: (b) => {
      const dis = new Set(W.draft.disabled_sources), doms = draftDomains();
      const ev = S.boot.sources.filter((s) => s.status === "events" && (s.domain === "mixed" || doms.includes(s.domain)));
      const other = S.boot.sources.filter((s) => s.status !== "events");
      b.innerHTML = `<div class="w-sources">${ev.map((s) => `<label class="w-src">
          <input type="checkbox" data-src="${s.id}" ${dis.has(s.id) ? "" : "checked"}><span class="box">${icon("check")}</span>
          <div><b>${esc(s.label)}</b><p>${esc(s.note)}</p></div></label>`).join("")}</div>
        <h3 class="w-h">${t("w6_news")}</h3><div class="w-sources">${other.map((s) => `<div class="w-src off">
          <span class="pill ${s.status}">${s.status === "news" ? t("w6_pill_news") : t("w6_pill_blocked")}</span><div><b>${esc(s.label)}</b><p>${esc(s.note)}</p></div></div>`).join("")}</div>`;
      b.onchange = (e) => {
        const id = e.target.dataset.src;
        if (!id) return;
        const set = new Set(W.draft.disabled_sources);
        e.target.checked ? set.delete(id) : set.add(id);
        W.draft.disabled_sources = [...set];
        wizardButtons();
      };
    },
    canNext: () => wizardSources().length > 0,
  },
  {
    id: "cities",
    render: (b) => {
      const doms = draftDomains();
      b.innerHTML = `<h3 class="w-h">Luma</h3><p class="hint">${t("w7_luma_hint")}</p>
        <div class="tag-input" id="w-luma"></div><div class="suggest" id="w-luma-s"></div>
        ${doms.includes("culture") ? `<h3 class="w-h">${t("prof_eb")}</h3><p class="hint">${t("prof_eb_sub")}</p><div class="tag-input" id="w-eb"></div><div class="suggest" id="w-eb-s"></div>` : ""}
        ${doms.includes("tech") ? `<h3 class="w-h">${t("prof_fc")}</h3><div class="tag-input" id="w-fc"></div><div class="suggest" id="w-fc-s"></div>` : ""}`;
      tagInput($("#w-luma"), $("#w-luma-s"), W.draft.luma_slugs, LUMA_SUGGEST);
      if ($("#w-eb")) tagInput($("#w-eb"), $("#w-eb-s"), W.draft.eventbrite_places, EB_SUGGEST);
      if ($("#w-fc")) tagInput($("#w-fc"), $("#w-fc-s"), W.draft.foundercal_cities, FC_SUGGEST);
    },
  },
  {
    id: "look",
    render: (b) => {
      b.innerHTML = `<h3 class="w-h">${t("w8_theme")}</h3><div class="theme-cards">${["dark", "light", "system"].map((v) =>
        `<button class="theme-card${W.draft.theme === v ? " on" : ""}" data-theme-pick="${v}"><span class="tp tp-${v}"><i></i><i></i><i></i></span>${themeLabel(v)}</button>`).join("")}</div>
        <h3 class="w-h">${t("w8_refresh")}</h3><p class="hint">${t("w8_refresh_hint")}</p>
        <div class="seg" id="w-refresh">${REFRESH_HOURS.map((v) => `<button data-v="${v}" class="${W.draft.auto_refresh_hours === v ? "on" : ""}">${refreshLabel(v)}</button>`).join("")}</div>`;
      b.onclick = (e) => {
        const th = e.target.closest("[data-theme-pick]");
        if (th) { W.draft.theme = th.dataset.themePick; setTheme(W.draft.theme); $$(".theme-card", b).forEach((x) => x.classList.toggle("on", x === th)); }
        const r = e.target.closest("#w-refresh button");
        if (r) { W.draft.auto_refresh_hours = Number(r.dataset.v); $$("#w-refresh button").forEach((x) => x.classList.toggle("on", x === r)); }
      };
    },
  },
  {
    id: "summary", nextLabel: "w_install",
    render: (b) => {
      const d = W.draft, on = wizardSources(), doms = draftDomains();
      const rows = [
        [t("w9_lang"), LANG() === "en" ? "English" : "Türkçe"],
        [t("w9_domains"), esc(META().domains.filter((x) => doms.includes(x.id)).map((x) => x.label).join(", "))],
        [t("w9_mode"), d.personalize === false ? t("mode_all") : t("mode_personal")],
        d.personalize !== false && [t("w9_interests"), levelSummary(META().categories.filter((c) => doms.includes(c.domain)), d.profile.interests)],
        d.personalize !== false && [t("w9_location"), levelSummary(META().regions, d.profile.regions)],
        d.personalize !== false && [t("w9_kind"), levelSummary(META().kinds, d.profile.kinds)],
        [t("w9_sources"), esc(t("w9_sources_v", on.length, on.map((s) => s.label).join(", ")))],
        ["Luma", esc(d.luma_slugs.join(", ") || "—")],
        doms.includes("culture") && ["Eventbrite", esc(d.eventbrite_places.join(", ") || "—")],
        doms.includes("tech") && ["Foundercal", esc(d.foundercal_cities.join(", ") || "—")],
        [t("w9_theme"), themeLabel(d.theme)],
        [t("w9_refresh"), refreshLabel(d.auto_refresh_hours)],
        [t("w9_data"), `<code>${esc(S.boot.data_dir)}</code>`],
      ].filter(Boolean);
      b.innerHTML = `<div class="summary">${rows.map(([k, v]) => `<div class="sum-row"><span>${k}</span><div>${v}</div></div>`).join("")}</div>`;
    },
  },
  {
    id: "install",
    canBack: () => false,
    canNext: () => W.installed,
    render: (b) => {
      b.innerHTML = `<div class="progress big"><div id="w-bar"></div></div><div class="install-log" id="w-log"></div>`;
      if (!W.installStarted) runInstall();
    },
  },
  {
    id: "done", nextLabel: "w_finish",
    canBack: () => false,
    render: (b) => {
      const upcoming = S.events.filter((e) => !isPast(e)).length;
      const cells = personal()
        ? [["up", t("d_like"), t("w11_like")], ["down", t("d_dislike"), t("w11_dislike")], ["bookmark", t("d_save"), t("w11_save")], ["percent", t("w11_fit"), t("w11_fit_d")]]
        : [["list", t("w11_mode"), t("w11_mode_d")], ["bookmark", t("d_save"), t("w11_save")], ["calendar", t("d_gcal"), ".ics"], ["sparkles", t("mode_personal"), t("mode_personal_tip")]];
      b.innerHTML = `<div class="done-box"><span class="ph-icon done">${icon("check")}</span>
        <div>${t("w11_ready", num(upcoming), S.news.length || t("w11_current"))}</div></div>
        <div class="info-grid">${cells.map(([i, k, v]) => `<div class="info"><small class="meta-line">${icon(i)}${esc(k)}</small><div>${esc(v)}</div></div>`).join("")}</div>
        <p class="hint">${t("w11_hint")}</p>`;
    },
  },
];
// rail / title / subtitle keys per step: w1… w11
const STEP_KEY = { welcome: "w1", terms: "w2", areas: "w3", interests: "w4", location: "w5", sources: "w6", cities: "w7", look: "w8", summary: "w9", install: "w10", done: "w11" };
const stepText = (st, part) => t(`${STEP_KEY[st.id]}_${part}`);
const visibleSteps = () => WIZARD_STEPS.filter((s) => !s.skip || !s.skip());
/** Event sources the draft will fetch: enabled and belonging to a chosen area (Luma serves both). */
function wizardSources() {
  const doms = draftDomains(), dis = new Set(W.draft.disabled_sources);
  return S.boot.sources.filter((s) => s.status === "events" && !dis.has(s.id) && (s.domain === "mixed" || doms.includes(s.domain)));
}
function openWizard(firstRun) {
  Object.assign(W, { step: 0, firstRun, accepted: false, installed: false, installStarted: false, prevTheme: S.boot.settings.theme });
  W.draft = JSON.parse(JSON.stringify(S.boot.settings));
  $("#setup").classList.add("open");
  renderWizard();
}
function wizardButtons() {
  const st = visibleSteps()[W.step];
  $("#setup-back").disabled = W.step === 0 || (st.canBack && !st.canBack());
  $("#setup-next").disabled = st.canNext ? !st.canNext() : false;
  $("#setup-next").textContent = t(st.nextLabel || "w_next");
  // a fresh install has nothing to go back to; once installing, cancelling makes no sense either
  $("#setup-cancel").style.visibility = W.firstRun || W.installStarted ? "hidden" : "visible";
}
function renderRail() {
  const steps = visibleSteps();
  $("#setup-steps").innerHTML = steps.map((s, i) =>
    `<li class="${i < W.step ? "done" : i === W.step ? "cur" : ""}"><span class="n">${i < W.step ? icon("check") : i + 1}</span>${esc(stepText(s, "rail"))}</li>`).join("");
  $("#setup-count").textContent = t("w_step", W.step + 1, steps.length);
}
function renderWizard() {
  const st = visibleSteps()[W.step];
  renderRail();
  $("#setup-title").textContent = W.installed && st.id === "install" ? t("w10_done_title") : stepText(st, "title");
  $("#setup-sub").textContent = stepText(st, "sub");
  const body = $("#setup-body");
  body.onclick = body.onchange = null;
  body.scrollTop = 0;
  st.render(body);
  wizardButtons();
}
async function runInstall() {
  W.installStarted = true;
  wizardButtons();
  // sources outside the chosen areas are switched off so the first download stays focused
  const doms = draftDomains();
  const off = S.boot.sources.filter((s) => s.status === "events" && s.domain !== "mixed" && !doms.includes(s.domain)).map((s) => s.id);
  W.draft.disabled_sources = [...new Set([...W.draft.disabled_sources, ...off])];
  S.boot.settings = await api.save_settings({ ...W.draft, domains: doms, onboarded: true });
  S.f.domain = defaultDomain();
  S.f.sort = personal() ? "score" : "date";
  applyI18n();
  const ic = { waiting: "clock", running: "refresh", done: "check", error: "x" };
  const word = { done: (r) => t("log_done", num(r.count ?? 0)), error: () => t("log_error"), running: () => t("log_running"), waiting: () => t("log_waiting") };
  S.refreshHook = (st) => {
    const rows = Object.values(st.sources || {});
    const done = rows.filter((r) => r.state === "done" || r.state === "error").length;
    if ($("#w-bar")) $("#w-bar").style.width = rows.length ? `${(done / rows.length) * 100}%` : "0";
    if ($("#w-log")) $("#w-log").innerHTML = rows.map((r) => `<div class="log-row ${r.state}">${icon(ic[r.state])}<span>${esc(r.label)}</span><em>${word[r.state](r)}</em></div>`).join("");
    if (!st.running) {
      S.refreshHook = null;
      W.installed = true;
      $("#setup-title").textContent = t("w10_done_title");
      wizardButtons();
    }
  };
  await startRefresh();
}
async function finishWizard() {
  $("#setup").classList.remove("open");
  W.draft = null;
  await loadEvents();
  buildFilters();
  show("discover");
}
function cancelWizard() {
  setTheme(W.prevTheme);
  W.draft = null;
  $("#setup").classList.remove("open");
}

// ---------- refresh ----------
let polling = false;
async function startRefresh(only = null) {
  const started = await api.refresh(only);
  if (!started && polling) return;
  pollRefresh();
}
async function pollRefresh() {
  if (polling) return;
  polling = true;
  const btn = $("#refresh-btn");
  btn.disabled = true; btn.classList.add("spin"); $("span", btn).textContent = t("refreshing");
  let st;
  while (true) {
    st = await api.refresh_status();
    if (S.refreshHook) S.refreshHook(st);
    const srcs = Object.values(st.sources || {});
    const done = srcs.filter((s) => s.state === "done" || s.state === "error").length;
    $("#refresh-bar").style.width = srcs.length ? `${(done / srcs.length) * 100}%` : "0";
    const running = srcs.filter((s) => s.state === "running").map((s) => s.label);
    $("#refresh-meta").textContent = st.running ? `${done}/${srcs.length} · ${running.slice(0, 2).join(", ")}` : "";
    if (!st.running) break;
    await new Promise((r) => setTimeout(r, 600));
  }
  polling = false;
  btn.disabled = false; btn.classList.remove("spin"); $("span", btn).textContent = t("refresh");
  const errs = Object.values(st.sources || {}).filter((s) => s.state === "error");
  const before = S.events.length;
  await loadEvents();
  S.boot.last_refresh = st.finished;
  setRefreshMeta();
  buildFilters();
  renderCurrent(true);
  toast(t("t_ready", num(S.events.length)) + (S.events.length > before && before ? t("t_new", num(S.events.length - before)) : "") + (errs.length ? t("t_errors", errs.length) : ""));
  setTimeout(() => ($("#refresh-bar").style.width = "0"), 1500);
}
function setRefreshMeta() {
  $("#refresh-meta").textContent = S.boot.last_refresh ? t("last_update", relTime(S.boot.last_refresh)) : t("never_fetched");
}

// ---------- toast ----------
let toastTimer;
function toast(msg, actLabel, fn) {
  const tt = $("#toast");
  $("#toast-msg").textContent = msg;
  const b = $("#toast-act");
  b.style.display = actLabel ? "" : "none";
  b.textContent = actLabel || "";
  b.onclick = () => { tt.classList.remove("show"); fn && fn(); };
  tt.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => tt.classList.remove("show"), actLabel ? 5000 : 2600);
}

// ---------- navigation ----------
function show(view) {
  S.view = view;
  $$(".nav-btn").forEach((b) => b.classList.toggle("active", b.dataset.view === view));
  $$(".view").forEach((v) => v.classList.toggle("active", v.id === "view-" + view));
  renderCurrent();
}
function renderCurrent(reload = false) {
  ({ discover: renderDiscover, calendar: renderCalendar, saved: renderSaved, news: () => renderNews(reload),
     sources: () => renderSources(true), profile: renderProfile, about: renderAbout })[S.view]();
}
const systemDark = window.matchMedia("(prefers-color-scheme: dark)");
function setTheme(th) {
  const resolved = th === "system" ? (systemDark.matches ? "dark" : "light") : th;
  document.documentElement.dataset.theme = resolved;
  $("#theme-btn").innerHTML = `${icon(resolved === "dark" ? "sun" : "moon")}<span>${resolved === "dark" ? t("theme_light") : t("theme_dark")}</span>`;
}
systemDark.addEventListener("change", () => S.boot?.settings.theme === "system" && setTheme("system"));

// ---------- wiring ----------
function wire() {
  $$("[data-icon]").forEach((el) => (el.tagName === "I" ? (el.outerHTML = icon(el.dataset.icon)) : (el.innerHTML = icon(el.dataset.icon))));
  $$(".nav-btn").forEach((b) => (b.onclick = () => show(b.dataset.view)));
  const rerender = () => { S.shown = 60; renderDiscover(); };
  let qTimer;
  $("#q").oninput = (e) => { clearTimeout(qTimer); qTimer = setTimeout(() => { S.f.q = e.target.value.trim(); rerender(); }, 160); };
  const seg = (sel, fn) => ($(sel).onclick = (e) => { const b = e.target.closest("button[data-v]"); if (!b) return; $$("button", $(sel)).forEach((x) => x.classList.toggle("on", x === b)); fn(b.dataset.v); });
  seg("#time-seg", (v) => { S.f.time = v; rerender(); });
  seg("#region-seg", (v) => { S.f.region = v; rerender(); });
  seg("#domain-seg", (v) => { S.f.domain = v; S.f.cats.clear(); S.f.kind = "all"; buildFilters(); rerender(); });
  seg("#layout-seg", (v) => { S.layout = v; renderDiscover(); });
  seg("#saved-seg", (v) => { S.savedTab = v; renderSaved(); });
  seg("#mode-seg", (v) => setPersonal(v === "personal"));
  seg("#prof-mode", (v) => setPersonal(v === "personal"));
  seg("#prof-lang", (v) => setLang(v));
  $("#lang-btn").onclick = () => setLang(LANG() === "en" ? "tr" : "en");
  $("#sort").onchange = (e) => { S.f.sort = e.target.value; rerender(); };
  $("#kind-sel").onchange = (e) => { S.f.kind = e.target.value; rerender(); };
  $("#src-sel").onchange = (e) => { S.f.src = e.target.value; rerender(); };
  [["#f-free", "free"], ["#f-past", "past"], ["#f-hidden", "hidden"]].forEach(([id, k]) => ($(id).onchange = (e) => { S.f[k] = e.target.checked; rerender(); }));
  $("#cat-chips").onclick = (e) => {
    const b = e.target.closest("[data-cat]"); if (!b) return;
    S.f.cats.has(b.dataset.cat) ? S.f.cats.delete(b.dataset.cat) : S.f.cats.add(b.dataset.cat);
    b.classList.toggle("on"); rerender();
  };
  $("#clear-filters").onclick = () => {
    Object.assign(S.f, { q: "", time: "all", domain: defaultDomain(), cats: new Set(), region: "all", kind: "all", src: "all", free: false, past: false, hidden: false });
    $("#q").value = ""; ["#f-free", "#f-past", "#f-hidden"].forEach((id) => ($(id).checked = false));
    $$("#time-seg button").forEach((b) => b.classList.toggle("on", b.dataset.v === "all"));
    buildFilters(); rerender();
  };
  $("#more-btn").onclick = () => { S.shown += 60; renderDiscover(); };

  // card / mini / feat clicks (delegated)
  document.body.addEventListener("click", (ev) => {
    const urlBtn = ev.target.closest("[data-url]");
    if (urlBtn) { ev.preventDefault(); return api.open_url(urlBtn.dataset.url); }
    const a = ev.target.closest("[data-act]");
    const card = ev.target.closest("[data-id]");
    if (a && card) { ev.stopPropagation(); return act(card.dataset.id, a.dataset.act); }
    const dact = ev.target.closest("[data-dact]");
    if (dact) {
      const e = S.byId[$("#drawer").dataset.id];
      const k = dact.dataset.dact;
      if (k === "open") return api.open_url(e.url);
      if (k === "gcal") return api.open_url(gcalUrl(e));
      if (k === "ics") return api.export_ics(e).then((p) => toast(t("t_ics", p.split(/[\\/]/).pop())));
      return act(e.id, k);
    }
    if (ev.target.closest("[data-close]") || ev.target.id === "scrim") return closeDrawer();
    if (card && !ev.target.closest("#drawer")) return openDrawer(card.dataset.id);
    const day = ev.target.closest("[data-day]");
    if (day) { S.cal.sel = new Date(day.dataset.day); renderCalendar(); }
    const nb = ev.target.closest("[data-news]");
    if (nb) { S.newsSrc = nb.dataset.news; renderNews(); }
    const sc = ev.target.closest("[data-scope]");
    if (sc) { S.newsScope = sc.dataset.scope; S.newsSrc = "all"; renderNews(); }
    const rs = ev.target.closest("[data-refresh-src]");
    if (rs) startRefresh([rs.dataset.refreshSrc]);
  });
  document.body.addEventListener("change", async (ev) => {
    const id = ev.target.dataset?.enable;
    if (!id) return;
    const dis = new Set(S.boot.settings.disabled_sources);
    ev.target.checked ? dis.delete(id) : dis.add(id);
    S.boot.settings = await api.save_settings({ disabled_sources: [...dis] });
    toast(ev.target.checked ? t("t_src_on") : t("t_src_off"));
  });
  $("#cal-prev").onclick = () => { S.cal.m--; if (S.cal.m < 0) { S.cal.m = 11; S.cal.y--; } renderCalendar(); };
  $("#cal-next").onclick = () => { S.cal.m++; if (S.cal.m > 11) { S.cal.m = 0; S.cal.y++; } renderCalendar(); };
  $("#cal-today").onclick = () => { const d = new Date(); Object.assign(S.cal, { y: d.getFullYear(), m: d.getMonth(), sel: d }); renderCalendar(); };
  $("#cal-saved").onchange = renderCalendar; $("#cal-top").onchange = renderCalendar;
  $("#refresh-btn").onclick = () => startRefresh();
  $("#theme-btn").onclick = async () => {
    const th = document.documentElement.dataset.theme === "dark" ? "light" : "dark";  // explicit choice ends "system"
    setTheme(th); S.boot.settings = await api.save_settings({ theme: th });
  };
  $("#reset-learning").onclick = async () => { await api.reset_learning(); await loadEvents(); renderLearned(); toast(t("t_learning_reset")); };
  $("#rerun-onboarding").onclick = () => openWizard(false);
  $("#factory-reset").onclick = () => toast(t("t_factory"), t("t_factory_btn"), async () => {
    S.boot.settings = await api.factory_reset();
    await loadEvents();
    openWizard(true);
  });
  $("#setup-back").onclick = () => { W.step--; renderWizard(); };
  $("#setup-next").onclick = () => { if (W.step === visibleSteps().length - 1) return finishWizard(); W.step++; renderWizard(); };
  $("#setup-cancel").onclick = cancelWizard;
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !$("#setup").classList.contains("open")) closeDrawer();
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") { e.preventDefault(); show("discover"); $("#q").focus(); }
  });
  setInterval(setRefreshMeta, 60000);
}

async function init() {
  api = window.pywebview.api;
  wire();
  S.boot = await api.bootstrap();
  // a fresh install follows the system language until the wizard asks
  if (!S.boot.settings.onboarded && !S.boot.settings.lang_chosen && !navigator.language.toLowerCase().startsWith("tr") && LANG() === "tr") {
    await api.save_settings({ lang: "en" });
    S.boot = await api.bootstrap();
  }
  S.f.domain = defaultDomain();
  S.f.sort = personal() ? "score" : "date";
  applyI18n();
  setTheme(S.boot.settings.theme || "dark");
  setRefreshMeta();
  await loadEvents();
  buildFilters();
  renderDiscover();
  $("#app-version").textContent = `v${S.boot.version}`;
  if (!S.boot.settings.onboarded) openWizard(true);
  else if (S.boot.needs_refresh || (!S.events.length && S.boot.settings.auto_refresh_hours)) startRefresh();
  else if (S.boot.missing_sources.length) {
    toast(t("t_new_sources", S.boot.missing_sources.map(srcLabel).join(", ")));
    startRefresh(S.boot.missing_sources);
  }
}
window.addEventListener("pywebviewready", init);
// surface UI errors in the Python console
window.addEventListener("error", (e) => window.pywebview?.api?.log(`${e.message} @${e.lineno}:${e.colno}`));
window.addEventListener("unhandledrejection", (e) => window.pywebview?.api?.log(String(e.reason?.stack || e.reason)));
