import React, { useEffect, useState } from 'react';
import { getAllPhotos } from '../services/mvpApi';
import { FolderHeart } from 'lucide-react';
import { AlbumDetail } from '../components/AlbumDetail';

export function AlbumsPage() {
  const [albums, setAlbums] = useState({});
  const [selectedAlbum, setSelectedAlbum] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    getAllPhotos().then((photos) => {
      const grouped = {};
      photos.forEach((p) => {
        const albumName = p.album || 'Miscellaneous';
        if (!grouped[albumName]) {
          grouped[albumName] = [];
        }
        grouped[albumName].push(p);
      });
      setAlbums(grouped);
      setIsLoading(false);
    });
  }, []);

  if (isLoading) {
    return <div style={{ textAlign: 'center', padding: 40, color: '#6b7280' }}>Loading albums...</div>;
  }

  if (selectedAlbum && albums[selectedAlbum]) {
    return (
      <AlbumDetail
        albumName={selectedAlbum}
        photos={albums[selectedAlbum]}
        onBack={() => setSelectedAlbum(null)}
      />
    );
  }

  return (
    <div>
      <div style={{ marginBottom: 20 }}>
        <h2 style={{ fontSize: 24, color: '#202124' }}>Albums & Collections</h2>
        <p style={{ fontSize: 14, color: '#5f6368' }}>Grouped memories across travel, family events, and document scans</p>
      </div>

      <div className="mobile-photo-grid">
        {Object.entries(albums).map(([name, list]) => (
          <div
            key={name}
            style={{
              background: 'white',
              borderRadius: 16,
              overflow: 'hidden',
              boxShadow: 'var(--shadow-card)',
              border: '1px solid #e5e7eb',
              cursor: 'pointer',
              display: 'flex',
              flexDirection: 'column'
            }}
            onClick={() => setSelectedAlbum(name)}
          >
            <div style={{ width: '100%', paddingTop: '75%', position: 'relative', background: '#f3f4f6' }}>
              {list[0] && (
                <img
                  src={list[0].image_url}
                  alt={name}
                  style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', objectFit: 'contain', background: '#f1f3f4', padding: 2 }}
                />
              )}
              <div
                style={{
                  position: 'absolute',
                  bottom: 8,
                  right: 8,
                  background: 'rgba(0,0,0,0.75)',
                  color: 'white',
                  padding: '3px 8px',
                  borderRadius: 10,
                  fontSize: 11,
                  fontWeight: 600
                }}
              >
                {list.length} {list.length === 1 ? 'photo' : 'photos'}
              </div>
            </div>
            <div style={{ padding: 10 }}>
              <h3 style={{ fontSize: 13, fontWeight: 700, color: '#1f2937', marginBottom: 2, display: 'flex', alignItems: 'center', gap: 6, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                <FolderHeart size={14} color="#1a73e8" style={{ flexShrink: 0 }} />
                <span style={{ overflow: 'hidden', textOverflow: 'ellipsis' }}>{name}</span>
              </h3>
              <p style={{ fontSize: 11, color: '#6b7280' }}>
                Latest: {list[0]?.date}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
