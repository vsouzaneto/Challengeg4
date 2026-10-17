// BEGIN: prototype.intelligence.historical-evidence
(() => {
  'use strict';

  const KEY = 'aimaster.prototype.operational-tickets.v1';

  function node(tag, text, cls) {
    const e = document.createElement(tag);
    if (text != null) e.textContent = text;
    if (cls) e.className = cls;
    return e;
  }

  function words(text) {
    return new Set(
      String(text || '').toLowerCase()
        .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
        .match(/[a-z]{4,}/g) || []
    );
  }

  function tickets() {
    try {
      const data = JSON.parse(localStorage.getItem(KEY) || '[]');
      return Array.isArray(data) && data.length <= 500
        ? data.filter(t =>
            t && typeof t.id === 'string' &&
            t.source === 'Local prototype')
        : [];
    } catch (_) {
      return [];
    }
  }

  function analyze(ticket, evidence) {
    const terms = words([
      ticket.subject,
      ticket.description,
      ticket.type,
      ticket.ticketType
    ].filter(v => typeof v === 'string').join(' '));

    const ranked = Object.entries(evidence.dataset2.categories)
      .map(([category, data]) => {
        const matches = data.terms.filter(t => terms.has(t.word));
        return {
          category,
          samples: data.documents,
          matches,
          score: matches.reduce((n, t) => n + t.weight, 0)
        };
      })
      .sort((a, b) => b.score - a.score);

    const top = ranked[0];
    const runner = ranked[1];

    const sufficient = Boolean(
      top &&
      top.matches.length >= 2 &&
      top.score > 0 &&
      (!runner || top.score >= runner.score * 1.35)
    );

    const typ = String(
      ticket.type || ticket.ticketType || ''
    ).toLowerCase();

    const historical = Object.entries(evidence.dataset1.ticket_types)
      .find(([name]) => name.toLowerCase() === typ);

    return { top, sufficient, historical };
  }

  async function initialize() {
    const list = document.getElementById('pc-create-list');
    if (!list || list.dataset.historicalReady === 'true') return;

    let evidence;

    try {
      const response = await fetch(
        '/static/data/prototype-historical-evidence.json?v=36846c99ee92507a',
        { cache: 'no-store' }
      );
      if (!response.ok) throw Error('Source unavailable');

      evidence = await response.json();
      if (
        evidence.schema !== 'aimaster.historical-evidence.v1' ||
        !evidence.dataset1 || !evidence.dataset2
      ) throw Error('Invalid evidence schema');
    } catch (error) {
      console.warn('Historical evidence:', error);
      return;
    }

    list.dataset.historicalReady = 'true';

    function decorate() {
      const lookup = new Map(tickets().map(t => [t.id, t]));

      for (const card of Array.from(list.children)) {
        const management = card.querySelector(
          '.pc-create-management[data-ticket-id]'
        );
        if (!management) continue;

        const body = management.querySelector('.pc-intelligence-body');
        if (!body || body.querySelector('.pc-historical-evidence')) {
          continue;
        }

        const ticket = lookup.get(management.dataset.ticketId);
        if (!ticket) continue;

        const result = analyze(ticket, evidence);
        const section = node('section', null, 'pc-historical-evidence');

        section.append(
          node('h4', 'Historical evidence · Datasets 1 + 2'),
          node(
            'p',
            evidence.dataset1.records.toLocaleString() +
            ' historical tickets · ' +
            evidence.dataset2.records.toLocaleString() +
            ' classified documents · Read-only aggregates'
          ),
          node('h4', 'Dataset 2 · Classification evidence')
        );

        if (result.sufficient) {
          section.append(
            node(
              'p',
              'Candidate category: ' + result.top.category +
              ' · Reference sample: ' + result.top.samples
            ),
            node(
              'p',
              'Matched terms: ' +
              result.top.matches.slice(0, 8)
                .map(t => t.word).join(', ')
            )
          );
        } else {
          section.append(node(
            'p',
            'Insufficient evidence for historical classification. ' +
            'No category is assigned.'
          ));
        }

        section.append(
          node('h4', 'Dataset 1 · Recorded priority distribution')
        );

        if (result.historical) {
          const [type, info] = result.historical;
          const distribution = Object.entries(info.priorities)
            .sort((a, b) => b[1] - a[1])
            .map(([priority, n]) =>
              priority + ': ' + n + ' (' +
              (n / info.count * 100).toFixed(1) + '%)'
            ).join(' · ');

          section.append(node(
            'p',
            type + ' · ' + info.count +
            ' observed records · ' + distribution
          ));
        } else {
          section.append(node(
            'p',
            'No exact historical ticket-type match. ' +
            'Priority distribution unavailable.'
          ));
        }

        section.append(node(
          'p',
          'Historical distributions are not confidence scores, ' +
          'SLA measurements or automatic decisions. ' +
          'Operator approval remains required.',
          'pc-historical-note'
        ));

        body.append(section);
      }
    }

    // Observe lifecycle card replacement only.
    // Do not observe our own nested DOM insertions.
    let queued = false;
    const observer = new MutationObserver(() => {
      if (queued) return;
      queued = true;
      queueMicrotask(() => {
        queued = false;
        decorate();
      });
    });

    observer.observe(list, { childList: true });
    window.addEventListener('storage', event => {
      if (event.key === KEY) decorate();
    });

    decorate();
  }

  if (document.readyState === 'loading') {
    document.addEventListener(
      'DOMContentLoaded', initialize, { once: true }
    );
  } else {
    initialize();
  }
})();
// END: prototype.intelligence.historical-evidence
