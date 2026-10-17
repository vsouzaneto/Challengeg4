// BEGIN: prototype.notifications
(() => {
  'use strict';

  const TICKETS = 'aimaster.prototype.operational-tickets.v1';
  const DECISIONS = 'aimaster.prototype.automation-decisions.v1';
  const READ = 'aimaster.prototype.notification-read.v1';
  const host = document.querySelector('#prototype .prototype-console .pc-header .pc-header-tools');

  if (!host || document.getElementById('pc-notifications')) return;

  const root = document.createElement('div');
  root.id = 'pc-notifications';
  root.className = 'pc-notifications';

  const trigger = document.createElement('button');
  trigger.type = 'button';
  trigger.className = 'pc-notifications-trigger';
  trigger.setAttribute('aria-expanded', 'false');
  trigger.setAttribute('aria-controls', 'pc-notifications-panel');
  trigger.setAttribute('aria-label', 'Notifications');

  trigger.innerHTML = `
    <svg viewBox="0 0 24 24" fill="none"
         stroke="currentColor" stroke-width="1.8"
         stroke-linecap="round" stroke-linejoin="round"
         aria-hidden="true">
      <path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9"/>
      <path d="M10 21h4"/>
    </svg>
    <span class="pc-notifications-count" hidden></span>
  `;

  const count = trigger.querySelector('.pc-notifications-count');
  const panel = document.createElement('section');
  panel.id = 'pc-notifications-panel';
  panel.className = 'pc-notifications-panel';
  panel.hidden = true;
  panel.setAttribute('aria-label', 'Notification history');

  const heading = document.createElement('div');
  heading.className = 'pc-notifications-heading';

  const title = document.createElement('strong');
  title.textContent = 'Notifications';

  const markRead = document.createElement('button');
  markRead.type = 'button';
  markRead.textContent = 'Mark all as read';
  markRead.className = 'pc-notifications-mark-read';

  heading.append(title, markRead);

  const description = document.createElement('p');
  description.className = 'pc-notifications-description';
  description.textContent =
    'Local prototype events · No external notifications';

  const list = document.createElement('div');
  list.className = 'pc-notifications-list';

  const feedback = document.createElement('p');
  feedback.className = 'pc-notifications-feedback';
  feedback.setAttribute('aria-live', 'polite');

  panel.append(heading, description, list, feedback);
  root.append(trigger, panel);
  host.append(root);

  function readArray(key, limit) {
    try {
      const data = JSON.parse(localStorage.getItem(key) || '[]');
      return Array.isArray(data) && data.length <= limit ? data : [];
    } catch (_) {
      return [];
    }
  }

  function marked() {
    return readArray(READ, 5000).filter(x => typeof x === 'string');
  }

  function events() {
    const output = [];

    readArray(TICKETS, 500).forEach(ticket => {
      if (!ticket || typeof ticket.id !== 'string' ||
          ticket.source !== 'Local prototype') return;

      const date = ticket.createdAt || ticket.created_at;
      const time = Date.parse(date);
      if (!Number.isFinite(time)) return;

      output.push({
        id: 'ticket:' + ticket.id,
        title: 'Ticket created',
        detail: ticket.id + ' · ' +
          String(ticket.subject || 'Support request').slice(0, 100),
        time
      });
    });

    readArray(DECISIONS, 2000).forEach((decision, index) => {
      if (!decision || typeof decision.ticketId !== 'string' ||
          !['approved', 'rejected'].includes(decision.decision) ||
          decision.execution !== 'Simulation only') return;

      const time = Date.parse(decision.timestamp);
      if (!Number.isFinite(time)) return;

      output.push({
        id: 'decision:' + index + ':' +
          decision.ticketId + ':' + decision.timestamp,
        title: decision.decision === 'approved'
          ? 'Automation simulation approved'
          : 'Automation proposal rejected',
        detail: decision.ticketId + ' · Decision recorded',
        time
      });
    });

    return output.sort((a, b) =>
      b.time - a.time || a.id.localeCompare(b.id)
    );
  }

  function render() {
    const items = events();
    const seen = new Set(marked());
    const unread = items.filter(item => !seen.has(item.id)).length;

    count.hidden = unread === 0;
    count.textContent = unread > 99 ? '99+' : String(unread);

    trigger.setAttribute('aria-label',
      unread ? 'Notifications, ' + unread + ' unread'
             : 'Notifications, none unread');

    markRead.disabled = unread === 0;
    list.replaceChildren();

    if (!items.length) {
      const empty = document.createElement('p');
      empty.className = 'pc-notifications-empty';
      empty.textContent = 'No local notifications yet.';
      list.append(empty);
      return;
    }

    items.slice(0, 30).forEach(item => {
      const article = document.createElement('article');
      article.className = 'pc-notifications-item';

      if (!seen.has(item.id)) {
        article.classList.add('pc-notifications-unread');
      }

      const heading = document.createElement('strong');
      heading.textContent = item.title;

      const detail = document.createElement('p');
      detail.textContent = item.detail;

      const date = document.createElement('time');
      date.dateTime = new Date(item.time).toISOString();
      date.textContent = new Date(item.time).toLocaleString();

      article.append(heading, detail, date);
      list.append(article);
    });

    if (items.length > 30) {
      const note = document.createElement('p');
      note.className = 'pc-notifications-empty';
      note.textContent =
        'Showing the latest 30 of ' + items.length + ' events.';
      list.append(note);
    }
  }

  function close() {
    panel.hidden = true;
    trigger.setAttribute('aria-expanded', 'false');
  }

  trigger.addEventListener('click', () => {
    const opening = panel.hidden;
    render();
    panel.hidden = !opening;
    trigger.setAttribute('aria-expanded', String(opening));
  });

  markRead.addEventListener('click', () => {
    const seen = new Set(marked());
    events().forEach(item => seen.add(item.id));

    try {
      localStorage.setItem(
        READ, JSON.stringify([...seen].slice(-5000))
      );
      feedback.textContent = 'Notifications marked as read.';
    } catch (_) {
      feedback.textContent = 'Unable to save read status.';
    }
    render();
  });

  document.addEventListener('pointerdown', event => {
    if (!root.contains(event.target)) close();
  });

  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && !panel.hidden) {
      close();
      trigger.focus();
    }
  });

  window.addEventListener('storage', event => {
    if ([TICKETS, DECISIONS, READ].includes(event.key)) render();
  });

  window.addEventListener('focus', render);

  let previous = null;

  function synchronize() {
    try {
      const current = [
        localStorage.getItem(TICKETS),
        localStorage.getItem(DECISIONS),
        localStorage.getItem(READ)
      ].join('|');

      if (current !== previous) {
        previous = current;
        render();
      }
    } catch (_) {
      // Storage may be unavailable in restricted browser sessions.
    }
  }

  synchronize();
  window.setInterval(synchronize, 5000);
})();
// END: prototype.notifications
