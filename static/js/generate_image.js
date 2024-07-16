document.addEventListener('DOMContentLoaded', function() {
    const generateButton = document.getElementById('generateImage');
    const aiImage = document.getElementById('aiImage');
    const catLoader = document.getElementById('catLoader');
    const downloadButton = document.getElementById('downloadImage');
    const uploadButton = document.getElementById('uploadToSpotify');
    const visualDescription = document.getElementById('visualDescription');
    const catGif = document.getElementById('catGif');
    const catGifs = ['cats1.gif', 'cats2.gif', 'cats3.gif', 'cats4.gif', 'cats5.gif', 'cats6.gif', 'cats7.gif', 'cats8.gif'];

    generateButton.addEventListener('click', function() {
        const playlistId = this.dataset.playlistId;
        console.log("Playlist id: ", playlistId);

        const randomCat = catGifs[Math.floor(Math.random() * catGifs.length)];
        catGif.src = `/static/${randomCat}`;
        
        // Show loader, hide existing image
        catLoader.style.display = 'block';
        aiImage.style.display = 'none';
        downloadButton.style.display = 'none';
        uploadButton.style.display = 'none';
        
        console.log("Cat loader display:", catLoader.style.display);
        console.log("AI Image display:", aiImage.style.display);
        console.log("Cat GIF source:", catGif.src);
        
        fetch(`/playlists/${playlistId}/generate_image`, { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                // Hide loader, show new image
                catLoader.style.display = 'none';
                aiImage.src = data.image_url;
                aiImage.style.display = 'block';
                
                // Update description and show buttons
                visualDescription.textContent = data.visual_description;
                downloadButton.href = data.image_url;
                downloadButton.style.display = 'inline-block';
                uploadButton.style.display = 'inline-block';
            })
            .catch(error => {
                console.error('Error:', error);
                catLoader.style.display = 'none';
                alert('An error occurred while generating the image. Please try again.');
            });
    });

    uploadButton.addEventListener('click', function() {
        const playlistId = generateButton.dataset.playlistId;
        uploadImageToSpotify(playlistId, aiImage.src);
    });

    downloadButton.addEventListener('click', function(event) {
        event.preventDefault();
        downloadImageDirectly(aiImage.src);
    });
});

function uploadImageToSpotify(playlistId, imageUrl) {
    fetch(`/playlists/${playlistId}/upload_image`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ image_url: imageUrl }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Image successfully uploaded to Spotify!');
        } else {
            alert('Failed to upload image to Spotify. Please try again.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while uploading the image. Please try again.');
    });
}

function downloadImageDirectly(imageUrl) {
    fetch(imageUrl)
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'playlist_cover.jpg';
            document.body.appendChild(a);
            a.click();
            setTimeout(() => {
                window.URL.revokeObjectURL(url);
            }, 100);
        })
        .catch(error => {
            console.error('Failed to download the image:', error);
        });
}