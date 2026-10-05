import React from 'react';
import { Sparkles } from 'lucide-react';

export function Header() {
  return (
    <header className="mobile-header">
      <div className="brand-section">
        <div className="brand-icon-mobile">
          <Sparkles size={16} />
        </div>
        <span className="brand-title-mobile">Google Photos</span>
        <span className="brand-badge-mobile">AI Search</span>
      </div>

      <button type="button" className="avatar-btn" title="User Profile">
        U
      </button>
    </header>
  );
}
