const TIMESTAMP_CONFIG = {
    1: { bg: "#008374", label: "Ćwiczenia" },
    2: { bg: "#c87f0a", label: "Zadania" },
    4: { bg: "#185FA5", label: "Matura Podstawowa" },
    5: { bg: "#534AB7", label: "Matura Rozszerzona" },
    6: { bg: "#d85a30", label: "Egzamin Ósmoklasisty" },
};

const timestamps = JSON.parse(
    document.getElementById('timestamps-data').textContent
);

const container = document.getElementById('timestamp-buttons');


const groups = {};
timestamps.forEach(ts => {
    if (!groups[ts.timestamp_type]) {
        groups[ts.timestamp_type] = [];
    }
    groups[ts.timestamp_type].push(ts);
});


Object.entries(groups).forEach(([type, items]) => {
    const config = TIMESTAMP_CONFIG[type] || { bg: "#008374", label: "Inne" };


    const header = document.createElement('p');
    header.className = 'timestamp-group-label';
    header.textContent = config.label;
    header.style.color = config.bg;
    container.appendChild(header);


    items.forEach(ts => {
        const btn = document.createElement('button');
        btn.className = 'timestamp-btn';
        btn.style.background = config.bg;
        btn.style.borderColor = config.bg;
        btn.innerHTML = `
            <span class="timestamp-btn__time">${ts.time}</span>
            <span class="timestamp-btn__label">${ts.label}</span>
        `;
        btn.onclick = () => seekTo(ts.seconds);
        container.appendChild(btn);
    });
});