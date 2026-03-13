document.getElementById("fetch-btn").addEventListener("click", function () {
    const url = document.getElementById("id_youtube_url").value;

    fetch(`?url=${encodeURIComponent(url)}`, {
        headers: {"X-Requested-With": "XMLHttpRequest"}
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
            return;
        }

        document.getElementById("preview-title").textContent = data.title;

        const container = document.getElementById("preview-timestamps");
        container.innerHTML = "";
        data.timestamps.forEach(ts => {
            const div = document.createElement("div");
            div.textContent = `${ts.start_time} - ${ts.label} (typ: ${ts.timestamp_type})`;
            container.appendChild(div);
        });

        document.getElementById("preview-card").classList.remove("d-none");
    })
    .catch(err => alert("Error: " + err));
});