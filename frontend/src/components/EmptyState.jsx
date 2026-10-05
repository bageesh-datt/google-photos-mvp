import React from 'react';
import { SearchX, RefreshCw } from 'lucide-react';

export function EmptyState({ query, onTrySample }) {
  return (
    <div style={{ textAlign: 'center', padding: '48px 24px', background: 'white', borderRadius: 24, boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
      <div style={{ width: 64, height: 64, borderRadius: '50%', background: '#fee2e2', color: '#ef4444', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px auto' }}>
        <SearchX size={32} />
      </div>
      <h3 style={{ fontSize: 20, color: '#1f2937', marginBottom: 8 }}>
        We couldn't find a strong match for "{query}"
      </h3>
      <p style={{ fontSize: 14, color: '#6b7280', maxWidth: 460, margin: '0 auto 24px auto', lineHeight: 1.5 }}>
        Try adding another detail about what you remember (such as a place, year, person, or visible text), or broaden your search criteria.
      </p>
    </div>
  );
}
