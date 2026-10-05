import React, { useState } from 'react';
import { ArrowLeft, FolderHeart } from 'lucide-react';
import { PhotoCard } from './PhotoCard';
import { PhotoDetailModal } from './PhotoDetailModal';

export function AlbumDetail({ albumName, photos, onBack }) {
  const [selectedPhoto, setSelectedPhoto] = useState(null);

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
        <button
          type="button"
          onClick={onBack}
          style={{
            background: '#f1f3f4',
            border: 'none',
            borderRadius: '50%',
            width: 36,
            height: 36,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
            color: '#3c4043'
          }}
          aria-label="Back to Albums"
        >
          <ArrowLeft size={20} />
        </button>
        <div>
          <h2 style={{ fontSize: 20, fontWeight: 700, color: '#1f2937', display: 'flex', alignItems: 'center', gap: 8 }}>
            <FolderHeart size={20} color="#1a73e8" />
            <span>{albumName}</span>
          </h2>
          <p style={{ fontSize: 13, color: '#6b7280' }}>
            {photos.length} {photos.length === 1 ? 'photo' : 'photos'}
          </p>
        </div>
      </div>

      <div className="mobile-photo-grid">
        {photos.map((photo) => (
          <PhotoCard
            key={photo.photo_id}
            result={photo}
            onSelectPhoto={(p) => setSelectedPhoto(p)}
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
