const videoId = JSON.parse(document.getElementById('video-id').textContent);

var tag = document.createElement('script')
tag.src = "https://www.youtube.com/iframe_api";
document.head.appendChild(tag);

var player;

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
        },
    });
}

function seekTo(seconds) {
    player.seekTo(seconds, true);
    player.playVideo();
}