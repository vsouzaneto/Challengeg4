// OWNER: prototype.tickets-page.router
// BEGIN: prototype.tickets-page.router
(() => {
  'use strict';

  const TICKET_HASHES = new Set([
    '#pc-tickets-page',
    '#pc-ticket-create',
    '#pc-first-contact',
    '#pc-inbox'
  ]);

  function initialize() {
    const consoleRoot = document.querySelector(
      '#prototype .prototype-console'
    );
    const header = consoleRoot &&
      consoleRoot.querySelector('.pc-header');
    const ticketForm = document.getElementById('pc-ticket-create');
    const firstContact = document.getElementById('pc-first-contact');
    const inbox = document.getElementById('pc-inbox');
    const ticketLink = consoleRoot &&
      consoleRoot.querySelector(
        '.pc-navigation a[href="#pc-tickets-page"]'
      );
    const overviewLink = consoleRoot &&
      consoleRoot.querySelector(
        '.pc-navigation a[href="#pc-overview"]'
      );

    if (!consoleRoot || !header || !ticketForm ||
        !firstContact || !inbox || !ticketLink ||
        !overviewLink) {
      console.error('Tickets page: required components missing');
      return;
    }

    if (consoleRoot.dataset.ticketsPageReady === 'true') return;

    // No cloning: each operational module has exactly one DOM owner.
    const page = document.createElement('main');
    page.id = 'pc-tickets-page';
    page.className = 'pc-tickets-page';
    page.hidden = true;
    page.setAttribute('aria-label', 'Tickets workspace');

    const heading = document.createElement('header');
    heading.className = 'pc-tickets-page-heading';

    const titleGroup = document.createElement('div');
    const eyebrow = document.createElement('span');
    eyebrow.className = 'pc-tickets-page-eyebrow';
    eyebrow.textContent = 'CUSTOMER SUPPORT · OPERATIONS';

    const title = document.createElement('h1');
    title.textContent = 'Tickets';

    const description = document.createElement('p');
    description.textContent =
      'Create, review and handle support requests. ' +
      'Operational and historical records remain separate.';

    titleGroup.append(eyebrow, title, description);
    heading.append(titleGroup);

    const shortcuts = document.createElement('nav');
    shortcuts.className = 'pc-tickets-page-shortcuts';
    shortcuts.setAttribute('aria-label', 'Ticket sections');

    [
      ['New Ticket', '#pc-ticket-create'],
      ['First Contact', '#pc-first-contact'],
      ['All Historical Tickets', '#pc-inbox']
    ].forEach(([label, destination]) => {
      const link = document.createElement('a');
      link.href = destination;
      link.textContent = label;
      shortcuts.append(link);
    });

    const notice = document.createElement('p');
    notice.className = 'pc-tickets-page-disclosure';
    notice.textContent =
      'New tickets: browser-local prototype. ' +
      'Historical inbox: Dataset 1, read-only. ' +
      'Shared storage and unified operational search are pending.';

    page.append(heading, shortcuts, notice);

    // OWNER: prototype.copilot.global
    // BEGIN: prototype.copilot.global
    // Share the ORIGINAL complete AI-assisted operations panel.
    // Do not clone it or create a second Copilot banner.
    const copilot = document.getElementById('pc-copilot');

    if (!copilot || !consoleRoot.contains(copilot)) {
      console.error('Original AI Copilot panel missing');
      return;
    }

    // Canonical HTML owner: #pc-overview.pc-hero.
    // Its five areas are populated dynamically; never validate them
    // through textContent before rendering.
    const sharedPanel = document.getElementById('pc-overview');

    if (
      !sharedPanel ||
      !sharedPanel.classList.contains('pc-hero') ||
      sharedPanel.parentElement !== consoleRoot ||
      !sharedPanel.contains(copilot) ||
      sharedPanel === header
    ) {
      console.error('Canonical AI hero owner is unavailable');
      return;
    }

    // Move the single existing complete panel.
    // Original CSS, interactions and descendants are preserved.
    header.after(sharedPanel);
    sharedPanel.after(page);
    // END: prototype.copilot.global

    // Preserve each component's existing event listeners,
    // application state and storage key by moving actual nodes.
    page.append(ticketForm, firstContact, inbox);

    const overviewNodes = Array.from(consoleRoot.children)
      .filter(child =>
        child !== header &&
        child !== page &&
        child !== sharedPanel
      );

    const visibility = new Map(
      overviewNodes.map(child => [child, child.hidden])
    );

    function selectNavigation(onTickets) {
      ticketLink.classList.toggle('pc-nav-active', onTickets);
      overviewLink.classList.toggle('pc-nav-active', !onTickets);

      ticketLink.setAttribute(
        'aria-current', onTickets ? 'page' : 'false'
      );
      overviewLink.setAttribute(
        'aria-current', onTickets ? 'false' : 'page'
      );
    }

    function navigate() {
      const hash = window.location.hash;
      const onTickets = TICKET_HASHES.has(hash);

      consoleRoot.classList.toggle(
        'pc-tickets-view-active', onTickets
      );

      page.hidden = !onTickets;

      overviewNodes.forEach(child => {
        child.hidden = onTickets ? true : visibility.get(child);
      });

      selectNavigation(onTickets);

      if (!onTickets) return;

      // Direct links to a subsection work on initial load
      // and when navigating from another page.
      if (hash && hash !== '#pc-tickets-page') {
        const destination = document.querySelector(hash);
        if (destination && page.contains(destination)) {
          requestAnimationFrame(() => {
            destination.scrollIntoView({
              behavior: 'auto',
              block: 'start'
            });
          });
        }
      } else {
        requestAnimationFrame(() => {
          // Ticket navigation starts at the shared shell,
          // not below the globally mounted AI Copilot.
          header.scrollIntoView({
            behavior: 'auto',
            block: 'start'
          });
        });
      }
    }

    // The header's native anchor links remain the only
    // navigation owners. No duplicate click handlers.
    window.addEventListener('hashchange', navigate);

    consoleRoot.dataset.ticketsPageReady = 'true';
    navigate();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize, {
      once: true
    });
  } else {
    initialize();
  }
})();
// END: prototype.tickets-page.router
