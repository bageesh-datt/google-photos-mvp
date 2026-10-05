import React from 'react';
import { PhotoCard } from './PhotoCard';

export function ResultsGrid({ results, onSelectPhoto, onToggleWhyMatched }) {
  if (!results || results.length === 0) return null;

  return (
    <div>
      <div style={{ fontSize: 13, fontWeight: 700, color: '#374151', marginBottom: 8, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span>Candidate Photos</span>
        <span style={{ fontSize: 11, fontWeight: 400, color: '#6b7280' }}>50 photos dataset</span>
      </div>
      <div className="mobile-photo-grid">
        {results.map((item) => (
          <PhotoCard
            key={item.photo_id}
            result={item}
            onSelectPhoto={onSelectPhoto}
            onToggleWhyMatched={onToggleWhyMatched}
          />
        ))}
      </div>
    </div>
  );
}
