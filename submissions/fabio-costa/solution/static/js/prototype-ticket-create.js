
// BEGIN: prototype.ticket-create
(() => {
  'use strict';

  const KEY = 'aimaster.prototype.operational-tickets.v1';
  const CHANNELS = ['Email', 'Phone', 'Social media', 'Chat'];
  const TYPES = ['Technical issue', 'Billing inquiry', 'Product inquiry', 'Other'];
  const PRIORITIES = ['Low', 'Medium', 'High', 'Critical'];
  const LIMIT = 500;

  function node(tag, value, className) {
    const item = document.createElement(tag);
    if (className) item.className = className;
    if (value !== null && value !== undefined) {
      item.textContent = String(value);
    }
    return item;
  }

  function validTicket(t) {
    return t && typeof t === 'object'
      && typeof t.id === 'string'
      && typeof t.createdAt === 'string'
      && !Number.isNaN(Date.parse(t.createdAt))
      && typeof t.customer === 'string'
      && typeof t.email === 'string'
      && typeof t.subject === 'string'
      && typeof t.description === 'string'
      && CHANNELS.includes(t.channel)
      && TYPES.includes(t.type)
      && PRIORITIES.includes(t.priority)
      && ['Open', 'In Progress', 'Pending Customer', 'Closed']
        .includes(t.status)
      && (!t.events || (
        Array.isArray(t.events) &&
        t.events.length <= 250 &&
        t.events.every(e =>
          e && typeof e.action === 'string' &&
          typeof e.detail === 'string' &&
          typeof e.at === 'string'
        )
      ))
      && t.source === 'Local prototype';
  }

  function init() {
    const root = document.getElementById('pc-ticket-create');
    if (!root || root.dataset.ready === 'true') return;

    const form = document.getElementById('pc-create-form');
    const list = document.getElementById('pc-create-list');
    const count = document.getElementById('pc-create-count');
    const feedback = document.getElementById('pc-create-feedback');
    if (!form || !list || !count || !feedback) return;

    let tickets = [];
    let storageAvailable = true;
    let storageSnapshot = null;

    function showFeedback(message, error = false) {
      feedback.textContent = message;
      feedback.dataset.status = error ? 'error' : 'success';
    }

    try {
      const raw = localStorage.getItem(KEY);
      storageSnapshot = raw;
      if (raw !== null) {
        const saved = JSON.parse(raw);
        if (!Array.isArray(saved) ||
            saved.length > LIMIT ||
            !saved.every(validTicket) ||
            new Set(saved.map(t => t.id)).size !== saved.length) {
          throw new Error('Invalid local ticket records');
        }
        tickets = saved;
      }
    } catch (error) {
      storageAvailable = false;
      showFeedback(
        'Stored tickets could not be loaded. Existing records will not be overwritten.',
        true
      );
    }

    root.dataset.ready = 'true';

    function render() {
      list.replaceChildren();
      count.textContent =
        tickets.length + (tickets.length === 1 ? ' local ticket' : ' local tickets');

      if (!tickets.length) {
        list.append(node('p', 'No operational tickets created yet.'));
        return;
      }

      for (const ticket of tickets) {
        const card = node('article', null, 'pc-create-ticket');
        const top = node('div', null, 'pc-create-ticket-head');

        top.append(
          node('strong', ticket.subject),
          node('span', ticket.status, 'pc-create-open')
        );

        const date = new Date(ticket.createdAt);

        card.append(
          top,
          node('p', ticket.id + ' · ' + ticket.channel + ' · ' +
            ticket.type + ' · ' + ticket.priority),
          node('p', ticket.customer + ' · ' + ticket.email),
          node('p', ticket.description, 'pc-create-ticket-description'),
          node('small', 'Created: ' + date.toLocaleString())
        );

        lifecycleFields(card, ticket);
        list.append(card);
      }
    }


  // OWNER: prototype.ticket-create.lifecycle
  // BEGIN: prototype.ticket-create.lifecycle

  const STATUSES = ['Open', 'In Progress', 'Pending Customer', 'Closed'];
  const MAX_EVENTS = 250;

  function makeEvent(action, detail) {
    return {
      action,
      detail,
      at: new Date().toISOString(),
      actor: 'Local operator · Simulation'
    };
  }

  function lifecycleFields(card, ticket) {
    const area = node('div', null, 'pc-create-management');
    area.dataset.ticketId = ticket.id;

    const heading = node('h4', 'Ticket management');
    area.append(heading);

    const grid = node('div', null, 'pc-create-management-grid');

    const ownerLabel = node('label', 'Assigned operator');
    const ownerInput = node('input');
    ownerInput.type = 'text';
    ownerInput.maxLength = 100;
    ownerInput.placeholder = 'Unassigned';
    ownerInput.value = ticket.assignee || '';
    ownerInput.dataset.field = 'assignee';
    ownerInput.disabled = ticket.status === 'Closed';
    ownerLabel.append(ownerInput);

    const priorityLabel = node('label', 'Priority');
    const priorityInput = node('select');
    priorityInput.dataset.field = 'priority';
    priorityInput.disabled = ticket.status === 'Closed';

    for (const value of PRIORITIES) {
      const option = node('option', value);
      option.value = value;
      option.selected = value === ticket.priority;
      priorityInput.append(option);
    }
    priorityLabel.append(priorityInput);

    const statusLabel = node('label', 'Status');
    const statusInput = node('select');
    statusInput.dataset.field = 'status';
    statusInput.disabled = ticket.status === 'Closed';

    for (const value of STATUSES.filter(s => s !== 'Closed')) {
      const option = node('option', value);
      option.value = value;
      option.selected = value === ticket.status;
      statusInput.append(option);
    }
    statusLabel.append(statusInput);

    grid.append(ownerLabel, priorityLabel, statusLabel);
    area.append(grid);

    const noteLabel = node('label', 'Operator note / action reason');
    noteLabel.className = 'pc-create-management-note';
    const note = node('textarea');
    note.rows = 2;
    note.maxLength = 1000;
    note.placeholder = 'Describe the action or record an internal note';
    note.dataset.field = 'note';
    noteLabel.append(note);
    area.append(noteLabel);

    const actions = node('div', null, 'pc-create-management-actions');

    const addButton = (label, action) => {
      const button = node('button', label);
      button.type = 'button';
      button.dataset.action = action;
      actions.append(button);
    };

    if (ticket.status === 'Closed') {
      addButton('Reopen ticket', 'reopen');
    } else {
      addButton('Save changes / note', 'save');
      addButton('Close ticket', 'close');
    }

    area.append(actions);

    const history = node('details', null, 'pc-create-history');
    const events = Array.isArray(ticket.events) ? ticket.events : [];

    history.append(
      node('summary', 'Activity history · ' + (
        events.length || 1
      ) + ' event(s)')
    );

    const historyList = node('ol');
    const entries = events.length
      ? events
      : [{
          action: 'Created',
          detail: 'Existing locally created ticket',
          at: ticket.createdAt,
          actor: 'Local prototype'
        }];

    for (const event of entries) {
      const item = node('li');
      item.append(
        node('strong', event.action),
        node('span', ' · ' + new Date(event.at).toLocaleString()),
        node('p', event.detail)
      );
      historyList.append(item);
    }

    history.append(historyList);
    area.append(history);
    card.append(area);
  }

  function applyLifecycleAction(event) {
    const button = event.target.closest('button[data-action]');
    if (!button || !list.contains(button)) return;

    const area = button.closest('.pc-create-management');
    if (!area) return;

    const id = area.dataset.ticketId;
    const index = tickets.findIndex(ticket => ticket.id === id);
    if (index < 0) return;

    if (!storageAvailable) {
      showFeedback('Local storage unavailable.', true);
      return;
    }

    // Avoid overwriting changes made in another browser tab.
    if (localStorage.getItem(KEY) !== storageSnapshot) {
      showFeedback(
        'Tickets changed in another tab. Reload before editing.',
        true
      );
      return;
    }

    const ticket = tickets[index];
    const action = button.dataset.action;

    const note = area.querySelector(
      '[data-field="note"]'
    ).value.trim();

    if (note.length > 1000) {
      showFeedback('Note exceeds the allowed length.', true);
      return;
    }

    const next = {
      ...ticket,
      events: Array.isArray(ticket.events)
        ? ticket.events.slice()
        : [makeLegacyCreationEvent(ticket)]
    };

    if (next.events.length >= MAX_EVENTS) {
      showFeedback('Event history limit reached.', true);
      return;
    }

    let description = '';

    if (action === 'save') {
      if (ticket.status === 'Closed') return;

      const assignee = area.querySelector(
        '[data-field="assignee"]'
      ).value.trim();

      const priority = area.querySelector(
        '[data-field="priority"]'
      ).value;

      const status = area.querySelector(
        '[data-field="status"]'
      ).value;

      if (assignee.length > 100 ||
          !PRIORITIES.includes(priority) ||
          !STATUSES.includes(status) ||
          status === 'Closed') {
        showFeedback('Invalid management fields.', true);
        return;
      }

      const changes = [];

      if (assignee !== (ticket.assignee || '')) {
        changes.push(
          'Owner: ' + (ticket.assignee || 'Unassigned') +
          ' → ' + (assignee || 'Unassigned')
        );
      }

      if (priority !== ticket.priority) {
        changes.push(
          'Priority: ' + ticket.priority + ' → ' + priority
        );
      }

      if (status !== ticket.status) {
        changes.push(
          'Status: ' + ticket.status + ' → ' + status
        );
      }

      if (!changes.length && !note) {
        showFeedback('No changes or note to save.', true);
        return;
      }

      next.assignee = assignee;
      next.priority = priority;
      next.status = status;

      description = changes.join('; ');
      if (note) {
        description += (description ? ' · ' : '') + note;
      }

    } else if (action === 'close') {
      if (ticket.status === 'Closed') return;

      if (note.length < 10) {
        showFeedback(
          'Closing a ticket requires a reason of at least 10 characters.',
          true
        );
        return;
      }

      next.status = 'Closed';
      next.closedAt = new Date().toISOString();
      description = 'Closure reason: ' + note;

    } else if (action === 'reopen') {
      if (ticket.status !== 'Closed') return;

      if (note.length < 10) {
        showFeedback(
          'Reopening requires a reason of at least 10 characters.',
          true
        );
        return;
      }

      next.status = 'Open';
      next.closedAt = null;
      description = 'Reopening reason: ' + note;

    } else {
      return;
    }

    const labels = {
      save: 'Updated',
      close: 'Closed',
      reopen: 'Reopened'
    };

    next.events.push(makeEvent(labels[action], description));
    next.updatedAt = next.events[next.events.length - 1].at;

    const updated = tickets.slice();
    updated[index] = next;
    const serialized = JSON.stringify(updated);

    try {
      localStorage.setItem(KEY, serialized);

      if (localStorage.getItem(KEY) !== serialized) {
        throw new Error('Storage verification failed');
      }
    } catch (error) {
      showFeedback('Ticket update could not be saved.', true);
      return;
    }

    storageSnapshot = serialized;
    tickets = updated;
    render();

    showFeedback(
      'Ticket ' + id + ' · ' + labels[action] +
      ' · ' + new Date(next.updatedAt).toLocaleString()
    );
  }

  function makeLegacyCreationEvent(ticket) {
    return {
      action: 'Created',
      detail: 'Ticket created before lifecycle tracking was enabled',
      at: ticket.createdAt,
      actor: 'Local prototype'
    };
  }

  // END: prototype.ticket-create.lifecycle

    render();
    list.addEventListener('click', applyLifecycleAction);

    form.addEventListener('submit', event => {
      event.preventDefault();

      if (!storageAvailable) {
        showFeedback('Local storage unavailable. Ticket not created.', true);
        return;
      }

      if (!form.reportValidity()) return;

      const data = new FormData(form);
      const read = key => String(data.get(key) || '').trim();

      const customer = read('customer');
      const email = read('email');
      const channel = read('channel');
      const type = read('type');
      const priority = read('priority');
      const subject = read('subject');
      const description = read('description');

      if (!customer || customer.length > 120 ||
          !email || email.length > 254 ||
          !subject || subject.length > 180 ||
          description.length < 10 || description.length > 5000 ||
          !CHANNELS.includes(channel) ||
          !TYPES.includes(type) ||
          !PRIORITIES.includes(priority)) {
        showFeedback('Invalid ticket information. Check all fields.', true);
        return;
      }

      if (tickets.length >= LIMIT) {
        showFeedback('Local prototype limit of 500 tickets reached.', true);
        return;
      }

      if (!window.crypto || typeof window.crypto.randomUUID !== 'function') {
        showFeedback('Secure ID generation is unavailable.', true);
        return;
      }

      const createdAt = new Date().toISOString();
      const ticket = {
        id: 'NEW-' + window.crypto.randomUUID(),
        createdAt,
        customer,
        email,
        channel,
        type,
        priority,
        subject,
        description,
        status: 'Open',
        source: 'Local prototype'
      };

      const next = [ticket, ...tickets];

      try {
        if (localStorage.getItem(KEY) !== storageSnapshot) {
          showFeedback(
            'Tickets changed in another tab. Reload before creating.',
            true
          );
          return;
        }
        const serialized = JSON.stringify(next);
        localStorage.setItem(KEY, serialized);
        if (localStorage.getItem(KEY) !== serialized) {
          throw new Error('Persistence verification failed');
        }
      } catch (error) {
        showFeedback('Ticket was not saved. Check browser storage.', true);
        return;
      }

      storageSnapshot = JSON.stringify(next);
      tickets = next;
      render();
      form.reset();

      showFeedback(
        'Ticket ' + ticket.id + ' created locally at ' +
        new Date(createdAt).toLocaleString() + '.'
      );
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, { once: true });
  } else {
    init();
  }
})();
// END: prototype.ticket-create

// BEGIN: prototype.ticket-create.operational-view
(() => {
  'use strict';

  const KEY = 'aimaster.prototype.operational-tickets.v1';
  const STATUSES = ['Open', 'In Progress', 'Pending Customer', 'Closed'];
  const PRIORITIES = ['Low', 'Medium', 'High', 'Critical'];
  const CHANNELS = ['Email', 'Phone', 'Social media', 'Chat'];

  function initialize() {
    const list = document.getElementById('pc-create-list');
    const count = document.getElementById('pc-create-count');

    if (!list || !count || !list.parentElement) return;
    if (document.getElementById('pc-operational-toolbar')) return;

    const toolbar = document.createElement('section');
    toolbar.id = 'pc-operational-toolbar';
    toolbar.className = 'pc-operational-toolbar';
    toolbar.setAttribute('aria-label', 'Operational ticket management');

    toolbar.innerHTML = `
      <div class="pc-operational-heading">
        <div>
          <h3>Operational Ticket Management</h3>
          <p>Search, filter and export locally created tickets.</p>
        </div>
        <button type="button" id="pc-operational-export">
          Export tickets · JSON
        </button>
      </div>
      <div id="pc-operational-metrics"
           class="pc-operational-metrics"
           aria-live="polite"></div>
      <div class="pc-operational-filters">
        <label>Search tickets
          <input type="search" id="pc-operational-search"
                 placeholder="ID, customer, subject, email">
        </label>
        <label>Status
          <select id="pc-operational-status">
            <option value="">All statuses</option>
            <option>Open</option>
            <option>In Progress</option>
            <option>Pending Customer</option>
            <option>Closed</option>
          </select>
        </label>
        <label>Priority
          <select id="pc-operational-priority">
            <option value="">All priorities</option>
            <option>Low</option>
            <option>Medium</option>
            <option>High</option>
            <option>Critical</option>
          </select>
        </label>
        <label>Channel
          <select id="pc-operational-channel">
            <option value="">All channels</option>
            <option>Email</option>
            <option>Phone</option>
            <option>Social media</option>
            <option>Chat</option>
          </select>
        </label>
      </div>
      <p id="pc-operational-result"
         class="pc-operational-result"
         aria-live="polite"></p>
    `;

    list.before(toolbar);

    const search = toolbar.querySelector('#pc-operational-search');
    const status = toolbar.querySelector('#pc-operational-status');
    const priority = toolbar.querySelector('#pc-operational-priority');
    const channel = toolbar.querySelector('#pc-operational-channel');
    const metrics = toolbar.querySelector('#pc-operational-metrics');
    const result = toolbar.querySelector('#pc-operational-result');
    const exportButton = toolbar.querySelector('#pc-operational-export');

    function readTickets() {
      try {
        const raw = localStorage.getItem(KEY);
        const records = raw === null ? [] : JSON.parse(raw);

        if (
          !Array.isArray(records) ||
          records.length > 500 ||
          records.some(ticket =>
            !ticket ||
            typeof ticket.id !== 'string' ||
            typeof ticket.status !== 'string' ||
            !STATUSES.includes(ticket.status) ||
            !PRIORITIES.includes(ticket.priority) ||
            !CHANNELS.includes(ticket.channel) ||
            ticket.source !== 'Local prototype'
          ) ||
          new Set(records.map(ticket => ticket.id)).size !== records.length
        ) {
          return null;
        }
        return records;
      } catch (_) {
        return null;
      }
    }

    function render() {
      const tickets = readTickets();

      if (!tickets) {
        metrics.replaceChildren();
        result.textContent =
          'Ticket records could not be read. Existing data was not modified.';
        exportButton.disabled = true;
        return;
      }

      exportButton.disabled = false;

      const values = [
        ['Total tickets', tickets.length],
        ['Open', tickets.filter(t => t.status === 'Open').length],
        ['In progress', tickets.filter(t => t.status === 'In Progress').length],
        ['Pending customer', tickets.filter(t => t.status === 'Pending Customer').length],
        ['Closed', tickets.filter(t => t.status === 'Closed').length]
      ];

      metrics.replaceChildren();

      for (const [label, value] of values) {
        const item = document.createElement('div');
        const title = document.createElement('span');
        const number = document.createElement('strong');
        title.textContent = label;
        number.textContent = String(value);
        item.append(title, number);
        metrics.append(item);
      }

      const query = search.value.trim().toLocaleLowerCase();
      const matches = new Set();

      for (const ticket of tickets) {
        const haystack = [
          ticket.id,
          ticket.customerName,
          ticket.customerEmail,
          ticket.subject,
          ticket.assignee
        ].filter(value => typeof value === 'string')
         .join(' ').toLocaleLowerCase();

        if (
          (!query || haystack.includes(query)) &&
          (!status.value || ticket.status === status.value) &&
          (!priority.value || ticket.priority === priority.value) &&
          (!channel.value || ticket.channel === channel.value)
        ) {
          matches.add(ticket.id);
        }
      }

      let visible = 0;

      for (const card of Array.from(list.children)) {
        const management = card.querySelector(
          '.pc-create-management[data-ticket-id]'
        );
        if (!management) continue;

        const show = matches.has(management.dataset.ticketId);
        card.hidden = !show;
        if (show) visible++;
      }

      result.textContent =
        `${visible} of ${tickets.length} tickets displayed · ` +
        'Local prototype records';
    }

    for (const input of [search, status, priority, channel]) {
      input.addEventListener(
        input === search ? 'input' : 'change',
        render
      );
    }

    exportButton.addEventListener('click', () => {
      const tickets = readTickets();

      if (!tickets) {
        result.textContent = 'Export blocked: invalid ticket data.';
        return;
      }

      const payload = {
        format: 'AI Master operational tickets',
        version: 1,
        exportedAt: new Date().toISOString(),
        storage: 'Local prototype',
        tickets
      };

      const blob = new Blob(
        [JSON.stringify(payload, null, 2)],
        { type: 'application/json' }
      );
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');

      link.href = url;
      link.download =
        'aimaster-operational-tickets-' +
        new Date().toISOString().slice(0, 10) + '.json';

      document.body.append(link);
      link.click();
      link.remove();

      setTimeout(() => URL.revokeObjectURL(url), 1000);
    });

    // The existing lifecycle renderer owns the ticket cards.
    // Observe list replacement without adding a second lifecycle handler.
    const observer = new MutationObserver(render);
    observer.observe(list, { childList: true });

    window.addEventListener('storage', event => {
      if (event.key === KEY) render();
    });

    render();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize, { once: true });
  } else {
    initialize();
  }
})();
// END: prototype.ticket-create.operational-view

// BEGIN: prototype.productivity.loader
(() => {
  const script = document.createElement('script');
  script.src = '/static/js/prototype-productivity.js?v=aef15e036526615a';
  script.defer = true;
  document.head.append(script);
})();
// END: prototype.productivity.loader
