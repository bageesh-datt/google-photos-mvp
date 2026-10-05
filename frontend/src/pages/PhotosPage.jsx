import React, { useEffect, useState } from 'react';
import { getAllPhotos } from '../services/mvpApi';
import { PhotoCard } from '../components/PhotoCard';
import { PhotoDetailModal } from '../components/PhotoDetailModal';

export function PhotosPage() {
  const [photos, setPhotos] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedPhoto, setSelectedPhoto] = useState(null);

  useEffect(() => {
    getAllPhotos()
      .then((data) => setPhotos(data))
      .catch((err) => console.error(err))
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading) {
    return <div style={{ textAlign: 'center', padding: 40, color: '#6b7280' }}>Loading photo library...</div>;
  }

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <h2 style={{ fontSize: 22, color: '#202124', fontWeight: 700 }}>Photo Library</h2>
        <p style={{ fontSize: 13, color: '#5f6368' }}>Browse all 50 photos in your demo dataset</p>
      </div>

      <div className="mobile-photo-grid">
        {photos.map((p) => (
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
