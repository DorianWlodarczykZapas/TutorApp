const startSeconds = JSON.parse(document.getElementById('start-seconds').textContent);
const endSeconds = JSON.parse(document.getElementById('end-seconds').textContent);
const slider = document.getElementById('seek-slider');
let intervalId = null;
document.getElementById('time-current').textContent = formatTime(startSeconds)
document.getElementById('time-end').textContent = formatTime(endSeconds)

slider.addEventListener('input', (e) => {
    seekTo(e.target.value);
});

function seekTo(seconds) {
    player.seekTo(seconds, true);
    player.playVideo();
    watchForEnd();
}

function formatTime(seconds) {
    const minutes = Math.floor(seconds/60)
    const secs = seconds % 60
    return `${String(minutes).padStart(2,'0')}:${String(secs).padStart(2,'0')}`;
}

function watchForEnd() {
    if (intervalId) clearInterval(intervalId);

    if (endSeconds === null) return;


    intervalId = setInterval(() => {
        slider.value = player.getCurrentTime();
        document.getElementById('time-current').textContent = formatTime(Math.floor(player.getCurrentTime()) )

        if (player.getCurrentTime() >= endSeconds) {
            clearInterval(intervalId);
            intervalId = null;
            seekTo(startSeconds);
        }
    }, 500);
}

function onYouTubeIframeAPIReady() {
    player = new YT.Player('player', {
        height: '100%',
        width: '100%',
        videoId: videoId,
        playerVars: {
            controls: 0,
            disablekb: 1,
            modestbranding: 1,
            rel: 0,
            fs: 0,
            start: startSeconds,
        },
        events: {
            onReady: (event) => {
                event.target.seekTo(startSeconds, true);
                watchForEnd();
            },
        },
    });
}