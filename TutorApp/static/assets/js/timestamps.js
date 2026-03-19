const timestamps = JSON.parse(
    document.getElementById('timestamps-data').textContent
);

const container = document.getElementById('timestamp-buttons');

timestamps.forEach(ts => {
    const btn = document.createElement('button');
    btn.className = 'timestamp-btn';
    btn.innerHTML = `
        <span class="timestamp-btn__time">${ts.time}</span>
        <span class="timestamp-btn__label">${ts.label}</span>
    `;
    btn.onclick = () => seekTo(ts.seconds);
    container.appendChild(btn);
});