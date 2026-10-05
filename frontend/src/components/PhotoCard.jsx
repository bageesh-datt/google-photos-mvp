import React from 'react';
import { Info } from 'lucide-react';

export function PhotoCard({ result, onSelectPhoto, onToggleWhyMatched }) {
  if (!result || !result.photo_id) {
    console.error('[PhotoCard] Invalid or missing result object', result);
    return null;
  }

  const matchPercent = result && result.score != null ? Math.round(result.score * 100) : null;
  const photoId = result.photo_id;
  const filename = result.filename || `${photoId}.jpg`;
  const imageUrl = result.image_url || `/photos/${filename}`;

  const canonicalItem = {
    ...result,
    photo_id: photoId,
    filename: filename,
    image_url: imageUrl,
  };

  const handleCardClick = () => {
    console.log(`[PhotoIdentity CardClick] photo_id=${photoId} filename=${filename} image_url=${imageUrl}`);
    if (onSelectPhoto) {
      onSelectPhoto(canonicalItem);
    }
  };

  const handleWhyClick = (e) => {
    e.stopPropagation();
    if (onToggleWhyMatched) {
      onToggleWhyMatched(result);
    }
  };

  const getCity = (loc) => {
    if (!loc) return '';
    if (typeof loc === 'string') return loc.split(',')[0];
    return loc.city || loc.landmark || loc.country || '';
  };

  return (
    <div
      className="mobile-photo-card"
      onClick={handleCardClick}
      data-testid={`photo-card-${photoId}`}
    >
      <div className="mobile-card-thumb-box">
        <img
          src={imageUrl}
          alt={result.event || result.filename || photoId}
          className="mobile-card-thumb"
          loading="lazy"
          data-testid={`photo-card-img-${photoId}`}
        />
        {matchPercent != null && matchPercent > 0 && (
          <div className="mobile-score-tag">
            {matchPercent}%
          </div>
        )}
      </div>

      <div className="mobile-card-details">
        <div className="mobile-card-title">{result.event || result.album || result.filename}</div>
        <div className="mobile-card-sub">
          {result.year ? `${result.year} • ` : ''}{getCity(result.location)}
        </div>

        {onToggleWhyMatched && (
          <button
            type="button"
            className="why-matched-btn-mobile"
            onClick={handleWhyClick}
          >
            <span>Why matched</span>
            <Info size={10} color="#1a73e8" />
          </button>
        )}
      </div>
    </div>
  );
}

