import React, { useEffect, useState } from 'react';
import { getAllPhotos } from '../services/mvpApi';
import { Heart } from 'lucide-react';
import { PhotoCard } from '../components/PhotoCard';
import { PhotoDetailModal } from '../components/PhotoDetailModal';

export function FavoritesPage() {
  const [favorites, setFavorites] = useState([]);
  const [selectedPhoto, setSelectedPhoto] = useState(null);

  useEffect(() => {
    getAllPhotos().then((photos) => {
      setFavorites(photos.filter((p) => p.is_favorite));
    });
  }, []);

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <h2 style={{ fontSize: 22, color: '#202124', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
          <Heart size={22} color="#ea4335" fill="#ea4335" />
          <span>Favorites</span>
        </h2>
        <p style={{ fontSize: 13, color: '#5f6368' }}>Your starred & favorite memories</p>
      </div>

      <div className="mobile-photo-grid">
        {favorites.map((p) => (
          <PhotoCard
            key={p.photo_id}
            result={p}
            onSelectPhoto={(photo) => setSelectedPhoto(photo)}
          />
        ))}
      </div>

      {selectedPhoto && (
        <PhotoDetailModal
          photo={selectedPhoto}
          onClose={() => setSelectedPhoto(null)}
          onConfirmPhoto={() => setSelectedPhoto(null)}
        />
      )}
    </div>
  );
}
