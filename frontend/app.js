
const API = "http://localhost:8000";


// ===================== UI HELPERS =====================
function setStatus(msg) {
    document.getElementById("status").innerText = msg;
}

function showProgress(show) {
    document.getElementById("progressContainer").style.display = show ? "block" : "none";
}

function setProgress(value) {
    document.getElementById("progressBar").style.width = value + "%";
}


// ===================== UPLOAD (WITH PROGRESS) =====================
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
        showProgress(true);
        setProgress(0);
        setStatus("Uploading...");
    };

    xhr.upload.onprogress = function (event) {
        if (event.lengthComputable) {
            const percent = Math.round((event.loaded / event.total) * 100);
            setProgress(percent);
            setStatus("Uploading... " + percent + "%");
        }
    };

    xhr.onload = function () {
        setProgress(100);
        setStatus("Upload complete ✅");

        try {
            const data = JSON.parse(xhr.responseText);
            console.log("Transcript:", data.transcript);
        } catch (e) {
            console.error(e);
        }
    };

    xhr.onerror = function () {
        setStatus("Upload failed ❌");
    };

    xhr.send(formData);

    // show video locally
    const video = document.getElementById("video");
    video.src = URL.createObjectURL(file);
}


// ===================== SEARCH =====================
async function search() {
    const query = document.getElementById("searchBox").value;

    showProgress(true);
    setProgress(30);
    setStatus("Searching...");

    try {
        const res = await fetch(API + "/search", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ query })
        });

        setProgress(80);

        const data = await res.json();

        setProgress(100);
        setStatus("Search complete ✅");

        const resultsDiv = document.getElementById("results");
        resultsDiv.innerHTML = "";

        const results = data.results || [];

        results.forEach(r => {
            const div = document.createElement("div");
            div.innerHTML = `
                <button onclick="jump(${r.start})">
                    ${formatTime(r.start)} - ${r.text}
                </button>
            `;
            resultsDiv.appendChild(div);
        });

        setTimeout(() => {
            showProgress(false);
            setStatus("");
        }, 800);

    } catch (err) {
        console.error(err);
        setStatus("Search failed ❌");
        showProgress(false);
    }
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
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ url })
    });

    const data = await response.json();

    document.getElementById("results").innerText =
        JSON.stringify(data.transcript, null, 2);
}
