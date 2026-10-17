// BEGIN: prototype.intelligence.modal-assistance
(() => {
  'use strict';

  const ROOT_SELECTOR = '[role="dialog"][aria-modal="true"]';
  const DATA_URL =
    '/static/data/prototype-historical-evidence.json?v=36846c99ee92507a';

  const STOP = new Set([
    'ticket','support','customer','request','please','thank',
    'about','with','your','this','that','from','have',
    'historical','recorded','simulation','assistant','reply',
    'issue','problem','details','information','message'
  ]);

  let evidence = null;
  let evidenceError = false;

  const make = (tag, text, cls) => {
    const e = document.createElement(tag);
    if (text != null) e.textContent = text;
    if (cls) e.className = cls;
    return e;
  };

  function words(text) {
    return new Set(
      (String(text || '').toLowerCase()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .match(/[a-z]{4,}/g) || [])
        .filter(w => !STOP.has(w))
    );
  }

  function context(dialog) {
    // Use the ticket heading and the original request when present.
    // Do not analyze simulated AI replies as customer evidence.
    const headings = Array.from(
      dialog.querySelectorAll('h1,h2,h3,h4')
    );

    const title = headings.find(el =>
      /ticket\s*#\s*\d+/i.test(el.textContent || '')
    );

    if (!title) return null;

    const number = (title.textContent || '')
      .match(/ticket\s*#\s*(\d+)/i);

    if (!number) return null;

    const request = Array.from(dialog.querySelectorAll(
      'section,article,div'
    )).filter(el => {
      const first = el.firstElementChild;
      return first && /customer request/i.test(
        (first.textContent || '').trim()
      );
    }).sort((a,b) =>
      a.textContent.length - b.textContent.length
    )[0];

    const requestText = request
      ? (request.textContent || '').slice(0, 2500)
      : '';

    return {
      id: number[1],
      title: (title.textContent || '').trim(),
      heading: title,
      text: [title.textContent, requestText].join(' ')
    };
  }

  async function getEvidence() {
    if (evidence) return evidence;
    if (evidenceError) return null;

    try {
      const response = await fetch(DATA_URL, {
        cache: 'no-store'
      });

      if (!response.ok) throw new Error('Evidence unavailable');

      const data = await response.json();

      if (
        data.schema !== 'aimaster.historical-evidence.v1' ||
        !data.dataset1 ||
        !data.dataset2 ||
        !data.dataset1.ticket_types ||
        !data.dataset2.categories
      ) throw new Error('Invalid evidence schema');

      evidence = data;
      return evidence;
    } catch (error) {
      evidenceError = true;
      console.warn('Modal AI Assistance:', error);
      return null;
    }
  }

  function evaluate(info, data) {
    const tokens = words(info.text);

    const categories = Object.entries(
      data.dataset2.categories
    ).map(([name, entry]) => {
      const matched = entry.terms.filter(t =>
        tokens.has(t.word)
      );
      return {
        name,
        documents: entry.documents,
        matched,
        weight: matched.reduce(
          (sum, t) => sum + t.weight, 0
        )
      };
    }).sort((a,b) => b.weight - a.weight);

    const top = categories[0];
    const second = categories[1];

    const sufficient = !!(
      top &&
      top.matched.length >= 2 &&
      top.weight > 0 &&
      (!second || top.weight >= second.weight * 1.35)
    );

    // Dataset 1 association requires an exact recognized type
    // in the ticket heading, not a guessed correspondence.
    const title = info.title.toLowerCase();

    const types = Object.entries(
      data.dataset1.ticket_types
    );

    const historical = types.find(([type]) =>
      title.includes(type.toLowerCase())
    ) || null;

    return { top, sufficient, historical };
  }

  function showAnalysis(panel, info, data) {
    const result = evaluate(info, data);
    panel.replaceChildren();

    panel.append(
      make('h4', 'Historical AI Assistance'),
      make('p',
        'Evidence-based rule analysis · Human review required. ' +
        'No LLM connected; no action executed.',
        'pc-modal-ai-note'
      ),
      make('h5', 'Dataset 2 · Classification')
    );

    if (result.sufficient) {
      panel.append(
        make('p',
          'Suggested category: ' + result.top.name +
          ' · Historical reference: ' +
          result.top.documents + ' documents.'
        ),
        make('p',
          'Matched terms: ' +
          result.top.matched.slice(0, 8)
            .map(t => t.word).join(', ')
        )
      );
    } else {
      panel.append(make('p',
        'Insufficient evidence to suggest a category.'
      ));
    }

    panel.append(make('h5', 'Dataset 1 · Priority evidence'));

    if (result.historical) {
      const [type, record] = result.historical;
      const distribution = Object.entries(record.priorities)
        .sort((a,b) => b[1] - a[1])
        .map(([priority, n]) =>
          priority + ': ' + n + ' (' +
          (100*n/record.count).toFixed(1) + '%)'
        ).join(' · ');

      panel.append(make('p',
        type + ' · ' + record.count +
        ' historical records · ' + distribution
      ));
    } else {
      panel.append(make('p',
        'No exact historical ticket-type match. ' +
        'No priority is automatically recommended.'
      ));
    }

    panel.append(
      make('h5', 'Suggested next step'),
      make('p',
        'Review the original request, verify the customer ' +
        'context and determine whether additional evidence ' +
        'or human authorization is needed before responding.'
      ),
      make('p',
        'Sources: Dataset 1 (' +
        data.dataset1.records.toLocaleString() +
        ' records) and Dataset 2 (' +
        data.dataset2.records.toLocaleString() +
        ' documents). Historical frequencies are not ' +
        'confidence scores or SLA measurements.',
        'pc-modal-ai-note'
      )
    );
  }

  function enhance(dialog) {
    if (dialog.querySelector('[data-modal-ai-owner]')) return;

    const info = context(dialog);
    if (!info) return;

    const section = make('div', null, 'pc-modal-ai-section');
    section.dataset.modalAiOwner = 'prototype.intelligence.modal-assistance';

    const button = make('button',
      'AI Assistance',
      'pc-modal-ai-button'
    );
    button.type = 'button';
    button.setAttribute('aria-expanded', 'false');

    const panel = make('div', null, 'pc-modal-ai-panel');
    panel.hidden = true;
    panel.setAttribute('aria-label', 'Historical AI Assistance');

    button.addEventListener('click', async () => {
      const opening = panel.hidden;

      panel.hidden = !opening;
      button.setAttribute(
        'aria-expanded', String(opening)
      );

      if (!opening) return;

      panel.replaceChildren(
        make('p', 'Loading historical evidence...')
      );

      const data = await getEvidence();
      if (!section.isConnected || panel.hidden) return;

      if (!data) {
        panel.replaceChildren(
          make('p',
            'Historical evidence unavailable. ' +
            'No recommendation can be made.'
          )
        );
        return;
      }

      // Re-read the current ticket, not stale modal content.
      const current = context(dialog);
      if (!current || current.id !== info.id) {
        panel.replaceChildren(
          make('p','Ticket context unavailable.')
        );
        return;
      }

      showAnalysis(panel, current, data);
    });

    section.append(button, panel);

    // OWNER: prototype.intelligence.modal-placement
    // BEGIN: prototype.intelligence.modal-placement
    // Use a dedicated band after the modal header.
    // Preserve the ticket title, close button and original handlers.
    const headerChild = Array.from(dialog.children).find(
      child => child === info.heading ||
        child.contains(info.heading)
    );

    if (!headerChild) return;

    section.classList.add('pc-modal-ai-band');

    // Existing modal styles must not turn the button into
    // an absolutely positioned or transparent header control.
    section.style.setProperty('display', 'block', 'important');
    section.style.setProperty('position', 'relative', 'important');
    section.style.setProperty('margin', '0', 'important');
    section.style.setProperty('padding', '12px 20px', 'important');
    section.style.setProperty('background', '#edf3ff', 'important');
    section.style.setProperty(
      'border-bottom', '1px solid #ccd9ee', 'important'
    );

    button.style.setProperty('display', 'inline-flex', 'important');
    button.style.setProperty('position', 'static', 'important');
    button.style.setProperty('width', 'auto', 'important');
    button.style.setProperty('height', 'auto', 'important');
    button.style.setProperty('min-height', '40px', 'important');
    button.style.setProperty('margin', '0', 'important');
    button.style.setProperty('padding', '10px 18px', 'important');
    button.style.setProperty('background', '#3159cd', 'important');
    button.style.setProperty('color', '#ffffff', 'important');
    button.style.setProperty(
      'border', '1px solid #3159cd', 'important'
    );
    button.style.setProperty('border-radius', '9px', 'important');
    button.style.setProperty('font-size', '13px', 'important');
    button.style.setProperty('font-weight', '700', 'important');
    button.style.setProperty('line-height', '1.4', 'important');
    button.style.setProperty('opacity', '1', 'important');
    button.style.setProperty('visibility', 'visible', 'important');
    button.style.setProperty('transform', 'none', 'important');
    button.style.setProperty('cursor', 'pointer', 'important');

    headerChild.after(section);
    // END: prototype.intelligence.modal-placement
  }

  function scan() {
    document.querySelectorAll(ROOT_SELECTOR).forEach(enhance);
  }

  let queued = false;

  function queueScan() {
    if (queued) return;
    queued = true;

    queueMicrotask(() => {
      queued = false;
      scan();
    });
  }

  function init() {
    scan();

    // Observe additions only; ignore text and attribute updates.
    new MutationObserver(queueScan).observe(document.body, {
      childList: true,
      subtree: true
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, {
      once: true
    });
  } else {
    init();
  }
})();
// END: prototype.intelligence.modal-assistance
