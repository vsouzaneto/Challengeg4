// BEGIN: prototype.automation.monitoring
(() => {
  'use strict';

  const TICKET_KEY = 'aimaster.prototype.operational-tickets.v1';
  const AUDIT_KEY = 'aimaster.prototype.automation-decisions.v1';
  const OWNER_ID = 'pc-automation-monitoring';

  const ROUTES = {
    'Technical issue': 'Technical Support',
    'Billing inquiry': 'Billing Review',
    'Payment issue': 'Billing Review',
    'Refund request': 'Billing Review',
    'Product inquiry': 'Product Support',
    'Other': 'General Triage'
  };

  const HIGH_RISK = [
    'security breach',
    'data loss',
    'unauthorized access',
    'perda de dados',
    'vazamento de dados',
    'fraud'
  ];

  function make(tag, text, cls) {
    const element = document.createElement(tag);
    if (text !== null && text !== undefined) {
      element.textContent = text;
    }
    if (cls) element.className = cls;
    return element;
  }

  function read(key, limit) {
    try {
      const raw = localStorage.getItem(key);
      const data = raw === null ? [] : JSON.parse(raw);
      if (!Array.isArray(data) || data.length > limit) return null;
      return data;
    } catch (_) {
      return null;
    }
  }

  function normalize(text) {
    return String(text || '').toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '');
  }

  // Read-only mirror of the Patch 30 routing rules.
  // Never execute actions or update ticket records here.
  function classify(ticket) {
    const type = String(ticket.type || ticket.ticketType || '').trim();
    const priority = String(ticket.priority || '');
    const content = normalize(
      [ticket.subject, ticket.description].join(' ')
    );

    if (ticket.status === 'Closed') return 'blocked';

    if (
      HIGH_RISK.some(term => content.includes(term)) ||
      priority === 'Critical'
    ) return 'review';

    if (
      !Object.keys(ROUTES).some(name =>
        normalize(name) === normalize(type)
      )
    ) return 'blocked';

    if (!String(ticket.description || '').trim()) return 'blocked';

    return 'eligible';
  }

  function timestamp(value) {
    const parsed = Date.parse(value);
    return Number.isFinite(parsed)
      ? new Date(parsed).toLocaleString()
      : 'Invalid timestamp';
  }

  function metric(label, value, description) {
    const card = make('div', null, 'pc-automation-metric');
    card.append(
      make('span', label, 'pc-automation-metric-label'),
      make('strong', String(value), 'pc-automation-metric-value'),
      make('small', description, 'pc-automation-metric-note')
    );
    return card;
  }

  function initialize() {
    if (document.getElementById(OWNER_ID)) return;

    const list = document.getElementById('pc-create-list');
    const count = document.getElementById('pc-create-count');

    if (!list || !count) return;

    const operational = document.getElementById(
      'pc-operational-toolbar'
    );

    if (!operational) return;

    const root = make('section', null, 'pc-automation-monitoring');
    root.id = OWNER_ID;
    root.setAttribute('aria-label', 'Automation monitoring');

    const heading = make('div', null, 'pc-automation-monitoring-heading');

    const labels = make('div');
    labels.append(
      make('h3', 'Automation Monitoring'),
      make(
        'p',
        'Deterministic proposals, human decisions and audit records'
      )
    );

    const exportButton = make(
      'button',
      'Export decision audit · JSON',
      'pc-automation-export'
    );
    exportButton.type = 'button';

    heading.append(labels, exportButton);

    const metrics = make('div', null, 'pc-automation-metrics');

    const explanation = make(
      'p',
      'Proposals describe the current ticket state. Decisions are ' +
      'historical simulation events; no routing, assignments, ' +
      'messages or external actions are executed.',
      'pc-automation-explanation'
    );

    const history = make('details', null, 'pc-automation-audit');
    const summary = make('summary', 'Decision history');
    const historyBody = make('div', null, 'pc-automation-audit-body');
    history.append(summary, historyBody);

    const feedback = make('p', '', 'pc-automation-feedback');
    feedback.setAttribute('aria-live', 'polite');

    root.append(
      heading,
      metrics,
      explanation,
      history,
      feedback
    );

    // Mount above the existing operational ticket list.
    // No existing form, toolbar or card is moved or cloned.
    operational.before(root);

    function snapshot() {
      const tickets = read(TICKET_KEY, 500);
      const decisions = read(AUDIT_KEY, 2000);

      if (!tickets || !decisions) return null;

      if (tickets.some(t =>
        !t ||
        typeof t.id !== 'string' ||
        typeof t.status !== 'string' ||
        t.source !== 'Local prototype'
      )) return null;

      if (decisions.some(d =>
        !d ||
        typeof d.ticketId !== 'string' ||
        !['approved', 'rejected'].includes(d.decision) ||
        typeof d.reason !== 'string' ||
        typeof d.timestamp !== 'string' ||
        d.execution !== 'Simulation only'
      )) return null;

      return { tickets, decisions };
    }

    function render() {
      const data = snapshot();

      metrics.replaceChildren();
      historyBody.replaceChildren();

      if (!data) {
        metrics.append(
          make('p', 'Local storage unavailable or invalid.')
        );
        return;
      }

      const totals = {
        eligible: 0,
        review: 0,
        blocked: 0
      };

      for (const ticket of data.tickets) {
        totals[classify(ticket)]++;
      }

      const approved = data.decisions.filter(
        d => d.decision === 'approved'
      ).length;

      const rejected = data.decisions.filter(
        d => d.decision === 'rejected'
      ).length;

      const escalations = data.decisions.filter(
        d => d.proposedRoute === 'Human Escalation'
      ).length;

      const unique = new Set(
        data.decisions.map(d => d.ticketId)
      ).size;

      metrics.append(
        metric('Operational tickets', data.tickets.length, 'Browser-local'),
        metric('Eligible proposals', totals.eligible, 'Current rules'),
        metric('Human review', totals.review, 'Current high-risk cases'),
        metric('Blocked proposals', totals.blocked, 'Current restrictions'),
        metric('Approvals', approved, 'Recorded decisions'),
        metric('Rejections', rejected, 'Recorded decisions'),
        metric('Escalation decisions', escalations, 'Historical proposals'),
        metric('Tickets reviewed', unique, 'Distinct ticket IDs')
      );

      const events = [...data.decisions].reverse();

      if (!events.length) {
        historyBody.append(
          make('p', 'No human decisions recorded yet.')
        );
      } else {
        for (const event of events.slice(0, 30)) {
          const row = make('div', null, 'pc-automation-audit-row');

          row.append(
            make(
              'strong',
              event.decision.toUpperCase() +
              ' · ' + event.ticketId
            ),
            make(
              'span',
              timestamp(event.timestamp) +
              ' · ' + (event.proposedRoute || 'No route')
            ),
            make('p', event.reason)
          );

          historyBody.append(row);
        }

        if (events.length > 30) {
          historyBody.append(make(
            'p',
            'Showing the latest 30 decisions. Export JSON for full history.'
          ));
        }
      }
    }

    exportButton.addEventListener('click', () => {
      const data = snapshot();

      if (!data) {
        feedback.textContent = 'Export blocked: invalid local records.';
        return;
      }

      const payload = {
        schema: 'aimaster.prototype.automation-audit.v1',
        exportedAt: new Date().toISOString(),
        scope: 'Browser-local simulated decisions',
        execution: 'No external actions',
        totalEvents: data.decisions.length,
        events: data.decisions
      };

      const blob = new Blob(
        [JSON.stringify(payload, null, 2)],
        { type: 'application/json' }
      );

      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');

      link.href = url;
      link.download =
        'aimaster-automation-decisions-' +
        new Date().toISOString().slice(0, 10) + '.json';

      document.body.append(link);
      link.click();
      link.remove();

      URL.revokeObjectURL(url);

      feedback.textContent =
        'Local decision audit exported. No data was sent.';
    });

    // UI refreshes after ticket or audit storage changes.
    // The Patch 30 owner remains the only writer of decisions.
    window.addEventListener('storage', event => {
      if (
        event.key === TICKET_KEY ||
        event.key === AUDIT_KEY
      ) render();
    });

    document.addEventListener('click', event => {
      if (
        event.target.closest('.pc-selective-automation-actions')
      ) {
        queueMicrotask(render);
      }
    });

    // Poll only the two local serialized values while this
    // screen is visible. No network requests are performed.
    let lastTickets = localStorage.getItem(TICKET_KEY);
    let lastAudit = localStorage.getItem(AUDIT_KEY);

    const observer = new MutationObserver(() => {
      const currentTickets = localStorage.getItem(TICKET_KEY);
      const currentAudit = localStorage.getItem(AUDIT_KEY);

      if (
        currentTickets === lastTickets &&
        currentAudit === lastAudit
      ) return;

      lastTickets = currentTickets;
      lastAudit = currentAudit;
      render();
    });

    observer.observe(list, { childList: true });

    render();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize, {
      once: true
    });
  } else {
    initialize();
  }
})();
// END: prototype.automation.monitoring
