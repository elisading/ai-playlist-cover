function generateAIImage(playlistId) {
    fetch(`/playlists/${playlistId}/generate_image`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            document.getElementById('aiImage').src = data.image_url;
            document.getElementById('aiImage').style.display = 'block';
            document.getElementById('downloadImage').href = data.image_url;
            document.getElementById('downloadImage').style.display = 'block';
            document.getElementById('visualDescription').textContent = data.visual_description;

            document.getElementById('uploadToSpotify').style.display = 'block';

        })
        .catch(error => {
            console.error("Error:", error);
        });
}

function uploadImageToSpotify(playlistId, imageUrl) {
    fetch(`/playlists/${playlistId}/upload_image`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            'image_url': imageUrl
        }),
    })
        .then(response => response.json())
        .catch(error => {
            console.error("Error uploading image to Spotify:", error);
        });
}

function downloadImageDirectly(imageUrl) {
    fetch(imageUrl)
        .then(response => response.blob())
        .then(blob => {
            let url = window.URL.createObjectURL(blob);
            let a = document.createElement('a');
            a.href = url;
            a.download = "playlist_cover.jpg";
            a.click();
        })
        .catch(error => {
            console.error("Download error:", error);
        });
}

document.getElementById("generateImage").addEventListener("click", function () {
    let playlistId = document.getElementById("generateImage").getAttribute("data-playlist-id");
    generateAIImage(playlistId);
});

document.getElementById("uploadToSpotify").addEventListener("click", function () {
    let playlistId = document.getElementById("generateImage").getAttribute("data-playlist-id");
    let imageUrl = document.getElementById('aiImage').src;
    uploadImageToSpotify(playlistId, imageUrl);
});

document.getElementById("downloadImage").addEventListener("click", function (event) {
    event.preventDefault();
    let imageUrl = document.getElementById('aiImage').src;
    downloadImageDirectly(imageUrl);
});
