import React, { useState, useEffect } from 'react';
import { Header } from './Header';
import { BottomNavigation } from './BottomNavigation';
import { SearchPage } from '../pages/SearchPage';
import { PhotosPage } from '../pages/PhotosPage';
import { AlbumsPage } from '../pages/AlbumsPage';
import { FavoritesPage } from '../pages/FavoritesPage';

function getInitialTab() {
  if (typeof window !== 'undefined') {
    const path = (window.location.pathname || '').toLowerCase();
    const hash = (window.location.hash || '').toLowerCase();
    if (path.includes('/search') || hash.includes('search')) {
      return 'search';
    }
    if (path.includes('/albums') || hash.includes('albums')) {
      return 'albums';
    }
    if (path.includes('/favorites') || hash.includes('favorites')) {
      return 'favorites';
    }
    if (path.includes('/photos') || hash.includes('photos')) {
      return 'photos';
    }
  }
  // Default launch experience when visiting / is Photos/Home
  return 'photos';
}

export function AppShell() {
  const [activeTab, setActiveTab] = useState(getInitialTab);

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    if (typeof window !== 'undefined' && window.history) {
      const currentPath = window.location.pathname || '/';
      const targetPath = `/${tab}`;
      if (currentPath !== targetPath) {
        window.history.pushState(null, '', targetPath);
      }
    }
  };

  useEffect(() => {
    const onPopState = () => {
      setActiveTab(getInitialTab());
    };
    window.addEventListener('popstate', onPopState);
    return () => window.removeEventListener('popstate', onPopState);
  }, []);

  return (
    <div className="desktop-viewport-wrapper">
      <div className="mobile-app-canvas">
        <Header />
        
        <div className="mobile-body-scroll">
          {activeTab === 'search' && <SearchPage />}
          {activeTab === 'photos' && <PhotosPage />}
          {activeTab === 'albums' && <AlbumsPage />}
          {activeTab === 'favorites' && <FavoritesPage />}
        </div>

        <BottomNavigation activeTab={activeTab} setActiveTab={handleTabChange} />
      </div>
    </div>
  );
}
