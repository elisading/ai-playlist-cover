import React from 'react';
import { handlePlaylistSelection } from './playlistUtils';

function Playlist({ playlists }) {
    return (
        <div>
            {playlists.map(playlist => (
                <div key={playlist.id}>
                    <img src={playlist.images[0].url} alt={playlist.name} />
                    <h3>{playlist.name}</h3>
                    <button onClick={() => handlePlaylistSelection(playlist.id)}>Select</button>
                </div>
            ))}
        </div>
    );
}

export default Playlist;
