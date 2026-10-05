import React, { useState, useEffect } from 'react';
import { Search, Sparkles, X } from 'lucide-react';

export function SearchBar({ onSearch, isLoading, initialQuery = '' }) {
  const [query, setQuery] = useState(initialQuery);

  useEffect(() => {
    setQuery(initialQuery);
  }, [initialQuery]);

  const handleSubmit = (e) => {
    if (e) e.preventDefault();
    const trimmed = query.trim();
    if (trimmed && !isLoading) {
      onSearch(trimmed);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="mobile-search-box">
      <Search size={18} color="#6b7280" style={{ marginRight: 8, flexShrink: 0 }} />
      <input
        type="text"
        placeholder="Describe the photo you remember..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        disabled={isLoading}
      />
      {query && (
        <button
          type="button"
          onClick={() => setQuery('')}
          style={{ border: 'none', background: 'none', cursor: 'pointer', padding: 2, display: 'flex', alignItems: 'center' }}
        >
          <X size={16} color="#6b7280" />
        </button>
      )}
      <button
        type="submit"
        className="search-action-btn"
        disabled={isLoading || !query.trim()}
      >
        <Sparkles size={14} />
        <span>{isLoading ? '...' : 'Find'}</span>
      </button>
    </form>
  );
}
