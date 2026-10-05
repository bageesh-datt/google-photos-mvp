import React from 'react';
import { CheckCircle2 } from 'lucide-react';

export function SuccessBanner({ selectedPhoto, attemptNumber, onReset }) {
  if (!selectedPhoto) return null;

  return (
    <div className="success-toast-mobile">
      <CheckCircle2 size={24} color="#22c55e" style={{ flexShrink: 0 }} />
      <div style={{ flex: 1 }}>
        <h4 style={{ fontSize: 13, fontWeight: 700, margin: 0 }}>
          🎉 Photo Found Successfully!
        </h4>
        <p style={{ fontSize: 11, margin: '2px 0 0 0', opacity: 0.9 }}>
          Retrieved photo <strong>{selectedPhoto.photo_id}</strong> in <strong>{attemptNumber}</strong> attempt{attemptNumber > 1 ? 's' : ''}!
        </p>
      </div>
      <button
        type="button"
        onClick={onReset}
        style={{
          background: '#16a34a',
          color: 'white',
          border: 'none',
          borderRadius: 14,
          padding: '6px 12px',
          fontWeight: 600,
          cursor: 'pointer',
          fontSize: 11,
          flexShrink: 0
        }}
      >
        New Search
      </button>
    </div>
  );
}
