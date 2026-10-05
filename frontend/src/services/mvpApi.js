const API_BASE = '/api/mvp';

export function getErrorMessage(err, defaultAction = 'Search') {
  if (!err) return `${defaultAction} failed. Please try again.`;
  if (err.name === 'AbortError') {
    return `${defaultAction} request timed out. Please try again.`;
  }
  const msg = String(err.message || err);
  if (msg.includes('Failed to fetch') || msg.includes('NetworkError') || msg.includes('Network Error')) {
    return 'Unable to connect to server. Ensure backend is running.';
  }
  if (msg.includes('status')) {
    return `${defaultAction} failed (${msg}). Please try again.`;
  }
  return msg || `${defaultAction} failed. Please try again.`;
}

export async function searchPhotos(query, sessionId = null) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 25000);
  try {
    const response = await fetch(`${API_BASE}/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, session_id: sessionId }),
      signal: controller.signal
    });
    if (!response.ok) {
      throw new Error(`server returned status ${response.status}`);
    }
    return await response.json();
  } finally {
    clearTimeout(timeoutId);
  }
}

export async function refinePhotos(sessionId, actionId = null, updatedClues = null) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 25000);
  try {
    const response = await fetch(`${API_BASE}/refine`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        action_id: actionId,
        updated_clues: updatedClues
      }),
      signal: controller.signal
    });
    if (!response.ok) {
      throw new Error(`server returned status ${response.status}`);
    }
    return await response.json();
  } finally {
    clearTimeout(timeoutId);
  }
}

export async function getAllPhotos() {
  const response = await fetch(`${API_BASE}/photos`);
  if (!response.ok) {
    throw new Error(`Failed to fetch photos: ${response.status}`);
  }
  return await response.json();
}

export async function getPhotoDetail(photoId) {
  const response = await fetch(`${API_BASE}/photos/${photoId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch photo detail: ${response.status}`);
  }
  return await response.json();
}

export async function confirmPhoto(sessionId, photoId) {
  const response = await fetch(`${API_BASE}/confirm`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      selected_photo_id: photoId
    })
  });
  if (!response.ok) {
    throw new Error(`Failed to confirm photo: ${response.status}`);
  }
  return await response.json();
}
