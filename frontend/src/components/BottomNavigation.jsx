import React from 'react';
import { Image, Search, FolderHeart, Heart } from 'lucide-react';

export function BottomNavigation({ activeTab, setActiveTab }) {
  return (
    <nav className="mobile-bottom-bar">
      <button
        type="button"
        className={`nav-btn-mobile ${activeTab === 'photos' ? 'active' : ''}`}
        onClick={() => setActiveTab('photos')}
      >
        <div className="nav-icon-box">
          <Image size={20} />
        </div>
        <span>Photos</span>
      </button>

      <button
        type="button"
        className={`nav-btn-mobile ${activeTab === 'search' ? 'active' : ''}`}
        onClick={() => setActiveTab('search')}
      >
        <div className="nav-icon-box">
          <Search size={20} />
        </div>
        <span>Search</span>
      </button>

      <button
        type="button"
        className={`nav-btn-mobile ${activeTab === 'albums' ? 'active' : ''}`}
        onClick={() => setActiveTab('albums')}
      >
        <div className="nav-icon-box">
          <FolderHeart size={20} />
        </div>
        <span>Albums</span>
      </button>

      <button
        type="button"
        className={`nav-btn-mobile ${activeTab === 'favorites' ? 'active' : ''}`}
        onClick={() => setActiveTab('favorites')}
      >
        <div className="nav-icon-box">
          <Heart size={20} />
        </div>
        <span>Favorites</span>
      </button>
    </nav>
  );
}
