import React from 'react';

const SAMPLE_PROMPTS = [
  { label: 'family beach photo', full: 'family beach photo from Goa around 2022' },
  { label: 'Goa trip 2022', full: 'Goa trip family beach 2022' },
  { label: 'birthday with cousin', full: 'birthday photo with my cousin Rohan' },
  { label: 'document text', full: 'document where passport text is visible' },
  { label: 'pizza restaurant', full: 'pizza photo from a restaurant in Bangalore' },
  { label: 'dog in park', full: 'golden retriever dog playing in Lodhi Garden' }
];

export function MemoryInput({ onSelectPrompt }) {
  return (
    <div className="sample-scroll-wrapper">
      <div className="sample-scroll-title">💡 Try a memory clue:</div>
      <div className="sample-scroll-chips">
        {SAMPLE_PROMPTS.map((item, index) => (
          <button
            key={index}
            className="sample-mobile-chip"
            onClick={() => onSelectPrompt(item.full)}
          >
            "{item.label}"
          </button>
        ))}
      </div>
    </div>
  );
}
