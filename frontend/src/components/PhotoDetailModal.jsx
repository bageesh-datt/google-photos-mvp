import React from 'react';
import { ArrowLeft, Check, Calendar, MapPin, Tag, ShieldCheck } from 'lucide-react';

export function PhotoDetailModal({ photo, onClose, onConfirmPhoto }) {
  if (!photo || !photo.photo_id) {
    console.error('[PhotoDetailModal] Received invalid or missing photo object', photo);
    return null;
  }

  const photoId = photo.photo_id;
  const filename = photo.filename || `${photoId}.jpg`;
  const imageUrl = photo.image_url || `/photos/${filename}`;

  console.log(`[PhotoIdentity ModalRender] photo_id=${photoId} filename=${filename} image_url=${imageUrl}`);

  const locationText = typeof photo.location === 'object' && photo.location
    ? (photo.location.landmark ? `${photo.location.landmark}, ${photo.location.city}` : `${photo.location.city}, ${photo.location.country}`)
    : (photo.location || '');

  return (
    <div className="mobile-detail-modal" data-testid="photo-detail-modal">
      <div className="detail-top-bar">
        <button type="button" className="detail-back-btn" onClick={onClose} data-testid="modal-back-btn">
          <ArrowLeft size={20} />
          <span>Back</span>
        </button>
        {typeof photo.score === 'number' && photo.score > 0 && (
          <span style={{ fontSize: 13, fontWeight: 700, color: '#4ade80', display: 'flex', alignItems: 'center', gap: 4 }}>
            <ShieldCheck size={16} />
            {Math.round(photo.score * 100)}% Match
          </span>
        )}
      </div>

      <div className="detail-photo-box">
        <img
          src={imageUrl}
          alt={photo.event || filename || photoId}
          className="detail-photo-img"
          data-testid="modal-photo-img"
          onError={(e) => {
            console.error(`[PhotoDetailModal] Failed to load image: ${imageUrl}`);
            // Safe unavailable state, DO NOT swap with another photo image!
            e.target.style.display = 'none';
          }}
        />
      </div>

      <div className="detail-bottom-sheet">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
          <h2 style={{ fontSize: 18, fontWeight: 700, color: '#1f2937' }} data-testid="modal-photo-title">
            {photo.event || photo.album || 'Photo Memory'}
          </h2>
          <span style={{ fontSize: 11, background: '#e8f0fe', color: '#1a73e8', padding: '2px 8px', borderRadius: 10, fontWeight: 700 }} data-testid="modal-photo-id">
            {photoId}
          </span>
        </div>

        {photo.description && (
          <p style={{ fontSize: 12, color: '#6b7280', marginBottom: 12, lineHeight: 1.4 }}>
            {photo.description}
          </p>
        )}

        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, fontSize: 12, color: '#374151', borderTop: '1px solid #f3f4f6', paddingTop: 10 }}>
          {photo.date && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
              <Calendar size={14} color="#6b7280" />
              <span>{photo.date}</span>
            </div>
          )}

          {locationText && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
              <MapPin size={14} color="#6b7280" />
              <span>{locationText}</span>
            </div>
          )}

          {photo.people && photo.people.length > 0 && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
              <Tag size={14} color="#6b7280" />
              <span>{photo.people.join(', ')}</span>
            </div>
          )}
        </div>

        {onConfirmPhoto && (
          <button
            type="button"
            className="confirm-photo-btn-mobile"
            onClick={() => onConfirmPhoto(photo)}
            data-testid="confirm-photo-btn"
          >
            <Check size={18} />
            <span>This is the photo I wanted!</span>
          </button>
        )}
      </div>
    </div>
  );
}

