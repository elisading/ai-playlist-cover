document.addEventListener('DOMContentLoaded', function() {
    const generateButton = document.getElementById('generateImage');
    const aiImage = document.getElementById('aiImage');
    const imageLoader = document.getElementById('imageLoader');
    const downloadButton = document.getElementById('downloadImage');
    const uploadButton = document.getElementById('uploadToSpotify');
    const visualDescription = document.getElementById('visualDescription');

    generateButton.addEventListener('click', function() {
        const playlistId = this.dataset.playlistId;
        console.log("Playlist id: ", playlistId)
        
        // Show loader, hide existing image
        imageLoader.style.display = 'flex';
        aiImage.style.display = 'none';
        downloadButton.style.display = 'none';
        uploadButton.style.display = 'none';
        
        fetch(`/generate_image/${playlistId}`)
            .then(response => response.json())
            .then(data => {
                // Hide loader, show new image
                imageLoader.style.display = 'none';
                aiImage.src = data.image_url;
                aiImage.style.display = 'block';
                
                // Update description and show buttons
                visualDescription.textContent = data.description;
                downloadButton.href = data.image_url;
                // downloadButton.setAttribute('download', 'playlist_cover.jpg'); 
                downloadButton.style.display = 'inline-block';
                uploadButton.style.display = 'inline-block';
            })
            .catch(error => {
                console.error('Error:', error);
                imageLoader.style.display = 'none';
            });
    });

    uploadButton.addEventListener('click', function() {
        const playlistId = generateButton.dataset.playlistId;
        
        fetch(`/upload_image/${playlistId}`, {
            method: 'POST',
            body: JSON.stringify({image_url: aiImage.src}),
            headers: {
                'Content-Type': 'application/json'
            }
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
            console.error('Error uploading:', error);
            alert('An error occurred while uploading the image. Please try again.');
        });
    });

    downloadButton.addEventListener('click', function() {
        const imageUrl = this.dataset.imageUrl;
        downloadImageDirectly(imageUrl);
    });

});

function generateAIImage(playlistId) {
    fetch(`/playlists/${playlistId}/generate_image`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            // Hide loader, show new image
            document.getElementById('imageLoader').style.display = 'none';
            document.getElementById('aiImage').src = data.image_url;
            document.getElementById('aiImage').style.display = 'block';
            
            // Update description and show buttons
            document.getElementById('visualDescription').textContent = data.visual_description;
            document.getElementById('downloadImage').href = data.image_url;
            document.getElementById('downloadImage').style.display = 'inline-block';
            document.getElementById('uploadToSpotify').style.display = 'inline-block';
        })
        .catch(error => {
            console.error("Error:", error);
            document.getElementById('imageLoader').style.display = 'none';
            alert('An error occurred while generating the image. Please try again.');
        });
}

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

function downloadImageThroughProxy(imageUrl) {
    const proxyUrl = `http://127.0.0.1:5000/download_image?url=${encodeURIComponent(imageUrl)}`;
    fetch(proxyUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = "playlist_cover.jpg";
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        })
        .catch(error => {
            console.error("Download error:", error);
            alert("Unable to download the image. Please try again or check the image URL.");
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
