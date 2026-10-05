import React from 'react';
import { HelpCircle, ChevronRight } from 'lucide-react';

export function RefinementPanel({ refinements = [], onSelectRefinement }) {
  if (!refinements || refinements.length === 0) return null;

  return (
    <div className="refinement-box-mobile">
      <div className="refinement-header-mobile">
        <HelpCircle size={16} />
        <span>Not the photo you're looking for?</span>
      </div>
      <div className="refinement-sub-mobile">
        Try one of these guided recovery paths:
      </div>
      <div className="refinement-pills-mobile">
        {refinements.map((option) => (
          <button
            key={option.id}
            className="refinement-pill-btn"
            onClick={() => onSelectRefinement(option)}
          >
            <span>{option.label}</span>
            <ChevronRight size={14} color="#b45309" />
          </button>
        ))}
      </div>
    </div>
  );
}
