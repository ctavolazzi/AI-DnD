const DATA_URL = "data/demo_run.json";
const AUTOPLAY_INTERVAL_MS = 2500;
const searchParams = new URLSearchParams(window.location.search);
const DEFAULT_SERVICE_URL = normalizeServiceUrl(
  searchParams.get("service") || "http://127.0.0.1:8001",
);
const DEFAULT_LIVE_MODE = searchParams.get("mode") === "live";

const questCard = document.getElementById("quest-card");
const questText = questCard?.querySelector(".quest-text");
const partyList = document.getElementById("party-list");
const enemyList = document.getElementById("enemy-list");
const eventLog = document.getElementById("event-log");
const cumulativeLog = document.getElementById("cumulative-log");
const turnTitle = document.getElementById("turn-title");
const turnLabel = document.getElementById("turn-label");
const partyCount = document.getElementById("party-count");
const enemyCount = document.getElementById("enemy-count");
const roundCount = document.getElementById("round-count");
const momentumFill = document.getElementById("momentum-fill");
const momentumLabel = document.getElementById("momentum-label");
const momentumTrack = document.querySelector(".momentum-track");
const timelineSlider = document.getElementById("timeline-slider");
const timelineMarks = document.getElementById("timeline-marks");
const timelineReadout = document.getElementById("timeline-readout");
const digestList = document.getElementById("turn-digest");
const statusEl = document.getElementById("status");
const sessionIndicator = document.getElementById("session-indicator");
const conclusionEl = document.getElementById("conclusion");
const refreshButton = document.getElementById("refresh-button");
const liveSessionButton = document.getElementById("live-session-button");
const fileInput = document.getElementById("file-input");
const serviceInput = document.getElementById("service-url");
const prevButton = document.getElementById("previous-turn");
const nextButton = document.getElementById("next-turn");
const playButton = document.getElementById("play-toggle");
const logTabButtons = Array.from(document.querySelectorAll(".tab-button"));
const dossierEmpty = document.getElementById("dossier-empty");
const dossierContent = document.getElementById("dossier-content");
const dossierPortrait = document.getElementById("dossier-portrait");
const dossierName = document.getElementById("dossier-name");
const dossierRole = document.getElementById("dossier-role");
const dossierStatus = document.getElementById("dossier-status");
const dossierHp = document.getElementById("dossier-hp");
const dossierSide = document.getElementById("dossier-side");
const dossierNote = document.getElementById("dossier-note");

const rosterTemplate = document.getElementById("roster-entry");
const eventTemplate = document.getElementById("event-line");
const digestTemplate = document.getElementById("digest-entry");

const state = {
  payload: null,
  turnIndex: 0,
  autoplayId: null,
  logView: "turn",
  selection: null,
  mode: "offline",
  sessionId: null,
  sessionComplete: false,
  serviceUrl: DEFAULT_SERVICE_URL,
};

window.addEventListener("DOMContentLoaded", () => {
  initializeServiceField();
  bindControls();
  if (DEFAULT_LIVE_MODE) {
    startLiveSession().catch((error) => {
      console.error("Failed to auto-start live session", error);
      attemptInitialLoad();
    });
  } else {
    attemptInitialLoad();
  }
});

function attemptInitialLoad() {
  state.mode = "offline";
  state.sessionId = null;
  state.sessionComplete = false;
  refreshSessionIndicator();
  loadFromUrl(DATA_URL).catch((error) => {
    console.warn("Initial load failed", error);
    showStatus(
      "No chronicle found. Generate data/demo_run.json or import a snapshot.",
      true,
    );
  });
}

function initializeServiceField() {
  setServiceUrl(state.serviceUrl, { silent: true });
  if (!serviceInput) {
    return;
  }
  serviceInput.value = state.serviceUrl;
  serviceInput.addEventListener("change", () => {
    setServiceUrl(serviceInput.value, { announce: true });
  });
  serviceInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      setServiceUrl(serviceInput.value, { announce: true });
      serviceInput.blur();
    }
  });
}

function bindControls() {
  refreshButton?.addEventListener("click", async () => {
    refreshButton.disabled = true;
    showStatus("Summoning latest chronicle…");
    try {
      await loadFromUrl(`${DATA_URL}?t=${Date.now()}`);
      showStatus("Loaded data/demo_run.json", false);
    } catch (error) {
      console.error(error);
      showStatus("Unable to load data/demo_run.json. Run generate_data.py first.", true);
    } finally {
      refreshButton.disabled = false;
    }
  });

  liveSessionButton?.addEventListener("click", () => {
    if (liveSessionButton.disabled) {
      return;
    }
    startLiveSession().catch((error) => {
      console.error(error);
      updateSessionIndicator("Session service unavailable", true);
    });
  });

  fileInput?.addEventListener("change", async (event) => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    showStatus(`Importing ${file.name}…`);
    try {
      const text = await file.text();
      const payload = JSON.parse(text);
      renderDataset(payload);
      showStatus(`Loaded ${file.name}`, false);
    } catch (error) {
      console.error(error);
      showStatus("That file is not valid JSON.", true);
    } finally {
      event.target.value = "";
    }
  });

  prevButton?.addEventListener("click", () => {
    if (state.turnIndex > 0) {
      stopAutoplay();
      setTurn(state.turnIndex - 1);
    }
  });

  nextButton?.addEventListener("click", async () => {
    if (!state.payload?.frames) {
      return;
    }
    if (state.turnIndex < state.payload.frames.length - 1) {
      stopAutoplay();
      setTurn(state.turnIndex + 1);
      return;
    }
    if (state.mode === "live" && !state.sessionComplete) {
      stopAutoplay();
      try {
        await advanceLiveSession();
      } catch (error) {
        console.error(error);
        updateSessionIndicator("Unable to advance session", true);
      }
    }
  });

  playButton?.addEventListener("click", () => {
    if (state.autoplayId) {
      stopAutoplay();
    } else if (state.payload?.frames?.length) {
      startAutoplay();
    }
  });

  timelineSlider?.addEventListener("input", (event) => {
    const raw = event.target.value;
    const index = Number.parseInt(raw, 10);
    if (Number.isNaN(index)) {
      return;
    }
    stopAutoplay();
    setTurn(index, { skipFocus: true });
  });

  logTabButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const view = button.dataset.logView;
      if (view === "turn" || view === "chronicle") {
        setLogView(view);
      }
    });
  });

  document.addEventListener("keydown", handleKeydown);
}

async function loadFromUrl(url) {
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  const payload = await response.json();
  renderDataset(payload);
}

async function startLiveSession() {
  setServiceUrl(serviceInput?.value || state.serviceUrl, { silent: true });
  if (liveSessionButton) {
    liveSessionButton.disabled = true;
    liveSessionButton.textContent = "Starting…";
  }
  stopAutoplay();
  const hostLabel = formatServiceHost(state.serviceUrl);
  const connectingMessage = hostLabel ? `Contacting ${hostLabel}…` : "Contacting session service…";
  updateSessionIndicator(connectingMessage);
  try {
    const payload = await createLiveSession();
    renderDataset(payload, {
      mode: "live",
      sessionId: payload.session_id,
      sessionComplete: payload.is_complete,
    });
    const readyMessage = hostLabel ? `Live session ready @ ${hostLabel}` : "Live session ready";
    showStatus(readyMessage, false);
  } catch (error) {
    showStatus("Live session unavailable.", true);
    updateSessionIndicator("Session service unavailable", true);
    throw error;
  } finally {
    if (liveSessionButton) {
      liveSessionButton.disabled = false;
      liveSessionButton.textContent = state.mode === "live" ? "Restart live session" : "Start live session";
      liveSessionButton.title = `Connect to ${state.serviceUrl}`;
    }
    if (state.mode === "live") {
      refreshSessionIndicator();
    }
  }
}

async function createLiveSession() {
  const baseUrl = state.serviceUrl || DEFAULT_SERVICE_URL;
  const response = await fetch(`${baseUrl}/sessions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mode: "demo" }),
  });
  if (!response.ok) {
    throw new Error(`Session creation failed (${response.status})`);
  }
  return response.json();
}

async function advanceLiveSession(options = {}) {
  if (!state.sessionId) {
    throw new Error("No live session active");
  }
  const { steps = 1, preserveAutoplay = false } = options;
  const baseUrl = state.serviceUrl || DEFAULT_SERVICE_URL;
  const response = await fetch(`${baseUrl}/sessions/${state.sessionId}/advance`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ steps }),
  });
  if (!response.ok) {
    throw new Error(`Advance failed (${response.status})`);
  }
  const payload = await response.json();
  renderDataset(payload, {
    mode: "live",
    sessionId: payload.session_id ?? state.sessionId,
    sessionComplete: payload.is_complete,
    preserveAutoplay,
  });
  return payload;
}

function renderDataset(payload, options = {}) {
  const {
    mode = "offline",
    sessionId = null,
    sessionComplete = false,
    preserveAutoplay = false,
  } = options;

  if (!preserveAutoplay) {
    stopAutoplay();
  }

  state.mode = mode;
  state.sessionId = sessionId;
  state.sessionComplete = Boolean(sessionComplete);
  state.payload = payload;

  const frames = Array.isArray(payload?.frames) ? payload.frames : [];

  if (!payload || frames.length === 0) {
    showStatus("This chronicle has no frames to display.", true);
    if (questText) {
      questText.textContent = "No quest hook recorded.";
    }
    clearRoster(partyList, "No allies present.");
    clearRoster(enemyList, "No foes detected.");
    clearLog(eventLog);
    clearLog(cumulativeLog);
    clearTimeline();
    resetMomentum();
    clearDigest();
    clearDossier();
    if (roundCount) {
      roundCount.textContent = "--";
    }
    conclusionEl?.classList.add("hidden");
    state.turnIndex = 0;
    state.selection = null;
    updateControls();
    refreshSessionIndicator();
    return;
  }

  const targetIndex = Math.max(
    0,
    Math.min(
      typeof payload.turn_index === "number" ? payload.turn_index : 0,
      frames.length - 1,
    ),
  );

  state.turnIndex = targetIndex;
  state.selection = null;
  renderQuest(payload.quest_hook);
  renderTimeline(frames);
  renderDigest(frames);
  updateConclusion();
  setLogView("turn");
  setTurn(targetIndex, { skipFocus: true });
  refreshSessionIndicator();
}

function renderQuest(questHook) {
  if (!questCard || !questText) {
    return;
  }
  questText.innerHTML = questHook ? escapeHtml(questHook) : "No quest hook recorded.";
}

function renderTimeline(frames) {
  if (!timelineSlider || !timelineMarks) {
    return;
  }

  timelineMarks.innerHTML = "";
  frames.forEach((frame, index) => {
    const mark = document.createElement("li");
    mark.textContent = frame.is_final ? "Finale" : `T${frame.turn}`;
    mark.setAttribute("data-index", index.toString());
    timelineMarks.appendChild(mark);
  });

  timelineSlider.min = "0";
  timelineSlider.max = Math.max(frames.length - 1, 0).toString();
  timelineSlider.value = "0";
  timelineSlider.step = "1";
  timelineSlider.disabled = frames.length <= 1;
}

function renderDigest(frames) {
  if (!digestList || !digestTemplate) {
    return;
  }

  digestList.innerHTML = "";
  frames.forEach((frame, index) => {
    const fragment = digestTemplate.content.cloneNode(true);
    const card = fragment.querySelector(".digest-card");
    const label = fragment.querySelector(".digest-label");
    const subtitle = fragment.querySelector(".digest-subtitle");

    if (card) {
      card.dataset.index = index.toString();
      card.addEventListener("click", () => {
        stopAutoplay();
        setTurn(index);
      });
    }

    if (label) {
      label.textContent = frame.is_final ? "Finale" : `Turn ${frame.turn}`;
    }

    if (subtitle) {
      subtitle.textContent = summarizeDigest(frame);
    }

    digestList.appendChild(fragment);
  });
}

function setTurn(index, options = {}) {
  if (!state.payload?.frames || !state.payload.frames[index]) {
    return;
  }

  state.turnIndex = index;
  renderFrame(state.payload.frames[index]);
  updateTimelineHighlight();
  updateControls();
  updateConclusion();
  updateDigestHighlight();
  updateDossier();

  if (!options.skipFocus) {
    focusActiveTimeline();
  }
}

function renderFrame(frame) {
  if (!frame) {
    return;
  }

  const isFinal = Boolean(frame.is_final);
  const title = isFinal ? "Finale" : `Turn ${frame.turn}`;
  if (turnTitle) {
    turnTitle.textContent = title;
  }
  if (turnLabel) {
    turnLabel.textContent = isFinal ? "Finale" : `T${frame.turn}`;
  }

  populateRoster(partyList, frame.players, "party");
  populateRoster(enemyList, frame.enemies, "enemy");
  updateBriefStats(frame);

  const turnEvents = Array.isArray(frame.new_events) && frame.new_events.length
    ? frame.new_events
    : ["No events recorded."];
  renderLog(eventLog, turnEvents, { appendConclusion: isFinal });

  const cumulativeEvents = Array.isArray(frame.cumulative_events) && frame.cumulative_events.length
    ? frame.cumulative_events
    : turnEvents;
  renderLog(cumulativeLog, cumulativeEvents, { markFinale: isFinal });
}

function populateRoster(container, roster = [], side) {
  if (!container) {
    return;
  }

  container.innerHTML = "";
  roster.forEach((entry, slot) => {
    const fragment = rosterTemplate?.content.cloneNode(true);
    const portrait = fragment?.querySelector(".portrait");
    const nameEl = fragment?.querySelector(".name");
    const metaEl = fragment?.querySelector(".meta");
    const hpEl = fragment?.querySelector(".hp");
    const hpFill = fragment?.querySelector(".hp-fill");
    const card = fragment?.querySelector(".roster-card");

    if (!fragment || !card) {
      return;
    }

    if (portrait) {
      portrait.style.background = generatePortraitGradient(side, slot);
    }

    if (nameEl) {
      nameEl.textContent = entry.name || (side === "party" ? "Ally" : "Foe");
    }

    if (metaEl) {
      const label = entry.char_class || entry.role || "";
      metaEl.textContent = label ? label.toUpperCase() : "UNKNOWN";
    }

    if (hpEl) {
      const hpCurrent = Number.isFinite(entry.hp) ? entry.hp : 0;
      const hpMax = Number.isFinite(entry.max_hp) && entry.max_hp > 0 ? entry.max_hp : 0;
      const hpText = hpMax ? `${hpCurrent}/${hpMax} HP` : `${hpCurrent} HP`;
      hpEl.textContent = hpText;
      const isAlive = entry.alive !== false;
      hpEl.dataset.status = isAlive ? "up" : "down";
      if (hpFill) {
        const ratio = hpMax ? Math.max(0, Math.min(hpCurrent / hpMax, 1)) : 0;
        hpFill.style.transform = `scaleX(${ratio})`;
        hpFill.classList.toggle("down", !isAlive || ratio <= 0);
      }
    }

    card.dataset.side = side;
    card.dataset.index = slot.toString();
    card.title = `${entry.name || "Combatant"} — ${side === "party" ? "Party" : "Opposition"}`;
    card.addEventListener("click", () => {
      selectCombatant(side, slot);
    });

    if (state.selection && state.selection.side === side && state.selection.index === slot) {
      card.classList.add("selected");
    }

    container.appendChild(fragment);
  });

  if (roster.length === 0) {
    const empty = document.createElement("li");
    empty.className = "roster-entry";
    empty.textContent = side === "party" ? "No allies present." : "No foes detected.";
    container.appendChild(empty);
  }
}

function updateBriefStats(frame) {
  const party = Array.isArray(frame.players) ? frame.players : [];
  const enemies = Array.isArray(frame.enemies) ? frame.enemies : [];
  const partyTotal = party.length;
  const enemyTotal = enemies.length;
  const partyAlive = party.filter((member) => member.alive !== false).length;
  const enemyAlive = enemies.filter((member) => member.alive !== false).length;
  const totalFrames = state.payload?.frames?.length ?? 0;
  const currentFrame = Math.min(state.turnIndex + 1, totalFrames);

  if (partyCount) {
    partyCount.textContent = partyTotal ? `${partyAlive}/${partyTotal}` : `${partyAlive}`;
  }

  if (enemyCount) {
    enemyCount.textContent = enemyTotal ? `${enemyAlive}/${enemyTotal}` : `${enemyAlive}`;
  }

  if (roundCount) {
    roundCount.textContent = totalFrames ? `${currentFrame}/${totalFrames}` : "--";
  }

  const netAdvantage = partyAlive - enemyAlive;
  const normalizer = Math.max(partyTotal || 1, enemyTotal || 1);
  const normalized = clamp01((netAdvantage / normalizer + 1) / 2);
  const percentage = Math.round(normalized * 100);

  if (momentumFill) {
    momentumFill.style.transform = `scaleX(${normalized})`;
    momentumFill.dataset.state = netAdvantage >= 0 ? "party" : "enemy";
  }

  if (momentumLabel) {
    let label;
    if (partyTotal === 0 && enemyTotal === 0) {
      label = "No combatants";
    } else if (netAdvantage > 1) {
      label = "Allies surging";
    } else if (netAdvantage === 1) {
      label = "Allies leaning";
    } else if (netAdvantage === 0) {
      label = "Even footing";
    } else if (netAdvantage === -1) {
      label = "Foes leaning";
    } else {
      label = "Foes surging";
    }
    momentumLabel.textContent = label.toUpperCase();
  }

  if (momentumTrack) {
    momentumTrack.setAttribute("aria-valuenow", percentage.toString());
    const ariaText = momentumLabel?.textContent ?? `${percentage}%`;
    momentumTrack.setAttribute("aria-valuetext", ariaText);
  }
}

function renderLog(container, events, options = {}) {
  if (!container || !eventTemplate) {
    return;
  }

  container.innerHTML = "";
  events.forEach((event, index) => {
    const fragment = eventTemplate.content.cloneNode(true);
    const line = fragment.querySelector(".event-line");
    if (line) {
      line.textContent = event;
      if (options.markFinale && index === events.length - 1) {
        line.classList.add("finale");
      }
    }
    container.appendChild(fragment);
  });

  if (options.appendConclusion && state.payload?.conclusion) {
    const fragment = eventTemplate.content.cloneNode(true);
    const line = fragment.querySelector(".event-line");
    if (line) {
      line.textContent = state.payload.conclusion;
      line.classList.add("finale");
    }
    container.appendChild(fragment);
  }
}

function updateTimelineHighlight() {
  const frames = state.payload?.frames ?? [];

  if (timelineSlider) {
    timelineSlider.value = state.turnIndex.toString();
    timelineSlider.disabled = frames.length <= 1;
  }

  if (timelineMarks) {
    const marks = timelineMarks.querySelectorAll("li");
    marks.forEach((mark) => {
      const index = Number.parseInt(mark.dataset.index || "", 10);
      mark.classList.toggle("active", index === state.turnIndex);
    });
  }

  if (timelineReadout) {
    const frame = frames[state.turnIndex];
    if (frame) {
      const label = frame.is_final ? "Finale" : `Turn ${frame.turn}`;
      const total = frames.length;
      timelineReadout.textContent = `${label} — ${state.turnIndex + 1}/${total}`;
    } else {
      timelineReadout.textContent = "--";
    }
  }
}

function focusActiveTimeline() {
  timelineSlider?.focus({ preventScroll: false });
}

function updateControls() {
  const frames = state.payload?.frames ?? [];
  if (prevButton) {
    prevButton.disabled = state.turnIndex <= 0;
  }
  if (nextButton) {
    const canAdvance =
      frames.length > 0 &&
      (state.turnIndex < frames.length - 1 || (state.mode === "live" && !state.sessionComplete));
    nextButton.disabled = !canAdvance;
  }

  if (playButton) {
    const canAutoplay =
      frames.length > 1 || (state.mode === "live" && !state.sessionComplete && frames.length > 0);
    playButton.disabled = !canAutoplay;
    playButton.textContent = state.autoplayId ? "⏸ Halt" : "▶ Auto-run";
  }
}

function updateConclusion() {
  if (!conclusionEl) {
    return;
  }

  if (!state.payload?.conclusion) {
    conclusionEl.classList.add("hidden");
    conclusionEl.textContent = "";
    return;
  }

  const isLastFrame = state.payload.frames && state.turnIndex === state.payload.frames.length - 1;
  conclusionEl.textContent = isLastFrame
    ? state.payload.conclusion
    : "Advance through the timeline to reveal the campaign verdict.";
  conclusionEl.classList.toggle("hidden", false);
}

function startAutoplay() {
  if (state.autoplayId) {
    return;
  }
  if (playButton) {
    playButton.textContent = "⏸ Halt";
  }

  const runTick = async () => {
    if (!state.payload?.frames) {
      stopAutoplay();
      return;
    }

    if (state.turnIndex < state.payload.frames.length - 1) {
      setTurn(state.turnIndex + 1, { skipFocus: true });
      scheduleNext();
      return;
    }

    if (state.mode === "live" && !state.sessionComplete) {
      try {
        await advanceLiveSession({ preserveAutoplay: true });
        scheduleNext();
      } catch (error) {
        console.error(error);
        updateSessionIndicator("Autoplay halted", true);
        stopAutoplay();
      }
      return;
    }

    stopAutoplay();
  };

  const scheduleNext = () => {
    state.autoplayId = window.setTimeout(runTick, AUTOPLAY_INTERVAL_MS);
  };

  scheduleNext();
}

function stopAutoplay() {
  if (state.autoplayId) {
    window.clearTimeout(state.autoplayId);
    state.autoplayId = null;
  }
  if (playButton) {
    playButton.textContent = "▶ Auto-run";
  }
}

function resetMomentum() {
  if (momentumFill) {
    momentumFill.style.transform = "scaleX(0.5)";
    momentumFill.dataset.state = "party";
  }
  if (momentumLabel) {
    momentumLabel.textContent = "EVEN FOOTING";
  }
  if (momentumTrack) {
    momentumTrack.setAttribute("aria-valuenow", "50");
    momentumTrack.setAttribute("aria-valuetext", "Even footing");
  }
}

function showStatus(message, isError = false) {
  if (!statusEl) {
    return;
  }
  statusEl.textContent = message;
  statusEl.classList.toggle("hidden", !message);
  statusEl.classList.toggle("error", isError);
}

function updateSessionIndicator(message, isError = false) {
  if (!sessionIndicator) {
    return;
  }
  sessionIndicator.textContent = message;
  sessionIndicator.classList.toggle("hidden", !message);
  sessionIndicator.classList.toggle("error", isError);
  if (liveSessionButton) {
    liveSessionButton.textContent = state.mode === "live" ? "Restart live session" : "Start live session";
    liveSessionButton.title = `Connect to ${state.serviceUrl}`;
  }
}

function refreshSessionIndicator() {
  const hostLabel = formatServiceHost(state.serviceUrl);
  if (state.mode !== "live") {
    const message = hostLabel ? `Service target · ${hostLabel}` : "";
    updateSessionIndicator(message, false);
    return;
  }
  const frames = Array.isArray(state.payload?.frames) ? state.payload.frames : [];
  const lastTurn = frames.length ? frames[frames.length - 1].turn : 0;
  const status = state.sessionComplete ? "complete" : "active";
  const shortId = state.sessionId ? state.sessionId.slice(0, 8) : "--";
  const prefix = hostLabel ? `Live ${shortId} @ ${hostLabel}` : `Live ${shortId}`;
  const message = frames.length
    ? `${prefix} · Turn ${lastTurn} · ${status}`
    : `${prefix} · awaiting first turn`;
  updateSessionIndicator(message, false);
}

function setServiceUrl(url, options = {}) {
  const { silent = false, announce = false } = options;
  const normalized = normalizeServiceUrl(url, state.serviceUrl || DEFAULT_SERVICE_URL);
  state.serviceUrl = normalized;
  if (serviceInput && serviceInput.value !== normalized) {
    serviceInput.value = normalized;
  }
  if (liveSessionButton) {
    liveSessionButton.title = `Connect to ${normalized}`;
  }
  if (announce) {
    showStatus(`Session service set to ${normalized}`, false);
  }
  if (!silent) {
    refreshSessionIndicator();
  }
  return normalized;
}

function escapeHtml(text = "") {
  return text
    .toString()
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function clamp01(value) {
  if (Number.isNaN(value)) {
    return 0;
  }
  return Math.min(1, Math.max(0, value));
}

function generatePortraitGradient(side, slot) {
  const hueBase = side === "party" ? 210 : 8;
  const hue = (hueBase + slot * 33) % 360;
  const secondaryHue = (hue + 48) % 360;
  return `linear-gradient(135deg, hsla(${hue}, 70%, 60%, 0.9), hsla(${secondaryHue}, 65%, 38%, 0.9))`;
}

function normalizeServiceUrl(value, fallback = "http://127.0.0.1:8001") {
  if (typeof value !== "string") {
    return fallback;
  }
  let trimmed = value.trim();
  if (!trimmed) {
    return fallback;
  }
  if (!/^https?:\/\//i.test(trimmed)) {
    trimmed = `http://${trimmed}`;
  }
  try {
    const parsed = new URL(trimmed);
    parsed.hash = "";
    let normalized = parsed.toString();
    normalized = normalized.replace(/\/+$/, "");
    return normalized || fallback;
  } catch (error) {
    console.warn("Invalid service URL provided", value, error);
    return fallback;
  }
}

function formatServiceHost(url) {
  if (!url) {
    return "";
  }
  try {
    const parsed = new URL(url);
    return parsed.host || parsed.hostname || url;
  } catch {
    return url;
  }
}

function summarizeDigest(frame) {
  const events = Array.isArray(frame.new_events) ? frame.new_events : [];
  const firstLine = events.find((line) => typeof line === "string" && line.trim());
  if (!firstLine) {
    return frame.is_final ? "Chronicle finale" : "No new entries";
  }
  const compact = firstLine.trim();
  if (compact.length <= 72) {
    return compact;
  }
  return `${compact.slice(0, 69)}…`;
}

function clearRoster(container, placeholder) {
  if (!container) {
    return;
  }
  container.innerHTML = "";
  if (placeholder) {
    const empty = document.createElement("li");
    empty.className = "roster-entry";
    empty.textContent = placeholder;
    container.appendChild(empty);
  }
}

function clearLog(container) {
  if (!container) {
    return;
  }
  container.innerHTML = "";
}

function clearTimeline() {
  if (timelineSlider) {
    timelineSlider.value = "0";
    timelineSlider.disabled = true;
  }
  if (timelineMarks) {
    timelineMarks.innerHTML = "";
  }
  if (timelineReadout) {
    timelineReadout.textContent = "--";
  }
}

function clearDigest() {
  if (digestList) {
    digestList.innerHTML = "";
  }
}

function clearDossier() {
  state.selection = null;
  updateRosterSelection();
  if (dossierEmpty && dossierContent) {
    dossierEmpty.classList.remove("hidden");
    dossierContent.classList.add("hidden");
  }
}

function updateDigestHighlight() {
  if (!digestList) {
    return;
  }
  const cards = digestList.querySelectorAll(".digest-card");
  cards.forEach((card) => {
    const index = Number.parseInt(card.dataset.index || "", 10);
    card.classList.toggle("active", index === state.turnIndex);
  });
}

function setLogView(view) {
  state.logView = view;
  if (eventLog && cumulativeLog) {
    const isTurn = view === "turn";
    eventLog.classList.toggle("hidden", !isTurn);
    cumulativeLog.classList.toggle("hidden", isTurn);
    cumulativeLog.setAttribute("aria-hidden", isTurn ? "true" : "false");
    eventLog.setAttribute("aria-hidden", isTurn ? "false" : "true");
  }
  logTabButtons.forEach((button) => {
    const isActive = button.dataset.logView === view;
    button.classList.toggle("active", isActive);
    button.setAttribute("aria-selected", isActive ? "true" : "false");
  });
}

function selectCombatant(side, index) {
  state.selection = { side, index };
  updateRosterSelection();
  updateDossier();
}

function updateRosterSelection() {
  const cards = document.querySelectorAll(".roster-card");
  cards.forEach((card) => {
    const side = card.dataset.side;
    const index = Number.parseInt(card.dataset.index || "", 10);
    const isActive = Boolean(
      state.selection && state.selection.side === side && state.selection.index === index,
    );
    card.classList.toggle("selected", isActive);
  });
}

function updateDossier() {
  if (!dossierEmpty || !dossierContent) {
    return;
  }

  const frames = state.payload?.frames ?? [];
  const frame = frames[state.turnIndex];
  if (!frame || !state.selection) {
    dossierEmpty.classList.remove("hidden");
    dossierContent.classList.add("hidden");
    return;
  }

  const roster = state.selection.side === "party" ? frame.players : frame.enemies;
  if (!Array.isArray(roster) || !roster[state.selection.index]) {
    state.selection = null;
    updateRosterSelection();
    dossierEmpty.classList.remove("hidden");
    dossierContent.classList.add("hidden");
    return;
  }

  const entry = roster[state.selection.index];
  dossierEmpty.classList.add("hidden");
  dossierContent.classList.remove("hidden");

  if (dossierPortrait) {
    dossierPortrait.style.background = generatePortraitGradient(state.selection.side, state.selection.index);
  }

  if (dossierName) {
    dossierName.textContent = entry.name || "Unknown";
  }

  if (dossierRole) {
    const label = entry.char_class || entry.role || "Adventurer";
    dossierRole.textContent = label.toUpperCase();
  }

  const hpCurrent = Number.isFinite(entry.hp) ? entry.hp : 0;
  const hpMax = Number.isFinite(entry.max_hp) && entry.max_hp > 0 ? entry.max_hp : 0;
  const ratio = hpMax ? Math.max(0, Math.min(hpCurrent / hpMax, 1)) : 0;
  const percent = Math.round(ratio * 100);

  if (dossierStatus) {
    const statusText = entry.alive !== false ? (percent >= 60 ? "Holding" : percent >= 25 ? "Wounded" : "Critical") : "Fallen";
    dossierStatus.textContent = statusText.toUpperCase();
  }

  if (dossierHp) {
    dossierHp.textContent = hpMax ? `${hpCurrent}/${hpMax} HP (${percent}%)` : `${hpCurrent} HP`;
  }

  if (dossierSide) {
    dossierSide.textContent = state.selection.side === "party" ? "PARTY" : "OPPOSITION";
  }

  if (dossierNote) {
    let note;
    if (entry.alive === false) {
      note = "Marked fallen. The console preserves their ledger for review.";
    } else if (percent >= 75) {
      note = "Standing strong and ready for the next exchange.";
    } else if (percent >= 40) {
      note = "Weathering the clash with manageable wounds.";
    } else {
      note = "On the brink. Consider decisive action or support.";
    }
    dossierNote.textContent = note;
  }
}

async function handleKeydown(event) {
  const target = event.target;
  if (target instanceof HTMLElement) {
    const tag = target.tagName;
    if (tag === "INPUT" || tag === "TEXTAREA" || target.isContentEditable) {
      return;
    }
  }

  if (!state.payload?.frames?.length) {
    return;
  }

  const frames = state.payload.frames;

  if (event.key === "ArrowRight" || event.key === "]") {
    event.preventDefault();
    if (state.turnIndex < frames.length - 1) {
      stopAutoplay();
      setTurn(state.turnIndex + 1, { skipFocus: true });
    } else if (state.mode === "live" && !state.sessionComplete) {
      stopAutoplay();
      try {
        await advanceLiveSession();
      } catch (error) {
        console.error(error);
        updateSessionIndicator("Unable to advance session", true);
      }
    }
  } else if (event.key === "ArrowLeft" || event.key === "[") {
    event.preventDefault();
    if (state.turnIndex > 0) {
      stopAutoplay();
      setTurn(state.turnIndex - 1, { skipFocus: true });
    }
  } else if (event.key === " " || event.key === "Spacebar") {
    event.preventDefault();
    if (state.autoplayId) {
      stopAutoplay();
    } else {
      startAutoplay();
    }
  } else if (event.key === "Home") {
    event.preventDefault();
    stopAutoplay();
    setTurn(0, { skipFocus: true });
  } else if (event.key === "End") {
    event.preventDefault();
    stopAutoplay();
    setTurn(state.payload.frames.length - 1, { skipFocus: true });
  }
}
