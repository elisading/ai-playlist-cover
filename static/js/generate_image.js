document.addEventListener('DOMContentLoaded', function() {
    const generateButton = document.getElementById('generateImage');
    const aiImage = document.getElementById('aiImage');
    const catLoader = document.getElementById('catLoader');
    const downloadButton = document.getElementById('downloadImage');
    const uploadButton = document.getElementById('uploadToSpotify');
    const visualDescription = document.getElementById('visualDescription');
    const catGif = document.getElementById('catGif');
    const catGifs = ['cats1.gif', 'cats2.gif', 'cats3.gif', 'cats4.gif', 'cats5.gif', 'cats6.gif', 'cats7.gif'];
    const themeButtons = document.querySelectorAll('.theme-btn');
    let selectedTheme = 'abstract';

    // Theme button functionality
    themeButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons
            themeButtons.forEach(btn => btn.classList.remove('active'));
            // Add active class to clicked button
            this.classList.add('active');
            // Update selected theme
            selectedTheme = this.dataset.theme;
        });
    });

    generateButton.addEventListener('click', function() {
        const playlistId = this.dataset.playlistId;
        console.log("Playlist id: ", playlistId);

        const randomCat = catGifs[Math.floor(Math.random() * catGifs.length)];
        catGif.src = `/static/${randomCat}`;
        
        // Show loading state on button
        const originalText = generateButton.textContent;
        generateButton.disabled = true;
        generateButton.textContent = 'generating... 🪄';
        
        // Show loader, hide existing image
        catLoader.style.display = 'block';
        aiImage.style.display = 'none';
        downloadButton.style.display = 'none';
        uploadButton.style.display = 'none';
        
        
        fetch(`/playlists/${playlistId}/generate_image`, { 
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ theme: selectedTheme })
        })
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
            })
            .finally(() => {
                // Reset button state
                generateButton.disabled = false;
                generateButton.textContent = originalText;
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
    const uploadButton = document.getElementById('uploadToSpotify');
    const originalText = uploadButton.textContent;
    
    // Show loading state
    uploadButton.disabled = true;
    uploadButton.innerHTML = '<span class="spinner"></span> Uploading...';
    
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
            showToast('🎶💫 Uploaded to Spotify!');
        } else {
            alert('Failed to upload image to Spotify. Please try again.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while uploading the image. Please try again.');
    })
    .finally(() => {
        // Reset button state
        uploadButton.disabled = false;
        uploadButton.textContent = originalText;
    });
}

function downloadImageDirectly(imageUrl) {
    // Handle base64 data URLs
    if (imageUrl.startsWith('data:image/')) {
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = imageUrl;
        a.download = 'playlist_cover.png';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    } else {
        // Handle regular URLs
        const proxyUrl = `/proxy_image?url=${encodeURIComponent(imageUrl)}`;
        fetch(proxyUrl)
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
}

function showToast(message) {
    // Create toast element
    const toast = document.createElement('div');
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%) translateY(-100%);
        background: #1db954;
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        font-size: 16px;
        font-weight: bold;
        z-index: 1000;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        transition: transform 0.3s ease;
    `;
    
    document.body.appendChild(toast);
    
    // Show toast (slide down from top)
    setTimeout(() => {
        toast.style.transform = 'translateX(-50%) translateY(0)';
    }, 100);
    
    // Hide toast after 3 seconds (slide back up)
    setTimeout(() => {
        toast.style.transform = 'translateX(-50%) translateY(-100%)';
        setTimeout(() => {
            if (toast.parentNode) {
                document.body.removeChild(toast);
            }
        }, 300);
    }, 3000);
}