const API = "https://ai-lecture-search-api.onrender.com";

const DOM = {
  status: document.getElementById("status"),
  loaderOverlay: document.getElementById("loaderOverlay"),
  loaderText: document.getElementById("loaderText"),
  video: document.getElementById("video"),
  fileInput: document.getElementById("fileInput"),
  searchBox: document.getElementById("searchBox"),

  mainSummary: document.getElementById("mainSummary"),
  searchTranscriptTab: document.getElementById("searchTranscriptTab"),
  searchSummaryTab: document.getElementById("searchSummaryTab"),
  aiSummaryTab: document.getElementById("aiSummaryTab"),

  mainSummarySection: document.getElementById("mainSummarySection"),
  searchTranscriptSection: document.getElementById("searchTranscriptSection"),
  aiSummarySection: document.getElementById("aiSummarySection"),
  searchSummarySection: document.getElementById("searchSummarySection"),
};

// ===================== APP STATE =====================
const state = {
  searchQuery: "",
  searchSummaryCache: {},
  aiSummaryCache: {},
  mainSummaryCache: null
};

// ===================== UI HELPERS =====================
function setStatus(msg) {
  DOM.status.innerText = msg;
}

// ===================== INITIAL LOAD =====================
window.onload = function () {
  clearUI();
  hideTabBar();
};

// ===================== UPLOAD (WITH PROGRESS) =====================
async function upload() {
  const fileInput = DOM.fileInput;

  if (!fileInput.files.length) {
    alert("Please select a file");
    return;
  }

  const file = fileInput.files[0];
  const formData = new FormData();
  formData.append("file", file);

  const xhr = new XMLHttpRequest();
  xhr.open("POST", API + "/upload");

  xhr.onloadstart = function () {
    showLoader("Uploading...");
    setStatus("Uploading...");
  };
      state.mainSummaryCache = null;
      state.searchSummaryCache = {};
      state.aiSummaryCache = {};
  xhr.upload.onprogress = function (event) {
    if (event.lengthComputable) {
      const percent = Math.round((event.loaded / event.total) * 100);
      if (percent == 100) {
        setStatus("Generating transcript ....");
        showLoader("Generating transcript ....");
      } else {
        setStatus("Uploading... " + percent + "%");
      }
    }
  };

  xhr.onload = function () {
    try {
      const data = JSON.parse(xhr.responseText);
      console.log("Transcript:", data.transcript);

      setStatus("Upload complete ✅");
      // New video uploaded -> clear summary caches

      saveToCache(file.name, {
        transcript: data.transcript,
        segments: data.segments,
        topics: data.topics,
      });

      showMainTopics();
    } catch (e) {
      console.error(e);
    }
  };

  xhr.onerror = function () {
    setStatus("Upload failed ❌");
  };

  xhr.send(formData);

  // show video locally
  const video = DOM.video;
  video.src = URL.createObjectURL(file);
}

// ===================== SEARCH =====================
async function search() {
  state.searchQuery = DOM.searchBox.value;
  console.log(state.searchQuery);
  delete state.searchSummaryCache[state.searchQuery];
  delete state.aiSummaryCache[state.searchQuery];
  showLoader("Searching...");
  setStatus("Searching...");
  DOM.mainSummarySection.innerHTML = "";
  try {
    const res = await fetch(API + "/search", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query: state.searchQuery }),
    });

    const data = await res.json();
    setStatus("Search complete ✅");
    const results = data.results || [];
    console.log(results);
    renderSearchResults("searchTranscriptSection", results, state.searchQuery);
    document.querySelector(".tab-link").click();
    // SHOW transcript tab
    document
      .querySelectorAll(".tab-pane")
      .forEach((tab) => tab.classList.remove("active-tab"));

    DOM.searchTranscriptTab.classList.add("active-tab");

    showTabBar();
    setTimeout(() => {
      hideLoader();
      setStatus("");
    }, 800);
  } catch (err) {
    console.error(err);
    setStatus("Search failed ❌");
    hideLoader();
  }
}

// =====================  GENERATE MAIN TOPICS =====================
async function generateMainTopics() {

    // CACHE HIT
  if (state.mainSummaryCache) {
    renderMainTopics(state.mainSummaryCache);
    return;
  }

  showLoader("Generating Lecture Summary...");
  setStatus("Generating Lecture Summary...");

  try {
    const cached = JSON.parse(localStorage.getItem("lectureCache") || "{}");
    const fileKeys = Object.keys(cached);

    if (!fileKeys.length) {
      setStatus("Please upload a lecture first.");
      return;
    }

    const latest = cached[fileKeys[fileKeys.length - 1]];
    const segments = latest.transcript;

    const res = await fetch(API + "/summary", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ segments }),
    });

    const data = await res.json();
    const results = data.results || [];
    // SAVE TO CACHE
    state.mainSummaryCache = results;
    renderMainTopics(results);
    setStatus("Summary generated ✅");
  } catch (err) {
    console.error(err);
    hideLoader();
    setStatus("Summary failed ❌");
  } finally {
    hideLoader();
  }
}

// =====================  GENERATE LECTURE SEARCH SUMMARY =====================
async function generateSearchSummary() {
  const query = state.searchQuery;

  // Use cached data if available
  if (state.searchSummaryCache[query]) {
    renderSearchSummary(state.searchSummaryCache[query]);
    return;
  }

  showLoader("Generating Lecture Summary...");
  setStatus("Generating Lecture Summary...");

  try {
    const cached = JSON.parse(localStorage.getItem("lectureCache") || "{}");
    const fileKeys = Object.keys(cached);

    if (!fileKeys.length) {
      setStatus("Please upload a lecture first.");
      return;
    }

    const latest = cached[fileKeys[fileKeys.length - 1]];
    const segments = latest.transcript;
    console.log(latest.transcript);
    const res = await fetch(API + "/search-summary", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ segments, query: state.searchQuery }),
    });

    const data = await res.json();
    const results = data.results || [];
    console.log(results);
    state.searchSummaryCache[query] = results;
    renderSearchSummary(results);
    setStatus("Summary generated ✅");
  } catch (err) {
    console.error(err);
    setStatus("Summary failed ❌");
  } finally {
    hideLoader();
  }
}

// =====================  GENERATE SEARCH AI SUMMARY =====================
async function generateSearchAISummary() {
  const query = state.searchQuery;
  // Use cached data if available
  if (state.aiSummaryCache[query]) {
    renderSearchAISummaries(state.aiSummaryCache[query]);
    return;
  }

  showLoader("Generating Search Summary using AI...");
  setStatus("Generating Search Summary using AI...");

  try {
    const cached = JSON.parse(localStorage.getItem("lectureCache") || "{}");
    const fileKeys = Object.keys(cached);

    if (!fileKeys.length) {
      setStatus("Please upload a lecture first.");
      return;
    }

    const latest = cached[fileKeys[fileKeys.length - 1]];
    const segments = latest.transcript;
    console.log(latest.transcript);
    const res = await fetch(API + "/search-ai-summary", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ segments, query: state.searchQuery }),
    });

    const data = await res.json();
    const results = data.results || [];
    state.aiSummaryCache[query] = results;
    renderSearchAISummaries(results);
    setStatus("AI Summary generated ✅");
  } catch (err) {
    console.error(err);
    setStatus("Summary failed ❌");
  } finally {
    hideLoader();
  }
}

// ===================== SHOW MAIN TOPICS =====================
async function showMainTopics() {
  // hide tab bar initially
  hideTabBar();
  // show Topics section by default
  document.querySelectorAll(".tab-pane").forEach((tab) => {
    tab.classList.remove("active-tab");
  });
  DOM.mainSummary.classList.add("active-tab");

  // ===== CACHE CHECK =====
  const fileInput = DOM.fileInput;
  if (!fileInput.files.length) {
    alert("Please select a file");
    return;
  }

  const file = fileInput.files[0];
  const cached = getFromCache(file.name);
  if (cached) {
    generateMainTopics();
  }
}

function renderMainTopics(topics) {
  // Hide all tabs
  document.querySelectorAll(".tab-pane").forEach(tab => {
    tab.classList.remove("active-tab");
  });

  // Show main summary tab
  DOM.mainSummary.classList.add("active-tab");
  hideTabBar();
  //DOM.mainSummary.classList.add("active-tab");

  renderCards({
    container: DOM.mainSummarySection,
    title: "Main Lecture Topics",
    items: topics,
  });
}

function renderSearchResults(tabId, results, query) {
  renderCards({
    container: document.getElementById(tabId),
    title: `Search Results for "${query}"`,
    items: results,
    type: "search-results",
    query,
    emptyMessage: "No transcript matches found.",
  });
}

function renderSearchSummary(topics) {
  //DOM.searchSummaryTab.classList.add("active-tab");

  renderCards({
    container: DOM.searchSummarySection,
    title: "Search Topics",
    items: topics,
  });
}

function renderSearchAISummaries(aiSummaries) {
  //DOM.aiSummaryTab.classList.add("active-tab");

  renderCards({
    container: DOM.aiSummarySection,
    title: "Main Lecture Topics",
    items: aiSummaries,
    summaryField: "lecture_summary",
    showResources: true,
  });
}

// ===================== TAB BAR CONTROL =====================
function hideTabBar() {
  document.querySelector(".dsv-tabbar").style.display = "none";
}

function showTabBar() {
  document.querySelector(".dsv-tabbar").style.display = "flex";
}

// ===================== TAB SYSTEM =====================
function openTab(tabId, button) {
  console.log(tabId);
  // hide all tabs
  const tabs = document.querySelectorAll(".tab-pane");
  tabs.forEach((tab) => {
    tab.classList.remove("active-tab");
  });

  // remove active button
  const buttons = document.querySelectorAll(".tab-link");
  buttons.forEach((btn) => {
    btn.classList.remove("active");
  });

  const link = document.querySelectorAll(".tab-link");
  link.forEach(btn => {
    btn.classList.remove("active");
  });

  // show selected tab
  document.getElementById(tabId).classList.add("active-tab");
  console.log(DOM.searchSummarySection.innerHTML.trim());
  // activate button
  button.classList.add("active");
  if (tabId === "aiSummaryTab") {
    generateSearchAISummary();
  }
  if (tabId == "searchSummaryTab") {
    generateSearchSummary();
  }

}

// ===================== HIGHLIGHT SEARCH =====================
function highlightKeyword(text, keyword) {
  const regex = new RegExp(`(${keyword})`, "gi");
  return text.replace(regex, `<mark>$1</mark>`);
}

// ===================== VIDEO SEEK =====================
function jump(time) {
  const video = DOM.video;
  video.currentTime = time;
  video.play();
}

// ===================== TIME FORMAT =====================
function formatTime(seconds) {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s < 10 ? "0" + s : s}`;
}

// ===================== CACHE =====================
function saveToCache(filename, data) {
  const cache = JSON.parse(localStorage.getItem("lectureCache") || "{}");

  cache[filename] = {
    ...data,
    timestamp: Date.now(),
  };

  localStorage.setItem("lectureCache", JSON.stringify(cache));
}

function getFromCache(filename) {
  const cache = JSON.parse(localStorage.getItem("lectureCache") || "{}");

  return cache[filename];
}

// ===================== RESET UI =====================
function clearUI() {
  DOM.mainSummarySection.innerHTML = "";
  DOM.searchTranscriptSection.innerHTML = "";
  DOM.aiSummarySection.innerHTML = "";
}

let loaderTimeout;

function showLoader(message = "Loading...") {
  loaderTimeout = setTimeout(() => {
    DOM.loaderOverlay.classList.remove("hidden");

    DOM.loaderText.innerText = message;
  }, 200);
}

function hideLoader() {
  clearTimeout(loaderTimeout);

  DOM.loaderOverlay.classList.add("hidden");
}

function renderCards({
  container,
  title,
  items,
  emptyMessage = "No data found.",
  type = "topics",
  summaryField = "summary",
  showResources = false,
  query = "",
}) {
  if (!container) return;

  if (!items || !items.length) {
    container.innerHTML = `
      <div class="empty-state">
        ${emptyMessage}
      </div>
    `;
    return;
  }

  let html = `<h2>${title}</h2>`;

  // =====================
  // SEARCH RESULTS MODE
  // =====================
  if (type === "search-results") {
    items.forEach((item) => {
      html += `
        <div class="segment">

          <button onclick="jump(${item.start})">
            ${formatTime(item.start)}
          </button>

          <span>
            ${highlightKeyword(item.text, query)}
          </span>

        </div>
      `;
    });

    container.innerHTML = html;
    return;
  }

  // =====================
  // TOPIC CARDS MODE
  // =====================
  items.forEach((item) => {
    html += `
      <div class="topic-card">

        <h3>${item.topic}</h3>

        <p>${item[summaryField] || ""}</p>

        <div class="keywords">
          ${(item.keywords || [])
            .map(
              (k) => `
                <span class="keyword">
                  ${k}
                </span>
              `,
            )
            .join("")}
        </div>
    `;

    // =====================
    // OPTIONAL RESOURCES
    // =====================
    if (showResources && item.resources?.length) {
      html += `
        <div class="resources">

          <h4>Learning Resources</h4>

          ${item.resources
            .map(
              (r) => `
                <div class="resource-link">

                  <a href="${r.url}" target="_blank">
                    ${r.title}
                  </a>

                </div>
              `,
            )
            .join("")}

        </div>
      `;
    }

    html += `
        <button onclick="jump(${item.start_timestamp})">
          Jump to ${formatTime(item.start_timestamp)}
        </button>

      </div>
    `;
  });

  container.innerHTML = html;
}
