// BEGIN: prototype.automation.selective
(() => {
  'use strict';

  const TICKETS = 'aimaster.prototype.operational-tickets.v1';
  const AUDIT = 'aimaster.prototype.automation-decisions.v1';
  const ROOT = 'pc-create-list';

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

  function element(tag, text, className) {
    const node = document.createElement(tag);
    if (text != null) node.textContent = text;
    if (className) node.className = className;
    return node;
  }

  function read(key, fallback) {
    try {
      const value = localStorage.getItem(key);
      return value === null ? fallback : JSON.parse(value);
    } catch (_) {
      return null;
    }
  }

  function tickets() {
    const data = read(TICKETS, []);
    if (!Array.isArray(data) || data.length > 500) return null;

    if (data.some(ticket =>
      !ticket ||
      typeof ticket.id !== 'string' ||
      typeof ticket.status !== 'string' ||
      ticket.source !== 'Local prototype'
    )) return null;

    return data;
  }

  function audit() {
    const data = read(AUDIT, []);
    return Array.isArray(data) && data.length <= 2000
      ? data
      : null;
  }

  function normalize(text) {
    return String(text || '').toLowerCase()
      .normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  }

  function proposal(ticket) {
    const type = String(
      ticket.type || ticket.ticketType || ''
    ).trim();

    const priority = String(ticket.priority || '');
    const content = normalize(
      [ticket.subject, ticket.description].join(' ')
    );

    const risk = HIGH_RISK.filter(term =>
      content.includes(term)
    );

    const route = Object.entries(ROUTES)
      .find(([name]) =>
        normalize(name) === normalize(type)
      );

    if (ticket.status === 'Closed') {
      return {
        state: 'blocked',
        route: null,
        reason: 'Closed ticket. Reopen before operational triage.'
      };
    }

    if (risk.length || priority === 'Critical') {
      return {
        state: 'review',
        route: 'Human Escalation',
        reason: risk.length
          ? 'Sensitive terms detected: ' + risk.join(', ')
          : 'Recorded Critical priority requires human review.'
      };
    }

    if (!route) {
      return {
        state: 'blocked',
        route: null,
        reason: 'No verified routing rule for this ticket type.'
      };
    }

    if (!String(ticket.description || '').trim()) {
      return {
        state: 'blocked',
        route: null,
        reason: 'Request description is missing.'
      };
    }

    return {
      state: 'eligible',
      route: route[1],
      reason: 'Routing rule matches the recorded ticket type.'
    };
  }

  function matchesRule(ticket) {
    return [
      ticket.type || ticket.ticketType || '',
      ticket.priority || '',
      ticket.status || '',
      ticket.subject || '',
      ticket.description || ''
    ].join('|');
  }

  function initialize() {
    const list = document.getElementById(ROOT);
    if (!list || list.dataset.automationReady === 'true') {
      return;
    }

    list.dataset.automationReady = 'true';

    function renderCard(card, ticket) {
      const management = card.querySelector(
        '.pc-create-management[data-ticket-id]'
      );

      if (!management) return;

      const old = management.querySelector(
        '.pc-selective-automation'
      );

      const signature = matchesRule(ticket);

      if (old && old.dataset.signature === signature) {
        return;
      }

      if (old) old.remove();

      const plan = proposal(ticket);
      const box = element(
        'details', null, 'pc-selective-automation'
      );
      box.dataset.signature = signature;
      box.dataset.ticketId = ticket.id;

      const summary = element(
        'summary', 'Selective Automation · Review decision'
      );

      box.append(summary);

      const body = element(
        'div', null, 'pc-selective-automation-body'
      );

      body.append(
        element(
          'p',
          'Deterministic demonstration · No external actions ' +
          'or automatic ticket updates.',
          'pc-selective-automation-note'
        ),
        element(
          'h4',
          plan.state === 'blocked'
            ? 'Automation blocked'
            : plan.state === 'review'
              ? 'Human escalation recommended'
              : 'Routing proposal available'
        ),
        element(
          'p',
          'Proposed destination: ' +
          (plan.route || 'No destination assigned')
        ),
        element('p', 'Evidence: ' + plan.reason)
      );

      if (plan.state === 'eligible') {
        body.append(element(
          'p',
          'Low-risk workflow proposal. Approval records the ' +
          'simulation only; it does not assign the ticket.'
        ));
      } else {
        body.append(element(
          'p',
          'Automatic execution is not authorized for this case.'
        ));
      }

      const label = element('label', 'Decision reason');
      const reason = element('textarea');
      reason.rows = 2;
      reason.maxLength = 500;
      reason.placeholder =
        'Document why the proposal is approved or rejected';
      label.append(reason);
      body.append(label);

      const controls = element(
        'div', null, 'pc-selective-automation-actions'
      );

      const approve = element('button', 'Approve simulation');
      const reject = element('button', 'Reject proposal');

      approve.type = 'button';
      reject.type = 'button';
      approve.disabled = plan.state === 'blocked';

      const feedback = element(
        'p', '', 'pc-selective-automation-feedback'
      );
      feedback.setAttribute('aria-live', 'polite');

      function decide(decision) {
        const current = tickets();
        const history = audit();

        if (!current || !history) {
          feedback.textContent =
            'Storage unavailable. No decision recorded.';
          return;
        }

        const latest = current.find(t => t.id === ticket.id);
        if (!latest || matchesRule(latest) !== signature) {
          feedback.textContent =
            'Ticket changed. Refresh the page and review again.';
          return;
        }

        if (decision === 'approved' &&
            proposal(latest).state === 'blocked') {
          feedback.textContent =
            'Approval blocked by the current rule.';
          return;
        }

        const explanation = reason.value.trim();

        if (explanation.length < 10) {
          feedback.textContent =
            'A reason of at least 10 characters is required.';
          return;
        }

        if (history.length >= 2000) {
          feedback.textContent =
            'Audit storage limit reached. Export records first.';
          return;
        }

        const entry = {
          ticketId: ticket.id,
          timestamp: new Date().toISOString(),
          decision,
          proposedRoute: plan.route,
          ruleState: plan.state,
          ruleEvidence: plan.reason,
          reason: explanation,
          execution: 'Simulation only'
        };

        try {
          localStorage.setItem(
            AUDIT, JSON.stringify([...history, entry])
          );

          feedback.textContent =
            'Decision recorded · No action executed.';
          reason.value = '';
          showHistory();
        } catch (_) {
          feedback.textContent =
            'Storage error. Decision not recorded.';
        }
      }

      approve.addEventListener('click', () => decide('approved'));
      reject.addEventListener('click', () => decide('rejected'));

      controls.append(approve, reject);
      body.append(controls, feedback);

      const history = element(
        'div', null, 'pc-selective-automation-history'
      );

      function showHistory() {
        history.replaceChildren();

        const events = audit();
        if (!events) {
          history.append(element('p', 'Audit unavailable.'));
          return;
        }

        const own = events.filter(e =>
          e && e.ticketId === ticket.id
        );

        history.append(element(
          'h4', 'Decision audit · ' + own.length + ' event(s)'
        ));

        for (const event of own.slice(-10).reverse()) {
          history.append(element(
            'p',
            new Date(event.timestamp).toLocaleString() +
            ' · ' + event.decision +
            ' · ' + (event.proposedRoute || 'No route') +
            ' · ' + event.reason
          ));
        }
      }

      showHistory();
      body.append(history);

      box.append(body);

      // New owner; existing ticket management handlers remain intact.
      management.append(box);
    }

    let running = false;

    function sync() {
      if (running) return;
      running = true;

      try {
        const records = tickets();
        if (!records) return;

        const byId = new Map(
          records.map(ticket => [ticket.id, ticket])
        );

        for (const card of Array.from(list.children)) {
          const management = card.querySelector(
            '.pc-create-management[data-ticket-id]'
          );

          if (!management) continue;

          const ticket = byId.get(management.dataset.ticketId);
          if (ticket) renderCard(card, ticket);
        }
      } finally {
        running = false;
      }
    }

    let queued = false;

    new MutationObserver(() => {
      if (queued) return;
      queued = true;

      queueMicrotask(() => {
        queued = false;
        sync();
      });
    }).observe(list, { childList: true });

    window.addEventListener('storage', event => {
      if (event.key === TICKETS) sync();
    });

    sync();
  }

  if (document.readyState === 'loading') {
    document.addEventListener(
      'DOMContentLoaded', initialize, {once: true}
    );
  } else {
    initialize();
  }
})();
// END: prototype.automation.selective
