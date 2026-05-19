const API = "http://localhost:8000";

// ===================== STATUS =====================
function setStatus(msg) {
    const el = document.getElementById("status");
    if (el) el.innerText = msg;
}

// ===================== UPLOAD =====================
function upload() {
    const fileInput = document.getElementById("fileInput");

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
        setStatus("Uploading lecture...");
    };

    xhr.upload.onprogress = function (event) {
        if (event.lengthComputable) {
            const percent = Math.round((event.loaded / event.total) * 100);
        }
    };

    xhr.onload = function () {
        setStatus("Upload complete ✅");

        let data = {};
        try {
            data = JSON.parse(xhr.responseText);
        } catch (e) {
            console.error("Invalid JSON", e);
        }

        console.log("Transcript:", data.transcript);

        // show video locally
        const video = document.getElementById("video");
        video.src = URL.createObjectURL(file);

        renderTopics(data.topics || []);

        // hide progress after short delay
        setTimeout(() => {
            setStatus("");
        }, 800);
    };

    xhr.onerror = function () {
        setStatus("Upload failed ❌");
    };

    xhr.send(formData);
}

// ===================== SEARCH =====================
async function search() {
    const query = document.getElementById("searchBox").value;

    try {
        const res = await fetch(API + "/search", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query })
        });

        const data = await res.json();

        const resultsDiv = document.getElementById("results");
        resultsDiv.innerHTML = "";

        (data.results || []).forEach(r => {
            const div = document.createElement("div");
            div.innerHTML = `
                <button onclick="jump(${r.start})">
                    ${formatTime(r.start)} - ${r.text}
                </button>
            `;
            resultsDiv.appendChild(div);
        });

    } catch (err) {
        console.error(err);
        setStatus("Search failed ❌");
    }
}

// ===================== TOPICS =====================
function renderTopics(topics) {
    const container = document.getElementById("topics");
    container.innerHTML = "";

    topics.forEach(t => {
        const btn = document.createElement("button");
        btn.className = "btn";
        btn.innerText = t.title;

        btn.onclick = () => {
            alert("Topic clicked: " + t.title);
        };

        container.appendChild(btn);
    });
}

// ===================== VIDEO SEEK =====================
function jump(time) {
    const video = document.getElementById("video");
    video.currentTime = time;
    video.play();
}

// ===================== TIME FORMAT =====================
function formatTime(seconds) {
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m}:${s < 10 ? "0" + s : s}`;
}

// ===================== DOWNLOAD URL =====================
async function downloadLecture() {
    const url = document.getElementById("lectureUrl").value;

    const response = await fetch(API + "/download-url", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url })
    });

    const data = await response.json();
    document.getElementById("results").innerText =
        JSON.stringify(data.transcript, null, 2);
}