document.getElementById("generateImage").addEventListener("click", function () {
    console.log("Button clicked");  // Check if button click is registered

    let playlistId = document.getElementById("generateImage").getAttribute("data-playlist-id");
    console.log("Playlist ID:", playlistId);  // Check the fetched playlistId

    fetch(`/playlists/${playlistId}/generate_image`, { method: 'POST' })
        .then(response => {
            console.log("Server Response:", response);  // Check raw response from the server
            return response.json();
        })
        .then(data => {
            console.log("Response Data:", data);  // Log the response data
            document.getElementById('aiImage').src = data.image_url;
            document.getElementById('aiImage').style.display = 'block';
            document.getElementById('visualDescription').textContent = data.visual_description;
        })
        .catch(error => {
            console.error("Error:", error);
        });
});
