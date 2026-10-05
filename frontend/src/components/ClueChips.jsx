import React from 'react';
import { Calendar, MapPin, Users, Sparkles, Tag, FileText, Palette, Activity, Compass, Sun, X } from 'lucide-react';

export function ClueChips({ clues, onRemoveClue }) {
  if (!clues) return null;

  const chips = [];
  const seenLabels = new Set();

  const addChip = (id, type, rawLabel, value, icon) => {
    if (!rawLabel || !rawLabel.trim()) return;
    const formatted = rawLabel.trim().charAt(0).toUpperCase() + rawLabel.trim().slice(1);
    const key = `${type}:${formatted.toLowerCase()}`;
    if (seenLabels.has(key)) return;
    seenLabels.add(key);
    chips.push({ id, type, label: formatted, value, icon });
  };

  if (clues.approximate_date) {
    addChip('approximate_date', 'approximate_date', clues.approximate_date, clues.approximate_date, Calendar);
  }

  (clues.location || []).forEach((loc, idx) => {
    addChip(`location_${idx}`, 'location', loc, loc, MapPin);
  });

  (clues.people || []).forEach((p, idx) => {
    addChip(`people_${idx}`, 'people', p, p, Users);
  });

  if ((!clues.people || clues.people.length === 0) && clues.people_count_bucket) {
    const bucketLabels = {
      crowd: 'Crowd',
      large_group: 'Large Group',
      medium_group: 'Medium Group',
      small_group: 'Small Group',
      two: 'Couple / 2 People',
      one: 'Individual',
    };
    const bLabel = bucketLabels[clues.people_count_bucket] || clues.people_count_bucket;
    addChip('people_group', 'people_count_bucket', bLabel, clues.people_count_bucket, Users);
  }

  (clues.event || []).forEach((ev, idx) => {
    addChip(`event_${idx}`, 'event', ev, ev, Sparkles);
  });

  (clues.animals || []).forEach((anim, idx) => {
    addChip(`animals_${idx}`, 'animals', anim, anim, Tag);
  });

  (clues.clothing || []).forEach((c, idx) => {
    addChip(`clothing_${idx}`, 'clothing', c, c, Tag);
  });

  (clues.colors || []).forEach((col, idx) => {
    addChip(`colors_${idx}`, 'colors', col, col, Palette);
  });

  (clues.objects || []).forEach((obj, idx) => {
    addChip(`objects_${idx}`, 'objects', obj, obj, Tag);
  });

  (clues.activities || []).forEach((act, idx) => {
    addChip(`activities_${idx}`, 'activities', act, act, Activity);
  });

  (clues.spatial_relations || []).forEach((sr, idx) => {
    addChip(`spatial_${idx}`, 'spatial_relations', sr, sr, Compass);
  });

  if (clues.environment) {
    addChip('environment', 'environment', clues.environment, clues.environment, Sun);
  }

  (clues.ocr_text || []).forEach((txt, idx) => {
    if (txt && txt.trim()) {
      chips.push({
        id: `ocr_${idx}`,
        type: 'ocr_text',
        label: `Text: ${txt.trim()}`,
        value: txt,
        icon: FileText
      });
    }
  });

  if (chips.length === 0) return null;

  return (
    <div className="clues-box-mobile">
      <div className="clues-label-mobile">
        <span>🧠 Parsed Memory Clues:</span>
        <span style={{ fontSize: 10, background: '#e2e8f0', color: '#475569', padding: '1px 6px', borderRadius: 8 }}>
          {clues.is_fallback ? 'Fallback' : 'Groq AI'}
        </span>
      </div>
      <div className="clues-wrapper-mobile">
        {chips.map((chip) => {
          const Icon = chip.icon;
          return (
            <span key={chip.id} className="clue-chip-mobile">
              <Icon size={12} />
              <span>{chip.label}</span>
              {onRemoveClue && (
                <button
                  type="button"
                  className="clue-remove-mobile"
                  onClick={() => onRemoveClue(chip)}
                  title="Remove clue"
                >
                  <X size={10} />
                </button>
              )}
            </span>
          );
        })}
      </div>
    </div>
  );
}

