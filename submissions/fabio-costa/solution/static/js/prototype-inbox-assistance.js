// BEGIN: prototype.intelligence.inbox-assistance
(() => {
  'use strict';

  const ROOT_ID = 'pc-inbox';
  const OWNER_ID = 'pc-inbox-ai-assistance';
  const URL = '/static/data/prototype-historical-evidence.json?v=36846c99ee92507a';

  let evidencePromise = null;

  const create = (tag, text, className) => {
    const item = document.createElement(tag);
    if (text != null) item.textContent = text;
    if (className) item.className = className;
    return item;
  };

  function normalized(text) {
    return String(text || '').toLowerCase()
      .normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  }

  function words(text) {
    return new Set(normalized(text).match(/[a-z]{4,}/g) || []);
  }

  function findHeading(root) {
    // Tag-independent exact-text lookup, restricted to the Inbox.
    const walker = document.createTreeWalker(
      root, NodeFilter.SHOW_TEXT
    );

    let text;
    while ((text = walker.nextNode())) {
      if (text.textContent.trim() !== 'Ticket Workspace') continue;

      const parent = text.parentElement;
      if (
        parent &&
        !parent.closest('#' + OWNER_ID) &&
        parent.children.length === 0
      ) return parent;
    }

    return null;
  }

  function selectedWorkspace(root, heading) {
    // Walk from the workspace heading toward its detail container.
    // Never use the historical queue as selected-ticket evidence.
    let current = heading.parentElement;

    for (let i = 0; current && i < 6; i++) {
      if (current === root) break;

      const copy = current.cloneNode(true);
      copy.querySelector('#' + OWNER_ID)?.remove();

      const text = copy.textContent || '';

      if (
        /Ticket\s*#\s*\d+/i.test(text) &&
        !/Historical ticket queue/i.test(text)
      ) return current;

      current = current.parentElement;
    }

    return null;
  }

  function context(root, heading) {
    const workspace = selectedWorkspace(root, heading);
    if (!workspace) return null;

    const copy = workspace.cloneNode(true);
    copy.querySelector('#' + OWNER_ID)?.remove();

    const text = copy.textContent || '';
    if (/No ticket selected/i.test(text)) return null;

    const match = text.match(/Ticket\s*#\s*(\d+)/i);
    if (!match) return null;

    const typeNodes = Array.from(
      copy.querySelectorAll('dt,th,label,span,strong,div')
    ).filter(node =>
      node.children.length === 0 &&
      /^Ticket type$/i.test(node.textContent.trim())
    );

    let type = '';

    for (const label of typeNodes) {
      const next = label.nextElementSibling;
      if (next && next.textContent.trim()) {
        type = next.textContent.trim();
        break;
      }

      const parent = label.parentElement;
      if (parent) {
        const siblings = Array.from(parent.children);
        const index = siblings.indexOf(label);
        if (index >= 0 && siblings[index + 1]) {
          type = siblings[index + 1].textContent.trim();
          break;
        }
      }
    }

    return {
      id: match[1],
      type,
      text: text.slice(0, 4500),
      signature: match[1] + '|' + type + '|' + text.slice(0, 800)
    };
  }

  function loadEvidence() {
    if (!evidencePromise) {
      evidencePromise = fetch(URL, {cache: 'no-store'})
        .then(response => {
          if (!response.ok) throw Error('Evidence unavailable');
          return response.json();
        })
        .then(data => {
          if (
            data.schema !== 'aimaster.historical-evidence.v1' ||
            !data.dataset1?.ticket_types ||
            !data.dataset2?.categories
          ) throw Error('Evidence contract invalid');

          return data;
        })
        .catch(error => {
          evidencePromise = null;
          throw error;
        });
    }

    return evidencePromise;
  }

  function analyze(ctx, data) {
    const vocabulary = words(ctx.text);

    const ranking = Object.entries(data.dataset2.categories)
      .map(([category, info]) => {
        const matches = info.terms.filter(term =>
          vocabulary.has(term.word)
        );

        return {
          category,
          matches,
          count: info.documents,
          score: matches.reduce(
            (sum, term) => sum + term.weight, 0
          )
        };
      })
      .sort((a, b) => b.score - a.score);

    const best = ranking[0];
    const runner = ranking[1];

    const sufficient = Boolean(
      best &&
      best.matches.length >= 2 &&
      best.score > 0 &&
      (!runner || best.score >= runner.score * 1.35)
    );

    const historical = Object.entries(data.dataset1.ticket_types)
      .find(([type]) => normalized(type) === normalized(ctx.type));

    return {best, sufficient, historical};
  }

  function render(panel, ctx, data) {
    const result = analyze(ctx, data);
    panel.replaceChildren();

    panel.append(
      create('h4', 'AI Assistance · Ticket #' + ctx.id),
      create('p',
        'Historical evidence · Read-only · No LLM connected · ' +
        'Human approval required.',
        'pc-inbox-ai-note'),
      create('h5', 'Dataset 2 · Classification')
    );

    if (result.sufficient) {
      panel.append(
        create('p',
          'Candidate category: ' + result.best.category +
          ' · ' + result.best.count + ' reference documents'),
        create('p',
          'Matched terms: ' + result.best.matches
            .slice(0, 8).map(t => t.word).join(', '))
      );
    } else {
      panel.append(create(
        'p', 'Insufficient evidence to classify this ticket.'
      ));
    }

    panel.append(create(
      'h5', 'Dataset 1 · Recorded priority distribution'
    ));

    if (result.historical) {
      const [type, record] = result.historical;
      const distribution = Object.entries(record.priorities)
        .sort((a, b) => b[1] - a[1])
        .map(([priority, n]) =>
          priority + ': ' + n + ' (' +
          (100 * n / record.count).toFixed(1) + '%)'
        ).join(' · ');

      panel.append(create(
        'p', type + ' · ' + record.count +
        ' observed tickets · ' + distribution
      ));
    } else {
      panel.append(create(
        'p', 'No verified matching historical ticket type.'
      ));
    }

    panel.append(
      create('h5', 'Suggested next step'),
      create('p',
        'Verify the original customer request, examine the ' +
        'available evidence and request additional context ' +
        'when necessary. No action has been executed.'),
      create('p',
        'Sources: Dataset 1 (' + data.dataset1.records +
        ' records) and Dataset 2 (' + data.dataset2.records +
        ' documents). Frequencies are not confidence scores.',
        'pc-inbox-ai-note')
    );
  }

  function initialize() {
    const root = document.getElementById(ROOT_ID);
    if (!root || root.dataset.inboxAiReady === 'true') return;

    const heading = findHeading(root);
    if (!heading) return;

    const owner = create('div', null, 'pc-inbox-ai');
    owner.id = OWNER_ID;

    const button = create(
      'button', 'AI Assistance', 'pc-inbox-ai-button'
    );
    button.type = 'button';
    button.disabled = true;
    button.setAttribute('aria-expanded', 'false');

    const panel = create('div', null, 'pc-inbox-ai-panel');
    panel.hidden = true;
    panel.setAttribute('aria-live', 'polite');

    owner.append(button, panel);

    // Keep controls at the beginning of Ticket Workspace,
    // not inside the historical ticket queue.
    heading.after(owner);
    root.dataset.inboxAiReady = 'true';

    let signature = null;
    let version = 0;

    function refresh() {
      const selected = context(root, heading);
      const next = selected?.signature || '';

      if (next === signature) return;

      signature = next;
      version++;
      panel.hidden = true;
      panel.replaceChildren();

      button.disabled = !selected;
      button.setAttribute('aria-expanded', 'false');
      button.title = selected
        ? 'Review selected ticket'
        : 'Select a historical ticket first';
    }

    button.addEventListener('click', async () => {
      const selected = context(root, heading);
      if (!selected) return;

      if (!panel.hidden) {
        panel.hidden = true;
        button.setAttribute('aria-expanded', 'false');
        return;
      }

      panel.hidden = false;
      button.setAttribute('aria-expanded', 'true');
      panel.replaceChildren(create(
        'p', 'Loading historical evidence...'
      ));

      const request = ++version;

      try {
        const data = await loadEvidence();
        const latest = context(root, heading);

        if (
          request !== version ||
          panel.hidden ||
          !latest ||
          latest.signature !== selected.signature
        ) return;

        render(panel, latest, data);
      } catch (_) {
        if (request === version && !panel.hidden) {
          panel.replaceChildren(create(
            'p',
            'Historical evidence unavailable. No recommendation made.'
          ));
        }
      }
    });

    let queued = false;

    new MutationObserver(records => {
      const external = records.some(record => {
        const target = record.target.nodeType === 1
          ? record.target : record.target.parentElement;

        return !target?.closest?.('#' + OWNER_ID);
      });

      if (!external || queued) return;

      queued = true;
      queueMicrotask(() => {
        queued = false;
        refresh();
      });
    }).observe(root, {
      childList: true,
      subtree: true,
      characterData: true
    });

    refresh();
  }

  function boot() {
    initialize();

    // Supports Inbox content inserted after initial page load.
    if (!document.getElementById(OWNER_ID)) {
      const root = document.getElementById(ROOT_ID);
      if (!root) return;

      const watcher = new MutationObserver(() => {
        initialize();
        if (document.getElementById(OWNER_ID)) {
          watcher.disconnect();
        }
      });

      watcher.observe(root, {childList: true, subtree: true});
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot, {once: true});
  } else {
    boot();
  }
})();
// END: prototype.intelligence.inbox-assistance
