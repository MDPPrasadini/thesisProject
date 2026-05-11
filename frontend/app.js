const API = "http://localhost:8000"

async function upload(){
    const file = document.getElementById("fileInput").files[0]
    const formData = new FormData()
    formData.append("file", file)

    await fetch(API + "/upload", {
        method: "POST",
        body: formData
    })

    document.getElementById("video").src = URL.createObjectURL(file)
}

async function search(){
    const query = document.getElementById("searchBox").value

    const res = await fetch(API + "/search?q=" + query)
    const data = await res.json()

    const results = document.getElementById("results")
    results.innerHTML = ""

    data.forEach(r => {
        const div = document.createElement("div")
        div.innerHTML = `
            <button onclick="jump(${r.start})">
            ${formatTime(r.start)} - ${r.text}
            </button>
        `
        results.appendChild(div)
    })
}

function jump(time){
    const video = document.getElementById("video")
    video.currentTime = time
    video.play()
}

function formatTime(seconds){
    const m = Math.floor(seconds / 60)
    const s = Math.floor(seconds % 60)
    return `${m}:${s}`
}

async function downloadLecture() {
    const url = document.getElementById("lectureUrl").value;

    const response = await fetch(
        "http://127.0.0.1:8000/download-url",
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ url })
        }
    );

    const data = await response.json();

    document.getElementById("result").innerText =
        data.transcript;
}
