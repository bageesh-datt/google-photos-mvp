import React, { useState } from 'react';
import { SearchBar } from '../components/SearchBar';
import { MemoryInput } from '../components/MemoryInput';
import { ClueChips } from '../components/ClueChips';
import { ResultsGrid } from '../components/ResultsGrid';
import { RefinementPanel } from '../components/RefinementPanel';
import { PhotoDetailModal } from '../components/PhotoDetailModal';
import { MatchExplanation } from '../components/MatchExplanation';
import { SuccessBanner } from '../components/SuccessBanner';
import { EmptyState } from '../components/EmptyState';
import { searchPhotos, refinePhotos, confirmPhoto, getErrorMessage } from '../services/mvpApi';

export function SearchPage() {
  const [query, setQuery] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [attemptNumber, setAttemptNumber] = useState(1);
  const [clues, setClues] = useState(null);
  const [results, setResults] = useState([]);
  const [refinements, setRefinements] = useState([]);
  const [resultStatus, setResultStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [requestSeq, setRequestSeq] = useState(0);
  
  const [selectedPhotoModal, setSelectedPhotoModal] = useState(null);
  const [whyMatchedPhoto, setWhyMatchedPhoto] = useState(null);
  const [confirmedPhoto, setConfirmedPhoto] = useState(null);

  const handleExecuteSearch = async (userQuery) => {
    if (!userQuery || !userQuery.trim()) return;
    
    const currentSeq = requestSeq + 1;
    setRequestSeq(currentSeq);
    
    setQuery(userQuery);
    setIsLoading(true);
    setError(null);
    setConfirmedPhoto(null);

    // Reset previous search session state for fresh query
    setClues(null);
    setResults([]);
    setRefinements([]);
    setResultStatus(null);
    setSessionId(null);
    setAttemptNumber(1);

    try {
      const data = await searchPhotos(userQuery);
      // Race condition check: only process if this is still the latest request
      setRequestSeq((latestSeq) => {
        if (latestSeq === currentSeq) {
          setSessionId(data.session_id);
          setAttemptNumber(data.attempt_number);
          setClues(data.clues);
          setResults(data.results);
          setRefinements(data.refinements);
          setResultStatus(data.result_status);
        }
        return latestSeq;
      });
    } catch (err) {
      console.error('Search error:', err);
      setError(getErrorMessage(err, 'Search'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectRefinement = async (option) => {
    if (!sessionId) return;
    setIsLoading(true);
    setError(null);

    try {
      let payloadClues = null;
      if (option.payload && option.payload.field) {
        const field = option.payload.field;
        const val = option.payload.value;
        payloadClues = { ...clues };

        if (field === 'people' && val) {
          payloadClues.people = [...(clues.people || []), val];
        } else if (field === 'location' && val) {
          payloadClues.location = [...(clues.location || []), val];
        } else if (field === 'approximate_date' && val) {
          payloadClues.approximate_date = val;
        } else if (field === 'ocr_text' && val) {
          payloadClues.ocr_text = [...(clues.ocr_text || []), ...val.split(' ')];
        }
      }

      const data = await refinePhotos(sessionId, option.id, payloadClues);
      setAttemptNumber(data.attempt_number);
      setClues(data.clues);
      setResults(data.results);
      setRefinements(data.refinements);
      setResultStatus(data.result_status);
    } catch (err) {
      console.error('Refinement error:', err);
      setError(getErrorMessage(err, 'Refinement'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleRemoveClue = async (chip) => {
    if (!clues || !sessionId) return;
    setIsLoading(true);

    const updated = { ...clues };
    if (chip.type === 'approximate_date') {
      updated.approximate_date = null;
    } else if (chip.type === 'location') {
      updated.location = (clues.location || []).filter((l) => l !== chip.value);
    } else if (chip.type === 'people') {
      updated.people = (clues.people || []).filter((p) => p !== chip.value);
    } else if (chip.type === 'people_count_bucket') {
      updated.people_count_bucket = null;
    } else if (chip.type === 'event') {
      updated.event = (clues.event || []).filter((e) => e !== chip.value);
    } else if (chip.type === 'objects') {
      updated.objects = (clues.objects || []).filter((o) => o !== chip.value);
    } else if (chip.type === 'clothing') {
      updated.clothing = (clues.clothing || []).filter((c) => c !== chip.value);
      updated.objects = (clues.objects || []).filter((o) => o !== chip.value);
    } else if (chip.type === 'colors') {
      updated.colors = (clues.colors || []).filter((c) => c !== chip.value);
    } else if (chip.type === 'animals') {
      updated.animals = (clues.animals || []).filter((a) => a !== chip.value);
      updated.objects = (clues.objects || []).filter((o) => o !== chip.value);
    } else if (chip.type === 'activities') {
      updated.activities = (clues.activities || []).filter((a) => a !== chip.value);
    } else if (chip.type === 'spatial_relations') {
      updated.spatial_relations = (clues.spatial_relations || []).filter((s) => s !== chip.value);
    } else if (chip.type === 'environment') {
      updated.environment = null;
    } else if (chip.type === 'ocr_text') {
      updated.ocr_text = (clues.ocr_text || []).filter((t) => t !== chip.value);
    }

    try {
      const data = await refinePhotos(sessionId, 'remove_clue', updated);
      setAttemptNumber(data.attempt_number);
      setClues(data.clues);
      setResults(data.results);
      setRefinements(data.refinements);
      setResultStatus(data.result_status);
    } catch (err) {
      console.error('Clue remove error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleConfirmPhoto = async (photo) => {
    if (sessionId) {
      try {
        await confirmPhoto(sessionId, photo.photo_id);
      } catch (err) {
        console.error('Confirm error:', err);
      }
    }
    setConfirmedPhoto(photo);
    setSelectedPhotoModal(null);
  };

  const handleReset = () => {
    setQuery('');
    setSessionId(null);
    setAttemptNumber(1);
    setClues(null);
    setResults([]);
    setRefinements([]);
    setResultStatus(null);
    setConfirmedPhoto(null);
  };

  return (
    <div>
      <div className="search-section-mobile">
        <h1 className="search-title-mobile">Search your photos</h1>

        <SearchBar
          onSearch={handleExecuteSearch}
          isLoading={isLoading}
          initialQuery={query}
        />

        <MemoryInput onSelectPrompt={handleExecuteSearch} />
      </div>

      {error && (
        <div style={{ padding: 12, background: '#fee2e2', color: '#dc2626', borderRadius: 12, marginBottom: 16, fontSize: 12, fontWeight: 500 }}>
          ⚠️ {error}
        </div>
      )}

      {confirmedPhoto && (
        <SuccessBanner
          selectedPhoto={confirmedPhoto}
          attemptNumber={attemptNumber}
          onReset={handleReset}
        />
      )}

      {clues && (
        <ClueChips
          clues={clues}
          onRemoveClue={handleRemoveClue}
        />
      )}

      {resultStatus === 'zero_matches' ? (
        <EmptyState query={query} onTrySample={handleExecuteSearch} />
      ) : (
        <>
          <ResultsGrid
            results={results}
            onSelectPhoto={(p) => {
              if (!p || !p.photo_id) {
                console.error('[SearchPage] Invalid photo selected', p);
                return;
              }
              console.log(`[SearchPage onSelectPhoto] photo_id=${p.photo_id} filename=${p.filename} image_url=${p.image_url}`);
              setSelectedPhotoModal(p);
            }}
            onToggleWhyMatched={(p) => setWhyMatchedPhoto(p)}
          />

          <RefinementPanel
            refinements={refinements}
            onSelectRefinement={handleSelectRefinement}
          />
        </>
      )}

      {whyMatchedPhoto && (
        <MatchExplanation
          photo={whyMatchedPhoto}
          onClose={() => setWhyMatchedPhoto(null)}
        />
      )}

      {selectedPhotoModal && (
        <PhotoDetailModal
          photo={selectedPhotoModal}
          onClose={() => setSelectedPhotoModal(null)}
          onConfirmPhoto={handleConfirmPhoto}
        />
      )}
    </div>
  );
}
