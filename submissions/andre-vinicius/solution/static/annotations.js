const annotationKey = 'foco-opportunity-notes-v1';
const progressOptions = { '': 'Sem status', parado: '⏸️ Parado', andando: '🚶 Andando' };

function readAnnotations(storage) {
  try {
    const value = JSON.parse(storage.getItem(annotationKey) || '{}');
    return value && typeof value === 'object' && !Array.isArray(value) ? value : {};
  } catch { return {}; }
}

function saveAnnotation(storage, id, changes) {
  if (!id) return false;
  const data = readAnnotations(storage);
  const previous = data[id] || {};
  const status = Object.hasOwn(progressOptions, changes.status) ? changes.status : (previous.status || '');
  const note = String(changes.note === undefined ? previous.note || '' : changes.note).slice(0, 2000);
  if (status || note.trim()) data[id] = { status, note };
  else delete data[id];
  try { storage.setItem(annotationKey, JSON.stringify(data)); return true; }
  catch { return false; }
}

if (typeof module !== 'undefined') module.exports = { readAnnotations, saveAnnotation, progressOptions };
