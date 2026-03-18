const TIMESTAMP_TYPE_LABELS = {
    1: "Exercise",
    2: "Task",
    3: "Lecture",
};

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

        document.getElementById("preview-title").value = data.title;

        const tbody = document.getElementById("preview-timestamps");
        tbody.innerHTML = "";
        data.timestamps.forEach(ts => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${ts.start_time}</td>
                <td>${ts.label}</td>
                <td>${TIMESTAMP_TYPE_LABELS[ts.timestamp_type] ?? ts.timestamp_type}</td>
            `;
            tbody.appendChild(tr);
        });

        document.getElementById("preview-card").classList.remove("preview-card--hidden");


    })
    .catch(err => alert("Error: " + err));
});