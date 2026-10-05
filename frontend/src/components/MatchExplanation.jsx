import React from 'react';
import { Info, X } from 'lucide-react';

export function MatchExplanation({ photo, onClose }) {
  if (!photo) return null;

  return (
    <div className="bottom-sheet-overlay" onClick={onClose}>
      <div className="bottom-sheet-content" onClick={(e) => e.stopPropagation()}>
        <div className="bottom-sheet-handle" />
        
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
          <div className="bottom-sheet-title" style={{ margin: 0 }}>
            <Info size={18} color="#1a73e8" />
            <span>Why {photo.photo_id} matched ({Math.round(photo.score * 100)}%)</span>
          </div>
          <button
            onClick={onClose}
            style={{ border: 'none', background: 'none', cursor: 'pointer', padding: 4 }}
          >
            <X size={18} color="#6b7280" />
          </button>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          {photo.match_reasons && photo.match_reasons.length > 0 ? (
            photo.match_reasons.map((reason, idx) => (
              <div key={idx} className="reason-pill">
                {reason}
              </div>
            ))
          ) : (
            <div className="reason-pill">
              ✓ Textual context matches album '{photo.album}'
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
