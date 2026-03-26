const startSeconds = JSON.parse(document.getElementById('start-seconds').textContent);
const endSeconds = JSON.parse(document.getElementById('end-seconds').textContent);

let intervalId = null;

function seekTo(seconds) {
    player.seekTo(seconds, true);
    player.playVideo();
    watchForEnd();
}

function watchForEnd() {
    if (intervalId) clearInterval(intervalId);

    if (endSeconds === null) return;

    intervalId = setInterval(() => {
        if (player.getCurrentTime() >= endSeconds) {
            player.pauseVideo();
            clearInterval(intervalId);
            intervalId = null;
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