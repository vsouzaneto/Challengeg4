// BEGIN: prototype.productivity
(() => {
  'use strict';

  const KEY = 'aimaster.prototype.operational-tickets.v1';
  const CHECK_KEY = 'aimaster.prototype.productivity-checklists.v1';

  const PRIORITY = {
    Critical: 4,
    High: 3,
    Medium: 2,
    Low: 1
  };

  const TEMPLATES = {
    'Acknowledge request':
      'Thank you for contacting support. We have received your request and will review the information provided before confirming the next steps.',

    'Request information':
      'To investigate your request, could you provide additional details about the issue, the affected product, and any steps already attempted? Please do not share passwords or payment card details.',

    'Technical troubleshooting':
      'We are reviewing the reported technical issue. Please confirm when the problem began, the device or environment affected, and any error message you observed.',

    'Billing review':
      'We will review the billing information available to our support team. Any adjustment or refund requires verification and authorization before confirmation.',

    'Pending customer':
      'We are awaiting the additional information requested to continue the investigation. The ticket will remain pending until the next response.',

    'Resolution follow-up':
      'We have documented the proposed resolution. Please confirm whether the issue has been resolved before the ticket is closed.'
  };

  const STEPS = [
    'Confirm customer and request',
    'Review available ticket evidence',
    'Record investigation or action',
    'Confirm next step or resolution'
  ];

  function element(tag, text, className) {
    const el = document.createElement(tag);
    if (text !== null && text !== undefined) el.textContent = text;
    if (className) el.className = className;
    return el;
  }

  function readTickets() {
    try {
      const data = JSON.parse(localStorage.getItem(KEY) || '[]');
      if (
        !Array.isArray(data) ||
        data.length > 500 ||
        data.some(t =>
          !t || typeof t.id !== 'string' ||
          typeof t.status !== 'string' ||
          t.source !== 'Local prototype'
        )
      ) return null;

      return data;
    } catch (_) {
      return null;
    }
  }

  function readChecklists() {
    try {
      const saved = JSON.parse(localStorage.getItem(CHECK_KEY) || '{}');
      if (!saved || Array.isArray(saved) || typeof saved !== 'object') {
        return {};
      }
      return saved;
    } catch (_) {
      return {};
    }
  }

  function initialize() {
    const toolbar = document.getElementById('pc-operational-toolbar');
    const list = document.getElementById('pc-create-list');

    if (!toolbar || !list || document.getElementById('pc-productivity')) {
      return;
    }

    const shell = element('section', null, 'pc-productivity');
    shell.id = 'pc-productivity';
    shell.setAttribute('aria-label', 'Operator productivity');

    const header = element('div', null, 'pc-productivity-heading');
    header.append(
      element('h3', 'Operator Productivity'),
      element('p', 'Local workflow · No external actions are sent')
    );
    shell.append(header);

    const controls = element('div', null, 'pc-productivity-controls');

    const queues = element('div', null, 'pc-productivity-queues');
    queues.setAttribute('aria-label', 'Ticket queues');

    const queueLabels = [
      ['all', 'All Tickets'],
      ['mine', 'My Tickets'],
      ['unassigned', 'Unassigned'],
      ['pending', 'Pending'],
      ['resolved', 'Resolved']
    ];

    for (const [value, label] of queueLabels) {
      const button = element('button', label);
      button.type = 'button';
      button.dataset.queue = value;
      button.setAttribute('aria-pressed', value === 'all' ? 'true' : 'false');
      queues.append(button);
    }

    const tools = element('div', null, 'pc-productivity-tools');

    const ownerLabel = element('label', 'Operator');
    const owner = element('input');
    owner.type = 'text';
    owner.maxLength = 100;
    owner.placeholder = 'My operator name';
    owner.id = 'pc-productivity-owner';
    ownerLabel.append(owner);

    const sortLabel = element('label', 'Sort tickets');
    const sort = element('select');
    sort.id = 'pc-productivity-sort';

    for (const [value, label] of [
      ['created-desc', 'Newest first'],
      ['created-asc', 'Oldest first'],
      ['priority', 'Highest priority'],
      ['updated', 'Recently updated']
    ]) {
      const option = element('option', label);
      option.value = value;
      sort.append(option);
    }

    sortLabel.append(sort);
    tools.append(ownerLabel, sortLabel);

    controls.append(queues, tools);
    shell.append(controls);

    const info = element('p', '', 'pc-productivity-feedback');
    info.setAttribute('aria-live', 'polite');
    shell.append(info);

    toolbar.after(shell);

    let activeQueue = 'all';

    function matching(ticket) {
      const assigned = (ticket.assignee || '').trim().toLocaleLowerCase();
      const mine = owner.value.trim().toLocaleLowerCase();

      if (activeQueue === 'mine') {
        return !!mine && assigned === mine &&
          ticket.status !== 'Closed';
      }

      if (activeQueue === 'unassigned') {
        return !assigned && ticket.status !== 'Closed';
      }

      if (activeQueue === 'pending') {
        return ticket.status === 'Pending Customer';
      }

      if (activeQueue === 'resolved') {
        return ticket.status === 'Closed';
      }

      return true;
    }

    function renderQueue() {
      const tickets = readTickets();

      if (!tickets) {
        info.textContent = 'Unable to read ticket records.';
        return;
      }

      const index = new Map(tickets.map(t => [t.id, t]));
      let shown = 0;

      for (const card of Array.from(list.children)) {
        const management = card.querySelector(
          '.pc-create-management[data-ticket-id]'
        );

        if (!management) continue;

        const ticket = index.get(management.dataset.ticketId);
        if (!ticket) continue;

        const allowed = matching(ticket);
        card.classList.toggle('pc-productivity-excluded', !allowed);

        if (allowed && !card.hidden) shown++;
      }

      for (const button of queues.querySelectorAll('[data-queue]')) {
        button.setAttribute(
          'aria-pressed',
          button.dataset.queue === activeQueue ? 'true' : 'false'
        );
      }

      info.textContent =
        activeQueue === 'mine' && !owner.value.trim()
          ? 'Enter an operator name to see My Tickets.'
          : 'Queue: ' + activeQueue +
            ' · Matching operational tickets: ' +
            tickets.filter(matching).length;
    }

    function sortCards() {
      const tickets = readTickets();
      if (!tickets) return;

      const indexed = new Map(tickets.map(t => [t.id, t]));
      const cards = Array.from(list.children).filter(card =>
        card.querySelector('.pc-create-management[data-ticket-id]')
      );

      function record(card) {
        const management = card.querySelector(
          '.pc-create-management[data-ticket-id]'
        );
        return indexed.get(management.dataset.ticketId) || {};
      }

      const time = value => {
        const n = Date.parse(value || '');
        return Number.isFinite(n) ? n : 0;
      };

      const originalPosition = new Map(
        cards.map((card, index) => [card, index])
      );

      cards.sort((a, b) => {
        const first = record(a);
        const second = record(b);

        let delta = 0;

        if (sort.value === 'created-asc') {
          delta = time(first.createdAt) - time(second.createdAt);
        } else if (sort.value === 'priority') {
          delta =
            (PRIORITY[second.priority] || 0) -
            (PRIORITY[first.priority] || 0);
        } else if (sort.value === 'updated') {
          delta =
            time(second.updatedAt || second.createdAt) -
            time(first.updatedAt || first.createdAt);
        } else {
          delta = time(second.createdAt) - time(first.createdAt);
        }

        return delta || originalPosition.get(a) - originalPosition.get(b);
      });

      // Sorting is user-driven; the original ticket renderer is untouched.
      for (const card of cards) list.append(card);

      renderQueue();
    }

    queues.addEventListener('click', event => {
      const button = event.target.closest('button[data-queue]');
      if (!button) return;

      activeQueue = button.dataset.queue;

      // The existing filter owner continues to control the other filters.
      renderQueue();
    });

    owner.addEventListener('input', renderQueue);
    sort.addEventListener('change', sortCards);

    function decorateCard(card, ticket) {
      const management = card.querySelector('.pc-create-management');
      if (!management || management.querySelector('.pc-productivity-detail')) {
        return;
      }

      const detail = element('details', null, 'pc-productivity-detail');
      detail.append(element('summary', 'Operator tools & checklist'));

      const content = element('div', null, 'pc-productivity-detail-content');

      const timestamp = Date.parse(ticket.createdAt || '');
      const age = element(
        'p',
        Number.isFinite(timestamp)
          ? 'Created: ' + new Date(timestamp).toLocaleString() +
            ' · Elapsed time measured from actual creation timestamp'
          : 'Creation timestamp unavailable · No elapsed-time calculation',
        'pc-productivity-age'
      );
      content.append(age);

      const templateLabel = element('label', 'Quick response template');
      const selector = element('select');

      const placeholder = element('option', 'Choose a template');
      placeholder.value = '';
      selector.append(placeholder);

      for (const name of Object.keys(TEMPLATES)) {
        const option = element('option', name);
        option.value = name;
        selector.append(option);
      }

      templateLabel.append(selector);

      const textarea = element('textarea');
      textarea.rows = 4;
      textarea.placeholder = 'Draft only · Review before using';
      textarea.maxLength = 3000;

      selector.addEventListener('change', () => {
        textarea.value = TEMPLATES[selector.value] || '';
      });

      const actions = element('div', null, 'pc-productivity-actions');
      const copy = element('button', 'Copy reviewed draft');
      copy.type = 'button';

      const message = element('span', '', 'pc-productivity-message');

      copy.addEventListener('click', async () => {
        const value = textarea.value.trim();
        if (!value) {
          message.textContent = 'Write or select a response first.';
          return;
        }

        try {
          if (!navigator.clipboard || !navigator.clipboard.writeText) {
            throw new Error('Clipboard unavailable');
          }
          await navigator.clipboard.writeText(value);
          message.textContent = 'Draft copied. No message was sent.';
        } catch (_) {
          message.textContent =
            'Clipboard unavailable. Select and copy the draft manually.';
          textarea.focus();
          textarea.select();
        }
      });

      actions.append(copy, message);

      content.append(templateLabel, textarea, actions);

      const checklist = element('fieldset', null, 'pc-productivity-checklist');
      checklist.append(element('legend', 'Operator checklist'));

      const saved = readChecklists();
      const checked = Array.isArray(saved[ticket.id]) ? saved[ticket.id] : [];

      for (let index = 0; index < STEPS.length; index++) {
        const label = element('label');
        const box = element('input');
        box.type = 'checkbox';
        box.checked = checked.includes(index);

        box.addEventListener('change', () => {
          const records = readChecklists();
          const values = new Set(
            Array.isArray(records[ticket.id]) ? records[ticket.id] : []
          );

          if (box.checked) values.add(index);
          else values.delete(index);

          records[ticket.id] = [...values].sort((a, b) => a - b);

          try {
            localStorage.setItem(CHECK_KEY, JSON.stringify(records));
          } catch (_) {
            message.textContent =
              'Checklist could not be saved in browser storage.';
          }
        });

        label.append(box, element('span', STEPS[index]));
        checklist.append(label);
      }

      content.append(checklist);
      detail.append(content);
      management.append(detail);
    }

    let scheduled = false;

    function sync() {
      scheduled = false;
      const tickets = readTickets();
      if (!tickets) return;

      const byId = new Map(tickets.map(t => [t.id, t]));

      for (const card of Array.from(list.children)) {
        const management = card.querySelector(
          '.pc-create-management[data-ticket-id]'
        );

        if (!management) continue;

        const ticket = byId.get(management.dataset.ticketId);
        if (ticket) decorateCard(card, ticket);
      }

      renderQueue();
    }

    // The lifecycle renderer replaces cards after save/close/reopen.
    // Keep our controls synchronized without recreating its handlers.
    const observer = new MutationObserver(() => {
      if (scheduled) return;
      scheduled = true;
      queueMicrotask(sync);
    });

    observer.observe(list, { childList: true });

    window.addEventListener('storage', event => {
      if (event.key === KEY || event.key === CHECK_KEY) sync();
    });

    sync();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize, { once: true });
  } else {
    initialize();
  }
})();
// END: prototype.productivity

// BEGIN: prototype.intelligence.loader
(() => {
  const script = document.createElement('script');
  script.src = '/static/js/prototype-intelligence.js?v=a8f50636b4e77e88';
  script.defer = true;
  document.head.append(script);
})();
// END: prototype.intelligence.loader
