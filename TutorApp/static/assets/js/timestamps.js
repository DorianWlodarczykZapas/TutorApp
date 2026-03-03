const timestamps = JSON.parse(
    document.getElementById('timestamps-data').textContent
);

const container = document.getElementById('timestamp-buttons');

timestamps.forEach(ts => {
    const btn = document.createElement('button');
    btn.textContent = `${ts.time} — ${ts.type}`;
    btn.onclick = () => seekTo(ts.seconds);
    container.appendChild(btn);
});