// -----------------------------------------------------------------------------
// NAVIGATION
// -----------------------------------------------------------------------------
const navItems = [...document.querySelectorAll('.nav-item')];
const panels = [...document.querySelectorAll('.panel')];
const prototypeNavToggle = document.getElementById('prototype-nav-toggle');

if (prototypeNavToggle) {
  prototypeNavToggle.addEventListener('click', function() {
    if (!document.body.classList.contains('prototype-mode')) return;

    const expanded = document.body.classList.toggle('prototype-nav-open');
    prototypeNavToggle.setAttribute('aria-expanded', String(expanded));
    prototypeNavToggle.setAttribute(
      'aria-label',
      expanded ? 'Collapse navigation' : 'Open navigation'
    );
  });
}

function showPanel(id) {
  const isPrototype = id === 'prototype';
  document.body.classList.toggle('prototype-mode', isPrototype);
  document.body.classList.remove('prototype-nav-open');

  if (prototypeNavToggle) {
    prototypeNavToggle.disabled = !isPrototype;
    prototypeNavToggle.setAttribute('aria-expanded', 'false');
    prototypeNavToggle.setAttribute('aria-label', 'Open navigation');
  }

  const automationView = ["automation","automation-model-training","automation-reports","architecture-map"].includes(id);
  const automationNav = document.querySelector(".automation-stage-nav");
  if (automationNav) automationNav.classList.toggle("is-visible",automationView);

  navItems.forEach(i => i.classList.toggle('active', i.dataset.target === id));
  panels.forEach(p => p.classList.toggle('active', p.id === id));

  if (
    id === 'diagnosis-reports'
    && currentDiagnostic
    && currentDiagnostic.status === 'ready'
  ) {
    requestAnimationFrame(function() {
      renderDiagnosisReport(currentDiagnostic);
      renderDiagnosisSpecializedReport(currentDiagnostic);

      const activeReportView =
        document.querySelector(
          '#diagnosis-reports .report-view.active'
        );

      if (
        activeReportView
        && activeReportView.id
          === 'report-cross-analysis'
      ) {
        renderCrossAnalysis();
      }
    });
  }
}
// OWNER: navigation.prototype.entry
// BEGIN: navigation.prototype.entry
navItems.forEach(item => item.addEventListener('click', () => {
  const target = item.dataset.target;
  showPanel(target);

  // Main sidebar always opens the Prototype Overview.
  // The Prototype's internal navigation remains hash-driven.
  if (target === 'prototype') {
    window.location.hash = '#pc-overview';
  }
}));
// END: navigation.prototype.entry

// -----------------------------------------------------------------------------
// PROTOTYPE / UNIFIED INBOX — READ-ONLY DATASET 1 CONSUMER
// Canonical data owner: DatasetExplorer.rows, via existing authenticated API.
// -----------------------------------------------------------------------------
// -----------------------------------------------------------------------------


// ============================================================================
// ============================================================================
// OWNER: prototype.hero.recommendations
// BEGIN: prototype.hero.recommendations
// Responsibility: personalized support activities, guidance, training,
// human-review candidates and independent recommendation rotation.
// Observed data: authenticated Dataset 1 Explorer API.
// Training and procedures: curated operator content.
// No model inference or external customer action is claimed.

function initPrototypeHeroRecommendations() {
  const hero = document.getElementById('pc-overview');
  const panel = document.getElementById('pc-hero-recommendations');
  const toggle = document.getElementById('pc-hero-copilot-toggle');

  if (!hero || !panel || !toggle ||
      hero.dataset.heroInitialized === 'true') return;

  hero.dataset.heroInitialized = 'true';

  const cards = [...panel.querySelectorAll('.pc-hero-recommendation')];
  if (cards.length !== 4) return;

  // OWNER: prototype.hero.recommendations.content
  // BEGIN: prototype.hero.recommendations.content

  const guidance = [
    {
      title: 'Payment issue',
      detail: 'Confirm the charge before recommending a refund.',
      action: 'View procedure',
      steps: [
        'Confirm the customer identity and the affected purchase.',
        'Check the payment details recorded in the authorized system.',
        'Verify whether the transaction was captured or duplicated.',
        'Do not promise a refund before validating the policy.',
        'Document the findings and escalate exceptions.'
      ]
    },
    {
      title: 'Product malfunction',
      detail: 'Verify the product and troubleshooting already attempted.',
      action: 'View procedure',
      steps: [
        'Confirm the exact product and purchase information.',
        'Ask the customer to describe the observed symptoms.',
        'Check troubleshooting steps already performed.',
        'Avoid repeating actions the customer has completed.',
        'Assess warranty, replacement or technical escalation.'
      ]
    },
    {
      title: 'Cancellation request',
      detail: 'Clarify the request before processing the cancellation.',
      action: 'View procedure',
      steps: [
        'Confirm identity and the relevant purchase or subscription.',
        'Ask whether the request concerns cancellation or refund.',
        'Review the applicable cancellation policy.',
        'Explain the options without pressuring the customer.',
        'Record the decision and obtain required approval.'
      ]
    },
    {
      title: 'Account access',
      detail: 'Protect the account while restoring customer access.',
      action: 'View procedure',
      steps: [
        'Verify identity using approved authentication methods.',
        'Never request passwords or security codes in chat.',
        'Determine whether access is blocked or credentials were lost.',
        'Use the approved recovery procedure.',
        'Escalate any indication of unauthorized access.'
      ]
    }
  ];

  const training = [
    {
      title: 'Active listening',
      detail: 'Confirm your understanding before proposing a solution.',
      action: 'Practice skill',
      steps: [
        'Read the customer request without interrupting.',
        'Summarize the problem in one sentence.',
        'Confirm whether your summary is accurate.',
        'Ask one relevant follow-up question.',
        'Propose the next step only after identifying the need.'
      ]
    },
    {
      title: 'Empathy in support',
      detail: 'Recognize frustration without promising the impossible.',
      action: 'Practice skill',
      steps: [
        'Acknowledge the impact of the problem.',
        'Use clear language without excessive apologies.',
        'Explain what you can verify or do next.',
        'Avoid guaranteeing an outcome before validation.',
        'Communicate the expected next step.'
      ]
    },
    {
      title: 'Handling objections',
      detail: 'Identify the reason behind customer resistance.',
      action: 'Practice skill',
      steps: [
        'Allow the customer to explain the objection.',
        'Separate factual concerns from expectations.',
        'Check the relevant product or policy information.',
        'Offer only verified alternatives.',
        'Confirm agreement before continuing.'
      ]
    },
    {
      title: 'Effective escalation',
      detail: 'Transfer complex cases without losing context.',
      action: 'Practice skill',
      steps: [
        'Identify the reason the case requires escalation.',
        'Summarize the issue and customer impact.',
        'Include the product, attempts and relevant evidence.',
        'State clearly what decision or support is needed.',
        'Inform the customer of the next operational step.'
      ]
    }
  ];

  const queues = {
    priority: [],
    intelligence: []
  };

  function text(record, key, fallback = '') {
    const value = record && record[key];
    return value === null || value === undefined || value === ''
      ? fallback : String(value);
  }

  function eligible(record) {
    return text(record, 'Ticket Status').toLowerCase() !== 'closed';
  }

  async function fetchTickets(field, value) {
    const params = new URLSearchParams({
      page: '1',
      page_size: '100',
      filter_field: field,
      filter_value: value
    });

    const response = await fetch(
      '/api/explorer/dataset1/rows?' + params.toString(),
      {credentials: 'same-origin', cache: 'no-store'}
    );

    if (!response.ok) throw new Error('HTTP ' + response.status);

    const data = await response.json();

    if (data.status !== 'ready' || !Array.isArray(data.rows)) {
      throw new Error('Dataset response invalid');
    }

    return data.rows;
  }

  async function loadCandidates() {
    try {
      const [critical, high, pending, open] = await Promise.all([
        fetchTickets('Ticket Priority', 'Critical'),
        fetchTickets('Ticket Priority', 'High'),
        fetchTickets('Ticket Status', 'Pending Customer Response'),
        fetchTickets('Ticket Status', 'Open')
      ]);

      // Priority is historical; the recommended action is a review,
      // never an assertion that a live SLA has been breached.
      queues.priority = [
        ...critical.filter(eligible),
        ...high.filter(eligible)
      ];

      // Intelligence candidates require human review, not an
      // invented model decision or generated customer response.
      queues.intelligence = [
        ...pending,
        ...open
      ];

    } catch (error) {
      queues.priority = [];
      queues.intelligence = [];
    }
  }


  // BEGIN: prototype.hero.recommendations.briefing
  // Responsibility: explain review reasons and next actions.
  // Source: observed Dataset 1 fields and curated support procedures.

  function ticketBrief(ticket, humanReview) {
    const status = text(ticket, 'Ticket Status');
    const priority = text(ticket, 'Ticket Priority');
    const subject = text(ticket, 'Ticket Subject');
    const description = text(ticket, 'Ticket Description');
    const product = text(ticket, 'Product Purchased');
    const issue = (subject + ' ' + description).toLowerCase();

    let nextAction = 'Review the customer request and verify the '
      + 'purchase context before deciding the next step.';

    if (/payment|billing|refund|charge/.test(issue)) {
      nextAction = 'Verify the payment record and refund policy. '
        + 'Do not confirm adjustments without authorization.';
    } else if (/access|login|password|account/.test(issue)) {
      nextAction = 'Verify identity using the approved process '
        + 'before taking any account recovery action.';
    } else if (/cancel|return|warranty|replace/.test(issue)) {
      nextAction = 'Check purchase eligibility and policy '
        + 'before authorizing cancellation or replacement.';
    } else if (/compatib|hardware|software|network|setup|bug|product/.test(issue)) {
      nextAction = 'Confirm product details, symptoms and previous '
        + 'troubleshooting before escalating.';
    }

    let reason = 'Recorded priority: ' + priority
      + '. Confirm whether intervention is still required.';

    if (status.toLowerCase() === 'open') {
      reason = 'Case is marked Open. Verify whether an initial '
        + 'response or resolution action is needed.';
    } else if (status.toLowerCase() === 'pending customer response') {
      reason = 'Customer response is pending. Check the last '
        + 'contact before deciding on follow-up.';
    }

    if (humanReview) {
      reason = status.toLowerCase() === 'pending customer response'
        ? 'Human decision: confirm whether the customer has '
          + 'supplied the information needed to proceed.'
        : 'Human decision: assess whether the case can proceed '
          + 'or requires specialist approval.';
    }

    return 'WHY: ' + reason
      + '\nACTION: ' + nextAction
      + '\nPRODUCT: ' + (product || 'Check purchase record');
  }

  function guidanceBrief(item) {
    return item.steps.slice(0, 3).map((step, index) =>
      String(index + 1).padStart(2, '0') + '  ' + step
    ).join('\n');
  }

  function mentorBrief(item) {
    const examples = {
      'Active listening':
        'EXAMPLE: "So the issue is the device not connecting, correct?"',
      'Empathy in support':
        'EXAMPLE: "I understand how this affects your experience."',
      'Handling objections':
        'EXAMPLE: "Which part of this solution concerns you most?"',
      'Effective escalation':
        'EXAMPLE: "I will summarize the checks for our specialist."'
    };

    const practice = {
      'Active listening':
        'PRACTICE: Summarize a customer concern in one sentence.',
      'Empathy in support':
        'PRACTICE: Rewrite a defensive reply using empathy.',
      'Handling objections':
        'PRACTICE: Ask a clarifying question without arguing.',
      'Effective escalation':
        'PRACTICE: Prepare a concise handoff with relevant evidence.'
    };

    return [
      'TECHNIQUE: ' + item.steps[0],
      examples[item.title] || 'EXAMPLE: Confirm the customer concern.',
      practice[item.title] || 'PRACTICE: Apply the method to a ticket.'
    ].join('\n');
  }
  // END: prototype.hero.recommendations.briefing

  // END: prototype.hero.recommendations.content

  // OWNER: prototype.hero.recommendations.navigation
  // BEGIN: prototype.hero.recommendations.navigation

  function openTicket(ticket, briefing = '') {
    const channel = text(ticket, 'Ticket Channel');
    const openChannel = window.pcOpenChannelTicket;

    if (typeof openChannel !== 'function') {
      console.error('Channel workspace unavailable');
      return;
    }

    // Reuse the channel-specific workspace; do not create a parallel modal.
    openChannel(channel, ticket);

    const overlay = document.getElementById('pc-channel-dialog');
    const dialog = overlay && overlay.querySelector('.pc-ws-dialog');

    if (!dialog) return;

    const previous = dialog.querySelector('[data-pc-copilot-briefing]');
    if (previous) previous.remove();

    const briefingPanel = document.createElement('section');
    briefingPanel.className = 'pc-ws-copilot-briefing';
    briefingPanel.dataset.pcCopilotBriefing = 'true';

    const heading = document.createElement('h3');
    heading.textContent = 'AI Copilot · Operational briefing';

    const description = document.createElement('p');
    description.textContent = briefing ||
      'Review the customer request and available evidence.';

    const notice = document.createElement('small');
    notice.textContent =
      'Decision support · Human approval for customer actions';

    briefingPanel.append(heading, description, notice);

    const header = dialog.querySelector('header');
    if (header) {
      header.insertAdjacentElement('afterend', briefingPanel);
    } else {
      dialog.prepend(briefingPanel);
    }

  }

  const dialog = document.createElement('dialog');
  dialog.className = 'pc-hero-guidance-dialog';
  dialog.setAttribute('aria-label', 'Operator guidance');
  dialog.innerHTML =
    '<div class="pc-hero-guide-head">' +
      '<div><small id="pc-guide-type"></small>' +
      '<h2 id="pc-guide-title"></h2></div>' +
      '<button type="button" aria-label="Close guidance">×</button>' +
    '</div>' +
    '<p id="pc-guide-description"></p>' +
    '<ol id="pc-guide-steps"></ol>';

  document.body.append(dialog);

  dialog.querySelector('button').addEventListener(
    'click', () => dialog.close()
  );

  dialog.addEventListener('click', event => {
    if (event.target === dialog) dialog.close();
  });

  function openGuide(item, type) {
    dialog.querySelector('#pc-guide-type').textContent = type;
    dialog.querySelector('#pc-guide-title').textContent = item.title;
    dialog.querySelector('#pc-guide-description').textContent = item.detail;

    const list = dialog.querySelector('#pc-guide-steps');
    list.replaceChildren();

    item.steps.forEach(step => {
      const line = document.createElement('li');
      line.textContent = step;
      list.append(line);
    });

    dialog.showModal();
  }

  // END: prototype.hero.recommendations.navigation

  // OWNER: prototype.hero.recommendations.rotation
  // BEGIN: prototype.hero.recommendations.rotation

  const indices = [0, 0, 0, 0];
  const timers = [];
  const paused = [false, false, false, false];
  const reduceMotion = window.matchMedia(
    '(prefers-reduced-motion: reduce)'
  ).matches;

  function recommendation(type, position) {
    if (type === 0) {
      const records = queues.priority;
      if (!records.length) return null;
      const ticket = records[position % records.length];

      return {
        kind: 'priority',
        category: 'PRIORITY ACTION',
        title: 'Ticket #' + text(ticket, 'Ticket ID'),
        count: text(ticket, 'Ticket Subject'),
        description:
          text(ticket, 'Customer Name') + ' · ' +
          text(ticket, 'Ticket Priority') + ' · ' +
          text(ticket, 'Ticket Channel') + '\n' +
          ticketBrief(ticket, false),
        action: 'Review ticket',
        ticket
      };
    }

    if (type === 1) {
      const item = guidance[position % guidance.length];
      return {
        kind: 'guidance',
        category: 'SUPPORT GUIDANCE',
        title: item.title,
        count: 'Procedure',
        description: guidanceBrief(item),
        action: 'View full procedure',
        item
      };
    }

    if (type === 2) {
      const item = training[position % training.length];
      return {
        kind: 'training',
        category: 'AI SUPPORT MENTOR',
        title: item.title,
        count: 'Skill tip',
        description: mentorBrief(item),
        action: 'Practice skill',
        item
      };
    }

    const records = queues.intelligence;
    if (!records.length) return null;
    const ticket = records[position % records.length];

    return {
      kind: 'intelligence',
      category: 'HUMAN REVIEW',
      title: 'Ticket #' + text(ticket, 'Ticket ID'),
      count: text(ticket, 'Ticket Subject'),
      description:
        text(ticket, 'Customer Name') + ' · ' +
        text(ticket, 'Ticket Status') + '\n' +
        ticketBrief(ticket, true),
      action: 'Inspect case',
      ticket
    };
  }

  function render(index, animate = false) {
    const card = cards[index];
    const recommendationData = recommendation(index, indices[index]);

    if (!recommendationData) {
      card.disabled = true;
      card.querySelector('.pc-hero-rec-type').textContent =
        'DATA UNAVAILABLE';
      card.querySelector('strong').textContent = 'Queue unavailable';
      card.querySelector('[data-rec-count]').textContent = '—';
      card.querySelector('.pc-hero-rec-description').textContent =
        'Refresh the page to retry.';
      card.querySelector('.pc-hero-rec-cta').textContent = '';
      return;
    }

    const apply = () => {
      card.disabled = false;
      card.querySelector('.pc-hero-rec-type').textContent =
        recommendationData.category;
      card.querySelector('strong').textContent =
        recommendationData.title;
      card.querySelector('[data-rec-count]').textContent =
        recommendationData.count;
      card.querySelector('.pc-hero-rec-description').textContent =
        recommendationData.description;
      card.querySelector('.pc-hero-rec-cta').textContent =
        recommendationData.action + ' ↗';

      card.onclick = () => {
        if (recommendationData.ticket) {
          openTicket(
            recommendationData.ticket,
            recommendationData.description
          );
        } else {
          openGuide(
            recommendationData.item,
            recommendationData.category
          );
        }
      };

      card.classList.remove('pc-rec-switching');
    };

    if (!animate || reduceMotion) {
      apply();
      return;
    }

    // BEGIN: prototype.hero.rotation.vertical
    // All four cards share exactly the same transition.
    card.classList.remove('pc-rec-switching', 'pc-rec-entering');
    void card.offsetWidth;
    card.classList.add('pc-rec-switching');

    window.setTimeout(() => {
      // Apply the new recommendation after the old one exits.
      apply();

      card.classList.remove('pc-rec-switching');
      card.classList.add('pc-rec-entering');

      window.setTimeout(() => {
        card.classList.remove('pc-rec-entering');
      }, 720);
    }, 520);
    // END: prototype.hero.rotation.vertical
  }

  // Each frame has a 15-second cycle and a 4-second phase offset.
  function startRotation() {
    cards.forEach((card, index) => {
      card.addEventListener('mouseenter', () => paused[index] = true);
      card.addEventListener('mouseleave', () => paused[index] = false);
      card.addEventListener('focusin', () => paused[index] = true);
      card.addEventListener('focusout', () => paused[index] = false);

      const initialDelay = 15000 + index * 4000;

      timers.push(window.setTimeout(() => {
        function rotate() {
          if (!paused[index] && dialog.open === false) {
            indices[index]++;
            render(index, true);
          }
        }

        rotate();
        timers.push(window.setInterval(rotate, 15000));
      }, initialDelay));
    });
  }

  // END: prototype.hero.recommendations.rotation

  // OWNER: prototype.hero.recommendations.animation
  // BEGIN: prototype.hero.recommendations.animation

  function collapse(collapsed) {
    hero.classList.toggle('is-recommendations', collapsed);
    panel.setAttribute('aria-hidden', String(!collapsed));
    toggle.setAttribute('aria-expanded', String(!collapsed));

    cards.forEach(card => {
      card.tabIndex = collapsed ? 0 : -1;
    });

    toggle.tabIndex = collapsed ? 0 : -1;
  }

  let revealTimer = null;

  toggle.addEventListener('click', () => {
    collapse(false);

    if (revealTimer !== null) clearTimeout(revealTimer);

    revealTimer = window.setTimeout(
      () => collapse(true), 5000
    );
  });

  collapse(false);

  Promise.resolve(loadCandidates()).then(() => {
    cards.forEach((card, index) => render(index));
    startRotation();
  });

  revealTimer = window.setTimeout(
    () => collapse(true), 5000
  );

  // END: prototype.hero.recommendations.animation
}

if (document.readyState === 'loading') {
  document.addEventListener(
    'DOMContentLoaded',
    initPrototypeHeroRecommendations,
    {once: true}
  );
} else {
  initPrototypeHeroRecommendations();
}

// END: prototype.hero.recommendations

// OWNER: prototype.first-contact
// BEGIN: prototype.first-contact
// Read-only historical tickets + simulated first-contact assistance.
// The shared prototype.channels.router owns the ticket modal.

function initPrototypeFirstContact() {
  const root = document.getElementById('pc-first-contact');
  const list = document.getElementById('pc-first-contact-list');
  const count = document.getElementById('pc-first-contact-count');
  const more = document.getElementById('pc-first-contact-more');
  if (!root || !list || !count || !more || root.dataset.ready) return;
  root.dataset.ready = 'true';

  const channels = [
    ['Email', 'Email'],
    ['Phone', 'Phone'],
    ['Social media', 'Social Media'],
    ['Chat', 'Customer Chat']
  ];
  const state = {page: 0, loaded: 0, busy: false, seen: new Set()};

  function value(ticket, key) {
    const item = ticket[key];
    return item == null ? '' : String(item).trim();
  }

  function node(tag, content, className) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (content != null) element.textContent = String(content);
    return element;
  }

  // BEGIN: prototype.first-contact.draft
  // Deterministic examples built from real ticket context.
  // All client replies, model replies and outcomes are SIMULATIONS.

  const simulatedOutcomes = new Map();

  function scenario(ticket) {
    const id = value(ticket, 'Ticket ID');
    if (simulatedOutcomes.has(id)) return simulatedOutcomes.get(id);

    const issue = (
      value(ticket, 'Ticket Subject') + ' ' +
      value(ticket, 'Ticket Description')
    ).toLowerCase();

    const sensitive =
      /refund|payment|billing|charge|cancel|fraud|password|security/.test(issue);

    const informational =
      /how to|instructions|setup|configure|information|guide|connect|install/.test(issue);

    const hash = Array.from(id).reduce(
      (sum, character) => sum + character.charCodeAt(0), 0
    );

    const result = sensitive || hash % 3 === 0
      ? 'human'
      : informational && hash % 3 === 1
        ? 'resolved'
        : 'awaiting';

    simulatedOutcomes.set(id, result);
    return result;
  }

  const outcomeLabels = {
    resolved: 'AI Resolved',
    awaiting: 'Awaiting Customer',
    human: 'Human Intervention'
  };

  function questionFor(ticket) {
    const issue = (
      value(ticket, 'Ticket Subject') + ' ' +
      value(ticket, 'Ticket Description')
    ).toLowerCase();

    if (/refund|payment|billing|charge/.test(issue)) {
      return 'Could you identify the relevant purchase or charge? ' +
        'Please do not share payment card information.';
    }
    if (/access|password|login|account/.test(issue)) {
      return 'What happens when you try to sign in? ' +
        'Please do not share passwords or security codes.';
    }
    if (/compatib|device|product|hardware|software|setup/.test(issue)) {
      return 'Could you confirm the model and the steps already attempted?';
    }
    if (/cancel|return|warranty/.test(issue)) {
      return 'Could you clarify your preferred outcome so that ' +
        'the applicable policy can be reviewed?';
    }
    return 'Could you share a little more detail about the problem?';
  }

  function conversation(ticket, outcome) {
    const customer = value(ticket, 'Customer Name').split(/\s+/)[0]
      || 'Customer';
    const subject = value(ticket, 'Ticket Subject') || 'Support request';
    const description = value(ticket, 'Ticket Description');
    const product = value(ticket, 'Product Purchased');
    const introduction = 'Hello ' + customer +
      '. I can help collect information about "' + subject +
      '" before an operator reviews the case.';

    const turns = [
      {
        role: 'customer',
        label: customer + ' · Simulated',
        message: description || 'I need assistance with ' + subject + '.'
      },
      {
        role: 'ai',
        label: 'AI Assistant · Simulated',
        message: introduction
      }
    ];

    if (outcome === 'resolved') {
      turns.push(
        {
          role: 'ai',
          label: 'AI Assistant · Simulated',
          message: 'For this example, start by checking the product ' +
            'instructions, verifying the relevant connection or setting, ' +
            'and repeating the setup procedure. Did this resolve the issue?'
        },
        {
          role: 'customer',
          label: customer + ' · Simulated',
          message: 'Yes, I followed those steps and it is working now. ' +
            'Thank you.'
        },
        {
          role: 'ai',
          label: 'AI Assistant · Simulated',
          message: 'Thank you for confirming. I will mark this example ' +
            'conversation as resolved. The historical ticket remains Open.'
        }
      );
    } else if (outcome === 'human') {
      turns.push(
        {
          role: 'ai',
          label: 'AI Assistant · Simulated',
          message: questionFor(ticket)
        },
        {
          role: 'customer',
          label: customer + ' · Simulated',
          message: 'I would like someone to review the available options ' +
            'and confirm the next step.'
        },
        {
          role: 'ai',
          label: 'AI Assistant · Simulated',
          message: 'This case needs an operator to verify the evidence ' +
            'and authorize any consequential action. I am preparing ' +
            'the handoff; no action has been executed.'
        }
      );
    } else {
      turns.push(
        {
          role: 'ai',
          label: 'AI Assistant · Simulated',
          message: questionFor(ticket)
        },
        {
          role: 'ai',
          label: 'AI Assistant · Simulated',
          message: 'The example is now awaiting additional information. ' +
            'An operator can continue the conversation if necessary.'
        }
      );
    }

    return {
      turns,
      outcome,
      product,
      subject
    };
  }
  // END: prototype.first-contact.draft

  // BEGIN: prototype.first-contact.workspace
  // The existing channel modal remains the sole ticket modal.
  // All changes are local examples; no outbound communication.

  const contactSessions = new Map();

  function contactSession(ticket) {
    const id = value(ticket, 'Ticket ID');

    if (!contactSessions.has(id)) {
      contactSessions.set(id, {
        messages: [],
        outcome: scenario(ticket),
        owner: 'AI Assistant',
        channel: value(ticket, 'Ticket Channel')
      });
    }

    return contactSessions.get(id);
  }

  function renderFirstContactStatus(ticket) {
    const id = value(ticket, 'Ticket ID');
    const status = contactSession(ticket).outcome;

    list.querySelectorAll('.pc-fc-ticket').forEach(button => {
      if (button.dataset.fcTicketId !== id) return;

      const badge = button.querySelector('.pc-fc-outcome');
      if (!badge) return;

      badge.className = 'pc-fc-outcome pc-fc-outcome-' + status;
      badge.textContent = outcomeLabels[status] + ' · Simulation';
    });
  }

  function openContact(ticket, channel) {
    const openChannel = window.pcOpenChannelTicket;

    if (typeof openChannel !== 'function') {
      count.textContent = 'Ticket workspace unavailable.';
      return;
    }

    const session = contactSession(ticket);
    session.channel = channel;

    // Rebuild the canonical channel modal, not a second modal.
    openChannel(channel, ticket);

    const overlay = document.getElementById('pc-channel-dialog');
    const dialog = overlay && overlay.querySelector('.pc-ws-dialog');

    if (!dialog || overlay.hidden) return;

    const historicalWorkspace = dialog.querySelector(
      '.pc-ws-dialog-body'
    );

    if (!historicalWorkspace) return;

    const previous = dialog.querySelector('[data-fc-context]');
    if (previous) previous.remove();

    dialog.classList.add('pc-fc-focus');

    const panel = node('section', null, 'pc-fc-context');
    panel.dataset.fcContext = 'true';

    const heading = node('div', null, 'pc-fc-context-head');
    heading.append(
      node('strong', 'First Contact · AI Conversation'),
      node(
        'span',
        outcomeLabels[session.outcome] + ' · Simulation',
        'pc-fc-outcome pc-fc-outcome-' + session.outcome
      )
    );

    const update = node('span', 'Update', 'pc-fc-badge');
    heading.append(update);

    const notice = node(
      'p',
      'Demonstration workflow. Customer and AI messages are ' +
      'simulated; no message is sent. Historical ticket data ' +
      'and its recorded status remain unchanged.'
    );

    const conversationData = conversation(
      ticket, scenario(ticket)
    );

    const thread = node('div', null, 'pc-fc-conversation');
    thread.setAttribute('role', 'log');
    thread.setAttribute(
      'aria-label', 'Simulated first-contact conversation'
    );

    function addBubble(turn) {
      const bubble = node(
        'div',
        null,
        'pc-fc-message pc-fc-message-' + turn.role
      );

      bubble.append(
        node('strong', turn.label),
        node('p', turn.message)
      );

      thread.append(bubble);
    }

    conversationData.turns.forEach(addBubble);
    session.messages.forEach(addBubble);

    const actions = node('div', null, 'pc-fc-workflow-actions');
    const input = node('textarea', null, 'pc-fc-workflow-input');
    input.rows = 3;
    input.maxLength = 2000;
    input.placeholder = 'Write a simulated customer or AI message…';
    input.setAttribute('aria-label', 'Simulated message');

    const feedback = node('p', '', 'pc-fc-workflow-feedback');
    feedback.setAttribute('role', 'status');

    function saveTurn(role, label, message, outcome) {
      if (session.outcome === 'resolved') {
        feedback.textContent =
          'This simulated conversation is already resolved.';
        return;
      }

      session.messages.push({
        role,
        label,
        message
      });

      if (outcome) {
        session.outcome = outcome;
      }

      renderFirstContactStatus(ticket);
      openContact(ticket, session.channel);
    }

    function addAction(label, callback) {
      const button = node(
        'button',
        label,
        'pc-fc-workflow-button'
      );
      button.type = 'button';
      button.addEventListener('click', callback);
      actions.append(button);
      return button;
    }

    addAction('Add customer reply', () => {
      const message = input.value.trim();

      if (!message) {
        feedback.textContent = 'Enter a simulated customer reply.';
        input.focus();
        return;
      }

      saveTurn(
        'customer',
        'Customer · Simulation',
        message,
        'awaiting'
      );
    });

    addAction('Continue with AI', () => {
      const message = input.value.trim() || questionFor(ticket);

      saveTurn(
        'ai',
        'AI Assistant · Simulation',
        message,
        'awaiting'
      );
    });

    addAction('Human takeover', () => {
      if (session.owner === 'Operator') {
        feedback.textContent =
          'The operator has already assumed this conversation.';
        return;
      }

      session.owner = 'Operator';

      saveTurn(
        'human',
        'Operator · Simulation',
        'An operator has assumed this example conversation. ' +
        'The original ticket has not been reassigned.',
        'human'
      );
    });

    addAction('Confirm resolution', () => {
      if (session.outcome === 'human') {
        feedback.textContent =
          'Human review is required for this scenario.';
        return;
      }

      if (session.outcome === 'resolved') {
        feedback.textContent =
          'This simulated conversation is already resolved.';
        return;
      }

      const last = session.messages[session.messages.length - 1];
      const message = last && last.role === 'customer'
        ? last.message.trim()
        : '';

      const positive = /\b(resolved|fixed|working|solved)\b/i;
      const negative = /\b(not|never|still|isn.t|wasn.t|doesn.t|didn.t)\b/i;

      if (!positive.test(message) || negative.test(message)) {
        feedback.textContent =
          'Add a customer reply explicitly confirming the solution. ' +
          'The text in the composer alone is not confirmation.';
        return;
      }

      session.outcome = 'resolved';
      renderFirstContactStatus(ticket);
      openContact(ticket, session.channel);
    });

    const status = node(
      'div',
      'Scenario: ' + outcomeLabels[session.outcome] +
      ' · Owner: ' + session.owner,
      'pc-fc-workflow-status'
    );

    const channelSection = node(
      'div', null, 'pc-fc-workflow-channels'
    );

    channelSection.append(
      node('strong', 'Continue through a support channel')
    );

    const options = node('div', null, 'pc-fc-channels');

    channels.forEach(([key, label]) => {
      const button = node('button', null, 'pc-fc-channel');
      button.type = 'button';

      button.append(
        node('span', label),
        node(
          'small',
          key === value(ticket, 'Ticket Channel')
            ? 'Recorded channel'
            : 'Simulation'
        )
      );

      button.classList.toggle('is-selected', key === channel);
      button.setAttribute(
        'aria-pressed',
        String(key === channel)
      );

      button.addEventListener('click', () => {
        if (key !== channel) {
          session.messages.push({
            role: 'ai',
            label: 'System · Simulation',
            message: 'Channel switched to ' + label +
              ' for this demonstration.'
          });
          openContact(ticket, key);
        }
      });

      options.append(button);
    });

    channelSection.append(options);

    const originalToggle = node(
      'button',
      'View original channel workspace',
      'pc-fc-workflow-toggle'
    );
    originalToggle.type = 'button';

    originalToggle.addEventListener('click', () => {
      const showing = dialog.classList.toggle('pc-fc-show-original');
      originalToggle.textContent = showing
        ? 'Hide original channel workspace'
        : 'View original channel workspace';
    });

    const provenance = node(
      'p',
      'Historical creation date: Not recorded · ' +
      'Historical status: ' + value(ticket, 'Ticket Status') +
      ' · First response: Not recorded',
      'pc-fc-workflow-provenance'
    );

    panel.append(
      heading,
      provenance,
      notice,
      thread,
      status,
      input,
      actions,
      feedback,
      channelSection,
      originalToggle
    );

    const modalHeader = dialog.querySelector(':scope > header');
    if (modalHeader) {
      modalHeader.insertAdjacentElement('afterend', panel);
    } else {
      dialog.prepend(panel);
    }
  }
  // END: prototype.first-contact.workspace

  // BEGIN: prototype.first-contact.queue
  function appendTicket(ticket) {
    const id = value(ticket, 'Ticket ID');
    if (!id || state.seen.has(id)) return;
    state.seen.add(id);
    state.loaded++;

    const button = node('button', null, 'pc-fc-ticket');
    button.type = 'button';
    button.dataset.fcTicketId = id;

    const identity = node('span', null, 'pc-fc-identity');
    identity.append(
      node('strong', '#' + id + ' · ' +
        (value(ticket, 'Ticket Subject') || 'Support request')),
      node('small', value(ticket, 'Customer Name') + ' · ' +
        value(ticket, 'Ticket Channel'))
    );

    const metadata = node('span', null, 'pc-fc-metadata');
    metadata.append(
      node('span', value(ticket, 'Ticket Priority'), 'pc-fc-priority'),
      node('span', 'Update', 'pc-fc-badge'),
      node('span', 'Open ticket ↗', 'pc-fc-open')
    );

    metadata.append(
      node('span', 'Recorded: ' + value(ticket, 'Ticket Status'),
        'pc-fc-recorded-status'),
      node('span', outcomeLabels[scenario(ticket)] + ' · Simulation',
        'pc-fc-outcome pc-fc-outcome-' + scenario(ticket))
    );

    button.append(identity, metadata);
    button.addEventListener('click', () => {
      openContact(ticket, value(ticket, 'Ticket Channel'));
    });
    list.append(button);
  }

  async function load() {
    if (state.busy) return;
    state.busy = true;
    more.disabled = true;

    try {
      const params = new URLSearchParams({
        page: String(state.page + 1),
        page_size: '100',
        filter_field: 'Ticket Status',
        filter_value: 'Open'
      });
      const response = await fetch(
        '/api/explorer/dataset1/rows?' + params.toString(),
        {credentials: 'same-origin', cache: 'no-store'}
      );
      if (!response.ok) throw new Error('Request failed');

      const data = await response.json();
      if (data.status !== 'ready' || !Array.isArray(data.rows)
          || !data.pagination) {
        throw new Error('Invalid response');
      }

      if (state.page === 0) list.replaceChildren();
      state.page = Number(data.pagination.page);

      data.rows.filter(ticket => {
        const responseTime = value(ticket, 'First Response Time');
        return value(ticket, 'Ticket Status') === 'Open'
          && (!responseTime || responseTime === 'NaT');
      }).forEach(appendTicket);

      count.textContent =
        state.loaded.toLocaleString((window.AIMASTER_I18N_LANG === 'pt-BR' ? 'pt-BR' : 'en-US')) + ' candidates loaded · ' +
        Number(data.pagination.total_rows).toLocaleString((window.AIMASTER_I18N_LANG === 'pt-BR' ? 'pt-BR' : 'en-US')) +
        ' Open tickets in the historical dataset';

      more.hidden = state.page >= Number(data.pagination.total_pages);
      if (!state.loaded) {
        list.append(node('p', 'No matching records in this page.'));
      }
    } catch (error) {
      count.textContent = 'Unable to load first-contact candidates.';
      more.hidden = false;
    } finally {
      state.busy = false;
      more.disabled = false;
    }
  }

  more.addEventListener('click', load);
  load();
  // END: prototype.first-contact.queue
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded',
    initPrototypeFirstContact, {once:true});
} else {
  initPrototypeFirstContact();
}
// END: prototype.first-contact

// OWNER: prototype.channels
// Source: Dataset 1 / authenticated Dataset Explorer API.
// UI events are local to the current page. Raw records are read-only.
// BEGIN: prototype.channels
// ============================================================================
function initPrototypeChannelWorkspaces() {
  const root = document.getElementById('pc-channel-workspaces');
  const overlay = document.getElementById('pc-channel-dialog');
  const body = document.getElementById('pc-channel-dialog-body');

  if (!root || !overlay || !body || root.dataset.ready === 'true') return;
  root.dataset.ready = 'true';

  const title = document.getElementById('pc-ws-dialog-title');
  const mode = document.getElementById('pc-ws-dialog-mode');
  const closeButton = overlay.querySelector('[data-pc-close]');

  let lastFocus = null;
  const drafts = new Map();

  // OWNER: prototype.channels.shared
  // BEGIN: prototype.channels.shared
  const el = (tag, content, className) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (content !== undefined && content !== null) {
      node.textContent = String(content);
    }
    return node;
  };

  const value = (ticket, key, fallback = 'Not recorded') => {
    const item = ticket[key];
    return item === null || item === undefined || item === ''
      ? fallback : String(item);
  };

  function line(parent, caption, content) {
    const row = el('div', null, 'pc-ws-detail-row');
    row.append(el('span', caption), el('strong', content));
    parent.append(row);
  }

  function field(parent, caption, initial, multiline = false) {
    const label = el('label', null, 'pc-ws-field');
    label.append(el('span', caption));
    const control = el(multiline ? 'textarea' : 'input');
    if (!multiline) control.type = 'text';
    control.value = initial || '';
    label.append(control);
    parent.append(label);
    return control;
  }

  function button(parent, caption, handler) {
    const control = el('button', caption, 'pc-ws-button');
    control.type = 'button';
    control.addEventListener('click', handler);
    parent.append(control);
    return control;
  }

  function feedback(parent, message) {
    const current = parent.querySelector('.pc-ws-confirmation');
    if (current) current.remove();
    parent.append(el('p', message, 'pc-ws-confirmation'));
  }

  function hashTicket(ticket) {
    const text = String(ticket['Ticket ID'] || '');
    let hash = 0;
    for (const character of text) {
      hash = (hash * 31 + character.charCodeAt(0)) >>> 0;
    }
    return hash;
  }

  function context(ticket) {
    const aside = el('aside', null, 'pc-ws-context');
    aside.append(el('h3', 'Customer information'));

    [
      ['Customer', 'Customer Name'],
      ['Email', 'Customer Email'],
      ['Product', 'Product Purchased'],
      ['Purchase date', 'Date of Purchase'],
      ['Payment method', 'Payment Method'],
      ['Priority', 'Ticket Priority'],
      ['Status', 'Ticket Status']
    ].forEach(([caption, key]) => {
      line(aside, caption, value(ticket, key));
    });

    aside.append(el('h3', 'Resolution'));
    aside.append(el('p', value(ticket, 'Resolution', 'Pending')));

    return aside;
  }

  function close() {
    overlay.hidden = true;
    body.replaceChildren();
    if (lastFocus && lastFocus.isConnected) lastFocus.focus();
  }

  closeButton.addEventListener('click', close);

  overlay.addEventListener('click', event => {
    if (event.target === overlay) close();
  });

  overlay.addEventListener('keydown', event => {
    if (event.key === 'Escape') {
      event.preventDefault();
      close();
    }
    if (event.key !== 'Tab') return;

    const controls = Array.from(overlay.querySelectorAll(
      'button:not([disabled]),input:not([disabled]),textarea:not([disabled])'
    )).filter(item => item.getClientRects().length);

    if (!controls.length) return;

    const first = controls[0];
    const last = controls[controls.length - 1];

    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  });
  // END: prototype.channels.shared

  // OWNER: prototype.channels.phone
  // Reserved 555-01xx range: non-dialable fictional display data.
  // BEGIN: prototype.channels.phone
  function phoneNumber(ticket) {
    const hash = hashTicket(ticket);
    const area = ['202', '212', '415', '646'][hash % 4];
    const suffix = String(hash % 100).padStart(2, '0');
    return '+1 (' + area + ') 555-01' + suffix;
  }

  function phoneWorkspace(main, ticket) {
    line(main, 'Customer phone', phoneNumber(ticket));
    line(main, 'Contact status', 'Customer contact record');

    const report = field(main, 'Call report / customer statements', '', true);
    const key = 'phone:' + value(ticket, 'Ticket ID');

    if (drafts.has(key)) report.value = drafts.get(key);

    button(main, 'Start call', () => {
      feedback(main, 'Call opened. Record the conversation below.');
    });

    button(main, 'Save call report', () => {
      if (!report.value.trim()) {
        feedback(main, 'Enter the call report before saving.');
        return;
      }
      drafts.set(key, report.value);
      feedback(main, 'Call report saved in this workspace.');
    });
  }
  // END: prototype.channels.phone

  // OWNER: prototype.channels.social
  // BEGIN: prototype.channels.social
  // Historical ticket data is read-only.
  // Network attribution is PROJECTED, not an observed dataset field.

  const networks = [
    {name: 'Instagram', slug: 'instagram'},
    {name: 'Facebook', slug: 'facebook'},
    {name: 'X', slug: 'x'},
    {name: 'TikTok', slug: 'tiktok'}
  ];

  function socialNetwork(ticket) {
    return networks[hashTicket(ticket) % networks.length];
  }

  // OWNER: prototype.channels.social.logo
  // BEGIN: prototype.channels.social.logo
  // Dependency-free vector logos; no external image requests.
  function socialLogo(brand, size = 24) {
    const ns = 'http://www.w3.org/2000/svg';
    const svg = document.createElementNS(ns, 'svg');

    svg.setAttribute('viewBox', '0 0 24 24');
    svg.setAttribute('width', String(size));
    svg.setAttribute('height', String(size));
    svg.setAttribute('aria-hidden', 'true');
    svg.classList.add('pc-network-logo');

    function path(d, attrs = {}) {
      const node = document.createElementNS(ns, 'path');
      node.setAttribute('d', d);
      for (const [key, value] of Object.entries(attrs)) {
        node.setAttribute(key, String(value));
      }
      svg.append(node);
    }

    function circle(cx, cy, r, attrs = {}) {
      const node = document.createElementNS(ns, 'circle');
      node.setAttribute('cx', String(cx));
      node.setAttribute('cy', String(cy));
      node.setAttribute('r', String(r));
      for (const [key, value] of Object.entries(attrs)) {
        node.setAttribute(key, String(value));
      }
      svg.append(node);
    }

    if (brand.slug === 'instagram') {
      const rect = document.createElementNS(ns, 'rect');
      for (const [key, val] of Object.entries({
        x: 3, y: 3, width: 18, height: 18, rx: 5,
        fill: 'none', stroke: 'currentColor', 'stroke-width': 2
      })) {
        rect.setAttribute(key, String(val));
      }
      svg.append(rect);
      circle(12, 12, 4, {
        fill: 'none', stroke: 'currentColor', 'stroke-width': 2
      });
      circle(17.5, 6.5, 1.2, {fill: 'currentColor'});
    } else if (brand.slug === 'facebook') {
      path('M14.3 22V13.1h3l.45-3.5h-3.45V7.4c0-1.02.29-1.72 1.73-1.72H18V2.55C17.65 2.5 16.46 2.4 15.08 2.4c-2.9 0-4.88 1.77-4.88 5.02V9.6H7v3.5h3.2V22z',
        {fill: 'currentColor'});
    } else if (brand.slug === 'x') {
      path('M18.2 2H21l-6.2 7.1L22 22h-5.7l-4.5-6.4L6.2 22H3.4l7.1-8.2L2 2h5.8l4.1 5.9L18.2 2zm-1 18h1.5L6.9 3.9H5.3z',
        {fill: 'currentColor'});
    } else {
      path('M14 2h3c.3 2.3 1.5 3.7 4 4.1v3.3c-1.7 0-3.4-.5-4.8-1.5v7c0 4-2.5 6.9-6.2 6.9-3.4 0-6-2.7-6-6.1 0-3.7 3-6.4 6.8-6.2v3.4c-1.9-.3-3.4.9-3.4 2.8 0 1.6 1.2 2.7 2.7 2.7 1.7 0 2.8-1.2 2.8-3V2z',
        {fill: 'currentColor'});
    }

    return svg;
  }
  // END: prototype.channels.social.logo

  function socialBadge(brand) {
    const badge = el('span', null,
      'pc-social-badge pc-social-' + brand.slug);
    badge.append(socialLogo(brand, 22), el('strong', brand.name));
    return badge;
  }

  // OWNER: prototype.channels.social.workspace
  // BEGIN: prototype.channels.social.workspace
  // Four distinct platform layouts; one shared reply composer.
  function socialWorkspace(main, ticket) {
    const brand = socialNetwork(ticket);
    const customer = value(ticket, 'Customer Name');
    const subject = value(ticket, 'Ticket Subject');
    const description = value(ticket, 'Ticket Description');

    const shell = el('section', null,
      'pc-social-shell pc-social-' + brand.slug);

    const heading = el('header', null, 'pc-social-platform-head');
    heading.append(socialLogo(brand, 30), el('strong', brand.name));
    heading.append(el('span', {
      instagram: 'Direct Messages',
      facebook: 'Comments',
      x: 'Post & Replies',
      tiktok: 'Video Comments'
    }[brand.slug], 'pc-social-platform-mode'));
    shell.append(heading);

    const avatar = () => el('span',
      customer.charAt(0).toUpperCase(), 'pc-social-avatar');

    if (brand.slug === 'instagram') {
      const profile = el('div', null, 'pc-social-profile');
      profile.append(avatar());

      const identity = el('div');
      identity.append(el('strong', customer));
      identity.append(el('small', 'Messages'));
      profile.append(identity);
      shell.append(profile);

      const messages = el('div', null, 'pc-social-messages');
      messages.append(el('span', subject, 'pc-social-message-meta'));
      messages.append(el('div', description, 'pc-social-message-in'));
      shell.append(messages);

    } else if (brand.slug === 'facebook') {
      const post = el('article', null, 'pc-social-post');

      const author = el('div', null, 'pc-social-author');
      author.append(avatar());

      const identity = el('div');
      identity.append(el('strong', customer));
      identity.append(el('small', 'Customer post'));
      author.append(identity);

      post.append(author, el('p', description));
      shell.append(post);

      shell.append(el('div',
        'Like     Comment     Share', 'pc-social-reactions'));

      const comment = el('div', null, 'pc-social-comment');
      comment.append(el('strong', customer));
      comment.append(el('p', subject));
      shell.append(comment);

    } else if (brand.slug === 'x') {
      const post = el('article', null, 'pc-social-x-post');
      post.append(avatar());

      const content = el('div', null, 'pc-social-x-content');
      content.append(el('strong', customer));
      content.append(el('small', 'Customer · Support request'));
      content.append(el('p', description));

      post.append(content);
      shell.append(post);
      shell.append(el('div',
        'Reply      Repost      Like      Share',
        'pc-social-x-actions'));

    } else {
      const layout = el('div', null, 'pc-social-tiktok-layout');

      const video = el('div', null, 'pc-social-video');
      video.append(socialLogo(brand, 55));
      video.append(el('strong', subject));
      video.append(el('small', 'Customer content'));
      layout.append(video);

      const comments = el('section', null,
        'pc-social-tiktok-comments');
      comments.append(el('h4', 'Comments'));

      const comment = el('div', null,
        'pc-social-tiktok-comment');
      comment.append(avatar());

      const text = el('div');
      text.append(el('strong', customer));
      text.append(el('p', description));
      comment.append(text);

      comments.append(comment);
      layout.append(comments);
      shell.append(layout);
    }

    main.append(shell);

    const key = 'social:' + value(ticket, 'Ticket ID');
    const caption = brand.slug === 'instagram'
      ? 'Message'
      : brand.slug === 'x'
        ? 'Reply to post'
        : 'Write a comment';

    const reply = field(main, caption,
      drafts.get(key) || '', true);

    button(main, 'Save ' + brand.name + ' reply', () => {
      if (!reply.value.trim()) {
        feedback(main, 'Write your response first.');
        return;
      }
      drafts.set(key, reply.value.trim());
      feedback(main, 'Reply saved in this workspace.');
    });
  }
  // END: prototype.channels.social.workspace
  // END: prototype.channels.social

  // OWNER: prototype.channels.email
  // BEGIN: prototype.channels.email
  function emailWorkspace(main, ticket) {
    line(main, 'Customer email', value(ticket, 'Customer Email'));

    const subject = field(main, 'Subject',
      'Re: ' + value(ticket, 'Ticket Subject'));

    const key = 'email:' + value(ticket, 'Ticket ID');
    const suggested =
      'Hello ' + value(ticket, 'Customer Name') + ',\n\n'
      + 'Thank you for contacting us about '
      + value(ticket, 'Ticket Subject') + '. '
      + 'We are reviewing your request and the product information. '
      + 'We will provide the next steps shortly.\n\n'
      + 'Best regards,\nCustomer Support';

    const draft = field(main, 'Suggested reply',
      drafts.get(key) || suggested, true);

    button(main, 'Save draft', () => {
      if (!draft.value.trim() || !subject.value.trim()) {
        feedback(main, 'Subject and reply are required.');
        return;
      }
      drafts.set(key, draft.value);
      feedback(main, 'Email draft saved in this workspace.');
    });
  }
  // END: prototype.channels.email

  // OWNER: prototype.channels.chat
  // Thread uses the observed ticket description as its historical source.
  // No nonexistent customer messages or AI decisions are manufactured.
  // BEGIN: prototype.channels.chat
  function bubble(thread, text, sender) {
    const item = el('div', null, 'pc-chat-bubble pc-chat-' + sender);
    item.append(
      el('strong', sender === 'customer' ? 'Customer' : 'Support'),
      el('p', text)
    );
    thread.append(item);
    thread.scrollTop = thread.scrollHeight;
  }

  async function customerHistory(ticket, target) {
    const email = ticket['Customer Email'];
    if (!email) return;

    const params = new URLSearchParams({
      page: '1',
      page_size: '100',
      q: String(email)
    });

    try {
      const response = await fetch(
        '/api/explorer/dataset1/rows?' + params,
        {credentials: 'same-origin', cache: 'no-store'}
      );

      if (!response.ok) throw new Error('HTTP ' + response.status);
      const data = await response.json();

      const matches = (data.rows || []).filter(row =>
        String(row['Customer Email'] || '').toLowerCase() ===
        String(email).toLowerCase()
      );

      target.append(el('h3', 'Customer tickets'));

      matches.forEach(row => {
        target.append(el('div',
          '#' + value(row, 'Ticket ID') + ' · '
          + value(row, 'Ticket Subject') + ' · '
          + value(row, 'Ticket Status'),
          'pc-ws-history-item'
        ));
      });

      if (data.pagination && data.pagination.total_pages > 1) {
        target.append(el('small',
          'More records may exist beyond this search page.'));
      }
    } catch (error) {
      target.append(el('small', 'Ticket history could not be loaded.'));
    }
  }

  function chatWorkspace(main, aside, ticket) {
    main.classList.add('pc-chat-main');

    const chatHeader = el('div', null, 'pc-chat-header');
    chatHeader.append(
      el('strong', value(ticket, 'Customer Name')),
      el('span', 'Customer conversation')
    );
    main.append(chatHeader);

    const facts = el('div', null, 'pc-chat-facts');

    [
      'Product: ' + value(ticket, 'Product Purchased'),
      'Purchased: ' + value(ticket, 'Date of Purchase'),
      'Priority: ' + value(ticket, 'Ticket Priority'),
      'Status: ' + value(ticket, 'Ticket Status')
    ].forEach(text => {
      facts.append(el('span', text, 'pc-chat-chip'));
    });

    main.append(facts);

    const thread = el('div', null, 'pc-chat-thread');

    // Original description is observed; chat transcripts were not provided.
    bubble(thread, value(ticket, 'Ticket Description'), 'customer');

    const key = 'chat:' + value(ticket, 'Ticket ID');
    const messages = drafts.get(key) || [];
    messages.forEach(text => bubble(thread, text, 'agent'));

    main.append(thread);

    const composer = el('div', null, 'pc-chat-composer');
    const input = el('textarea');
    input.placeholder = 'Write a message...';
    composer.append(input);

    button(composer, 'Send', () => {
      const text = input.value.trim();
      if (!text) return;

      messages.push(text);
      drafts.set(key, messages);
      bubble(thread, text, 'agent');
      input.value = '';
    });

    main.append(composer);

    const history = el('section', null, 'pc-ws-history');
    aside.append(history);
    customerHistory(ticket, history);
  }
  // END: prototype.channels.chat

  // OWNER: prototype.channels.router
  // BEGIN: prototype.channels.router
  window.pcOpenChannelTicket = openTicket;
function openTicket(channel, ticket) {
    const workspaceDialog = overlay.querySelector('.pc-ws-dialog');
    if (workspaceDialog) {
      workspaceDialog.classList.remove(
        'pc-fc-focus', 'pc-fc-show-original'
      );
      workspaceDialog.querySelectorAll('[data-fc-context]').forEach(
        panel => panel.remove()
      );
    }

    lastFocus = document.activeElement;
    body.replaceChildren();

    mode.textContent = channel + ' · Customer Support';
    title.textContent = 'Ticket #' + value(ticket, 'Ticket ID')
      + ' — ' + value(ticket, 'Ticket Subject');

    const grid = el('div', null, 'pc-ws-dialog-grid');
    const main = el('div', null, 'pc-ws-dialog-main');
    const aside = context(ticket);

    grid.append(main, aside);
    body.append(grid);

    if (channel !== 'Chat') {
      main.append(el('h3', 'Customer request'));
      main.append(el('p', value(ticket, 'Ticket Description'),
        'pc-ws-note'));
    }

    if (channel === 'Email') emailWorkspace(main, ticket);
    else if (channel === 'Phone') phoneWorkspace(main, ticket);
    else if (channel === 'Social media') socialWorkspace(main, ticket);
    else if (channel === 'Chat') chatWorkspace(main, aside, ticket);

    overlay.hidden = false;
    closeButton.focus();
  }

  async function loadChannel(card) {
    const channel = card.dataset.channel;
    const list = card.querySelector('.pc-ws-tickets');
    const count = card.querySelector('.pc-ws-count');

    const params = new URLSearchParams({
      page: '1',
      page_size: '100',
      filter_field: 'Ticket Channel',
      filter_value: channel
    });

    try {
      const response = await fetch(
        '/api/explorer/dataset1/rows?' + params,
        {cache: 'no-store', credentials: 'same-origin'}
      );

      if (!response.ok) throw new Error('HTTP ' + response.status);

      const data = await response.json();
      if (data.status !== 'ready' || !Array.isArray(data.rows)) {
        throw new Error('Unexpected API contract');
      }

      count.textContent =
        Number(data.pagination.total_rows).toLocaleString() + ' tickets';

      let activeNetwork = 'All';
      const filters = card.querySelector('#pc-social-filters');

      function render() {
        list.replaceChildren();

        const records = channel === 'Social media' && activeNetwork !== 'All'
          ? data.rows.filter(ticket =>
              socialNetwork(ticket).name === activeNetwork)
          : data.rows;

        records.slice(0, 12).forEach(ticket => {
          const item = el('button', null, 'pc-ws-ticket');
          item.type = 'button';

          if (channel === 'Social media') {
            item.append(socialBadge(socialNetwork(ticket)));
          }

          item.append(
            el('strong', '#' + value(ticket, 'Ticket ID')
              + ' · ' + value(ticket, 'Ticket Subject')),
            el('span', value(ticket, 'Customer Name')
              + ' · ' + value(ticket, 'Ticket Priority'))
          );

          item.addEventListener('click', () => openTicket(channel, ticket));
          list.append(item);
        });

        if (!records.length) {
          list.append(el('p', 'No tickets in this selection.'));
        }
      }

      if (filters) {
        filters.replaceChildren();

        ['All', ...networks.map(item => item.name)].forEach(name => {
          const control = el('button', name, 'pc-social-filter');
          control.type = 'button';
          control.addEventListener('click', () => {
            activeNetwork = name;
            filters.querySelectorAll('button').forEach(item =>
              item.classList.toggle('is-active',
                item === control)
            );
            render();
          });
          control.classList.toggle('is-active', name === 'All');
          filters.append(control);
        });
      }

      render();

    } catch (error) {
      count.textContent = 'Unavailable';
      list.replaceChildren(el('p',
        'Unable to load tickets: ' + error.message));
    }
  }

  root.querySelectorAll('.pc-channel-workspace').forEach(loadChannel);
  // END: prototype.channels.router
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded',
    initPrototypeChannelWorkspaces);
} else {
  initPrototypeChannelWorkspaces();
}
// END: prototype.channels
function initPrototypeInbox() {
  const root = document.getElementById('pc-inbox');
  const form = document.getElementById('pc-ticket-search');
  if (!root || !form || root.dataset.ticketInitialized === 'true') return;

  const elements = {
    query: document.getElementById('pc-ticket-query'),
    filter: document.getElementById('pc-ticket-filter'),
    filterValue: document.getElementById('pc-ticket-filter-value'),
    reset: document.getElementById('pc-ticket-reset'),
    status: document.getElementById('pc-ticket-status'),
    list: document.getElementById('pc-ticket-list'),
    detail: document.getElementById('pc-ticket-detail-content'),
    total: document.getElementById('pc-ticket-total'),
    page: document.getElementById('pc-ticket-page'),
    prev: document.getElementById('pc-ticket-prev'),
    next: document.getElementById('pc-ticket-next')
  };
  if (Object.values(elements).some(element => !element)) return;

  root.dataset.ticketInitialized = 'true';

  const state = {
    page: 1,
    pages: 1,
    request: 0,
    records: []
  };

  function node(tag, value, className) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (value !== undefined && value !== null) {
      element.textContent = String(value);
    }
    return element;
  }

  function value(record, key) {
    const item = record[key];
    return item === null || item === undefined || item === ''
      ? 'Not recorded'
      : String(item);
  }

  function field(container, label, content) {
    const row = node('div', null, 'pc-ticket-field');
    row.appendChild(node('dt', label));
    row.appendChild(node('dd', content));
    container.appendChild(row);
  }

  function showTicket(record) {
    elements.detail.replaceChildren();

    const heading = node('div', null, 'pc-ticket-selected-heading');
    heading.appendChild(node('strong', 'Ticket #' + value(record, 'Ticket ID')));
    heading.appendChild(node('span', value(record, 'Ticket Status')));
    elements.detail.appendChild(heading);

    const main = node('div', null, 'pc-ticket-selected-main');
    main.appendChild(node('h4', value(record, 'Ticket Subject')));
    main.appendChild(node('p', value(record, 'Ticket Description')));
    elements.detail.appendChild(main);

    const details = node('dl', null, 'pc-ticket-fields');
    [
      ['Customer', 'Customer Name'],
      ['Customer email', 'Customer Email'],
      ['Product purchased', 'Product Purchased'],
      ['Purchase date', 'Date of Purchase'],
      ['Channel', 'Ticket Channel'],
      ['Priority', 'Ticket Priority'],
      ['Ticket type', 'Ticket Type'],
      ['Status', 'Ticket Status'],
      ['First response time', 'First Response Time'],
      ['Time to resolution', 'Time to Resolution'],
      ['Customer satisfaction', 'Customer Satisfaction Rating']
    ].forEach(([label, key]) => field(details, label, value(record, key)));

    elements.detail.appendChild(details);

    const resolution = node('section', null, 'pc-ticket-resolution');
    resolution.appendChild(node('strong', 'Recorded resolution'));
    resolution.appendChild(node('p', value(record, 'Resolution')));
    elements.detail.appendChild(resolution);
  }

  function showRows(rows) {
    elements.list.replaceChildren();
    state.records = rows;

    if (!rows.length) {
      elements.status.textContent = 'No tickets match the selected filters.';
      elements.detail.replaceChildren();
      elements.detail.appendChild(node('p', 'No ticket selected.'));
      return;
    }

    elements.status.textContent = '';

    rows.forEach((record, index) => {
      const button = node('button', null, 'pc-ticket-row');
      button.type = 'button';

      const top = node('div', null, 'pc-ticket-row-top');
      top.appendChild(node('strong', '#' + value(record, 'Ticket ID')));
      top.appendChild(node('span', value(record, 'Ticket Channel')));
      button.appendChild(top);

      button.appendChild(
        node('div', value(record, 'Ticket Subject'), 'pc-ticket-row-subject')
      );

      const bottom = node('div', null, 'pc-ticket-row-bottom');
      bottom.appendChild(node('span', value(record, 'Customer Name')));
      bottom.appendChild(node('span', value(record, 'Ticket Priority')));
      button.appendChild(bottom);

      button.addEventListener('click', () => {
        elements.list.querySelectorAll('.pc-ticket-row').forEach(item => {
          item.classList.remove('is-selected');
          item.setAttribute('aria-pressed', 'false');
        });
        button.classList.add('is-selected');
        button.setAttribute('aria-pressed', 'true');
        showTicket(record);
      });

      elements.list.appendChild(button);

      if (index === 0) button.click();
    });
  }

  async function loadTickets() {
    const request = ++state.request;
    elements.status.textContent = 'Loading historical tickets...';
    elements.prev.disabled = true;
    elements.next.disabled = true;

    const params = new URLSearchParams({
      page: String(state.page),
      page_size: '25'
    });

    const query = elements.query.value.trim();
    const filter = elements.filter.value;
    const filterValue = elements.filterValue.value.trim();

    if (query) params.set('q', query);
    if (filter && filterValue) {
      params.set('filter_field', filter);
      params.set('filter_value', filterValue);
    }

    try {
      const response = await fetch(
        '/api/explorer/dataset1/rows?' + params.toString(),
        {cache: 'no-store', credentials: 'same-origin'}
      );

      if (!response.ok) throw new Error('HTTP ' + response.status);

      const data = await response.json();
      if (request !== state.request) return;

      if (data.status !== 'ready' || !Array.isArray(data.rows)
          || !data.pagination) {
        throw new Error('Dataset 1 is not available.');
      }

      state.page = data.pagination.page;
      state.pages = data.pagination.total_pages;
      elements.total.textContent =
        Number(data.pagination.total_rows).toLocaleString() + ' tickets';
      elements.page.textContent =
        'Page ' + state.page + ' of ' + state.pages;
      elements.prev.disabled = state.page <= 1;
      elements.next.disabled = state.page >= state.pages;
      showRows(data.rows);

    } catch (error) {
      if (request !== state.request) return;
      elements.list.replaceChildren();
      elements.status.textContent = 'Unable to load tickets: ' + error.message;
      elements.total.textContent = 'Unavailable';
      elements.page.textContent = 'Page —';
      elements.detail.replaceChildren();
      elements.detail.appendChild(
        node('p', 'Ticket details are unavailable until data can be loaded.')
      );
    }
  }

  form.addEventListener('submit', event => {
    event.preventDefault();
    state.page = 1;
    loadTickets();
  });

  elements.reset.addEventListener('click', () => {
    elements.query.value = '';
    elements.filter.value = '';
    elements.filterValue.value = '';
    state.page = 1;
    loadTickets();
  });

  elements.prev.addEventListener('click', () => {
    if (state.page > 1) {
      state.page -= 1;
      loadTickets();
    }
  });

  elements.next.addEventListener('click', () => {
    if (state.page < state.pages) {
      state.page += 1;
      loadTickets();
    }
  });

  loadTickets();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initPrototypeInbox);
} else {
  initPrototypeInbox();
}


function enhanceAutomationTrainingLayout() {
  const panel = document.getElementById('automation-model-training');
  if (!panel || panel.dataset.layoutEnhanced === 'true') return;

  const children = [...panel.children];
  const h2Index = children.findIndex(el => el.tagName === 'H2');
  const firstH3Index = children.findIndex(el => el.tagName === 'H3');

  if (h2Index === -1 || firstH3Index === -1 || firstH3Index <= h2Index) return;

  panel.classList.add('training-panel-shell');

  const introNodes = children.slice(h2Index + 1, firstH3Index);
  const introText = introNodes.map(node => node.textContent.trim()).filter(Boolean);

  const summaryGrid = document.createElement('div');
  summaryGrid.className = 'training-summary-grid';

  const metrics = [];
  const corpusLine = introText[0] || '';
  const selectedLine = introText.find(text => text.includes('Selected model')) || '';

  const docsMatch = corpusLine.match(/([0-9][0-9,\.]*)\s+documents/i);
  const classMatch = corpusLine.match(/([0-9]+)\s+classes/i);
  const modelMatch = selectedLine.match(/Selected model:\s*([^·]+)/i);
  const macroMatch = selectedLine.match(/Test Macro-F1:\s*([0-9.]+%)/i);

  if (docsMatch) metrics.push(['Training corpus', docsMatch[1], 'Dataset 2 labeled documents']);
  if (classMatch) metrics.push(['Classes', classMatch[1], 'Supervised topic groups']);
  if (modelMatch) metrics.push(['Selected model', modelMatch[1].trim(), 'Highest validation macro-F1']);
  if (macroMatch) metrics.push(['Test Macro-F1', macroMatch[1], 'Held-out benchmark result']);

  metrics.forEach(([label, value, note]) => {
    const card = document.createElement('article');
    card.className = 'training-metric-card';

    const eyebrow = document.createElement('span');
    eyebrow.textContent = label;

    const strong = document.createElement('strong');
    strong.textContent = value;

    const helper = document.createElement('p');
    helper.textContent = note;

    card.appendChild(eyebrow);
    card.appendChild(strong);
    card.appendChild(helper);
    summaryGrid.appendChild(card);
  });

  const firstHeading = children[firstH3Index];
  if (metrics.length) panel.insertBefore(summaryGrid, firstHeading);

  const detailGrid = document.createElement('div');
  detailGrid.className = 'training-detail-grid';
  panel.insertBefore(detailGrid, firstHeading);

  const contextCard = document.createElement('article');
  contextCard.className = 'training-detail-card training-context-card is-wide';

  const contextTitle = document.createElement('h3');
  contextTitle.textContent = 'Benchmark scope';
  contextCard.appendChild(contextTitle);

  introNodes.forEach(node => contextCard.appendChild(node));
  detailGrid.appendChild(contextCard);

  const headings = [...panel.querySelectorAll(':scope > h3')];
  headings.forEach(heading => {
    const card = document.createElement('article');
    card.className = 'training-detail-card';

    const normalized = heading.textContent.trim().toLowerCase();
    if (
      normalized.includes('performance by class')
      || normalized.includes('confusion matrix')
    ) {
      card.classList.add('is-wide');
    }

    panel.insertBefore(card, heading);
    card.appendChild(heading);

    let node = card.nextElementSibling;
    while (node && node.tagName !== 'H3') {
      const next = node.nextElementSibling;
      card.appendChild(node);
      node = next;
    }

    detailGrid.appendChild(card);
  });

  detailGrid.querySelectorAll('table').forEach(table => {
    table.classList.add('training-table');
  });

  detailGrid.querySelectorAll('p').forEach(p => {
    p.classList.add('training-copy');
  });

  panel.dataset.layoutEnhanced = 'true';
}

enhanceAutomationTrainingLayout();

// -----------------------------------------------------------------------------
// FORMATTERS AND SHARED STATE
// -----------------------------------------------------------------------------
const fmt = new Intl.NumberFormat((window.AIMASTER_I18N_LANG === 'pt-BR' ? 'pt-BR' : 'en-US'));
const pct = value => `${Number(value || 0).toLocaleString((window.AIMASTER_I18N_LANG === 'pt-BR' ? 'pt-BR' : 'en-US'), {minimumFractionDigits: 1, maximumFractionDigits: 2})}%`;
const dec = value => Number(value || 0).toLocaleString((window.AIMASTER_I18N_LANG === 'pt-BR' ? 'pt-BR' : 'en-US'), {minimumFractionDigits: 2, maximumFractionDigits: 4});
let currentAudit = null;
let currentDiagnostic = null;
const charts = {};

// -----------------------------------------------------------------------------
// DIAGNOSIS REPORTS · NAVIGATION
// -----------------------------------------------------------------------------
const reportTabs = [
  ...document.querySelectorAll(
    '.report-tab[data-report-target]'
  )
];

const reportViews = [
  ...document.querySelectorAll(
    '#diagnosis-reports .report-view'
  )
];

function showDiagnosisReport(id) {
  const target = document.getElementById(id);

  if (!target) return;

  reportTabs.forEach(function(button) {
    const active =
      button.dataset.reportTarget === id;

    button.classList.toggle(
      'active',
      active
    );

    button.setAttribute(
      'aria-selected',
      active ? 'true' : 'false'
    );

    if (active) {
      button.setAttribute(
        'aria-current',
        'page'
      );
    } else {
      button.removeAttribute(
        'aria-current'
      );
    }
  });

  reportViews.forEach(function(view) {
    view.classList.toggle(
      'active',
      view.id === id
    );
  });

  if (
    currentDiagnostic
    && currentDiagnostic.status === 'ready'
  ) {
    requestAnimationFrame(function() {
      if (
        id === 'report-general-overview'
      ) {
        renderDiagnosisReport(
          currentDiagnostic
        );
      } else if (
        id === 'report-cross-analysis'
      ) {
        renderCrossAnalysis();
      } else {
        renderDiagnosisSpecializedReport(
          currentDiagnostic
        );
      }
    });
  }
}

reportTabs.forEach(function(button) {
  button.addEventListener(
    'click',
    function() {
      showDiagnosisReport(
        button.dataset.reportTarget
      );
    }
  );
});

function setText(id, value) { const el = document.getElementById(id); if (el) el.textContent = value; }

// -----------------------------------------------------------------------------
// DATA QUALITY AND AUDIT
// -----------------------------------------------------------------------------
async function loadAudit() {
  const summary = document.getElementById('audit-summary');
  const findingsEl = document.getElementById('audit-findings');
  const details = document.getElementById('dataset-details');
  try {
    const response = await fetch('/api/audit', {cache: 'no-store'});
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    currentAudit = data;
    document.getElementById('dataset-count').textContent = `${data.dataset_count} dataset${data.dataset_count === 1 ? '' : 's'}`;
    document.getElementById('system-status').textContent = data.status === 'ready' ? 'Audit engine active' : 'Awaiting datasets';
    document.getElementById('data-progress').style.width = data.dataset_count >= 2 ? '100%' : data.dataset_count === 1 ? '50%' : '0%';
    document.getElementById('data-readiness').textContent = data.dataset_count ? `${data.dataset_count}/2 datasets detected in data/raw/.` : 'Waiting for datasets in data/raw/.';

    const totalRows = data.datasets.reduce((acc, d) => acc + d.rows, 0);
    const totalDupes = data.datasets.reduce((acc, d) => acc + d.duplicate_rows, 0);
    const totalMissing = data.datasets.reduce((acc, d) => acc + d.missing_cells, 0);
    summary.innerHTML = `<div class="audit-metrics">
      <div class="audit-metric"><span>Datasets detected</span><strong>${fmt.format(data.dataset_count)}</strong></div>
      <div class="audit-metric"><span>Records read</span><strong>${fmt.format(totalRows)}</strong></div>
      <div class="audit-metric"><span>Duplicate rows</span><strong>${fmt.format(totalDupes)}</strong></div>
      <div class="audit-metric"><span>Missing cells</span><strong>${fmt.format(totalMissing)}</strong></div>
    </div>`;

    findingsEl.innerHTML = data.findings.length ? data.findings.map(f => `<article class="finding ${f.severity}"><h4>${escapeHtml(f.title)}</h4><p>${escapeHtml(f.detail)}</p><p><strong>Impact:</strong> ${escapeHtml(f.impact)}</p></article>`).join('') : '<div class="empty">No data-quality issues detected.</div>';

    renderOverview();

    details.innerHTML = data.datasets.map(d => {
      const temporal = renderTemporal(d.temporal || {});
      const previews = renderPreviews(d.operational_preview || {});
      return `<article class="dataset-card">
        <h3>${escapeHtml(d.file)}</h3>
        <div class="dataset-meta"><span>${fmt.format(d.rows)} records</span><span>${fmt.format(d.columns)} columns</span><span>${escapeHtml(d.kind)}</span></div>
        ${temporal}${previews}
        <table><thead><tr><th>Field</th><th>Type</th><th>Missing</th><th>Missing %</th><th>Unique</th></tr></thead><tbody>
        ${d.column_profiles.map(c => `<tr><td>${escapeHtml(c.name)}</td><td>${escapeHtml(c.dtype)}</td><td>${fmt.format(c.missing)}</td><td>${c.missing_pct.toFixed(2)}%</td><td>${fmt.format(c.unique)}</td></tr>`).join('')}
        </tbody></table>
      </article>`;
    }).join('');
  } catch (err) {
    summary.innerHTML = `<div class="empty">Failed to load audit: ${escapeHtml(err.message)}</div>`;
  }
}

function renderTemporal(temporal) {
  const pair = temporal.response_resolution_pair;
  const purchase = temporal['date of purchase'];
  if (!pair && !purchase) return '';
  const items = [];
  if (purchase) items.push(`<div><span>Purchase range</span><strong>${escapeHtml(String(purchase.min).slice(0,10))} → ${escapeHtml(String(purchase.max).slice(0,10))}</strong><small>does not represent ticket creation</small></div>`);
  if (pair) {
    items.push(`<div><span>Comparable timestamp pairs</span><strong>${fmt.format(pair.comparable_rows)}</strong></div>`);
    items.push(`<div><span>Resolution earlier than first response</span><strong>${fmt.format(pair.resolution_before_first_response)} · ${pct(pair.resolution_before_first_response_pct)}</strong></div>`);
    items.push(`<div><span>Same second component in both timestamps</span><strong>${fmt.format(pair.same_second_component)} · ${pct(pair.same_second_component_pct)}</strong></div>`);
  }
  return `<div class="evidence-grid">${items.join('')}</div>`;
}

function renderPreviews(previews) {
  const entries = Object.entries(previews);
  if (!entries.length) return '';
  return `<div class="preview-grid">${entries.map(([name, rows]) => `<div><h4>${escapeHtml(name)}</h4>${rows.slice(0,8).map(r => `<p><span>${escapeHtml(r.label)}</span><strong>${fmt.format(r.count)}</strong></p>`).join('')}</div>`).join('')}</div>`;
}

// -----------------------------------------------------------------------------
// OPERATIONAL DIAGNOSIS
// -----------------------------------------------------------------------------
async function loadDiagnostic() {
  const bottleneck = document.getElementById('bottleneck-result');
  const workflowAnswer = bottleneck
    ? bottleneck.previousElementSibling
    : null;
  const satisfaction = document.getElementById('satisfaction-result');
  const waste = document.getElementById('waste-result');
  const evidence = document.getElementById('diagnostic-evidence');
  try {
    const response = await fetch('/api/diagnostic', {cache: 'no-store'});
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    currentDiagnostic = data;
    if (data.status !== 'ready') throw new Error(data.message || 'Diagnosis unavailable');
    renderExplorerEvidence();

    const reportsPanel = document.getElementById('diagnosis-reports');

    if (
      reportsPanel
      && reportsPanel.classList.contains('active')
    ) {
      requestAnimationFrame(function() {
        renderDiagnosisReport(data);
        renderDiagnosisSpecializedReport(data);

        const activeReportView =
          document.querySelector(
            '#diagnosis-reports .report-view.active'
          );

        if (
          activeReportView
          && activeReportView.id
            === 'report-cross-analysis'
        ) {
          renderCrossAnalysis();
        }
      });
    }

    const state = document.getElementById('diagnostic-state');
    state.textContent = 'Observed data loaded';
    state.classList.remove('pending');
    state.classList.add('active-state');

    const flow = data.flow.snapshot;
    const dimensions = data.flow.dimensions;

    const channelRows = Array.from(
      dimensions["Ticket Channel"] || []
    );

    const priorityRows = Array.from(
      dimensions["Ticket Priority"] || []
    );

    const typeRows = Array.from(
      dimensions["Ticket Type"] || []
    ).sort(
      (a, b) =>
        Number(b.unresolved || 0)
        - Number(a.unresolved || 0)
    );

    const channelVolume = Array.from(
      channelRows
    ).sort(
      (a, b) =>
        Number(b.unresolved || 0)
        - Number(a.unresolved || 0)
    )[0] || {};

    const channelRate = Array.from(
      channelRows
    ).sort(
      (a, b) =>
        Number(b.unresolved_pct || 0)
        - Number(a.unresolved_pct || 0)
    )[0] || {};

    const priorityVolume = Array.from(
      priorityRows
    ).sort(
      (a, b) =>
        Number(b.unresolved || 0)
        - Number(a.unresolved || 0)
    )[0] || {};

    const priorityRate = Array.from(
      priorityRows
    ).sort(
      (a, b) =>
        Number(b.unresolved_pct || 0)
        - Number(a.unresolved_pct || 0)
    )[0] || {};

    const closedTime =
      data.bottleneck_combinations.closed_resolution_time;

    const overallMedian = Number(
      closedTime.overall_median_hours || 0
    );

    const ticketRiskFields = [
      "open",
      "pending",
      "unresolved",
      "unresolved_pct"
    ];

    const ticketRiskRanks = {};

    ticketRiskFields.forEach(field => {
      ticketRiskRanks[field] = Array.from(
        typeRows
      ).sort(
        (a, b) =>
          Number(b[field] || 0)
          - Number(a[field] || 0)
      ).map(
        row => row.label
      );
    });

    const ticketRiskLevel = row => {
      const isLeader = ticketRiskFields.some(
        field =>
          ticketRiskRanks[field][0]
          === row.label
      );

      if (isLeader) {
        return "critical";
      }

      const isRunnerUp = ticketRiskFields.some(
        field =>
          ticketRiskRanks[field][1]
          === row.label
      );

      return isRunnerUp
        ? "attention"
        : "lower";
    };

    const ticketRiskLabel = level => {
      if (level === "critical") {
        return "Critical relative risk";
      }

      if (level === "attention") {
        return "Attention";
      }

      return "Lower relative exposure";
    };

    const typeTableRows = typeRows.map(
      row => {
        const risk = ticketRiskLevel(row);
        const riskLabel = ticketRiskLabel(risk);

        return `
          <tr>
            <td>
              <span class="risk-label">
                <i
                  class="risk-dot risk-${risk}"
                  title="${escapeHtml(riskLabel)}"
                  aria-label="${escapeHtml(riskLabel)}"
                ></i>
                ${escapeHtml(row.label)}
              </span>
            </td>
            <td>${fmt.format(row.open)}</td>
            <td>${fmt.format(row.pending)}</td>
            <td>
              <strong>${fmt.format(row.unresolved)}</strong>
              <small>${pct(row.unresolved_pct)}</small>
            </td>
          </tr>`;
      }
    ).join('');

    const openStageRisk = "critical";
    const pendingStageRisk = "attention";

    const stalledTypeLeader =
      typeRows[0] || {};

    const stalledRateTypeLeader = Array.from(
      typeRows
    ).sort(
      (a, b) =>
        Number(b.unresolved_pct || 0)
        - Number(a.unresolved_pct || 0)
    )[0] || {};

    const openTypeLeader = Array.from(
      typeRows
    ).sort(
      (a, b) =>
        Number(b.open || 0)
        - Number(a.open || 0)
    )[0] || {};

    const worstResolution =
      (closedTime.rows || [])[0] || {};

    const worstResolutionMedian = Number(
      worstResolution.median_hours || 0
    );

    const worstResolutionDelta =
      overallMedian
        ? Math.round(
            (
              worstResolutionMedian
              / overallMedian
              - 1
            ) * 100
          )
        : 0;

    const resolutionItems = (
      closedTime.rows || []
    ).slice(0, 3).map(
      (row, index) => {
        const median = Number(
          row.median_hours || 0
        );

        const delta = overallMedian
          ? Math.round(
              (
                median / overallMedian
                - 1
              ) * 100
            )
          : 0;

        const deltaLabel =
          `${delta >= 0 ? '+' : ''}${delta}%`;

        const resolutionRisk =
          index === 0
            ? "critical"
            : "attention";

        const resolutionRiskLabel =
          resolutionRisk === "critical"
            ? "Critical"
            : "Attention";

        return `
          <li>
            <span class="risk-label">
              <i
                class="risk-dot risk-${resolutionRisk}"
                title="${resolutionRiskLabel}"
                aria-label="${resolutionRiskLabel}"
              ></i>
              ${escapeHtml(
                row.channel
                + ' · '
                + row.priority
                + ' · '
                + row.ticket_type
                + ' · n='
                + row.tickets
              )}
            </span>
            <strong>${median.toFixed(2)}h · ${deltaLabel}</strong>
          </li>`;
      }
    ).join('');

    if (workflowAnswer) {
      workflowAnswer.className = 'workflow-answer';

      workflowAnswer.textContent =
        `${pct(flow.not_closed_pct)} of tickets are stalled: `
        + `${fmt.format(flow.open_without_first_response)} have no first response `
        + `and ${fmt.format(flow.pending_after_first_response)} are pending customer response.`;
    }

    bottleneck.className = 'diagnostic-block';

    bottleneck.innerHTML = `
      <div class="metric-line workflow-total">
        <span class="risk-label">
          <i
            class="risk-dot risk-critical"
            title="Critical"
            aria-label="Critical"
          ></i>
          Workflow stalled
        </span>
        <strong>${fmt.format(flow.not_closed)} · ${pct(flow.not_closed_pct)}</strong>
      </div>

      <h4 class="diagnostic-section-title">Where the flow stalls</h4>

      <div class="analysis-scope">
        OPEN / PENDING
      </div>

      <p class="diagnostic-insight">
        No First Response is the critical service gap.
        Pending Customer Response is the secondary operational bottleneck after initial contact.
      </p>

      <ul class="rank-list">
        <li>
          <span class="risk-label">
            <i
              class="risk-dot risk-${openStageRisk}"
              title="Critical"
              aria-label="Critical"
            ></i>
            No First Response
          </span>

          <strong>
            ${fmt.format(flow.open_without_first_response)}
            ·
            ${pct(flow.open_without_first_response / data.rows * 100)}
          </strong>
        </li>

        <li>
          <span class="risk-label">
            <i
              class="risk-dot risk-${pendingStageRisk}"
              title="Attention"
              aria-label="Attention"
            ></i>
            Pending Customer Response
          </span>

          <strong>
            ${fmt.format(flow.pending_after_first_response)}
            ·
            ${pct(flow.pending_after_first_response / data.rows * 100)}
          </strong>
        </li>
      </ul>

      <h4 class="diagnostic-section-title">
        Bottlenecks
      </h4>

      <p class="diagnostic-insight">
        ${escapeHtml(channelVolume.label || '—')} leads stalled channel volume;
        ${escapeHtml(channelRate.label || '—')} has the highest channel rate.
        ${escapeHtml(priorityVolume.label || '—')} leads priority volume;
        ${escapeHtml(priorityRate.label || '—')} has the highest priority rate.
      </p>

      <div class="bottleneck-cards">

        <div class="bottleneck-card">
          <span class="risk-label">
            <i
              class="risk-dot risk-critical"
              title="Critical"
              aria-label="Critical"
            ></i>
            Channel · volume
          </span>

          <strong>
            ${escapeHtml(channelVolume.label || '—')}
            ·
            ${fmt.format(channelVolume.unresolved || 0)}
          </strong>
        </div>

        <div class="bottleneck-card">
          <span class="risk-label">
            <i
              class="risk-dot risk-critical"
              title="Critical"
              aria-label="Critical"
            ></i>
            Channel · rate
          </span>

          <strong>
            ${escapeHtml(channelRate.label || '—')}
            ·
            ${pct(channelRate.unresolved_pct || 0)}
          </strong>
        </div>

        <div class="bottleneck-card">
          <span class="risk-label">
            <i
              class="risk-dot risk-critical"
              title="Critical"
              aria-label="Critical"
            ></i>
            Priority · volume
          </span>

          <strong>
            ${escapeHtml(priorityVolume.label || '—')}
            ·
            ${fmt.format(priorityVolume.unresolved || 0)}
          </strong>
        </div>

        <div class="bottleneck-card">
          <span class="risk-label">
            <i
              class="risk-dot risk-critical"
              title="Critical"
              aria-label="Critical"
            ></i>
            Priority · rate
          </span>

          <strong>
            ${escapeHtml(priorityRate.label || '—')}
            ·
            ${pct(priorityRate.unresolved_pct || 0)}
          </strong>
        </div>

      </div>

      <h4 class="diagnostic-section-title">
        Ticket Type
      </h4>

      <p class="diagnostic-insight">
        ${escapeHtml(stalledTypeLeader.label || '—')} leads stalled volume
        (${fmt.format(stalledTypeLeader.unresolved || 0)});
        ${escapeHtml(stalledRateTypeLeader.label || '—')} leads stalled rate
        (${pct(stalledRateTypeLeader.unresolved_pct || 0)}).
        ${escapeHtml(openTypeLeader.label || '—')} has the most No First Response tickets
        (${fmt.format(openTypeLeader.open || 0)}).
      </p>

      <div class="ticket-risk-table-wrap">
        <table class="ticket-risk-table">

          <thead>
            <tr>
              <th>Ticket Type</th>
              <th>Open</th>
              <th>Pending</th>
              <th>Stalled</th>
            </tr>
          </thead>

          <tbody>
            ${typeTableRows}
          </tbody>

        </table>
      </div>

      <h4 class="diagnostic-section-title">
        Worst Closed resolution-time combinations
      </h4>

      <p class="diagnostic-insight">
        ${escapeHtml(
          (worstResolution.channel || '—')
          + ' · '
          + (worstResolution.priority || '—')
          + ' · '
          + (worstResolution.ticket_type || '—')
        )}
        has the worst median interval:
        ${worstResolutionMedian.toFixed(2)}h,
        ${worstResolutionDelta >= 0 ? '+' : ''}${worstResolutionDelta}%
        versus the ${overallMedian.toFixed(2)}h overall median.
      </p>

      <ul class="rank-list">
        ${resolutionItems}
      </ul>

      <div class="metric-line">
        <span class="risk-label">
          <i
            class="risk-dot risk-lower"
            title="Reference"
            aria-label="Reference"
          ></i>
          Closed · overall median
        </span>

        <strong>
          ${overallMedian.toFixed(2)}h
        </strong>
      </div>

      <div class="risk-legend risk-legend-final">

        <span>
          <i class="risk-dot risk-critical"></i>
          Critical
        </span>

        <span>
          <i class="risk-dot risk-attention"></i>
          Attention
        </span>

        <span>
          <i class="risk-dot risk-lower"></i>
          Lower relative
        </span>

      </div>`;

    const sat = data.satisfaction;
    if (sat.status === 'ready') {
      const satisfactionAnswer = document.getElementById('satisfaction-answer');
      const pct2 = (value) => `${Number(value || 0).toFixed(2)}%`;
      const hours2 = (value) => value === null || value === undefined
        ? 'n/a'
        : `${Number(value).toFixed(2)}h`;

      const product = sat.groups['Product Purchased'] || {rows: [], dissatisfaction_min: 0, dissatisfaction_max: 0};
      const subject = sat.groups['Ticket Subject'] || {rows: [], dissatisfaction_min: 0, dissatisfaction_max: 0};
      const ticketType = sat.groups['Ticket Type'] || {rows: [], dissatisfaction_min: 0, dissatisfaction_max: 0};
      const channel = sat.groups['Ticket Channel'] || {rows: [], dissatisfaction_min: 0, dissatisfaction_max: 0};

      const satisfactionRange = (group) => {
        const values = (group.rows || []).map((row) => Number(row.satisfied_pct));
        return {
          min: values.length ? Math.min(...values) : 0,
          max: values.length ? Math.max(...values) : 0,
        };
      };

      const productSat = satisfactionRange(product);
      const subjectSat = satisfactionRange(subject);
      const typeSat = satisfactionRange(ticketType);
      const channelSat = satisfactionRange(channel);

      const topProduct = product.rows[0] || {
        label: 'n/a',
        dissatisfied_pct: 0,
      };

      const topSubject = subject.rows[0] || {
        label: 'n/a',
        dissatisfied_pct: 0,
      };

      const topSubjects = subject.rows.slice(0, 3);
      const topProducts = product.rows.slice(0, 3);

      const productsBySatisfaction = Array.from(product.rows).sort(
        (a, b) => b.satisfied_pct - a.satisfied_pct
      );

      const bestProduct = productsBySatisfaction[0] || {
        label: 'n/a',
        satisfied_pct: 0,
      };

      const secondBestProduct = productsBySatisfaction[1] || {
        label: 'n/a',
        satisfied_pct: 0,
      };

      const technicalType = ticketType.rows.find(
        (row) => row.label === 'Technical issue'
      ) || ticketType.rows[0] || {
        label: 'n/a',
        dissatisfied_pct: 0,
      };

      const worstChannel = channel.rows[0] || {
        label: 'n/a',
        dissatisfied_pct: 0,
      };

      const channelsBySatisfaction = Array.from(channel.rows).sort(
        (a, b) => b.satisfied_pct - a.satisfied_pct
      );

      const bestChannel = channelsBySatisfaction[0] || {
        label: 'n/a',
        satisfied_pct: 0,
      };

      if (satisfactionAnswer) {
        satisfactionAnswer.textContent =
          `${pct2(sat.dissatisfied.pct)} of Closed tickets score 1–3. ` +
          `Purchased product and the specific issue reported show the strongest satisfaction differences.`;
      }

      const ratingLabels = {
        1: 'Very dissatisfied',
        2: 'Dissatisfied',
        3: 'Dissatisfied · gap remains',
        4: 'Satisfied · improve',
        5: 'Full satisfaction',
      };

      const ratingScale = sat.distribution.map((row) => {
        const rating = Number(row.rating);
        const share = sat.rated_tickets
          ? row.count / sat.rated_tickets * 100
          : 0;

        return `<div class="satisfaction-step rating-${rating}">
          <strong>${rating}</strong>
          <span>${escapeHtml(ratingLabels[rating] || '')}</span>
          <small>${fmt.format(row.count)} · ${pct2(share)}</small>
        </div>`;
      }).join('');

      const driverRows = [
        {
          variable: 'Product Purchased',
          low: `${pct2(product.dissatisfaction_min)}–${pct2(product.dissatisfaction_max)}`,
          high: `${pct2(productSat.min)}–${pct2(productSat.max)}`,
          answer: 'Strongest separation',
        },
        {
          variable: 'Ticket Subject',
          low: `${pct2(subject.dissatisfaction_min)}–${pct2(subject.dissatisfaction_max)}`,
          high: `${pct2(subjectSat.min)}–${pct2(subjectSat.max)}`,
          answer: 'Strong problem signal',
        },
        {
          variable: 'Ticket Type',
          low: `${pct2(ticketType.dissatisfaction_min)}–${pct2(ticketType.dissatisfaction_max)}`,
          high: `${pct2(typeSat.min)}–${pct2(typeSat.max)}`,
          answer: 'Moderate',
        },
        {
          variable: 'Ticket Channel',
          low: `${pct2(channel.dissatisfaction_min)}–${pct2(channel.dissatisfaction_max)}`,
          high: `${pct2(channelSat.min)}–${pct2(channelSat.max)}`,
          answer: 'Secondary',
        },
      ].map((row) => `<tr>
        <td>${escapeHtml(row.variable)}</td>
        <td><strong>${escapeHtml(row.low)}</strong></td>
        <td>${escapeHtml(row.high)}</td>
        <td>${escapeHtml(row.answer)}</td>
      </tr>`).join('');

      const subjectSecondary = topSubjects.slice(1).map(
        (row) => `${escapeHtml(row.label)} ${pct2(row.dissatisfied_pct)}`
      ).join(' · ');

      const productSecondary = topProducts.slice(1).map(
        (row) => `${escapeHtml(row.label)} ${pct2(row.dissatisfied_pct)}`
      ).join(' · ');

      satisfaction.className = 'diagnostic-block';

      satisfaction.innerHTML = `
        <div class="analysis-scope">CLOSED · CSAT</div>

        <div class="satisfaction-hotline">
          <div class="satisfaction-hotline-head">
            <span>DISSATISFACTION · ${pct2(sat.dissatisfied.pct)}</span>
            <span>SATISFACTION · ${pct2(sat.satisfied.pct)}</span>
          </div>

          <div class="satisfaction-hotline-bar">
            <span class="hotline-break"></span>
          </div>

          <div class="satisfaction-scale">
            ${ratingScale}
          </div>
        </div>

        <p class="diagnostic-insight">
          Ratings 1–3 represent dissatisfaction or an unmet expectation.
          Rating 4 means satisfied with improvement opportunity.
          Rating 5 represents full satisfaction.
        </p>

        <h4 class="diagnostic-section-title">WHAT IMPACTS SATISFACTION?</h4>

        <p class="diagnostic-insight">
          The strongest descriptive signals are the purchased product and the specific issue reported.
          Delivery and compatibility problems stand out among issue subjects.
        </p>

        <div class="bottleneck-cards">

          <div class="bottleneck-card is-critical">
            <span class="risk-label">
              <i class="risk-dot risk-critical"></i>
              #1 issue signal
            </span>

            <strong>
              ${escapeHtml(topSubject.label)} ·
              ${pct2(topSubject.dissatisfied_pct)}
            </strong>

            <small>${subjectSecondary}</small>
          </div>

          <div class="bottleneck-card is-critical">
            <span class="risk-label">
              <i class="risk-dot risk-critical"></i>
              #1 product dissatisfaction
            </span>

            <strong>
              ${escapeHtml(topProduct.label)} ·
              ${pct2(topProduct.dissatisfied_pct)}
            </strong>

            <small>${productSecondary}</small>
          </div>

          <div class="bottleneck-card is-positive is-wide">
            <span class="risk-label">
              <i class="risk-dot risk-lower"></i>
              Best satisfaction benchmark
            </span>

            <strong>
              ${escapeHtml(bestProduct.label)} ·
              ${pct2(bestProduct.satisfied_pct)} Rating 4–5
            </strong>

            <small>
              Next: ${escapeHtml(secondBestProduct.label)} ·
              ${pct2(secondBestProduct.satisfied_pct)}
            </small>
          </div>

        </div>

        <h4 class="diagnostic-section-title">
          WHICH VARIABLES MOST INFLUENCE CSAT?
        </h4>

        <p class="diagnostic-insight">
          Product Purchased shows the widest observed separation,
          followed by Ticket Subject. Ticket Type and Channel show
          considerably smaller differences.
        </p>

        <div class="ticket-risk-table-wrap">
          <table class="ticket-risk-table csat-driver-table">
            <thead>
              <tr>
                <th>Variable</th>
                <th>Rating 1–3</th>
                <th>Rating 4–5</th>
                <th>Reading</th>
              </tr>
            </thead>

            <tbody>
              ${driverRows}
            </tbody>
          </table>
        </div>

        <h4 class="diagnostic-section-title">
          IS IT RESOLUTION TIME, CHANNEL, OR PROBLEM TYPE?
        </h4>

        <div class="bottleneck-cards csat-answer-cards">

          <div class="bottleneck-card is-warning">
            <span class="risk-label">
              <i class="risk-dot risk-attention"></i>
              Resolution time
            </span>

            <strong>
              ${hours2(sat.solution_time.dissatisfied_mean_hours)}
              vs
              ${hours2(sat.solution_time.satisfied_mean_hours)}
            </strong>

            <small>
              No meaningful CSAT separation.
              Operational alert:
              ${hours2(sat.solution_time.overall_mean_hours)} mean ·
              ${hours2(sat.solution_time.overall_p90_hours)} P90.
            </small>
          </div>

          <div class="bottleneck-card is-positive">
            <span class="risk-label">
              <i class="risk-dot risk-lower"></i>
              Channel
            </span>

            <strong>
              ${escapeHtml(worstChannel.label)} ·
              ${pct2(worstChannel.dissatisfied_pct)} dissatisfied
            </strong>

            <small>
              Secondary effect.
              Best observed:
              ${escapeHtml(bestChannel.label)} ·
              ${pct2(bestChannel.satisfied_pct)} satisfied.
            </small>
          </div>

          <div class="bottleneck-card is-critical is-wide">
            <span class="risk-label">
              <i class="risk-dot risk-critical"></i>
              Problem type
            </span>

            <strong>
              Yes · specific Ticket Subject is more informative
              than broad Ticket Type
            </strong>

            <small>
              ${escapeHtml(topSubject.label)}
              ${pct2(topSubject.dissatisfied_pct)} ·
              ${topSubjects[1]
                ? `${escapeHtml(topSubjects[1].label)} ${pct2(topSubjects[1].dissatisfied_pct)} · `
                : ''}
              Technical issue
              ${pct2(technicalType.dissatisfied_pct)}.
            </small>
          </div>

        </div>`;

    }

    const w = data.waste;
    const wasteAnswer = document.getElementById('waste-answer');

    const wasteScope = w.waste || {};
    const timeCost = w.time_cost || {};
    const commercialCost = w.commercial_cost || {};
    const financialExposure = w.financial_exposure || {};
    const recoverableWaste = w.recoverable_waste || {};

    const targets = timeCost.targets || {};
    const target2h = targets.target_2h || {};
    const target1h = targets.target_1h || {};

    const topProducts =
      financialExposure.top_products || [];

    const topIssues =
      financialExposure.top_issue_subjects || [];

    const topCommercialProduct =
      topProducts.length
        ? topProducts[0]
        : null;

    const topCommercialIssue =
      topIssues.length
        ? topIssues[0]
        : null;

    const satisfactionData =
      data.satisfaction || {};

    const satisfactionGroups =
      satisfactionData.groups || {};

    const csatProductGroup =
      satisfactionGroups['Product Purchased'] || null;

    const csatRiskProduct =
      csatProductGroup &&
      csatProductGroup.rows &&
      csatProductGroup.rows.length
        ? csatProductGroup.rows[0]
        : null;

    const wastePct2 = (value) =>
      `${Number(value || 0).toFixed(2)}%`;

    const wasteHours2 = (value) =>
      Number.isFinite(Number(value))
        ? `${Number(value).toFixed(2)}h`
        : 'n/a';

    if (wasteAnswer) {
      wasteAnswer.textContent =
        `${fmt.format(wasteScope.count || 0)} tickets — ` +
        `${wastePct2(wasteScope.pct_base)} of the analyzed base — ` +
        `are tied to operational or commercial waste.`;
    }

    const commercialProductEvidence =
      topCommercialProduct
        ? `${escapeHtml(topCommercialProduct.label)} · ` +
          `${fmt.format(topCommercialProduct.loss_count)} of ` +
          `${fmt.format(topCommercialProduct.tickets)} tickets · ` +
          `${wastePct2(topCommercialProduct.loss_rate_pct)}`
        : 'No product evidence available';

    const commercialProductActive =
      topCommercialProduct
        ? `${fmt.format(topCommercialProduct.active_loss)} cases still active`
        : '';

    const issueEvidence =
      topCommercialIssue
        ? `${escapeHtml(topCommercialIssue.label)} · ` +
          `${fmt.format(topCommercialIssue.loss_count)} loss cases · ` +
          `${wastePct2(topCommercialIssue.loss_rate_pct)}`
        : '';

    const csatVsCommercial =
      csatRiskProduct && topCommercialProduct
        ? `<p class="diagnostic-insight">
            <strong>CSAT risk ≠ commercial-loss risk.</strong>
            ${escapeHtml(csatRiskProduct.label)} leads observed CSAT dissatisfaction,
            while ${escapeHtml(topCommercialProduct.label)} leads the observed
            Refund/Cancellation rate.
          </p>`
        : '';

    waste.className = 'diagnostic-block';

    waste.innerHTML = `
      <div class="bottleneck-cards">
        <div class="bottleneck-card is-critical">
          <span class="risk-label">
            No First Response
          </span>
          <strong>
            ${fmt.format(wasteScope.no_first_response || 0)}
            · ${wastePct2(wasteScope.no_first_response_pct)}
          </strong>
        </div>

        <div class="bottleneck-card is-warning">
          <span class="risk-label">
            Pending Customer Response
          </span>
          <strong>
            ${fmt.format(wasteScope.pending_customer || 0)}
            · ${wastePct2(wasteScope.pending_customer_pct)}
          </strong>
        </div>

        <div class="bottleneck-card is-critical">
          <span class="risk-label">
            Closed Refund + Cancellation
          </span>
          <strong>
            ${fmt.format(wasteScope.closed_refund_cancellation || 0)}
            · ${wastePct2(wasteScope.closed_refund_cancellation_pct)}
          </strong>
        </div>

        <div class="bottleneck-card is-critical">
          <span class="risk-label">
            Total waste surface
          </span>
          <strong>
            ${fmt.format(wasteScope.count || 0)}
            · ${wastePct2(wasteScope.pct_base)}
          </strong>
        </div>
      </div>

      <h4 class="diagnostic-section-title">
        QUANTIFY IN HOURS AND ESTIMATE COST
      </h4>

      <p class="diagnostic-insight">
        The valid Closed baseline averages
        <strong>${wasteHours2(timeCost.mean_hours)}</strong>.
        A redesigned 1–2h target implies an estimated reduction of
        <strong>
          ${wasteHours2(target2h.reduction_per_ticket_hours)}
          –
          ${wasteHours2(target1h.reduction_per_ticket_hours)}
        </strong>
        per affected ticket.
      </p>

      <div class="bottleneck-cards">
        <div class="bottleneck-card is-warning">
          <span class="risk-label">
            Time cost · current baseline
          </span>

          <strong>
            ${wasteHours2(timeCost.mean_hours)} average
            · ${wasteHours2(timeCost.median_hours)} median
          </strong>

          <p class="limit">
            P90 ${wasteHours2(timeCost.p90_hours)} ·
            90% of valid cases are at or below this threshold.
          </p>
        </div>

        <div class="bottleneck-card is-positive">
          <span class="risk-label">
            Estimated time reduction
          </span>

          <strong>
            ${wasteHours2(target2h.reduction_per_ticket_hours)}
            –
            ${wasteHours2(target1h.reduction_per_ticket_hours)}
            per ticket
          </strong>

          <p class="limit">
            ≈ ${fmt.format(Math.round(target2h.estimated_reduction_ticket_hours || 0))}
            –
            ${fmt.format(Math.round(target1h.estimated_reduction_ticket_hours || 0))}
            ticket-hours across the
            ${fmt.format(timeCost.estimate_basis_tickets || 0)}
            stalled tickets.
          </p>
        </div>

        <div class="bottleneck-card is-critical">
          <span class="risk-label">
            Commercial cost
          </span>

          <strong>
            ${fmt.format(commercialCost.count || 0)}
            Refund + Cancellation
          </strong>

          <p class="limit">
            ${wastePct2(commercialCost.pct_base)}
            of all analyzed tickets ·
            ${fmt.format(commercialCost.active_count || 0)}
            still active.
          </p>
        </div>

        <div class="bottleneck-card is-warning">
          <span class="risk-label">
            Financial exposure · top product
          </span>

          <strong>
            ${commercialProductEvidence}
          </strong>

          <p class="limit">
            ${commercialProductActive}
            ${issueEvidence
              ? ` · Top issue signal: ${issueEvidence}`
              : ''}
          </p>
        </div>
      </div>

      <h4 class="diagnostic-section-title">
        WHERE IS THE LARGEST RECOVERABLE WASTE?
      </h4>

      <p class="diagnostic-insight">
        First Response + Follow-up is the largest operational opportunity.
        Commercially, Refund/Cancellation creates a second recovery front
        inside the same active queue.
      </p>

      <div class="bottleneck-cards">
        <div class="bottleneck-card is-positive">
          <span class="risk-label">
            First Response + Follow-up
          </span>

          <strong>
            ${fmt.format(recoverableWaste.operational_count || 0)}
            · ${wastePct2(recoverableWaste.operational_pct_base)}
          </strong>

          <p class="limit">
            Open / Pending tickets requiring response,
            follow-up, escalation or controlled closure.
          </p>
        </div>

        <div class="bottleneck-card is-warning">
          <span class="risk-label">
            Commercial recovery window
          </span>

          <strong>
            ${fmt.format(recoverableWaste.commercial_active_count || 0)}
            active Refund/Cancellation cases
          </strong>

          <p class="limit">
            ${wastePct2(recoverableWaste.commercial_active_pct_of_loss)}
            of all Refund/Cancellation cases are still Open/Pending.
          </p>
        </div>
      </div>

      ${csatVsCommercial}
    `;

    const limits = data.measurement_limits;
    evidence.innerHTML = `<article><span class="pill observed">OBSERVED</span><strong>${fmt.format(data.rows)}</strong><p>tickets no Dataset 1</p></article>
      <article><span class="pill observed">OBSERVED</span><strong>${fmt.format(data.sample.csat_available)}</strong><p>tickets com CSAT</p></article>
      <article><span class="pill derived">DERIVED</span><strong>${pct(limits.resolution_before_response_pct)}</strong><p>pairs with negative chronology</p></article>
      <article><span class="pill derived">DERIVED</span><strong>${pct(limits.same_second_component_pct)}</strong><p>pairs with the same second component</p></article>
      <article><span class="pill normalized">NORMALIZED</span><strong>${pct(data.scope.relative_to_annual_context_pct)}</strong><p>provided dataset relative to stated annual volume</p></article>`;
    renderOverview();
    renderDiagnosticCharts(data);
    renderBottleneckCombinations(data);
  } catch (err) {
    bottleneck.innerHTML = `Failed to load diagnosis: ${escapeHtml(err.message)}`;
    satisfaction.innerHTML = `Failed to load diagnosis: ${escapeHtml(err.message)}`;
    waste.innerHTML = `Failed to load diagnosis: ${escapeHtml(err.message)}`;
  }
}


// -----------------------------------------------------------------------------
// SHARED OPERATIONAL VISUALIZATION
// -----------------------------------------------------------------------------
function renderDimensionMix(elementId, rows) {
  const el = document.getElementById(elementId);
  if (!el) return;
  el.innerHTML = (rows || []).map(row => `
    <div class="dimension-row">
      <div><span>${escapeHtml(row.label)}</span><strong>${fmt.format(row.count)} · ${pct(row.pct)}</strong></div>
      <div class="dimension-bar"><i style="width:${Math.max(0, Math.min(100, Number(row.pct || 0)))}%"></i></div>
    </div>`).join('');
}

function renderBottleneckCombinations(data) {
  const body = document.getElementById('combination-body');
  const note = document.getElementById('combination-note');
  const timeState = document.getElementById('combination-time-state');
  if (!body || !data?.bottleneck_combinations) return;
  const combo = data.bottleneck_combinations;
  const rows = (combo.rows || []).slice(0, 12);
  body.innerHTML = rows.map((row, index) => `<tr>
    <td>${index + 1}</td>
    <td>${escapeHtml(row.channel)}</td>
    <td>${escapeHtml(row.priority)}</td>
    <td>${escapeHtml(row.ticket_type)}</td>
    <td>${fmt.format(row.tickets)}</td>
    <td>${fmt.format(row.open)}</td>
    <td>${fmt.format(row.pending)}</td>
    <td>${fmt.format(row.closed)}</td>
    <td><strong>${fmt.format(row.unresolved)} · ${pct(row.unresolved_pct)}</strong></td>
  </tr>`).join('') || '<tr><td colspan="9">No combinations available.</td></tr>';
  if (note) note.textContent = `Ranking por ${combo.ranking_label.toLowerCase()}. ${combo.resolution_time_reason}`;
  if (timeState) timeState.textContent = combo.resolution_time_status === 'blocked' ? 'resolution time: blocked' : combo.resolution_time_status;
}

// -----------------------------------------------------------------------------
// OVERVIEW
// -----------------------------------------------------------------------------
function renderOverview() {
  const d = currentDiagnostic;
  const a = currentAudit;
  if (d && d.status === 'ready') {
    if (d.scope) {
      const annualVolume = Number(
        d.scope.annual_context_tickets || 0
      );

      const observedVolume = Number(
        d.scope.observed_tickets || d.rows || 0
      );

      const monthlyVolume =
        annualVolume > 0
          ? annualVolume / 12
          : 0;

      const dailyVolume =
        annualVolume > 0
          ? annualVolume / 365
          : 0;

      const annualShare = Number(
        d.scope.relative_to_annual_context_pct || 0
      );

      const equivalentMonths =
        monthlyVolume > 0
          ? observedVolume / monthlyVolume
          : 0;

      const equivalentDays = Number(
        d.scope.equivalent_volume_days || 0
      );

      setText(
        'header-annual-volume',
        `≈ ${fmt.format(Math.round(annualVolume))} / year`
      );

      setText(
        'header-operational-rate',
        `≈ ${fmt.format(Math.round(monthlyVolume))} / month · ≈ ${fmt.format(Math.round(dailyVolume))} / day`
      );

      setText(
        'top-sample',
        `${fmt.format(observedVolume)} tickets`
      );

      setText(
        'header-sample-context',
        `${pct(annualShare)} · ≈ ${equivalentMonths.toFixed(2)} months · ≈ ${fmt.format(Math.round(equivalentDays))} days`
      );
    }

    setText('overview-sample', fmt.format(d.rows));
    setText('overview-unresolved', `${fmt.format(d.waste.unresolved_snapshot_count)} · ${pct(d.waste.unresolved_snapshot_pct)}`);
    setText('overview-csat', `${fmt.format(d.satisfaction.rated_tickets)} · ${pct(d.satisfaction.coverage_pct)}`);
    if (d.flow?.snapshot) {
      const flow = d.flow.snapshot;
      setText('flow-open', `${fmt.format(flow.open)} · ${pct(flow.open / d.rows * 100)}`);
      setText('flow-pending', `${fmt.format(flow.pending_customer)} · ${pct(flow.pending_customer / d.rows * 100)}`);
      setText('flow-closed-resolved', `${fmt.format(flow.closed_with_resolution)} · ${pct(flow.closed_with_resolution / d.rows * 100)}`);
      setText('flow-closed-no-resolution', `${fmt.format(flow.closed_without_resolution)} · ${pct(flow.closed_without_resolution / d.rows * 100)}`);
      renderDimensionMix('overview-channel-mix', d.volume.by_channel);
      renderDimensionMix('overview-priority-mix', d.volume.by_priority);
      renderDimensionMix('overview-type-mix', d.volume.by_type);
    }
    if (d.scope) {
      setText('scope-observed', fmt.format(d.scope.observed_tickets));
      setText('scope-annual', fmt.format(d.scope.annual_context_tickets));
      setText('scope-share', pct(d.scope.relative_to_annual_context_pct));
      setText('scope-days', `~${Number(d.scope.equivalent_volume_days).toLocaleString((window.AIMASTER_I18N_LANG === 'pt-BR' ? 'pt-BR' : 'en-US'), {maximumFractionDigits: 0})} days`);
      setText('scope-note', d.scope.interpretation);
    }
  }
  if (a && Array.isArray(a.datasets)) {
    const nlp = a.datasets.find(x => x.kind === 'it_classification');
    if (nlp) setText('overview-classifier', fmt.format(nlp.rows));
  }
  const ledger = document.getElementById('overview-findings');
  if (!ledger || !d || d.status !== 'ready') return;
  const satGroups = Object.values(d.satisfaction.groups || {});
  const noStructuredCsatSignal = satGroups.length > 0 && satGroups.every(g => !g.test?.significant_005);
  ledger.innerHTML = [
    `<article class="ledger-item critical"><span>DATA LIMIT</span><strong>Historical SLA blocked</strong><p>Created At missing; ${pct(d.measurement_limits.resolution_before_response_pct)} of comparable pairs have negative chronology.</p></article>`,
    `<article class="ledger-item valid"><span>OBSERVED</span><strong>${pct(d.waste.unresolved_snapshot_pct)} not closed</strong><p>${fmt.format(d.waste.unresolved_snapshot_count)} tickets are Open or Pending in the snapshot. Backlog age is unknown.</p></article>`,
    `<article class="ledger-item valid"><span>CSAT</span><strong>${noStructuredCsatSignal ? 'No structural driver detected' : 'Association detected'}</strong><p>Channel, priority, and ticket type ${noStructuredCsatSignal ? 'were not significant at the 5% level' : 'require further investigation'}.</p></article>`,
    `<article class="ledger-item next"><span>NEXT</span><strong>Deepen CSAT analysis</strong><p>Subject, product, age, gender, and ticket text are the next candidate drivers.</p></article>`
  ].join('');
}

// -----------------------------------------------------------------------------
// DIAGNOSIS REPORTS · GENERAL OVERVIEW
// -----------------------------------------------------------------------------
function renderDiagnosisReport(data) {
  if (
    !data
    || data.status !== 'ready'
    || typeof Chart === 'undefined'
  ) {
    return;
  }

  const sample = data.sample || {};
  const scope = data.scope || {};
  const volume = data.volume || {};
  const satisfaction = data.satisfaction || {};
  const waste = data.waste || {};

  const wasteScope = waste.waste || {};
  const commercialCost = waste.commercial_cost || {};
  const timeCost = waste.time_cost || {};

  const total = Number(
    sample.tickets || data.rows || 0
  );

  const reportShare = function(count) {
    if (!total) return 0;

    return (
      Number(count || 0)
      / total
      * 100
    );
  };

  const reportPct = function(value) {
    return (
      Number(value || 0).toLocaleString(
        (window.AIMASTER_I18N_LANG === 'pt-BR' ? 'pt-BR' : 'en-US'),
        {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2
        }
      )
      + '%'
    );
  };

  const reportHours = function(value) {
    if (
      value === null
      || value === undefined
      || !Number.isFinite(Number(value))
    ) {
      return 'n/a';
    }

    return (
      Number(value).toLocaleString(
        (window.AIMASTER_I18N_LANG === 'pt-BR' ? 'pt-BR' : 'en-US'),
        {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2
        }
      )
      + 'h'
    );
  };

  const openPending = Number(
    waste.unresolved_snapshot_count
    || (
      Number(sample.open || 0)
      + Number(sample.pending_customer || 0)
    )
  );

  const openPendingPct = Number(
    waste.unresolved_snapshot_pct
    || reportShare(openPending)
  );

  const closed = Number(
    sample.closed || 0
  );

  const firstResponse = Number(
    sample.first_response_available || 0
  );

  const resolutionAvailable = Number(
    sample.resolution_available || 0
  );

  const csatAvailable = Number(
    sample.csat_available || 0
  );

  const commercialCount = Number(
    commercialCost.count || 0
  );

  const commercialPct = Number(
    commercialCost.pct_base || 0
  );

  const wasteCount = Number(
    wasteScope.count || 0
  );

  const wastePct = Number(
    wasteScope.pct_base || 0
  );

  const dissatisfied = (
    satisfaction.dissatisfied
    || {}
  );

  setText(
    'report-kpi-sample',
    fmt.format(total) + ' tickets'
  );

  setText(
    'report-kpi-sample-meta',
    reportPct(
      scope.relative_to_annual_context_pct
    )
    + ' of stated annual scale'
  );

  setText(
    'report-kpi-annual',
    '≈ '
    + fmt.format(
      scope.annual_context_tickets || 0
    )
    + ' / year'
  );

  setText(
    'report-kpi-annual-meta',
    '≈ '
    + Number(
      scope.annual_average_tickets_per_day || 0
    ).toLocaleString(
      (window.AIMASTER_I18N_LANG === 'pt-BR' ? 'pt-BR' : 'en-US'),
      {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }
    )
    + ' tickets / day'
  );

  setText(
    'report-kpi-open-pending',
    fmt.format(openPending)
    + ' · '
    + reportPct(openPendingPct)
  );

  setText(
    'report-kpi-closed',
    fmt.format(closed)
    + ' · '
    + reportPct(
      reportShare(closed)
    )
  );

  setText(
    'report-kpi-first-response',
    fmt.format(firstResponse)
    + ' · '
    + reportPct(
      reportShare(firstResponse)
    )
  );

  setText(
    'report-kpi-csat',
    fmt.format(csatAvailable)
    + ' · '
    + reportPct(
      satisfaction.coverage_pct
      || reportShare(csatAvailable)
    )
  );

  setText(
    'report-kpi-commercial-loss',
    fmt.format(commercialCount)
    + ' · '
    + reportPct(commercialPct)
  );

  setText(
    'report-kpi-waste',
    fmt.format(wasteCount)
    + ' · '
    + reportPct(wastePct)
  );

  setText(
    'report-status-total',
    fmt.format(total) + ' tickets'
  );

  setText(
    'report-coverage-total',
    fmt.format(total) + ' analyzed'
  );

  setText(
    'report-scope-note',
    fmt.format(total)
    + ' tickets represent '
    + reportPct(
      scope.relative_to_annual_context_pct
    )
    + ' of the stated ≈ '
    + fmt.format(
      scope.annual_context_tickets || 0
    )
    + ' tickets/year scale. The ≈ '
    + Number(
      scope.equivalent_volume_days || 0
    ).toLocaleString(
      (window.AIMASTER_I18N_LANG === 'pt-BR' ? 'pt-BR' : 'en-US'),
      {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }
    )
    + '-day equivalent is volume normalization, not an observed historical period.'
  );

  setText(
    'report-finding-flow-title',
    fmt.format(openPending)
    + ' tickets · '
    + reportPct(openPendingPct)
  );

  setText(
    'report-finding-flow',
    'Open and Pending Customer Response dominate the current workload and define the primary operational bottleneck.'
  );

  setText(
    'report-finding-loss-title',
    fmt.format(commercialCount)
    + ' tickets · '
    + reportPct(commercialPct)
  );

  setText(
    'report-finding-loss',
    'Refund and Cancellation represent a material commercial-loss signal across the analyzed support operation.'
  );

  setText(
    'report-finding-csat-title',
    fmt.format(
      dissatisfied.count || 0
    )
    + ' Rating 1–3 · '
    + reportPct(
      dissatisfied.pct || 0
    )
  );

  setText(
    'report-finding-csat',
    'Most observed Closed-ticket ratings fall between 1 and 3, indicating dissatisfaction or an unmet-expectation signal.'
  );

  setText(
    'report-finding-time-title',
    reportHours(
      timeCost.mean_hours
    )
  );

  setText(
    'report-finding-time',
    'Measured on '
    + fmt.format(
      timeCost.valid_closed_intervals || 0
    )
    + ' Closed tickets with valid post-response chronology; median '
    + reportHours(
      timeCost.median_hours
    )
    + ' and P90 '
    + reportHours(
      timeCost.p90_hours
    )
    + '.'
  );

  const destroyReportChart = function(id) {
    if (charts[id]) {
      charts[id].destroy();
      delete charts[id];
    }
  };

  const reportFontFamily =
    'Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif';

  const baseTickFont = {
    family: reportFontFamily,
    size: 13
  };

  const strongTickFont = {
    family: reportFontFamily,
    size: 13,
    weight: '700'
  };

  const makeCenterPlugin = function(
    primary,
    secondary
  ) {
    return {
      id: 'reportCenterText',

      afterDraw: function(chart) {
        const meta = chart.getDatasetMeta(0);

        if (
          !meta
          || !meta.data
          || !meta.data.length
        ) {
          return;
        }

        const center = meta.data[0];
        const ctx = chart.ctx;

        ctx.save();
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';

        ctx.fillStyle = '#173342';
        ctx.font =
          '800 28px '
          + reportFontFamily;

        ctx.fillText(
          primary,
          center.x,
          center.y - 9
        );

        ctx.fillStyle = '#72818d';
        ctx.font =
          '700 11px '
          + reportFontFamily;

        ctx.fillText(
          secondary,
          center.x,
          center.y + 18
        );

        ctx.restore();
      }
    };
  };

  const renderSummary = function(
    id,
    rows,
    colors
  ) {
    const element =
      document.getElementById(id);

    if (!element) return;

    element.innerHTML = rows.map(
      function(row, index) {
        return (
          '<div class="report-summary-chip">'
          + '<i style="background:'
          + colors[index]
          + '"></i>'
          + '<span>'
          + escapeHtml(row.label)
          + '</span>'
          + '<strong>'
          + fmt.format(row.count)
          + ' · '
          + reportPct(row.pct)
          + '</strong>'
          + '</div>'
        );
      }
    ).join('');
  };

  const rawStatusRows =
    Array.from(
      volume.by_status || []
    );

  const statusOrder = [
    'Open',
    'Pending Customer Response',
    'Closed'
  ];

  const statusRows =
    statusOrder.map(
      function(label) {
        return rawStatusRows.find(
          function(row) {
            return row.label === label;
          }
        );
      }
    ).filter(Boolean);

  const statusColors = statusRows.map(
    function(row) {
      if (row.label === 'Open') {
        return '#d71920';
      }

      if (
        row.label
        === 'Pending Customer Response'
      ) {
        return '#e5b329';
      }

      if (row.label === 'Closed') {
        return '#198754';
      }

      return '#7b8b99';
    }
  );

  destroyReportChart(
    'report-status-chart'
  );

  const statusCanvas =
    document.getElementById(
      'report-status-chart'
    );

  if (statusCanvas) {
    charts['report-status-chart'] =
      new Chart(
        statusCanvas,
        {
          type: 'doughnut',

          plugins: [
            makeCenterPlugin(
              fmt.format(total),
              'ANALYZED TICKETS'
            )
          ],

          data: {
            labels: statusRows.map(
              function(row) {
                return row.label;
              }
            ),

            datasets: [
              {
                data: statusRows.map(
                  function(row) {
                    return row.count;
                  }
                ),

                backgroundColor:
                  statusColors,

                borderColor:
                  '#ffffff',

                borderWidth: 6,

                hoverOffset: 12
              }
            ]
          },

          options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '63%',

            animation: {
              duration: 450
            },

            plugins: {
              legend: {
                position: 'bottom',

                labels: {
                  usePointStyle: true,
                  pointStyle: 'circle',
                  padding: 22,

                  font: {
                    family:
                      reportFontFamily,
                    size: 13,
                    weight: '700'
                  }
                }
              },

              tooltip: {
                titleFont: {
                  family:
                    reportFontFamily,
                  size: 13,
                  weight: '700'
                },

                bodyFont: {
                  family:
                    reportFontFamily,
                  size: 13,
                  weight: '600'
                },

                callbacks: {
                  label: function(context) {
                    const row =
                      statusRows[
                        context.dataIndex
                      ];

                    return (
                      ' '
                      + row.label
                      + ': '
                      + fmt.format(
                        row.count
                      )
                      + ' tickets · '
                      + reportPct(
                        row.pct
                      )
                    );
                  }
                }
              }
            }
          }
        }
      );
  }

  renderSummary(
    'report-status-summary',
    statusRows,
    statusColors
  );

  const typeRows =
    Array.from(
      volume.by_type || []
    );

  const typeColor = function(label) {
    if (
      label === 'Refund request'
    ) {
      return '#d71920';
    }

    if (
      label
      === 'Cancellation request'
    ) {
      return '#a82d4b';
    }

    if (
      label === 'Technical issue'
    ) {
      return '#2e78aa';
    }

    if (
      label === 'Product inquiry'
    ) {
      return '#2f9a8a';
    }

    if (
      label === 'Billing inquiry'
    ) {
      return '#7656a8';
    }

    return '#748594';
  };

  destroyReportChart(
    'report-type-chart-bi'
  );

  const typeCanvas =
    document.getElementById(
      'report-type-chart-bi'
    );

  if (typeCanvas) {
    charts['report-type-chart-bi'] =
      new Chart(
        typeCanvas,
        {
          type: 'bar',

          data: {
            labels: typeRows.map(
              function(row) {
                return row.label;
              }
            ),

            datasets: [
              {
                label: 'Tickets',

                data: typeRows.map(
                  function(row) {
                    return row.count;
                  }
                ),

                backgroundColor:
                  typeRows.map(
                    function(row) {
                      return typeColor(
                        row.label
                      );
                    }
                  ),

                borderWidth: 0,
                borderRadius: 9,
                barThickness: 38
              }
            ]
          },

          options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,

            animation: {
              duration: 450
            },

            plugins: {
              legend: {
                display: false
              },

              tooltip: {
                callbacks: {
                  label: function(context) {
                    const row =
                      typeRows[
                        context.dataIndex
                      ];

                    return (
                      ' '
                      + fmt.format(
                        row.count
                      )
                      + ' tickets · '
                      + reportPct(
                        row.pct
                      )
                    );
                  }
                }
              }
            },

            scales: {
              x: {
                beginAtZero: true,

                grid: {
                  color: '#edf1f4'
                },

                ticks: {
                  precision: 0,
                  font: baseTickFont
                }
              },

              y: {
                grid: {
                  display: false
                },

                ticks: {
                  color: '#283845',
                  font: strongTickFont
                }
              }
            }
          }
        }
      );
  }

  const channelRows =
    Array.from(
      volume.by_channel || []
    );

  const channelColors = [
    '#2e78aa',
    '#2f9a8a',
    '#7656a8',
    '#6c9fbd'
  ];

  destroyReportChart(
    'report-channel-chart'
  );

  const channelCanvas =
    document.getElementById(
      'report-channel-chart'
    );

  if (channelCanvas) {
    charts['report-channel-chart'] =
      new Chart(
        channelCanvas,
        {
          type: 'doughnut',

          plugins: [
            makeCenterPlugin(
              '4',
              'CHANNELS'
            )
          ],

          data: {
            labels: channelRows.map(
              function(row) {
                return row.label;
              }
            ),

            datasets: [
              {
                data: channelRows.map(
                  function(row) {
                    return row.count;
                  }
                ),

                backgroundColor:
                  channelColors,

                borderColor:
                  '#ffffff',

                borderWidth: 6,

                hoverOffset: 11
              }
            ]
          },

          options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '61%',

            animation: {
              duration: 450
            },

            plugins: {
              legend: {
                position: 'bottom',

                labels: {
                  usePointStyle: true,
                  pointStyle: 'circle',
                  padding: 20,

                  font: {
                    family:
                      reportFontFamily,
                    size: 13,
                    weight: '700'
                  }
                }
              },

              tooltip: {
                callbacks: {
                  label: function(context) {
                    const row =
                      channelRows[
                        context.dataIndex
                      ];

                    return (
                      ' '
                      + row.label
                      + ': '
                      + fmt.format(
                        row.count
                      )
                      + ' · '
                      + reportPct(
                        row.pct
                      )
                    );
                  }
                }
              }
            }
          }
        }
      );
  }

  renderSummary(
    'report-channel-summary',
    channelRows,
    channelColors
  );

  const priorityRows =
    Array.from(
      volume.by_priority || []
    );

  const priorityColor =
    function(label) {
      if (label === 'Critical') {
        return '#d71920';
      }

      if (label === 'High') {
        return '#df6d2d';
      }

      if (label === 'Medium') {
        return '#e5b329';
      }

      if (label === 'Low') {
        return '#198754';
      }

      return '#748594';
    };

  destroyReportChart(
    'report-priority-chart'
  );

  const priorityCanvas =
    document.getElementById(
      'report-priority-chart'
    );

  if (priorityCanvas) {
    charts['report-priority-chart'] =
      new Chart(
        priorityCanvas,
        {
          type: 'bar',

          data: {
            labels: priorityRows.map(
              function(row) {
                return row.label;
              }
            ),

            datasets: [
              {
                label: 'Tickets',

                data: priorityRows.map(
                  function(row) {
                    return row.count;
                  }
                ),

                backgroundColor:
                  priorityRows.map(
                    function(row) {
                      return priorityColor(
                        row.label
                      );
                    }
                  ),

                borderWidth: 0,
                borderRadius: 10,
                maxBarThickness: 78
              }
            ]
          },

          options: {
            responsive: true,
            maintainAspectRatio: false,

            animation: {
              duration: 450
            },

            plugins: {
              legend: {
                display: false
              },

              tooltip: {
                callbacks: {
                  label: function(context) {
                    const row =
                      priorityRows[
                        context.dataIndex
                      ];

                    return (
                      ' '
                      + fmt.format(
                        row.count
                      )
                      + ' tickets · '
                      + reportPct(
                        row.pct
                      )
                    );
                  }
                }
              }
            },

            scales: {
              y: {
                beginAtZero: true,

                grid: {
                  color: '#edf1f4'
                },

                ticks: {
                  precision: 0,
                  font: baseTickFont
                }
              },

              x: {
                grid: {
                  display: false
                },

                ticks: {
                  color: '#283845',
                  font: strongTickFont
                }
              }
            }
          }
        }
      );
  }

  const coverageRows = [
    {
      label: 'First Response',
      count: firstResponse,
      pct: reportShare(
        firstResponse
      )
    },
    {
      label: 'Resolution',
      count: resolutionAvailable,
      pct: reportShare(
        resolutionAvailable
      )
    },
    {
      label: 'CSAT',
      count: csatAvailable,
      pct: Number(
        satisfaction.coverage_pct
        || reportShare(
          csatAvailable
        )
      )
    }
  ];

  const coverageColors = [
    '#2e78aa',
    '#2f9a8a',
    '#7656a8'
  ];

  destroyReportChart(
    'report-coverage-chart'
  );

  const coverageCanvas =
    document.getElementById(
      'report-coverage-chart'
    );

  if (coverageCanvas) {
    charts['report-coverage-chart'] =
      new Chart(
        coverageCanvas,
        {
          type: 'bar',

          data: {
            labels: coverageRows.map(
              function(row) {
                return row.label;
              }
            ),

            datasets: [
              {
                label: 'Coverage',

                data: coverageRows.map(
                  function(row) {
                    return row.pct;
                  }
                ),

                backgroundColor:
                  coverageColors,

                borderWidth: 0,
                borderRadius: 10,
                barThickness: 42
              }
            ]
          },

          options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,

            animation: {
              duration: 450
            },

            plugins: {
              legend: {
                display: false
              },

              tooltip: {
                callbacks: {
                  label: function(context) {
                    const row =
                      coverageRows[
                        context.dataIndex
                      ];

                    return (
                      ' '
                      + reportPct(
                        row.pct
                      )
                      + ' coverage · '
                      + fmt.format(
                        row.count
                      )
                      + ' tickets'
                    );
                  }
                }
              }
            },

            scales: {
              x: {
                beginAtZero: true,
                max: 100,

                grid: {
                  color: '#edf1f4'
                },

                ticks: {
                  callback: function(value) {
                    return value + '%';
                  },

                  font: baseTickFont
                }
              },

              y: {
                grid: {
                  display: false
                },

                ticks: {
                  color: '#283845',

                  font: {
                    family:
                      reportFontFamily,
                    size: 14,
                    weight: '700'
                  }
                }
              }
            }
          }
        }
      );
  }
}

// -----------------------------------------------------------------------------
// DIAGNOSIS REPORTS · SPECIALIZED BI VIEWS
// -----------------------------------------------------------------------------
function renderDiagnosisSpecializedReport(data) {
  if (
    !data
    || data.status !== 'ready'
    || typeof Chart === 'undefined'
  ) {
    return;
  }

  const activeView =
    document.querySelector(
      '#diagnosis-reports .report-view.active'
    );

  if (
    !activeView
    || activeView.id
      === 'report-general-overview'
  ) {
    return;
  }

  const total = Number(
    data.rows || 0
  );

  const flow =
    data.flow || {};

  const snapshot =
    flow.snapshot || {};

  const dimensions =
    flow.dimensions || {};

  const bottlenecks =
    data.bottleneck_combinations || {};

  const satisfaction =
    data.satisfaction || {};

  const satisfactionGroups =
    satisfaction.groups || {};

  const waste =
    data.waste || {};

  const wasteScope =
    waste.waste || {};

  const timeCost =
    waste.time_cost || {};

  const commercialCost =
    waste.commercial_cost || {};

  const financialExposure =
    waste.financial_exposure || {};

  const recoverableWaste =
    waste.recoverable_waste || {};

  const reportId =
    activeView.id;

  const chartFontFamily =
    'Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif';

  const tickFont = {
    family: chartFontFamily,
    size: 12
  };

  const strongTickFont = {
    family: chartFontFamily,
    size: 12,
    weight: '700'
  };

  const COLORS = {
    danger: '#d71920',
    dangerSoft: '#df6d2d',
    warning: '#e5b329',
    ok: '#198754',
    accent: '#2e78aa',
    teal: '#2f9a8a',
    purple: '#7656a8',
    slate: '#748594',
    rose: '#a82d4b'
  };

  const rows = function(value) {
    return Array.isArray(value)
      ? Array.from(value)
      : [];
  };

  const share = function(count) {
    if (!total) return 0;

    return (
      Number(count || 0)
      / total
      * 100
    );
  };

  const percent2 = function(value) {
    return (
      Number(value || 0).toLocaleString(
        (window.AIMASTER_I18N_LANG === 'pt-BR' ? 'pt-BR' : 'en-US'),
        {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2
        }
      )
      + '%'
    );
  };

  const hours2 = function(value) {
    if (
      value === null
      || value === undefined
      || !Number.isFinite(
        Number(value)
      )
    ) {
      return 'n/a';
    }

    return (
      Number(value).toLocaleString(
        (window.AIMASTER_I18N_LANG === 'pt-BR' ? 'pt-BR' : 'en-US'),
        {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2
        }
      )
      + 'h'
    );
  };

  const destroyChart = function(id) {
    if (charts[id]) {
      charts[id].destroy();
      delete charts[id];
    }
  };

  const makeBar = function(
    id,
    labels,
    datasets,
    config
  ) {
    const canvas =
      document.getElementById(id);

    if (!canvas) return;

    const options =
      config || {};

    const horizontal =
      Boolean(options.horizontal);

    const stacked =
      Boolean(options.stacked);

    const isPercent =
      Boolean(options.percent);

    destroyChart(id);

    const xScale = {
      beginAtZero: true,
      stacked: stacked,
      grid: {
        color: horizontal
          ? '#edf1f4'
          : '#edf1f4'
      },
      ticks: {
        precision: 0,
        font: tickFont
      }
    };

    const yScale = {
      beginAtZero: true,
      stacked: stacked,
      grid: {
        color: horizontal
          ? 'rgba(0,0,0,0)'
          : '#edf1f4'
      },
      ticks: {
        precision: 0,
        color: '#283845',
        font: horizontal
          ? strongTickFont
          : tickFont
      }
    };

    if (!horizontal) {
      xScale.grid.display = false;
      xScale.ticks.color = '#283845';
      xScale.ticks.font =
        strongTickFont;
    }

    if (isPercent) {
      if (horizontal) {
        xScale.max = 100;
        xScale.ticks.callback =
          function(value) {
            return value + '%';
          };
      } else {
        yScale.max = 100;
        yScale.ticks.callback =
          function(value) {
            return value + '%';
          };
      }
    }

    const preparedDatasets =
      datasets.map(
        function(dataset) {
          return Object.assign(
            {
              borderWidth: 0,
              borderRadius: 8
            },
            dataset
          );
        }
      );

    charts[id] = new Chart(
      canvas,
      {
        type: 'bar',

        data: {
          labels: labels,
          datasets: preparedDatasets
        },

        options: {
          indexAxis:
            horizontal
              ? 'y'
              : 'x',

          responsive: true,
          maintainAspectRatio: false,

          animation: {
            duration: 450
          },

          plugins: {
            legend: {
              display:
                options.legend !== false
                && datasets.length > 1,

              position: 'bottom',

              labels: {
                usePointStyle: true,
                pointStyle: 'circle',
                padding: 18,

                font: {
                  family:
                    chartFontFamily,
                  size: 12,
                  weight: '700'
                }
              }
            },

            tooltip: {
              callbacks: {
                label: function(context) {
                  const value =
                    Number(
                      context.raw || 0
                    );

                  return (
                    ' '
                    + (
                      context.dataset.label
                      || 'Value'
                    )
                    + ': '
                    + (
                      isPercent
                        ? percent2(value)
                        : fmt.format(value)
                    )
                  );
                }
              }
            }
          },

          scales: {
            x: xScale,
            y: yScale
          }
        }
      }
    );
  };

  const makeDoughnut = function(
    id,
    labels,
    values,
    colors
  ) {
    const canvas =
      document.getElementById(id);

    if (!canvas) return;

    destroyChart(id);

    charts[id] = new Chart(
      canvas,
      {
        type: 'doughnut',

        data: {
          labels: labels,

          datasets: [
            {
              data: values,
              backgroundColor: colors,
              borderColor: '#ffffff',
              borderWidth: 6,
              hoverOffset: 12
            }
          ]
        },

        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: '61%',

          animation: {
            duration: 450
          },

          plugins: {
            legend: {
              position: 'bottom',

              labels: {
                usePointStyle: true,
                pointStyle: 'circle',
                padding: 20,

                font: {
                  family:
                    chartFontFamily,
                  size: 12,
                  weight: '700'
                }
              }
            },

            tooltip: {
              callbacks: {
                label: function(context) {
                  const value =
                    Number(
                      context.raw || 0
                    );

                  const sum =
                    context.dataset.data.reduce(
                      function(totalValue, item) {
                        return (
                          totalValue
                          + Number(item || 0)
                        );
                      },
                      0
                    );

                  const itemPct =
                    sum
                      ? value / sum * 100
                      : 0;

                  return (
                    ' '
                    + context.label
                    + ': '
                    + fmt.format(value)
                    + ' · '
                    + percent2(itemPct)
                  );
                }
              }
            }
          }
        }
      }
    );
  };

  const byFieldDesc = function(
    sourceRows,
    field
  ) {
    return rows(sourceRows).sort(
      function(a, b) {
        return (
          Number(b[field] || 0)
          - Number(a[field] || 0)
        );
      }
    );
  };


  // ===========================================================================
  // FLOW & BOTTLENECKS
  // ===========================================================================
  if (
    reportId
    === 'report-flow-bottlenecks'
  ) {
    const channelRows =
      rows(
        dimensions['Ticket Channel']
      );

    const priorityRows =
      rows(
        dimensions['Ticket Priority']
      );

    const typeRows =
      rows(
        dimensions['Ticket Type']
      );

    const combinationRows =
      rows(
        bottlenecks.rows
      ).slice(0, 10);

    const channelVolume =
      byFieldDesc(
        channelRows,
        'unresolved'
      )[0] || {};

    const channelRate =
      byFieldDesc(
        channelRows,
        'unresolved_pct'
      )[0] || {};

    const priorityVolume =
      byFieldDesc(
        priorityRows,
        'unresolved'
      )[0] || {};

    const worstCombination =
      combinationRows[0] || {};

    setText(
      'report-flow-kpi-stalled',
      fmt.format(
        snapshot.not_closed || 0
      )
      + ' · '
      + percent2(
        snapshot.not_closed_pct || 0
      )
    );

    setText(
      'report-flow-kpi-open',
      fmt.format(
        snapshot.open_without_first_response
        || 0
      )
      + ' · '
      + percent2(
        share(
          snapshot.open_without_first_response
          || 0
        )
      )
    );

    setText(
      'report-flow-kpi-pending',
      fmt.format(
        snapshot.pending_after_first_response
        || 0
      )
      + ' · '
      + percent2(
        share(
          snapshot.pending_after_first_response
          || 0
        )
      )
    );

    setText(
      'report-flow-kpi-combination',
      percent2(
        worstCombination.unresolved_pct
        || 0
      )
    );

    setText(
      'report-flow-kpi-combination-meta',
      worstCombination.channel
        ? (
            worstCombination.channel
            + ' · '
            + worstCombination.priority
            + ' · '
            + worstCombination.ticket_type
          )
        : 'Channel · Priority · Type'
    );

    setText(
      'report-flow-note',
      fmt.format(
        snapshot.not_closed || 0
      )
      + ' tickets remain Open/Pending. '
      + 'Volume and non-closure rate are shown separately '
      + 'to distinguish workload size from relative risk.'
    );

    makeBar(
      'report-flow-channel-chart',
      channelRows.map(
        function(row) {
          return row.label;
        }
      ),
      [
        {
          label: 'No First Response',
          data: channelRows.map(
            function(row) {
              return row.open;
            }
          ),
          backgroundColor:
            COLORS.danger
        },
        {
          label: 'Pending Customer Response',
          data: channelRows.map(
            function(row) {
              return row.pending;
            }
          ),
          backgroundColor:
            COLORS.warning
        }
      ],
      {
        stacked: true
      }
    );

    makeBar(
      'report-flow-priority-chart',
      priorityRows.map(
        function(row) {
          return row.label;
        }
      ),
      [
        {
          label: 'Stalled rate',
          data: priorityRows.map(
            function(row) {
              return row.unresolved_pct;
            }
          ),
          backgroundColor:
            priorityRows.map(
              function(row) {
                if (
                  row.label === 'Low'
                ) {
                  return COLORS.danger;
                }

                if (
                  row.label === 'Medium'
                ) {
                  return COLORS.warning;
                }

                if (
                  row.label === 'High'
                ) {
                  return COLORS.dangerSoft;
                }

                return COLORS.accent;
              }
            )
        }
      ],
      {
        percent: true,
        legend: false
      }
    );

    const typeRank =
      byFieldDesc(
        typeRows,
        'unresolved'
      );

    makeBar(
      'report-flow-type-chart',
      typeRank.map(
        function(row) {
          return row.label;
        }
      ),
      [
        {
          label: 'No First Response',
          data: typeRank.map(
            function(row) {
              return row.open;
            }
          ),
          backgroundColor:
            COLORS.danger
        },
        {
          label: 'Pending Customer Response',
          data: typeRank.map(
            function(row) {
              return row.pending;
            }
          ),
          backgroundColor:
            COLORS.warning
        }
      ],
      {
        horizontal: true,
        stacked: true
      }
    );

    makeBar(
      'report-flow-combination-chart',
      combinationRows.map(
        function(row) {
          return (
            row.channel
            + ' · '
            + row.priority
            + ' · '
            + row.ticket_type
          );
        }
      ),
      [
        {
          label: 'Non-closure rate',
          data: combinationRows.map(
            function(row) {
              return row.unresolved_pct;
            }
          ),
          backgroundColor:
            combinationRows.map(
              function(row, index) {
                return (
                  index === 0
                    ? COLORS.danger
                    : (
                        index < 4
                          ? COLORS.warning
                          : COLORS.accent
                      )
                );
              }
            )
        }
      ],
      {
        horizontal: true,
        percent: true,
        legend: false
      }
    );

    setText(
      'report-flow-finding-channel-volume-title',
      (channelVolume.label || '—')
      + ' · '
      + fmt.format(
        channelVolume.unresolved || 0
      )
    );

    setText(
      'report-flow-finding-channel-volume',
      'Highest observed stalled channel volume.'
    );

    setText(
      'report-flow-finding-channel-rate-title',
      (channelRate.label || '—')
      + ' · '
      + percent2(
        channelRate.unresolved_pct || 0
      )
    );

    setText(
      'report-flow-finding-channel-rate',
      'Highest observed channel non-closure rate.'
    );

    setText(
      'report-flow-finding-priority-volume-title',
      (priorityVolume.label || '—')
      + ' · '
      + fmt.format(
        priorityVolume.unresolved || 0
      )
    );

    setText(
      'report-flow-finding-priority-volume',
      'Largest unresolved workload by priority.'
    );

    setText(
      'report-flow-finding-combination-title',
      worstCombination.channel
        ? (
            worstCombination.channel
            + ' · '
            + worstCombination.priority
          )
        : '—'
    );

    setText(
      'report-flow-finding-combination',
      worstCombination.ticket_type
        ? (
            worstCombination.ticket_type
            + ' · '
            + percent2(
              worstCombination.unresolved_pct
              || 0
            )
            + ' non-closure rate.'
          )
        : '—'
    );

    return;
  }


  // ===========================================================================
  // SATISFACTION & CSAT
  // ===========================================================================
  if (
    reportId
    === 'report-satisfaction-csat'
  ) {
    const ratingRows =
      rows(
        satisfaction.distribution
      );

    const dissatisfied =
      satisfaction.dissatisfied || {};

    const satisfied =
      satisfaction.satisfied || {};

    const productGroup =
      satisfactionGroups[
        'Product Purchased'
      ] || {};

    const subjectGroup =
      satisfactionGroups[
        'Ticket Subject'
      ] || {};

    const typeGroup =
      satisfactionGroups[
        'Ticket Type'
      ] || {};

    const channelGroup =
      satisfactionGroups[
        'Ticket Channel'
      ] || {};

    const productRows =
      byFieldDesc(
        productGroup.rows || [],
        'dissatisfied_pct'
      );

    const subjectRows =
      byFieldDesc(
        subjectGroup.rows || [],
        'dissatisfied_pct'
      );

    const typeRows =
      byFieldDesc(
        typeGroup.rows || [],
        'dissatisfied_pct'
      );

    const channelRows =
      byFieldDesc(
        channelGroup.rows || [],
        'dissatisfied_pct'
      );

    const bestProduct =
      byFieldDesc(
        productGroup.rows || [],
        'satisfied_pct'
      )[0] || {};

    const worstProduct =
      productRows[0] || {};

    const worstSubject =
      subjectRows[0] || {};

    const worstChannel =
      channelRows[0] || {};

    setText(
      'report-csat-kpi-rated',
      fmt.format(
        satisfaction.rated_tickets
        || 0
      )
      + ' · '
      + percent2(
        satisfaction.coverage_pct || 0
      )
    );

    setText(
      'report-csat-kpi-dissatisfied',
      fmt.format(
        dissatisfied.count || 0
      )
      + ' · '
      + percent2(
        dissatisfied.pct || 0
      )
    );

    setText(
      'report-csat-kpi-satisfied',
      fmt.format(
        satisfied.count || 0
      )
      + ' · '
      + percent2(
        satisfied.pct || 0
      )
    );

    setText(
      'report-csat-kpi-mean',
      Number(
        satisfaction.mean || 0
      ).toFixed(2)
      + ' / 5'
    );

    setText(
      'report-satisfaction-note',
      fmt.format(
        satisfaction.rated_tickets
        || 0
      )
      + ' Closed tickets have CSAT. '
      + percent2(
        dissatisfied.pct || 0
      )
      + ' score 1–3.'
    );

    makeBar(
      'report-csat-rating-chart',
      ratingRows.map(
        function(row) {
          return 'Rating ' + row.rating;
        }
      ),
      [
        {
          label: 'Tickets',
          data: ratingRows.map(
            function(row) {
              return row.count;
            }
          ),
          backgroundColor: [
            COLORS.danger,
            COLORS.dangerSoft,
            COLORS.warning,
            COLORS.accent,
            COLORS.ok
          ]
        }
      ],
      {
        legend: false
      }
    );

    makeDoughnut(
      'report-csat-sentiment-chart',
      [
        'Rating 1–3',
        'Rating 4–5'
      ],
      [
        dissatisfied.count || 0,
        satisfied.count || 0
      ],
      [
        COLORS.danger,
        COLORS.ok
      ]
    );

    const topProducts =
      productRows.slice(0, 10);

    makeBar(
      'report-csat-product-chart',
      topProducts.map(
        function(row) {
          return row.label;
        }
      ),
      [
        {
          label: 'Rating 1–3',
          data: topProducts.map(
            function(row) {
              return row.dissatisfied_pct;
            }
          ),
          backgroundColor:
            topProducts.map(
              function(row, index) {
                return (
                  index === 0
                    ? COLORS.danger
                    : COLORS.dangerSoft
                );
              }
            )
        }
      ],
      {
        horizontal: true,
        percent: true,
        legend: false
      }
    );

    const topSubjects =
      subjectRows.slice(0, 10);

    makeBar(
      'report-csat-subject-chart',
      topSubjects.map(
        function(row) {
          return row.label;
        }
      ),
      [
        {
          label: 'Rating 1–3',
          data: topSubjects.map(
            function(row) {
              return row.dissatisfied_pct;
            }
          ),
          backgroundColor:
            topSubjects.map(
              function(row, index) {
                return (
                  index === 0
                    ? COLORS.danger
                    : COLORS.warning
                );
              }
            )
        }
      ],
      {
        horizontal: true,
        percent: true,
        legend: false
      }
    );

    makeBar(
      'report-csat-type-chart',
      typeRows.map(
        function(row) {
          return row.label;
        }
      ),
      [
        {
          label: 'Rating 1–3',
          data: typeRows.map(
            function(row) {
              return row.dissatisfied_pct;
            }
          ),
          backgroundColor:
            COLORS.rose
        }
      ],
      {
        percent: true,
        legend: false
      }
    );

    makeBar(
      'report-csat-channel-chart',
      channelRows.map(
        function(row) {
          return row.label;
        }
      ),
      [
        {
          label: 'Rating 1–3',
          data: channelRows.map(
            function(row) {
              return row.dissatisfied_pct;
            }
          ),
          backgroundColor:
            COLORS.accent
        }
      ],
      {
        percent: true,
        legend: false
      }
    );

    setText(
      'report-csat-finding-product-title',
      (worstProduct.label || '—')
      + ' · '
      + percent2(
        worstProduct.dissatisfied_pct
        || 0
      )
    );

    setText(
      'report-csat-finding-product',
      'Highest observed product dissatisfaction rate among Closed tickets.'
    );

    setText(
      'report-csat-finding-subject-title',
      (worstSubject.label || '—')
      + ' · '
      + percent2(
        worstSubject.dissatisfied_pct
        || 0
      )
    );

    setText(
      'report-csat-finding-subject',
      'Strongest observed specific issue signal.'
    );

    setText(
      'report-csat-finding-best-product-title',
      (bestProduct.label || '—')
      + ' · '
      + percent2(
        bestProduct.satisfied_pct
        || 0
      )
    );

    setText(
      'report-csat-finding-best-product',
      'Best observed Rating 4–5 product benchmark.'
    );

    setText(
      'report-csat-finding-channel-title',
      (worstChannel.label || '—')
      + ' · '
      + percent2(
        worstChannel.dissatisfied_pct
        || 0
      )
    );

    setText(
      'report-csat-finding-channel',
      'Channel differences are smaller than product and issue differences.'
    );

    return;
  }


  // ===========================================================================
  // WASTE & COST
  // ===========================================================================
  if (
    reportId
    === 'report-waste-cost'
  ) {
    const targets =
      timeCost.targets || {};

    const target2 =
      targets.target_2h || {};

    const target1 =
      targets.target_1h || {};

    const outsideWaste =
      Math.max(
        total
        - Number(
          wasteScope.count || 0
        ),
        0
      );

    setText(
      'report-waste-kpi-total',
      fmt.format(
        wasteScope.count || 0
      )
      + ' · '
      + percent2(
        wasteScope.pct_base || 0
      )
    );

    setText(
      'report-waste-kpi-operational',
      fmt.format(
        wasteScope.open_pending || 0
      )
      + ' · '
      + percent2(
        wasteScope.open_pending_pct || 0
      )
    );

    setText(
      'report-waste-kpi-commercial',
      fmt.format(
        commercialCost.count || 0
      )
      + ' · '
      + percent2(
        commercialCost.pct_base || 0
      )
    );

    setText(
      'report-waste-kpi-active',
      fmt.format(
        commercialCost.active_count || 0
      )
      + ' · '
      + percent2(
        commercialCost.active_pct_of_loss
        || 0
      )
    );

    setText(
      'report-waste-note',
      'Observed waste volume is separated from the ESTIMATED '
      + '1–2h time-reduction scenario. '
      + 'Estimated hours represent elapsed ticket-hours.'
    );

    makeDoughnut(
      'report-waste-surface-chart',
      [
        'Measured waste surface',
        'Outside measured waste surface'
      ],
      [
        wasteScope.count || 0,
        outsideWaste
      ],
      [
        COLORS.danger,
        COLORS.ok
      ]
    );

    makeBar(
      'report-waste-operational-chart',
      [
        'No First Response',
        'Pending Customer Response'
      ],
      [
        {
          label: 'Tickets',
          data: [
            wasteScope.no_first_response
              || 0,
            wasteScope.pending_customer
              || 0
          ],
          backgroundColor: [
            COLORS.danger,
            COLORS.warning
          ]
        }
      ],
      {
        legend: false
      }
    );

    makeBar(
      'report-waste-time-chart',
      [
        'Mean',
        'Median',
        'P90'
      ],
      [
        {
          label: 'Hours',
          data: [
            timeCost.mean_hours || 0,
            timeCost.median_hours || 0,
            timeCost.p90_hours || 0
          ],
          backgroundColor: [
            COLORS.warning,
            COLORS.accent,
            COLORS.danger
          ]
        }
      ],
      {
        legend: false
      }
    );

    makeBar(
      'report-waste-estimate-chart',
      [
        '2h target',
        '1h target'
      ],
      [
        {
          label: 'Estimated ticket-hours reduced',
          data: [
            Math.round(
              target2.estimated_reduction_ticket_hours
              || 0
            ),
            Math.round(
              target1.estimated_reduction_ticket_hours
              || 0
            )
          ],
          backgroundColor: [
            COLORS.teal,
            COLORS.ok
          ]
        }
      ],
      {
        legend: false
      }
    );

    setText(
      'report-waste-finding-operational-title',
      fmt.format(
        recoverableWaste.operational_count
        || 0
      )
      + ' · '
      + percent2(
        recoverableWaste.operational_pct_base
        || 0
      )
    );

    setText(
      'report-waste-finding-operational',
      'Open/Pending tickets require first response, follow-up, escalation or controlled closure.'
    );

    setText(
      'report-waste-finding-time-title',
      '≈ '
      + fmt.format(
        Math.round(
          target2.estimated_reduction_ticket_hours
          || 0
        )
      )
      + '–'
      + fmt.format(
        Math.round(
          target1.estimated_reduction_ticket_hours
          || 0
        )
      )
      + ' ticket-hours'
    );

    setText(
      'report-waste-finding-time',
      'Estimated against the 5,700 stalled tickets using the redesigned 1–2h target.'
    );

    setText(
      'report-waste-finding-baseline-title',
      hours2(
        timeCost.mean_hours
      )
      + ' mean · '
      + hours2(
        timeCost.median_hours
      )
      + ' median'
    );

    setText(
      'report-waste-finding-baseline',
      'Derived from '
      + fmt.format(
        timeCost.valid_closed_intervals
        || 0
      )
      + ' valid Closed post-response intervals; P90 '
      + hours2(
        timeCost.p90_hours
      )
      + '.'
    );

    setText(
      'report-waste-finding-commercial-title',
      fmt.format(
        commercialCost.count || 0
      )
      + ' Refund + Cancellation'
    );

    setText(
      'report-waste-finding-commercial',
      fmt.format(
        commercialCost.active_count || 0
      )
      + ' remain active. Commercial exposure overlaps the active operational queue and is not added twice.'
    );

    return;
  }


  // ===========================================================================
  // COMMERCIAL LOSS
  // ===========================================================================
  if (
    reportId
    === 'report-commercial-loss'
  ) {
    const products =
      byFieldDesc(
        financialExposure.top_products
        || [],
        'loss_rate_pct'
      );

    const issues =
      byFieldDesc(
        financialExposure.top_issue_subjects
        || [],
        'loss_rate_pct'
      );

    const activeProducts =
      byFieldDesc(
        financialExposure.top_products
        || [],
        'active_loss'
      );

    const activeIssues =
      byFieldDesc(
        financialExposure.top_issue_subjects
        || [],
        'active_loss'
      );

    const topProduct =
      products[0] || {};

    const topIssue =
      issues[0] || {};

    const topActiveProduct =
      activeProducts[0] || {};

    const topActiveIssue =
      activeIssues[0] || {};

    const csatProductGroup =
      satisfactionGroups[
        'Product Purchased'
      ] || {};

    const topCsatProduct =
      byFieldDesc(
        csatProductGroup.rows || [],
        'dissatisfied_pct'
      )[0] || {};

    setText(
      'report-commercial-kpi-total',
      fmt.format(
        commercialCost.count || 0
      )
      + ' · '
      + percent2(
        commercialCost.pct_base || 0
      )
    );

    setText(
      'report-commercial-kpi-active',
      fmt.format(
        commercialCost.active_count || 0
      )
    );

    setText(
      'report-commercial-kpi-closed',
      fmt.format(
        commercialCost.closed_count || 0
      )
    );

    setText(
      'report-commercial-kpi-window',
      percent2(
        commercialCost.active_pct_of_loss
        || 0
      )
    );

    setText(
      'report-commercial-note',
      fmt.format(
        commercialCost.count || 0
      )
      + ' Refund/Cancellation tickets represent '
      + percent2(
        commercialCost.pct_base || 0
      )
      + ' of the analyzed base; '
      + percent2(
        commercialCost.active_pct_of_loss
        || 0
      )
      + ' of those cases are still Open/Pending.'
    );

    makeDoughnut(
      'report-commercial-window-chart',
      [
        'Active Open / Pending',
        'Closed'
      ],
      [
        commercialCost.active_count || 0,
        commercialCost.closed_count || 0
      ],
      [
        COLORS.ok,
        COLORS.danger
      ]
    );

    makeBar(
      'report-commercial-active-product-chart',
      activeProducts.map(
        function(row) {
          return row.label;
        }
      ),
      [
        {
          label: 'Active loss cases',
          data: activeProducts.map(
            function(row) {
              return row.active_loss;
            }
          ),
          backgroundColor:
            COLORS.ok
        }
      ],
      {
        horizontal: true,
        legend: false
      }
    );

    makeBar(
      'report-commercial-product-chart',
      products.map(
        function(row) {
          return row.label;
        }
      ),
      [
        {
          label: 'Refund + Cancellation rate',
          data: products.map(
            function(row) {
              return row.loss_rate_pct;
            }
          ),
          backgroundColor:
            products.map(
              function(row, index) {
                return (
                  index === 0
                    ? COLORS.danger
                    : COLORS.dangerSoft
                );
              }
            )
        }
      ],
      {
        horizontal: true,
        percent: true,
        legend: false
      }
    );

    makeBar(
      'report-commercial-issue-chart',
      issues.map(
        function(row) {
          return row.label;
        }
      ),
      [
        {
          label: 'Refund + Cancellation rate',
          data: issues.map(
            function(row) {
              return row.loss_rate_pct;
            }
          ),
          backgroundColor:
            issues.map(
              function(row, index) {
                return (
                  index === 0
                    ? COLORS.danger
                    : COLORS.warning
                );
              }
            )
        }
      ],
      {
        horizontal: true,
        percent: true,
        legend: false
      }
    );

    setText(
      'report-commercial-finding-product-title',
      (topProduct.label || '—')
      + ' · '
      + percent2(
        topProduct.loss_rate_pct || 0
      )
    );

    setText(
      'report-commercial-finding-product',
      fmt.format(
        topProduct.loss_count || 0
      )
      + ' of '
      + fmt.format(
        topProduct.tickets || 0
      )
      + ' observed tickets are Refund/Cancellation.'
    );

    setText(
      'report-commercial-finding-active-title',
      (topActiveProduct.label || '—')
      + ' · '
      + fmt.format(
        topActiveProduct.active_loss || 0
      )
      + ' active'
    );

    setText(
      'report-commercial-finding-active',
      percent2(
        topActiveProduct.recovery_window_pct
        || 0
      )
      + ' of its observed commercial-loss cases remain Open/Pending.'
    );

    setText(
      'report-commercial-finding-issue-title',
      (topIssue.label || '—')
      + ' · '
      + percent2(
        topIssue.loss_rate_pct || 0
      )
    );

    setText(
      'report-commercial-finding-issue',
      fmt.format(
        topIssue.loss_count || 0
      )
      + ' observed commercial-loss cases. '
      + (
        topActiveIssue.label
          ? (
              'Largest active issue window: '
              + topActiveIssue.label
              + ' · '
              + fmt.format(
                topActiveIssue.active_loss || 0
              )
              + ' active.'
            )
          : ''
      )
    );

    setText(
      'report-commercial-finding-csat-title',
      (topCsatProduct.label || '—')
      + ' ≠ '
      + (topProduct.label || '—')
    );

    setText(
      'report-commercial-finding-csat',
      topCsatProduct.label
        ? (
            topCsatProduct.label
            + ' leads observed CSAT dissatisfaction, while '
            + topProduct.label
            + ' leads observed Refund/Cancellation rate.'
          )
        : 'CSAT and commercial-loss risk are evaluated independently.'
    );

    return;
  }
}

// -----------------------------------------------------------------------------
// DIAGNOSIS REPORTS · CROSS ANALYSIS
// -----------------------------------------------------------------------------

const CROSS_ANALYSIS_DIMENSIONS = [
  {
    key: 'channel',
    label: 'Ticket Channel'
  },
  {
    key: 'priority',
    label: 'Ticket Priority'
  },
  {
    key: 'ticket_type',
    label: 'Ticket Type'
  },
  {
    key: 'product',
    label: 'Product Purchased'
  },
  {
    key: 'subject',
    label: 'Ticket Subject'
  }
];

const CROSS_ANALYSIS_METRICS = {
  open_pending: [
    {
      key: 'ticket_count',
      label: 'Ticket Count'
    },
    {
      key: 'no_first_response',
      label: 'No First Response'
    },
    {
      key: 'pending_customer_response',
      label: 'Pending Customer Response'
    },
    {
      key: 'commercial_loss',
      label: 'Refund + Cancellation'
    }
  ],

  closed: [
    {
      key: 'ticket_count',
      label: 'Ticket Count'
    },
    {
      key: 'rating_1_3',
      label: 'Rating 1–3'
    },
    {
      key: 'rating_4_5',
      label: 'Rating 4–5'
    },
    {
      key: 'average_csat',
      label: 'Average CSAT'
    },
    {
      key: 'commercial_loss',
      label: 'Refund + Cancellation'
    },
    {
      key: 'solution_time',
      label: 'Solution Time · Median'
    }
  ]
};

let crossAnalysisInitialized = false;
let crossAnalysisScope = 'open_pending';
let crossAnalysisRequestSerial = 0;
const crossAnalysisCache = {};


function crossDimensionLabel(key) {
  const match =
    CROSS_ANALYSIS_DIMENSIONS.find(
      function(item) {
        return item.key === key;
      }
    );

  return match
    ? match.label
    : key;
}


function crossMetricLabel(
  scope,
  key
) {
  const rows =
    CROSS_ANALYSIS_METRICS[
      scope
    ] || [];

  const match =
    rows.find(
      function(item) {
        return item.key === key;
      }
    );

  return match
    ? match.label
    : key;
}


function crossFormatValue(
  value,
  metric
) {
  if (
    value === null
    || value === undefined
    || !Number.isFinite(
      Number(value)
    )
  ) {
    return '—';
  }

  if (
    metric.format === 'integer'
  ) {
    return fmt.format(
      Math.round(
        Number(value)
      )
    );
  }

  if (
    metric.format === 'hours'
  ) {
    return (
      Number(value).toLocaleString(
        (window.AIMASTER_I18N_LANG === 'pt-BR' ? 'pt-BR' : 'en-US'),
        {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2
        }
      )
      + 'h'
    );
  }

  return Number(
    value
  ).toLocaleString(
    (window.AIMASTER_I18N_LANG === 'pt-BR' ? 'pt-BR' : 'en-US'),
    {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }
  );
}


function crossFormatPct(value) {
  if (
    value === null
    || value === undefined
    || !Number.isFinite(
      Number(value)
    )
  ) {
    return '—';
  }

  return (
    Number(value).toLocaleString(
      (window.AIMASTER_I18N_LANG === 'pt-BR' ? 'pt-BR' : 'en-US'),
      {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }
    )
    + '%'
  );
}


function crossCombinationLabel(row) {
  if (!row) return '—';

  return (
    String(
      row.dimension_a_value || '—'
    )
    + ' × '
    + String(
      row.dimension_b_value || '—'
    )
  );
}


function crossPopulateDimensionSelects() {
  const selectA =
    document.getElementById(
      'report-cross-dimension-a'
    );

  const selectB =
    document.getElementById(
      'report-cross-dimension-b'
    );

  if (
    !selectA
    || !selectB
  ) {
    return;
  }

  const options =
    CROSS_ANALYSIS_DIMENSIONS.map(
      function(item) {
        return (
          '<option value="'
          + escapeHtml(item.key)
          + '">'
          + escapeHtml(item.label)
          + '</option>'
        );
      }
    ).join('');

  selectA.innerHTML = options;
  selectB.innerHTML = options;

  selectA.value = 'channel';
  selectB.value = 'ticket_type';
}


function crossPopulateMetricSelect(
  preserveCurrent
) {
  const select =
    document.getElementById(
      'report-cross-metric'
    );

  if (!select) return;

  const current =
    preserveCurrent
      ? select.value
      : '';

  const metrics =
    CROSS_ANALYSIS_METRICS[
      crossAnalysisScope
    ] || [];

  select.innerHTML =
    metrics.map(
      function(item) {
        return (
          '<option value="'
          + escapeHtml(item.key)
          + '">'
          + escapeHtml(item.label)
          + '</option>'
        );
      }
    ).join('');

  const currentStillValid =
    metrics.some(
      function(item) {
        return item.key === current;
      }
    );

  if (currentStillValid) {
    select.value = current;
    return;
  }

  if (
    crossAnalysisScope
    === 'closed'
  ) {
    select.value =
      'rating_1_3';
  } else {
    select.value =
      'ticket_count';
  }
}


function crossEnsureDistinctDimensions(
  changed
) {
  const selectA =
    document.getElementById(
      'report-cross-dimension-a'
    );

  const selectB =
    document.getElementById(
      'report-cross-dimension-b'
    );

  if (
    !selectA
    || !selectB
    || selectA.value
      !== selectB.value
  ) {
    return;
  }

  const alternative =
    CROSS_ANALYSIS_DIMENSIONS.find(
      function(item) {
        return (
          item.key
          !== (
            changed === 'a'
              ? selectA.value
              : selectB.value
          )
        );
      }
    );

  if (!alternative) return;

  if (changed === 'a') {
    selectB.value =
      alternative.key;
  } else {
    selectA.value =
      alternative.key;
  }
}


function crossSelectScope(scope) {
  if (
    !CROSS_ANALYSIS_METRICS[
      scope
    ]
  ) {
    return;
  }

  crossAnalysisScope = scope;

  const buttons = [
    ...document.querySelectorAll(
      '.report-xa-scope-button'
    )
  ];

  buttons.forEach(
    function(button) {
      const active =
        button.dataset.crossScope
        === scope;

      button.classList.toggle(
        'active',
        active
      );

      button.setAttribute(
        'aria-pressed',
        active ? 'true' : 'false'
      );
    }
  );

  crossPopulateMetricSelect(
    true
  );
}


function initializeCrossAnalysis() {
  if (
    crossAnalysisInitialized
  ) {
    return;
  }

  const runButton =
    document.getElementById(
      'report-cross-run'
    );

  const selectA =
    document.getElementById(
      'report-cross-dimension-a'
    );

  const selectB =
    document.getElementById(
      'report-cross-dimension-b'
    );

  const metricSelect =
    document.getElementById(
      'report-cross-metric'
    );

  if (
    !runButton
    || !selectA
    || !selectB
    || !metricSelect
  ) {
    return;
  }

  crossPopulateDimensionSelects();
  crossPopulateMetricSelect(
    false
  );

  const scopeButtons = [
    ...document.querySelectorAll(
      '.report-xa-scope-button'
    )
  ];

  scopeButtons.forEach(
    function(button) {
      button.addEventListener(
        'click',
        function() {
          crossSelectScope(
            button.dataset.crossScope
          );

          runCrossAnalysis(
            true
          );
        }
      );
    }
  );

  selectA.addEventListener(
    'change',
    function() {
      crossEnsureDistinctDimensions(
        'a'
      );

      runCrossAnalysis(
        true
      );
    }
  );

  selectB.addEventListener(
    'change',
    function() {
      crossEnsureDistinctDimensions(
        'b'
      );

      runCrossAnalysis(
        true
      );
    }
  );

  metricSelect.addEventListener(
    'change',
    function() {
      runCrossAnalysis(
        true
      );
    }
  );

  runButton.addEventListener(
    'click',
    function() {
      runCrossAnalysis(
        true
      );
    }
  );

  crossAnalysisInitialized = true;
}


function renderCrossAnalysis() {
  initializeCrossAnalysis();

  if (
    !crossAnalysisInitialized
  ) {
    return;
  }

  runCrossAnalysis(
    false
  );
}


async function runCrossAnalysis(
  force
) {
  const selectA =
    document.getElementById(
      'report-cross-dimension-a'
    );

  const selectB =
    document.getElementById(
      'report-cross-dimension-b'
    );

  const metricSelect =
    document.getElementById(
      'report-cross-metric'
    );

  const state =
    document.getElementById(
      'report-cross-state'
    );

  const runButton =
    document.getElementById(
      'report-cross-run'
    );

  if (
    !selectA
    || !selectB
    || !metricSelect
    || !state
    || !runButton
  ) {
    return;
  }

  crossEnsureDistinctDimensions(
    'a'
  );

  const dimensionA =
    selectA.value;

  const dimensionB =
    selectB.value;

  const metric =
    metricSelect.value;

  const requestKey = [
    crossAnalysisScope,
    dimensionA,
    dimensionB,
    metric
  ].join('|');

  if (
    !force
    && crossAnalysisCache[
      requestKey
    ]
  ) {
    renderCrossAnalysisResult(
      crossAnalysisCache[
        requestKey
      ]
    );

    return;
  }

  const serial =
    ++crossAnalysisRequestSerial;

  runButton.disabled = true;

  state.className =
    'report-xa-state is-loading';

  state.textContent =
    'Calculating observed Dataset 1 cross-analysis...';

  const params =
    new URLSearchParams();

  params.set(
    'scope',
    crossAnalysisScope
  );

  params.set(
    'dimension_a',
    dimensionA
  );

  params.set(
    'dimension_b',
    dimensionB
  );

  params.set(
    'metric',
    metric
  );

  try {
    const response =
      await fetch(
        '/api/diagnostic/cross-analysis?'
        + params.toString(),
        {
          cache: 'no-store'
        }
      );

    const data =
      await response.json();

    if (
      !response.ok
      || data.status
        !== 'ready'
    ) {
      throw new Error(
        data.message
        || (
          'HTTP '
          + response.status
        )
      );
    }

    if (
      serial
      !== crossAnalysisRequestSerial
    ) {
      return;
    }

    crossAnalysisCache[
      requestKey
    ] = data;

    renderCrossAnalysisResult(
      data
    );

    state.className =
      'report-xa-state is-ready';

    state.textContent =
      'Observed Dataset 1 cross-analysis loaded.';
  } catch (error) {
    if (
      serial
      !== crossAnalysisRequestSerial
    ) {
      return;
    }

    state.className =
      'report-xa-state is-error';

    state.textContent =
      'Cross Analysis failed: '
      + error.message;
  } finally {
    if (
      serial
      === crossAnalysisRequestSerial
    ) {
      runButton.disabled = false;
    }
  }
}


function renderCrossAnalysisResult(
  data
) {
  const scope =
    data.scope || {};

  const dimensions =
    data.dimensions || {};

  const metric =
    data.metric || {};

  const summary =
    data.summary || {};

  const matrix =
    data.matrix || {};

  const finding =
    data.finding || {};

  const method =
    data.method || {};

  const dimensionA =
    dimensions.a || {};

  const dimensionB =
    dimensions.b || {};

  const leader =
    summary.leader || null;

  const topVolume =
    summary.top_volume || null;

  const topRate =
    summary.top_supported_rate
    || null;

  setText(
    'report-cross-note',
    fmt.format(
      scope.tickets || 0
    )
    + ' '
    + String(
      scope.label || ''
    )
    + ' tickets · '
    + String(
      dimensionA.label || ''
    )
    + ' × '
    + String(
      dimensionB.label || ''
    )
    + ' · '
    + String(
      metric.label || ''
    )
    + '.'
  );

  setText(
    'report-cross-kpi-scope',
    fmt.format(
      scope.tickets || 0
    )
    + ' tickets'
  );

  setText(
    'report-cross-kpi-scope-meta',
    scope.label || 'Ticket scope'
  );

  setText(
    'report-cross-kpi-combinations',
    fmt.format(
      summary.observed_combinations
      || 0
    )
    + ' / '
    + fmt.format(
      summary.possible_matrix_cells
      || 0
    )
  );

  setText(
    'report-cross-kpi-volume',
    crossCombinationLabel(
      topVolume
    )
  );

  setText(
    'report-cross-kpi-volume-meta',
    topVolume
      ? (
          fmt.format(
            topVolume.tickets || 0
          )
          + ' tickets'
        )
      : '—'
  );

  setText(
    'report-cross-kpi-leader',
    crossCombinationLabel(
      leader
    )
  );

  setText(
    'report-cross-kpi-leader-meta',
    leader
      ? (
          String(
            metric.label || ''
          )
          + ' · '
          + crossFormatValue(
              leader.value,
              metric
            )
        )
      : '—'
  );

  setText(
    'report-cross-chart-title',
    String(
      metric.label || 'Metric'
    )
    + ' by '
    + String(
      dimensionA.label || ''
    )
    + ' × '
    + String(
      dimensionB.label || ''
    )
  );

  setText(
    'report-cross-chart-meta',
    String(
      scope.label || ''
    )
  );

  setText(
    'report-cross-matrix-title',
    String(
      dimensionA.label || ''
    )
    + ' × '
    + String(
      dimensionB.label || ''
    )
  );

  setText(
    'report-cross-ranking-rule',
    metric.ranking_direction
      === 'asc'
      ? 'Lowest supported value first'
      : 'Highest value first'
  );

  renderCrossAnalysisChart(
    data
  );

  renderCrossAnalysisMatrix(
    data
  );

  renderCrossAnalysisRanking(
    data
  );

  setText(
    'report-cross-finding-leader-title',
    finding.headline || '—'
  );

  setText(
    'report-cross-finding-leader',
    finding.detail || '—'
  );

  setText(
    'report-cross-finding-volume-title',
    crossCombinationLabel(
      topVolume
    )
  );

  setText(
    'report-cross-finding-volume',
    topVolume
      ? (
          fmt.format(
            topVolume.tickets || 0
          )
          + ' tickets · '
          + crossFormatPct(
              (
                scope.tickets
                  ? Number(
                      topVolume.tickets
                    )
                    / Number(
                        scope.tickets
                      )
                    * 100
                  : 0
              )
            )
          + ' of selected scope.'
        )
      : '—'
  );

  if (topRate) {
    setText(
      'report-cross-finding-rate-title',
      crossCombinationLabel(
        topRate
      )
      + ' · '
      + crossFormatPct(
          topRate.secondary_pct
        )
    );

    setText(
      'report-cross-finding-rate',
      'Highest supported '
      + String(
          metric.secondary_label
          || 'rate'
        ).toLowerCase()
      + ' with n='
      + fmt.format(
          topRate.metric_count
          || 0
        )
      + '.'
    );
  } else {
    setText(
      'report-cross-finding-rate-title',
      crossFormatPct(
        metric.coverage_pct
      )
      + ' coverage'
    );

    setText(
      'report-cross-finding-rate',
      fmt.format(
        metric.valid_count || 0
      )
      + ' valid observations support the selected metric.'
    );
  }

  setText(
    'report-cross-finding-method',
    (
      metric.key
      === 'solution_time'
        ? method.solution_time_rule
        : method.causality
    )
    || 'Dataset 1 descriptive analysis.'
  );
}


function renderCrossAnalysisChart(
  data
) {
  const canvas =
    document.getElementById(
      'report-cross-chart'
    );

  if (
    !canvas
    || typeof Chart
      === 'undefined'
  ) {
    return;
  }

  const metric =
    data.metric || {};

  const ranking =
    Array.from(
      data.ranking || []
    ).slice(
      0,
      12
    );

  if (
    charts[
      'report-cross-chart'
    ]
  ) {
    charts[
      'report-cross-chart'
    ].destroy();

    delete charts[
      'report-cross-chart'
    ];
  }

  const firstColor =
    metric.semantics
    === 'positive_high'
      ? '#198754'
      : (
          metric.semantics
          === 'neutral'
            ? '#2f9a8a'
            : '#d71920'
        );

  const remainingColor =
    metric.semantics
    === 'positive_high'
      ? '#2f9a8a'
      : (
          metric.semantics
          === 'neutral'
            ? '#2e78aa'
            : '#e5b329'
        );

  const xScale = {
    beginAtZero: true,

    grid: {
      color: '#edf1f4'
    },

    ticks: {
      font: {
        family:
          'Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
        size: 12
      }
    }
  };

  if (
    metric.format
    === 'decimal'
    && metric.key
      === 'average_csat'
  ) {
    xScale.max = 5;
  }

  charts[
    'report-cross-chart'
  ] = new Chart(
    canvas,
    {
      type: 'bar',

      data: {
        labels: ranking.map(
          function(row) {
            return crossCombinationLabel(
              row
            );
          }
        ),

        datasets: [
          {
            label:
              metric.label
              || 'Metric',

            data: ranking.map(
              function(row) {
                return row.value;
              }
            ),

            backgroundColor:
              ranking.map(
                function(row, index) {
                  return (
                    index === 0
                      ? firstColor
                      : remainingColor
                  );
                }
              ),

            borderWidth: 0,
            borderRadius: 8,
            barThickness: 30
          }
        ]
      },

      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,

        animation: {
          duration: 450
        },

        plugins: {
          legend: {
            display: false
          },

          tooltip: {
            callbacks: {
              label: function(context) {
                const row =
                  ranking[
                    context.dataIndex
                  ];

                let text =
                  ' '
                  + String(
                      metric.label || ''
                    )
                  + ': '
                  + crossFormatValue(
                      row.value,
                      metric
                    );

                text += (
                  ' · '
                  + fmt.format(
                      row.tickets || 0
                    )
                  + ' tickets'
                );

                if (
                  row.secondary_pct
                  !== null
                  && row.secondary_pct
                  !== undefined
                ) {
                  text += (
                    ' · '
                    + String(
                        metric.secondary_label
                        || ''
                      )
                    + ': '
                    + crossFormatPct(
                        row.secondary_pct
                      )
                  );
                }

                return text;
              }
            }
          }
        },

        scales: {
          x: xScale,

          y: {
            grid: {
              display: false
            },

            ticks: {
              color: '#283845',

              font: {
                family:
                  'Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
                size: 12,
                weight: '700'
              }
            }
          }
        }
      }
    }
  );
}


function crossMatrixTone(
  value,
  minValue,
  maxValue
) {
  if (
    value === null
    || value === undefined
    || !Number.isFinite(
      Number(value)
    )
  ) {
    return 'is-empty';
  }

  const min =
    Number(minValue);

  const max =
    Number(maxValue);

  if (
    !Number.isFinite(min)
    || !Number.isFinite(max)
    || max <= min
  ) {
    return 'tone-2';
  }

  const ratio =
    (
      Number(value)
      - min
    )
    / (
      max
      - min
    );

  if (ratio >= 0.7) {
    return 'tone-3';
  }

  if (ratio >= 0.35) {
    return 'tone-2';
  }

  return 'tone-1';
}


function renderCrossAnalysisMatrix(
  data
) {
  const target =
    document.getElementById(
      'report-cross-matrix'
    );

  if (!target) return;

  const matrix =
    data.matrix || {};

  const metric =
    data.metric || {};

  const dimensions =
    data.dimensions || {};

  const dimensionA =
    dimensions.a || {};

  const dimensionB =
    dimensions.b || {};

  const columns =
    Array.from(
      matrix.columns || []
    );

  const rows =
    Array.from(
      matrix.rows || []
    );

  const head =
    '<thead><tr>'
    + '<th>'
    + escapeHtml(
        String(
          dimensionA.label || ''
        )
      )
    + ' × '
    + escapeHtml(
        String(
          dimensionB.label || ''
        )
      )
    + '</th>'
    + columns.map(
        function(column) {
          return (
            '<th title="'
            + escapeHtml(
                fmt.format(
                  column.tickets || 0
                )
                + ' tickets'
              )
            + '">'
            + escapeHtml(
                column.label
              )
            + '</th>'
          );
        }
      ).join('')
    + '</tr></thead>';

  const body =
    '<tbody>'
    + rows.map(
        function(row) {
          return (
            '<tr>'
            + '<th>'
            + escapeHtml(
                row.label
              )
            + '<small>'
            + fmt.format(
                row.tickets || 0
              )
            + ' tickets</small>'
            + '</th>'
            + Array.from(
                row.cells || []
              ).map(
                function(cell) {
                  const tone =
                    crossMatrixTone(
                      cell.value,
                      matrix.min_value,
                      matrix.max_value
                    );

                  let title =
                    fmt.format(
                      cell.tickets || 0
                    )
                    + ' tickets';

                  if (
                    cell.secondary_pct
                    !== null
                    && cell.secondary_pct
                    !== undefined
                  ) {
                    title += (
                      ' · '
                      + String(
                          metric.secondary_label
                          || ''
                        )
                      + ': '
                      + crossFormatPct(
                          cell.secondary_pct
                        )
                    );
                  }

                  return (
                    '<td class="'
                    + tone
                    + '" title="'
                    + escapeHtml(title)
                    + '">'
                    + crossFormatValue(
                        cell.value,
                        metric
                      )
                    + '</td>'
                  );
                }
              ).join('')
            + '</tr>'
          );
        }
      ).join('')
    + '</tbody>';

  target.innerHTML =
    '<table class="report-xa-matrix">'
    + head
    + body
    + '</table>';
}


function renderCrossAnalysisRanking(
  data
) {
  const target =
    document.getElementById(
      'report-cross-ranking'
    );

  if (!target) return;

  const metric =
    data.metric || {};

  const dimensions =
    data.dimensions || {};

  const dimensionA =
    dimensions.a || {};

  const dimensionB =
    dimensions.b || {};

  const rows =
    Array.from(
      data.ranking || []
    ).slice(
      0,
      15
    );

  target.innerHTML =
    '<table class="report-xa-ranking">'
    + '<thead><tr>'
    + '<th>#</th>'
    + '<th>'
    + escapeHtml(
        String(
          dimensionA.label || ''
        )
      )
    + '</th>'
    + '<th>'
    + escapeHtml(
        String(
          dimensionB.label || ''
        )
      )
    + '</th>'
    + '<th>Tickets</th>'
    + '<th>'
    + escapeHtml(
        String(
          metric.label || 'Metric'
        )
      )
    + '</th>'
    + '<th>'
    + escapeHtml(
        String(
          metric.secondary_label
          || 'Context'
        )
      )
    + '</th>'
    + '</tr></thead>'
    + '<tbody>'
    + rows.map(
        function(row, index) {
          return (
            '<tr>'
            + '<td><strong>'
            + fmt.format(
                index + 1
              )
            + '</strong></td>'
            + '<td>'
            + escapeHtml(
                row.dimension_a_value
              )
            + '</td>'
            + '<td>'
            + escapeHtml(
                row.dimension_b_value
              )
            + '</td>'
            + '<td>'
            + fmt.format(
                row.tickets || 0
              )
            + '</td>'
            + '<td><strong>'
            + crossFormatValue(
                row.value,
                metric
              )
            + '</strong></td>'
            + '<td>'
            + crossFormatPct(
                row.secondary_pct
              )
            + '</td>'
            + '</tr>'
          );
        }
      ).join('')
    + '</tbody>'
    + '</table>';
}

// -----------------------------------------------------------------------------
// DIAGNOSTIC CHARTS
// -----------------------------------------------------------------------------
function renderDiagnosticCharts(data) {
  if (typeof Chart === 'undefined') return;
  const build = (id, rows, label) => {
    const canvas = document.getElementById(id);
    if (!canvas) return;
    if (charts[id]) charts[id].destroy();
    charts[id] = new Chart(canvas, {
      type: 'bar',
      data: {labels: rows.map(r => r.label), datasets: [{label, data: rows.map(r => r.count), borderWidth: 1}]},
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {legend: {display: false}},
        scales: {
          y: {beginAtZero: true, ticks: {precision: 0}},
          x: {ticks: {maxRotation: 35, minRotation: 0}}
        }
      }
    });
  };
  build('status-chart', data.volume.by_status || [], 'Tickets');
  build('type-chart', data.volume.by_type || [], 'Tickets');
}

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
}

document.getElementById('refresh-audit').addEventListener('click', () => { loadAudit(); loadDiagnostic(); loadDataset2Diagnostic(); });
loadAudit();
loadDiagnostic();
loadDataset2Diagnostic();

// -----------------------------------------------------------------------------
// DATASET 1 EXPLORER — OPERATIONAL DIAGNOSIS
// -----------------------------------------------------------------------------
let explorerSummary = null;
let explorerPage = 1;
let automationD2Page = 1;

function datasetConfig(name) {
  return explorerSummary?.datasets?.[name] || null;
}

async function loadExplorerSummary() {
  try {
    const response = await fetch('/api/explorer/summary', {cache: 'no-store'});
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    explorerSummary = data;
    if (data.status !== 'ready') throw new Error(data.message || 'Explorer unavailable');

    const d1 = data.datasets.dataset1;
    const d2 = data.datasets.dataset2;

    setText('explorer-d1-rows', fmt.format(d1.rows));
    setText('explorer-d1-meta', `${d1.columns_count} fields · operational tickets · ${d1.file}`);
    setText('about-d1-rows', fmt.format(d1.rows));
    setText('about-d2-rows', fmt.format(d2.rows));
    setText('automation-d2-rows', fmt.format(d2.rows));
    setText('automation-d2-file', d2.file);
    setText('explorer-current-file', d1.file);

    renderExplorerEvidence();
    configureExplorerFilters();
    configureAutomationD2Filters();
    await Promise.all([loadExplorerRows(), loadAutomationD2Rows()]);
  } catch (err) {
    const wrap = document.getElementById('explorer-table-wrap');
    if (wrap) wrap.innerHTML = `<div class="empty">Failed to load Dataset Explorer: ${escapeHtml(err.message)}</div>`;
    const d2Wrap = document.getElementById('automation-d2-table-wrap');
    if (d2Wrap) d2Wrap.innerHTML = `<div class="empty">Failed to load training corpus: ${escapeHtml(err.message)}</div>`;
  }
}

function renderExplorerEvidence() {
  if (currentDiagnostic?.status === 'ready') {
    const snap = currentDiagnostic.flow?.snapshot || {};
    const total = Number(currentDiagnostic.rows || 0);
    const pair = (count) => `${fmt.format(count || 0)} · ${pct(total ? (Number(count || 0) / total * 100) : 0)}`;
    setText('explorer-flow-open', pair(snap.open));
    setText('explorer-flow-pending', pair(snap.pending_customer));
    setText('explorer-flow-closed-resolution', pair(snap.closed_with_resolution));
    setText('explorer-flow-closed-no-resolution', pair(snap.closed_without_resolution));
    renderDimensionMix('explorer-channel-mix', currentDiagnostic.volume?.by_channel || []);
    renderDimensionMix('explorer-priority-mix', currentDiagnostic.volume?.by_priority || []);
    renderDimensionMix('explorer-type-mix', currentDiagnostic.volume?.by_type || []);
  }

  const c = explorerSummary?.customer_summary;
  if (c?.status === 'ready') {
    setText('explorer-customer-emails', fmt.format(c.unique_customer_emails));
    setText('explorer-customer-names', fmt.format(c.unique_customer_names));
    setText('explorer-repeat-customers', `${fmt.format(c.multi_ticket_customers)} · ${pct(c.multi_ticket_customer_pct)}`);
    setText('explorer-repeat-customers-meta', `${fmt.format(c.tickets_from_multi_ticket_customers)} tickets belong to repeat customers`);
    setText('explorer-max-tickets-customer', fmt.format(c.max_tickets_per_customer));
    setText('explorer-customer-note', c.note);
  }
}

function configureExplorerFilters() {
  const config = datasetConfig('dataset1');
  if (!config) return;
  const field = document.getElementById('explorer-filter-field');
  const value = document.getElementById('explorer-filter-value');
  field.innerHTML = '<option value="">No filter</option>' + Object.keys(config.filters || {})
    .map(name => `<option value="${escapeHtml(name)}">${escapeHtml(name)}</option>`).join('');
  value.innerHTML = '<option value="">All</option>';
  value.disabled = true;
}

function configureExplorerValues() {
  const config = datasetConfig('dataset1');
  const field = document.getElementById('explorer-filter-field');
  const value = document.getElementById('explorer-filter-value');
  const values = config?.filters?.[field.value] || [];
  value.innerHTML = '<option value="">All</option>' + values.map(v => `<option value="${escapeHtml(v)}">${escapeHtml(v)}</option>`).join('');
  value.disabled = !field.value;
}

async function loadExplorerRows() {
  const wrap = document.getElementById('explorer-table-wrap');
  if (!wrap || !explorerSummary || explorerSummary.status !== 'ready') return;
  wrap.innerHTML = '<div class="empty">Loading original data...</div>';

  const params = new URLSearchParams({
    page: String(explorerPage),
    page_size: document.getElementById('explorer-page-size').value,
    q: document.getElementById('explorer-query').value.trim(),
    filter_field: document.getElementById('explorer-filter-field').value,
    filter_value: document.getElementById('explorer-filter-value').value,
  });

  try {
    const response = await fetch(`/api/explorer/dataset1/rows?${params.toString()}`, {cache: 'no-store'});
    const data = await response.json();
    if (!response.ok || data.status !== 'ready') throw new Error(data.error || `HTTP ${response.status}`);
    renderRawTable(wrap, data);
    explorerPage = data.pagination.page;
    setText('explorer-page-info', `Page ${data.pagination.page} of ${data.pagination.total_pages} · ${fmt.format(data.pagination.total_rows)} rows`);
    document.getElementById('explorer-prev').disabled = data.pagination.page <= 1;
    document.getElementById('explorer-next').disabled = data.pagination.page >= data.pagination.total_pages;
  } catch (err) {
    wrap.innerHTML = `<div class="empty">Failed to read Dataset 1: ${escapeHtml(err.message)}</div>`;
  }
}

function configureAutomationD2Filters() {
  const config = datasetConfig('dataset2');
  if (!config) return;
  const field = document.getElementById('automation-d2-filter-field');
  const value = document.getElementById('automation-d2-filter-value');
  if (!field || !value) return;
  field.innerHTML = '<option value="">No filter</option>' + Object.keys(config.filters || {})
    .map(name => `<option value="${escapeHtml(name)}">${escapeHtml(name)}</option>`).join('');
  value.innerHTML = '<option value="">All</option>';
  value.disabled = true;
}

function configureAutomationD2Values() {
  const config = datasetConfig('dataset2');
  const field = document.getElementById('automation-d2-filter-field');
  const value = document.getElementById('automation-d2-filter-value');
  if (!field || !value) return;
  const values = config?.filters?.[field.value] || [];
  value.innerHTML = '<option value="">All</option>' + values.map(v => `<option value="${escapeHtml(v)}">${escapeHtml(v)}</option>`).join('');
  value.disabled = !field.value;
}

async function loadAutomationD2Rows() {
  const wrap = document.getElementById('automation-d2-table-wrap');
  if (!wrap || !explorerSummary || explorerSummary.status !== 'ready') return;
  wrap.innerHTML = '<div class="empty">Loading corpus...</div>';

  const params = new URLSearchParams({
    page: String(automationD2Page),
    page_size: document.getElementById('automation-d2-page-size').value,
    q: document.getElementById('automation-d2-query').value.trim(),
    filter_field: document.getElementById('automation-d2-filter-field').value,
    filter_value: document.getElementById('automation-d2-filter-value').value,
  });

  try {
    const response = await fetch(`/api/explorer/dataset2/rows?${params.toString()}`, {cache: 'no-store'});
    const data = await response.json();
    if (!response.ok || data.status !== 'ready') throw new Error(data.error || `HTTP ${response.status}`);
    renderRawTable(wrap, data);
    automationD2Page = data.pagination.page;
    setText('automation-d2-page-info', `Page ${data.pagination.page} of ${data.pagination.total_pages} · ${fmt.format(data.pagination.total_rows)} rows`);
    document.getElementById('automation-d2-prev').disabled = data.pagination.page <= 1;
    document.getElementById('automation-d2-next').disabled = data.pagination.page >= data.pagination.total_pages;
  } catch (err) {
    wrap.innerHTML = `<div class="empty">Failed to read Dataset 2: ${escapeHtml(err.message)}</div>`;
  }
}

function renderRawTable(wrap, data) {
  if (!data.rows.length) {
    wrap.innerHTML = '<div class="empty">No rows match the current filters.</div>';
    return;
  }
  const head = data.columns.map(c => `<th>${escapeHtml(c)}</th>`).join('');
  const body = data.rows.map(row => `<tr>${data.columns.map(c => {
    const raw = row[c];
    const display = raw === null ? '—' : String(raw);
    return `<td title="${escapeHtml(display)}">${escapeHtml(display)}</td>`;
  }).join('')}</tr>`).join('');
  wrap.innerHTML = `<table class="raw-table"><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table>`;
}

document.getElementById('explorer-filter-field')?.addEventListener('change', () => { configureExplorerValues(); explorerPage = 1; });
document.getElementById('explorer-apply')?.addEventListener('click', () => { explorerPage = 1; loadExplorerRows(); });
document.getElementById('explorer-page-size')?.addEventListener('change', () => { explorerPage = 1; loadExplorerRows(); });
document.getElementById('explorer-query')?.addEventListener('keydown', event => { if (event.key === 'Enter') { explorerPage = 1; loadExplorerRows(); } });
document.getElementById('explorer-prev')?.addEventListener('click', () => { if (explorerPage > 1) { explorerPage -= 1; loadExplorerRows(); } });
document.getElementById('explorer-next')?.addEventListener('click', () => { explorerPage += 1; loadExplorerRows(); });

document.getElementById('automation-d2-filter-field')?.addEventListener('change', () => { configureAutomationD2Values(); automationD2Page = 1; });
document.getElementById('automation-d2-apply')?.addEventListener('click', () => { automationD2Page = 1; loadAutomationD2Rows(); });
document.getElementById('automation-d2-page-size')?.addEventListener('change', () => { automationD2Page = 1; loadAutomationD2Rows(); });
document.getElementById('automation-d2-query')?.addEventListener('keydown', event => { if (event.key === 'Enter') { automationD2Page = 1; loadAutomationD2Rows(); } });
document.getElementById('automation-d2-prev')?.addEventListener('click', () => { if (automationD2Page > 1) { automationD2Page -= 1; loadAutomationD2Rows(); } });
document.getElementById('automation-d2-next')?.addEventListener('click', () => { automationD2Page += 1; loadAutomationD2Rows(); });

loadExplorerSummary();

// -----------------------------------------------------------------------------
// DATASET 2 — TRAINING CORPUS DIAGNOSTICS
// -----------------------------------------------------------------------------
async function loadDataset2Diagnostic() {
  const topicMix = document.getElementById('topic-group-mix');
  const qualityMetrics = document.getElementById('document-quality-metrics');
  if (!topicMix && !qualityMetrics) return;
  try {
    const response = await fetch('/api/dataset2/diagnostic', {cache: 'no-store'});
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    if (data.status !== 'ready') throw new Error(data.message || 'Dataset 2 unavailable');

    if (topicMix) renderDimensionMix('topic-group-mix', data.topic_groups.rows || []);
    setText('topic-group-note', data.topic_groups.interpretation);

    const q = data.document_quality;
    if (qualityMetrics) {
      qualityMetrics.innerHTML = [
        ['Documents', fmt.format(q.documents)],
        ['Exact duplicates', fmt.format(q.exact_duplicate_documents)],
        ['Tokens · median', dec(q.token_count_median)],
        ['Unique tokens · mean', pct(q.mean_unique_token_ratio_pct)],
        ['Repeated bigrams', `${fmt.format(q.documents_with_repeated_bigrams)} · ${pct(q.documents_with_repeated_bigrams_pct)}`],
        ['Mean bigram repetition', pct(q.mean_repeated_bigram_ratio_pct)],
        ['Contains punctuation', pct(q.documents_with_punctuation_pct)],
        ['Lowercase only', pct(q.lowercase_only_pct)],
      ].map(([label, value]) => `<div><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong></div>`).join('');
    }
    setText('document-quality-note', q.interpretation);
  } catch (err) {
    if (topicMix) topicMix.innerHTML = `<div class="empty">Failed to analyze Dataset 2: ${escapeHtml(err.message)}</div>`;
    if (qualityMetrics) qualityMetrics.innerHTML = `<div class="empty">Failed to audit Document: ${escapeHtml(err.message)}</div>`;
  }
}

// AM6 CONNECTION A: APPLICATION SERVER TO API GATEWAY
// Single owner: dynamic connector within Option A.
(function () {
  const host = document.querySelector(
    '#architecture-map .am6-api-internal-layout'
  );
  const source = document.querySelector(
    '[data-am6-node="a-application-server"]'
  );
  const target = document.querySelector(
    '[data-am6-node="a-api-gateway"]'
  );
  const path = host?.querySelector(
    '.am6-application-gateway-link path'
  );
  if (!host || !source || !target || !path) return;

  host.style.position = 'relative';

  function draw() {
    const panel = document.getElementById('architecture-map');
    if (!panel?.classList.contains('active')) return;

    const base = host.getBoundingClientRect();
    const a = source.getBoundingClientRect();
    const b = target.getBoundingClientRect();
    if (!base.width || !base.height || !a.width || !b.width) return;

    // Right-center of Application Server.
    const x1 = a.right - base.left;
    const y1 = a.top + a.height / 2 - base.top;

    // Top-center of API Gateway.
    const x2 = b.left + b.width / 2 - base.left;
    const y2 = b.top - base.top;

    // Single horizontal run, followed by a vertical drop.
    // The corner is rounded by the SVG stroke-linejoin.
    path.setAttribute(
      'd',
      `M ${x1} ${y1} H ${x2} V ${y2}`
    );
  }

  const schedule = () => requestAnimationFrame(draw);
  window.addEventListener('resize', schedule);
  document.querySelectorAll('[data-target="architecture-map"]')
    .forEach(button => button.addEventListener('click', schedule));

  if (typeof ResizeObserver !== 'undefined') {
    const observer = new ResizeObserver(schedule);
    observer.observe(host);
    observer.observe(source);
    observer.observe(target);
  }

  schedule();
})();

// AM6 ORANGE FLOW: SECRETS AND EGRESS TO GATEWAY
(function () {
  function init() {
    const host = document.querySelector(
      '#architecture-map .am6-api-internal-layout');
    if (!host || host.querySelector('[data-am6-orange-flow]')) return;

    const node = id => document.querySelector(
      '#architecture-map [data-am6-node="' + id + '"]');
    const secrets = node('a-secrets-manager');
    const egress = node('a-egress-policy');
    const gateway = node('a-api-gateway');
    if (!secrets || !egress || !gateway) return;

    const ns = 'http://www.w3.org/2000/svg';
    const svg = document.createElementNS(ns, 'svg');
    svg.setAttribute('data-am6-orange-flow', '');
    svg.setAttribute('aria-hidden', 'true');
    Object.assign(svg.style, {
      position:'absolute', inset:'0', width:'100%', height:'100%',
      overflow:'visible', pointerEvents:'none', zIndex:'3'
    });

    function path() {
      const p = document.createElementNS(ns, 'path');
      for (const [k,v] of Object.entries({
        fill:'none', stroke:'#e58c17', 'stroke-width':'2.5',
        'stroke-dasharray':'6 5', 'stroke-linecap':'round',
        'stroke-linejoin':'round'
      })) p.setAttribute(k,v);
      svg.appendChild(p);
      return p;
    }

    const a=path(), b=path(), trunk=path();
    const dot=document.createElementNS(ns,'circle');
    dot.setAttribute('r','3.5');
    dot.setAttribute('fill','#e58c17');
    svg.appendChild(dot);

    if (getComputedStyle(host).position==='static')
      host.style.position='relative';
    a.setAttribute('data-am6-route-title', "Secrets Manager → Security Junction");
    a.setAttribute('data-am6-route-purpose', "Credential controls enter the shared security junction.");
    b.setAttribute('data-am6-route-title', "Egress Policy → Security Junction");
    b.setAttribute('data-am6-route-purpose', "Outbound data controls enter the shared security junction.");
    trunk.setAttribute('data-am6-route-title', "Security Junction → API Gateway");
    trunk.setAttribute('data-am6-route-purpose', "Combined security controls reach the API Gateway.");
    host.appendChild(svg);

    function draw() {
      const h=host.getBoundingClientRect();
      const s=secrets.getBoundingClientRect();
      const e=egress.getBoundingClientRect();
      const g=gateway.getBoundingClientRect();
      if (!h.width || !h.height) return;

      const sx=s.right-h.left, sy=s.top+s.height/2-h.top;
      const ex=e.right-h.left, ey=e.top+e.height/2-h.top;
      const gx=g.left-h.left, gy=g.top+g.height/2-h.top;
      const jx=(Math.max(sx,ex)+gx)/2, jy=gy;

      function branch(x,y) {
        const control=(jx-x)*0.55;
        return `M ${x} ${y} C ${x+control} ${y}, `+
               `${jx-control} ${jy}, ${jx} ${jy}`;
      }

      svg.setAttribute('viewBox',`0 0 ${h.width} ${h.height}`);
      a.setAttribute('d',branch(sx,sy));
      b.setAttribute('d',branch(ex,ey));
      trunk.setAttribute('d',`M ${jx} ${jy} H ${gx}`);
      dot.setAttribute('cx',jx);
      dot.setAttribute('cy',jy);
    }

    let pending=false;
    function schedule() {
      if (pending) return;
      pending=true;
      requestAnimationFrame(()=>{pending=false;draw();});
    }
    if (typeof ResizeObserver!=='undefined') {
      const observer=new ResizeObserver(schedule);
      [host,secrets,egress,gateway].forEach(n=>observer.observe(n));
    }
    window.addEventListener('resize',schedule);
    schedule();
  }
  if (document.readyState==='loading')
    document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();
})();

// AM6 BLUE FLOW: GATEWAY TO RETRIEVAL AND KNOWLEDGE
// Owner: Option A cross-zone retrieval connections.
(function () {
  function initBlueRagFlow() {
    var host = document.querySelector(
      '#architecture-map .am6-api .am6-topology'
    );
    if (!host || host.querySelector('[data-am6-blue-rag]')) return;

    function node(id) {
      return host.querySelector('[data-am6-node="' + id + '"]');
    }

    var gateway = node('a-api-gateway');
    var indexNode = node('a-index-retrieval');
    var knowledge = node('a-knowledge-store');
    var promptBuilder = node('a-prompt-builder');

    if (!gateway || !indexNode || !knowledge || !promptBuilder) return;

    var ns = 'http://www.w3.org/2000/svg';
    var svg = document.createElementNS(ns, 'svg');
    svg.setAttribute('data-am6-blue-rag', '');
    svg.setAttribute('aria-hidden', 'true');

    Object.assign(svg.style, {
      position: 'absolute',
      inset: '0',
      width: '100%',
      height: '100%',
      overflow: 'visible',
      pointerEvents: 'none',
      zIndex: '3'
    });

    function makePath() {
      var p = document.createElementNS(ns, 'path');
      p.setAttribute('fill', 'none');
      p.setAttribute('stroke', '#168ed0');
      p.setAttribute('stroke-width', '2.5');
      p.setAttribute('stroke-dasharray', '6 5');
      p.setAttribute('stroke-linecap', 'round');
      p.setAttribute('stroke-linejoin', 'round');
      svg.appendChild(p);
      return p;
    }

    var toIndex = makePath();
    var toKnowledge = makePath();
    var knowledgeToIndex = makePath();
    var indexToPrompt = makePath();
    var toPrompt = makePath();
    toPrompt.setAttribute('stroke', '#e58c17');

    if (getComputedStyle(host).position === 'static') {
      host.style.position = 'relative';
    }
    toIndex.setAttribute('data-am6-route-title', "API Gateway → Index / Retrieval");
    toIndex.setAttribute('data-am6-route-purpose', "Routes requests into the retrieval layer.");
    toKnowledge.setAttribute('data-am6-route-title', "Gateway Branch → Knowledge Store");
    toKnowledge.setAttribute('data-am6-route-purpose', "Connects the gateway request path with source knowledge.");
    knowledgeToIndex.setAttribute('data-am6-route-title', "Knowledge Store → Index / Retrieval");
    knowledgeToIndex.setAttribute('data-am6-route-purpose', "Connects source knowledge to retrieval.");
    indexToPrompt.setAttribute('data-am6-route-title', "Index / Retrieval → Prompt Builder");
    indexToPrompt.setAttribute('data-am6-route-purpose', "Supplies retrieved context for prompt preparation.");
    toPrompt.setAttribute('data-am6-route-title', "Gateway Branch → Prompt Builder");
    toPrompt.setAttribute('data-am6-route-purpose', "Routes request context toward prompt preparation.");
    host.appendChild(svg);

    function draw() {
      var panel = document.getElementById('architecture-map');
      if (!panel || !panel.classList.contains('active')) return;

      var hostBox = host.getBoundingClientRect();
      var gatewayBox = gateway.getBoundingClientRect();
      var indexBox = indexNode.getBoundingClientRect();
      var knowledgeBox = knowledge.getBoundingClientRect();
      var promptBox = promptBuilder.getBoundingClientRect();

      if (!hostBox.width || !gatewayBox.width || !indexBox.width || !knowledgeBox.width) {
        return;
      }

      // API Gateway: lateral direita
      var gx = Math.round(gatewayBox.right - hostBox.left);

      // Index / Retrieval: lateral esquerda + centro vertical
      var ix = Math.round(indexBox.left - hostBox.left);
      var iy = Math.round(indexBox.top + (indexBox.height / 2) - hostBox.top);

      // Knowledge Store: lateral esquerda + centro vertical
      var kx = Math.round(knowledgeBox.left - hostBox.left);
      var ky = Math.round(knowledgeBox.top + (knowledgeBox.height / 2) - hostBox.top);

      // Linha principal: reta horizontal até o Index / Retrieval
      toIndex.setAttribute(
        'd',
        'M ' + gx + ' ' + iy + ' L ' + ix + ' ' + iy
      );

      // Ramificação sobe a partir da linha principal e entra
      // na lateral esquerda do Knowledge Store
      var branchX = Math.round(gx + ((ix - gx) * 0.42));
      var deltaY = Math.abs(iy - ky);
      var deltaX = Math.abs(kx - branchX);
      var radius = Math.max(6, Math.min(12, deltaY / 3, deltaX / 3));

      var verticalStop = ky + radius;

      toKnowledge.setAttribute(
        'd',
        'M ' + branchX + ' ' + iy +
        ' V ' + verticalStop +
        ' Q ' + branchX + ' ' + ky + ' ' + (branchX + radius) + ' ' + ky +
        ' H ' + kx
      );

      // Orange flow starts 2px below the blue connection.
      // It turns downward and terminates at Prompt Builder's left edge.
      var py = Math.round(
        promptBox.top + promptBox.height / 2 - hostBox.top
      );
      var px = Math.round(promptBox.left - hostBox.left);
      var startY = iy + 2;
      var startX = gx;

      // Keep the bend within the gap between the two zones.
      var gap = px - startX;
      var radius = Math.max(0, Math.min(
        10, gap / 6, Math.abs(py - startY) / 4
      ));
      var bendX = startX + gap * 0.48;

      var orangePath;
      if (gap > 0 && py > startY && radius > 0) {
        orangePath =
          'M ' + startX + ' ' + startY +
          ' H ' + (bendX - radius) +
          ' Q ' + bendX + ' ' + startY +
          ' ' + bendX + ' ' + (startY + radius) +
          ' V ' + (py - radius) +
          ' Q ' + bendX + ' ' + py +
          ' ' + (bendX + radius) + ' ' + py +
          ' H ' + px;
      } else {
        // Geometry fallback, without changing any card position.
        orangePath =
          'M ' + startX + ' ' + startY +
          ' H ' + bendX +
          ' V ' + py +
          ' H ' + px;
      }
      toPrompt.setAttribute('d', orangePath);

      // RAG vertical flow: bottom-center to top-center.
      var promptBox = promptBuilder.getBoundingClientRect();

      var knowledgeBottomX =
        knowledgeBox.left + knowledgeBox.width / 2 - hostBox.left;
      var knowledgeBottomY = knowledgeBox.bottom - hostBox.top;
      var indexTopX =
        indexBox.left + indexBox.width / 2 - hostBox.left;
      var indexTopY = indexBox.top - hostBox.top;

      var indexBottomX =
        indexBox.left + indexBox.width / 2 - hostBox.left;
      var indexBottomY = indexBox.bottom - hostBox.top;
      var promptTopX =
        promptBox.left + promptBox.width / 2 - hostBox.left;
      var promptTopY = promptBox.top - hostBox.top;

      knowledgeToIndex.setAttribute(
        'd',
        'M ' + knowledgeBottomX + ' ' + knowledgeBottomY +
        ' L ' + indexTopX + ' ' + indexTopY
      );

      indexToPrompt.setAttribute(
        'd',
        'M ' + indexBottomX + ' ' + indexBottomY +
        ' L ' + promptTopX + ' ' + promptTopY
      );

      svg.setAttribute(
        'viewBox',
        '0 0 ' + Math.ceil(hostBox.width) + ' ' + Math.ceil(hostBox.height)
      );
    }

    var pending = false;
    function schedule() {
      if (pending) return;
      pending = true;
      requestAnimationFrame(function () {
        pending = false;
        draw();
      });
    }

    if (typeof ResizeObserver !== 'undefined') {
      var observer = new ResizeObserver(schedule);
      [host, gateway, indexNode, knowledge, promptBuilder].forEach(function (el) {
        observer.observe(el);
      });
    }

    document.querySelectorAll('[data-target="architecture-map"]').forEach(function (button) {
      button.addEventListener('click', schedule);
    });

    window.addEventListener('resize', schedule);
    schedule();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initBlueRagFlow, { once: true });
  } else {
    initBlueRagFlow();
  }
})();

// AM6 BLUE FLOW: RAG THREE NODES TO EXTERNAL PROVIDER
// Owner: Option A, rectilinear RAG-to-provider connection.
(function () {
  function init() {
    const host = document.querySelector(
      '#architecture-map .am6-api .am6-topology'
    );
    if (!host || host.querySelector('[data-am6-provider-flow]')) return;

    const node = id => host.querySelector(
      '[data-am6-node="' + id + '"]'
    );

    const knowledge = node('a-knowledge-store');
    const retrieval = node('a-index-retrieval');
    const prompt = node('a-prompt-builder');
    const provider = node('a-external-provider-api');

    if (!knowledge || !retrieval || !prompt || !provider) return;

    const ns = 'http://www.w3.org/2000/svg';
    const svg = document.createElementNS(ns, 'svg');
    svg.setAttribute('data-am6-provider-flow', '');
    svg.setAttribute('aria-hidden', 'true');

    Object.assign(svg.style, {
      position: 'absolute',
      inset: '0',
      width: '100%',
      height: '100%',
      overflow: 'visible',
      pointerEvents: 'none',
      zIndex: '3'
    });

    function makePath() {
      const p = document.createElementNS(ns, 'path');
      [
        ['fill', 'none'],
        ['stroke', '#168ed0'],
        ['stroke-width', '2.5'],
        ['stroke-dasharray', '6 5'],
        ['stroke-linecap', 'round'],
        ['stroke-linejoin', 'round']
      ].forEach(([k, v]) => p.setAttribute(k, v));
      svg.appendChild(p);
      return p;
    }

    const pKnowledge = makePath();
    const pRetrieval = makePath();
    const pPrompt = makePath();
    const pCollector = makePath();
    const pTrunk = makePath();

    const dot = document.createElementNS(ns, 'circle');
    dot.setAttribute('r', '3.5');
    dot.setAttribute('fill', '#168ed0');
    svg.appendChild(dot);

    if (getComputedStyle(host).position === 'static') {
      host.style.position = 'relative';
    }
    pKnowledge.setAttribute('data-am6-route-title', "Knowledge Store → Context Junction");
    pKnowledge.setAttribute('data-am6-route-purpose', "Knowledge branch feeding the context collector.");
    pRetrieval.setAttribute('data-am6-route-title', "Index / Retrieval → Context Junction");
    pRetrieval.setAttribute('data-am6-route-purpose', "Retrieval branch feeding the context collector.");
    pPrompt.setAttribute('data-am6-route-title', "Prompt Builder → Context Junction");
    pPrompt.setAttribute('data-am6-route-purpose', "Prepared prompt feeding the context collector.");
    pCollector.setAttribute('data-am6-route-title', "Context Junction");
    pCollector.setAttribute('data-am6-route-purpose', "Collector shared by the three context branches.");
    pTrunk.setAttribute('data-am6-route-title', "Context Junction → External Provider API");
    pTrunk.setAttribute('data-am6-route-purpose', "Combined context routed to the external provider.");
    host.appendChild(svg);

    function draw() {
      const panel = document.getElementById('architecture-map');
      if (!panel || !panel.classList.contains('active')) return;

      const base = host.getBoundingClientRect();
      const k = knowledge.getBoundingClientRect();
      const r = retrieval.getBoundingClientRect();
      const p = prompt.getBoundingClientRect();
      const t = provider.getBoundingClientRect();

      if (!base.width || !base.height || !k.width || !r.width || !p.width || !t.width) {
        return;
      }

      const kx = k.right - base.left;
      const ky = k.top + k.height / 2 - base.top;

      const rx = r.right - base.left;
      const ry = r.top + r.height / 2 - base.top;

      const px = p.right - base.left;
      const py = p.top + p.height / 2 - base.top;

      const tx = t.left - base.left;
      const ty = t.top + t.height / 2 - base.top;

      const maxSourceX = Math.max(kx, rx, px);

      // Coletor vertical mais reto, no mesmo padrão do outro lado.
      // Mantém folga antes do provider e não invade os cards.
      const collectorX = Math.min(tx - 26, maxSourceX + 34);

      const topY = Math.min(ky, ry, py);
      const bottomY = Math.max(ky, ry, py);

      svg.setAttribute('viewBox', '0 0 ' + base.width + ' ' + base.height);

      // Saídas horizontais dos microcards.
      pKnowledge.setAttribute('d', 'M ' + kx + ' ' + ky + ' H ' + collectorX);
      pRetrieval.setAttribute('d', 'M ' + rx + ' ' + ry + ' H ' + collectorX);
      pPrompt.setAttribute('d', 'M ' + px + ' ' + py + ' H ' + collectorX);

      // Coletor vertical.
      pCollector.setAttribute('d', 'M ' + collectorX + ' ' + topY + ' V ' + bottomY);

      // Saída única até a lateral esquerda do provider.
      pTrunk.setAttribute('d', 'M ' + collectorX + ' ' + ty + ' H ' + tx);

      dot.setAttribute('cx', collectorX);
      dot.setAttribute('cy', ty);
    }

    let pending = false;
    function schedule() {
      if (pending) return;
      pending = true;
      requestAnimationFrame(function () {
        pending = false;
        draw();
      });
    }

    if (typeof ResizeObserver !== 'undefined') {
      const observer = new ResizeObserver(schedule);
      [host, knowledge, retrieval, prompt, provider].forEach(el => observer.observe(el));
    }

    document.querySelectorAll('[data-target="architecture-map"]')
      .forEach(button => button.addEventListener('click', schedule));

    window.addEventListener('resize', schedule);
    schedule();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, { once: true });
  } else {
    init();
  }
})();

// AM6 PURPLE FLOW: PROVIDER TO USAGE AND VALIDATION
// Owner: Option A External Provider internal flow.
(function () {
  function init() {
    const host = document.querySelector(
      '#architecture-map .am6-api .am6-topology'
    );
    if (!host || host.querySelector('[data-am6-purple-flow]')) return;

    const node = id => host.querySelector(
      '[data-am6-node="' + id + '"]'
    );
    const provider = node('a-external-provider-api');
    const usage = node('a-usage-meter');
    const validation = node('a-response-validation');
    const fallback = node('a-fallback-gate');
    if (!provider || !usage || !validation || !fallback) return;

    const ns = 'http://www.w3.org/2000/svg';
    const svg = document.createElementNS(ns, 'svg');
    svg.setAttribute('data-am6-purple-flow', '');
    svg.setAttribute('aria-hidden', 'true');

    Object.assign(svg.style, {
      position: 'absolute',
      inset: '0',
      width: '100%',
      height: '100%',
      overflow: 'visible',
      pointerEvents: 'none',
      zIndex: '3'
    });

    function makePath() {
      const path = document.createElementNS(ns, 'path');
      for (const [key, value] of [
        ['fill', 'none'],
        ['stroke', '#986cdb'],
        ['stroke-width', '2.5'],
        ['stroke-dasharray', '6 5'],
        ['stroke-linecap', 'round'],
        ['stroke-linejoin', 'round']
      ]) path.setAttribute(key, value);
      svg.appendChild(path);
      return path;
    }

    const topPath = makePath();
    const bottomPath = makePath();
    const fallbackPath = makePath();
    fallbackPath.setAttribute('stroke', '#168ed0');
    // Orange companions to the existing fallback connector.
    const orangeUsage = makePath();
    const orangeValidation = makePath();
    orangeUsage.setAttribute('stroke', '#e58c17');
    orangeValidation.setAttribute('stroke', '#e58c17');


    if (getComputedStyle(host).position === 'static') {
      host.style.position = 'relative';
    }
    topPath.setAttribute('data-am6-route-title', "External Provider API → Usage Meter");
    topPath.setAttribute('data-am6-route-purpose', "Provider activity forwarded for usage measurement.");
    bottomPath.setAttribute('data-am6-route-title', "External Provider API → Response Validation");
    bottomPath.setAttribute('data-am6-route-purpose', "Provider output forwarded for validation.");
    fallbackPath.setAttribute('data-am6-route-title', "External Provider API → Fallback Gate");
    fallbackPath.setAttribute('data-am6-route-purpose', "Provider integration connected to failure handling.");
    orangeUsage.setAttribute('data-am6-route-title', "Provider Controls → Usage Meter");
    orangeUsage.setAttribute('data-am6-route-purpose', "Controlled usage-measurement branch.");
    orangeValidation.setAttribute('data-am6-route-title', "Provider Controls → Response Validation");
    orangeValidation.setAttribute('data-am6-route-purpose', "Controlled validation branch.");
    host.appendChild(svg);

    function draw() {
      const panel = document.getElementById('architecture-map');
      if (!panel || !panel.classList.contains('active')) return;

      const base = host.getBoundingClientRect();
      const p = provider.getBoundingClientRect();
      const u = usage.getBoundingClientRect();
      const v = validation.getBoundingClientRect();
      const f = fallback.getBoundingClientRect();

      if (!base.width || !p.width || !u.width || !v.width || !f.width) return;

      const centerX = p.left + p.width / 2 - base.left;
      const topY = p.top - base.top;
      const bottomY = p.bottom - base.top;

      function targetPoint(rect) {
        return {
          x: rect.left - base.left,
          y: rect.top + rect.height / 2 - base.top
        };
      }

      const up = targetPoint(u);
      const down = targetPoint(v);

      // Keep the connectors within the available horizontal gap.
      const gap = Math.min(up.x, down.x) - centerX;
      if (gap < 24) {
        topPath.setAttribute('d', '');
        bottomPath.setAttribute('d', '');
        return;
      }

      const bendX = Math.min(up.x, down.x) - 16;
      const radius = 8;
      const upperRail = Math.min(topY - 18, up.y - 18);
      const lowerRail = Math.max(bottomY + 18, down.y + 18);

      // Center-top of Provider -> left-center of Usage Meter.
      topPath.setAttribute('d',
        `M ${centerX} ${topY}` +
        ` V ${upperRail + radius}` +
        ` Q ${centerX} ${upperRail} ${centerX + radius} ${upperRail}` +
        ` H ${bendX - radius}` +
        ` Q ${bendX} ${upperRail} ${bendX} ${upperRail + radius}` +
        ` V ${up.y - radius}` +
        ` Q ${bendX} ${up.y} ${bendX + radius} ${up.y}` +
        ` H ${up.x}`
      );

      // Center-bottom of Provider -> left-center of Response Validation.
      bottomPath.setAttribute('d',
        `M ${centerX} ${bottomY}` +
        ` V ${lowerRail - radius}` +
        ` Q ${centerX} ${lowerRail} ${centerX + radius} ${lowerRail}` +
        ` H ${bendX - radius}` +
        ` Q ${bendX} ${lowerRail} ${bendX} ${lowerRail - radius}` +
        ` V ${down.y + radius}` +
        ` Q ${bendX} ${down.y} ${bendX + radius} ${down.y}` +
        ` H ${down.x}`
      );

      // Provider -> Fallback Gate: straight horizontal link.
      const fx1 = p.right - base.left;
      const fx2 = f.left - base.left;
      const fy = f.top + f.height / 2 - base.top;
      const providerTop = p.top - base.top;
      const providerBottom = p.bottom - base.top;

      if (fx2 > fx1 && fy >= providerTop && fy <= providerBottom) {
        fallbackPath.setAttribute('d', `M ${fx1} ${fy} H ${fx2}`);
      } else {
        fallbackPath.setAttribute('d', '');
      }

      // AM6 ORANGE COMPANIONS: PROVIDER TO USAGE AND VALIDATION
      // Starts are offset relative to the blue fallback line.
      // Arrivals are offset relative to the purple connections.
      function orangeRoute(target, startOffset, endOffset) {
        const sx = p.right - base.left;
        const sy = fy + startOffset;
        const tx = target.left - base.left;
        const ty = target.top + target.height / 2 - base.top
          + endOffset;

        const gap = tx - sx;
        if (gap <= 20) return '';

        const mid = sx + gap * 0.50;
        const dy = ty - sy;
        const direction = dy >= 0 ? 1 : -1;
        const radius = Math.min(
          9, gap / 8, Math.abs(dy) / 4
        );

        if (radius < 1) {
          return `M ${sx} ${sy} H ${tx}`;
        }

        return (
          `M ${sx} ${sy} ` +
          `H ${mid - radius} ` +
          `Q ${mid} ${sy} ${mid} ${sy + direction * radius} ` +
          `V ${ty - direction * radius} ` +
          `Q ${mid} ${ty} ${mid + radius} ${ty} ` +
          `H ${tx}`
        );
      }

      orangeUsage.setAttribute(
        'd', orangeRoute(u, -2, 2)
      );
      orangeValidation.setAttribute(
        'd', orangeRoute(v, 2, -2)
      );

      svg.setAttribute(
        'viewBox', `0 0 ${base.width} ${base.height}`
      );
    }

    let pending = false;
    function schedule() {
      if (pending) return;
      pending = true;
      requestAnimationFrame(() => {
        pending = false;
        draw();
      });
    }

    if (typeof ResizeObserver !== 'undefined') {
      const observer = new ResizeObserver(schedule);
      [host, provider, usage, validation, fallback].forEach(
        element => observer.observe(element)
      );
    }

    document.querySelectorAll('[data-target="architecture-map"]')
      .forEach(button => button.addEventListener('click', schedule));

    window.addEventListener('resize', schedule);
    schedule();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, {once:true});
  } else {
    init();
  }
})();

// AM6 BLUE FLOW: RESPONSE VALIDATION TO TICKET AUDIT
// Owner: Option A validation-to-output connection.
(function () {
  function init() {
    const host = document.querySelector(
      '#architecture-map .am6-api .am6-topology'
    );
    if (!host || host.querySelector('[data-am6-audit-link]')) return;

    const source = host.querySelector(
      '[data-am6-node="a-response-validation"]'
    );
    const target = host.querySelector(
      '[data-am6-node="a-ticket-audit"]'
    );
    const fallback = host.querySelector(
      '[data-am6-node="a-fallback-gate"]'
    );
    const operator = host.querySelector(
      '[data-am6-node="a-operator-review"]'
    );
    const usage = host.querySelector(
      '[data-am6-node="a-usage-meter"]'
    );
    const gateway = host.querySelector(
      '[data-am6-node="a-api-gateway"]'
    );
    if (!source || !target || !fallback ||
        !operator || !usage || !gateway) return;

    const ns = 'http://www.w3.org/2000/svg';
    const svg = document.createElementNS(ns, 'svg');
    svg.setAttribute('data-am6-audit-link', '');
    svg.setAttribute('aria-hidden', 'true');

    Object.assign(svg.style, {
      position: 'absolute',
      inset: '0',
      width: '100%',
      height: '100%',
      overflow: 'visible',
      pointerEvents: 'none',
      zIndex: '3'
    });

    const path = document.createElementNS(ns, 'path');
    [
      ['fill', 'none'],
      ['stroke', '#168ed0'],
      ['stroke-width', '2.5'],
      ['stroke-dasharray', '6 5'],
      ['stroke-linecap', 'round'],
      ['stroke-linejoin', 'round']
    ].forEach(([key, value]) => path.setAttribute(key, value));

    svg.appendChild(path);

    // Fallback Gate -> Operator Review: same SVG owner.
    const orangePath = document.createElementNS(ns, 'path');
    [
      ['fill', 'none'],
      ['stroke', '#e58c17'],
      ['stroke-width', '2.5'],
      ['stroke-dasharray', '6 5'],
      ['stroke-linecap', 'round'],
      ['stroke-linejoin', 'round']
    ].forEach(([key, value]) =>
      orangePath.setAttribute(key, value)
    );
    svg.appendChild(orangePath);

    const purplePath = document.createElementNS(ns, 'path');
    [
      ['fill', 'none'],
      ['stroke', '#986cdb'],
      ['stroke-width', '2.5'],
      ['stroke-dasharray', '6 5'],
      ['stroke-linecap', 'round'],
      ['stroke-linejoin', 'round']
    ].forEach(([key, value]) =>
      purplePath.setAttribute(key, value)
    );
    svg.appendChild(purplePath);

    // Operator Review -> Ticket + Audit.
    const reviewAuditPath = document.createElementNS(ns, 'path');
    [
      ['fill', 'none'],
      ['stroke', '#986cdb'],
      ['stroke-width', '2.5'],
      ['stroke-dasharray', '6 5'],
      ['stroke-linecap', 'round'],
      ['stroke-linejoin', 'round']
    ].forEach(([key, value]) =>
      reviewAuditPath.setAttribute(key, value)
    );
    svg.appendChild(reviewAuditPath);

    // Purple return bus: Ticket + Audit -> API Gateway,
    // with a branch to Response Validation.
    function returnPath() {
      const p = document.createElementNS(ns, 'path');
      [
        ['fill', 'none'],
        ['stroke', '#986cdb'],
        ['stroke-width', '2.5'],
        ['stroke-dasharray', '6 5'],
        ['stroke-linecap', 'round'],
        ['stroke-linejoin', 'round']
      ].forEach(([key, value]) => p.setAttribute(key, value));
      svg.appendChild(p);
      return p;
    }

    const auditReturnPath = returnPath();
    const validationReturnPath = returnPath();

    if (getComputedStyle(host).position === 'static') {
      host.style.position = 'relative';
    }
    path.setAttribute('data-am6-route-title', "Response Validation → Ticket + Audit");
    path.setAttribute('data-am6-route-purpose', "Validation output connected to audit recording.");
    orangePath.setAttribute('data-am6-route-title', "Fallback Gate → Operator Review");
    orangePath.setAttribute('data-am6-route-purpose', "Provider failures, missing evidence or blocked responses are escalated for operator assessment instead of being silently completed.");
    purplePath.setAttribute('data-am6-route-title', "Usage Meter → Operator Review");
    purplePath.setAttribute('data-am6-route-purpose', "Provider consumption and usage anomalies are available for investigating cost, latency and reliability.");
    reviewAuditPath.setAttribute('data-am6-route-title', "Operator Review → Ticket + Audit");
    reviewAuditPath.setAttribute('data-am6-route-purpose', "Human-reviewed outcome connected to audit recording.");
    auditReturnPath.setAttribute('data-am6-route-title', "Ticket + Audit → Shared Return Bus");
    auditReturnPath.setAttribute('data-am6-route-purpose', "The recorded ticket outcome enters the return rail, which links the audit stage with the gateway and validation controls.");
    validationReturnPath.setAttribute('data-am6-route-title', "Shared Return Bus → Response Validation");
    validationReturnPath.setAttribute('data-am6-route-purpose', "The return rail reaches validation for consistency checks against the recorded outcome.");
    host.appendChild(svg);

    function draw() {
      const panel = document.getElementById('architecture-map');
      if (!panel || !panel.classList.contains('active')) return;

      const base = host.getBoundingClientRect();
      const a = source.getBoundingClientRect();
      const b = target.getBoundingClientRect();
      const f = fallback.getBoundingClientRect();
      const o = operator.getBoundingClientRect();
      const u = usage.getBoundingClientRect();

      if (!base.width || !base.height || !a.width || !b.width) {
        path.setAttribute('d', '');
        return;
      }

      const x1 = a.right - base.left;
      const y1 = a.top + a.height / 2 - base.top;
      const x2 = b.left - base.left;
      const y2 = b.top + b.height / 2 - base.top;

      // Never draw backwards through either microcard.
      if (x2 <= x1) {
        path.setAttribute('d', '');
        return;
      }

      let route;

      if (Math.abs(y2 - y1) <= 2) {
        // Horizontal connector between card side centers.
        route = `M ${x1} ${y1} H ${x2}`;
      } else {
        // Orthogonal route with rounded corners.
        const mid = (x1 + x2) / 2;
        const sign = Math.sign(y2 - y1);
        const radius = Math.min(
          9,
          (x2 - x1) / 4,
          Math.abs(y2 - y1) / 4
        );

        route =
          `M ${x1} ${y1}` +
          ` H ${mid - radius}` +
          ` Q ${mid} ${y1} ${mid} ${y1 + sign * radius}` +
          ` V ${y2 - sign * radius}` +
          ` Q ${mid} ${y2} ${mid + radius} ${y2}` +
          ` H ${x2}`;
      }

      svg.setAttribute(
        'viewBox',
        `0 0 ${base.width} ${base.height}`
      );
      path.setAttribute('d', route);

      // Orange route, from right-center to left-center.
      const ox1 = f.right - base.left;
      const oy1 = f.top + f.height / 2 - base.top;
      const ox2 = o.left - base.left;
      const oy2 = o.top + o.height / 2 - base.top;
      let orangeRoute = '';

      if (f.width && o.width && ox2 > ox1) {
        if (Math.abs(oy2 - oy1) <= 2) {
          orangeRoute = `M ${ox1} ${oy1} H ${ox2}`;
        } else {
          const middle = (ox1 + ox2) / 2;
          const direction = Math.sign(oy2 - oy1);
          const radius = Math.min(
            9,
            (ox2 - ox1) / 4,
            Math.abs(oy2 - oy1) / 4
          );

          orangeRoute =
            `M ${ox1} ${oy1}` +
            ` H ${middle - radius}` +
            ` Q ${middle} ${oy1} ` +
            `${middle} ${oy1 + direction * radius}` +
            ` V ${oy2 - direction * radius}` +
            ` Q ${middle} ${oy2} ` +
            `${middle + radius} ${oy2}` +
            ` H ${ox2}`;
        }
      }
      orangePath.setAttribute('d', orangeRoute);

      // Usage Meter -> Operator Review, 4px above orange arrival.
      const ux = u.right - base.left;
      const uy = u.top + u.height / 2 - base.top;
      const tx = o.left - base.left;
      const ty = o.top + o.height / 2 - base.top - 4;
      let purpleRoute = '';

      if (u.width && o.width && tx > ux) {
        if (Math.abs(ty - uy) <= 2) {
          purpleRoute = `M ${ux} ${uy} H ${tx}`;
        } else {
          const mid = (ux + tx) / 2;
          const sign = Math.sign(ty - uy);
          const radius = Math.min(
            9, (tx - ux) / 4, Math.abs(ty - uy) / 4
          );
          purpleRoute =
            `M ${ux} ${uy}` +
            ` H ${mid - radius}` +
            ` Q ${mid} ${uy} ${mid} ${uy + sign * radius}` +
            ` V ${ty - sign * radius}` +
            ` Q ${mid} ${ty} ${mid + radius} ${ty}` +
            ` H ${tx}`;
        }
      }
      purplePath.setAttribute('d', purpleRoute);

      // Bottom-center of Operator Review -> top-center of Ticket + Audit.
      const reviewX = o.left + o.width / 2 - base.left;
      const reviewY = o.bottom - base.top;
      const auditX = b.left + b.width / 2 - base.left;
      const auditY = b.top - base.top;

      let reviewAuditRoute = '';

      if (o.width && b.width && auditY > reviewY) {
        if (Math.abs(auditX - reviewX) <= 2) {
          reviewAuditRoute =
            `M ${reviewX} ${reviewY} V ${auditY}`;
        } else {
          // Orthogonal route, with rounded corners.
          const midY = (reviewY + auditY) / 2;
          const direction = Math.sign(auditX - reviewX);
          const radius = Math.min(
            9,
            (auditY - reviewY) / 4,
            Math.abs(auditX - reviewX) / 4
          );

          reviewAuditRoute =
            `M ${reviewX} ${reviewY}` +
            ` V ${midY - radius}` +
            ` Q ${reviewX} ${midY} ` +
            `${reviewX + direction * radius} ${midY}` +
            ` H ${auditX - direction * radius}` +
            ` Q ${auditX} ${midY} ` +
            `${auditX} ${midY + radius}` +
            ` V ${auditY}`;
        }
      }

      reviewAuditPath.setAttribute('d', reviewAuditRoute);

      // Shared lower return rail; geometry follows live cards.
      const gatewayBox = gateway.getBoundingClientRect();

      const ticketX = b.left + b.width / 2 - base.left;
      const ticketY = b.bottom - base.top;

      const gatewayX =
        gatewayBox.left + gatewayBox.width / 2 - base.left;
      const gatewayY = gatewayBox.bottom - base.top;

      const validationX =
        a.left + a.width / 2 - base.left;
      const validationY = a.bottom - base.top;

      const railY = Math.max(
        ticketY, gatewayY, validationY
      ) + 24;

      let returnRoute = '';
      let validationRoute = '';

      // One common return rail, from Ticket + Audit to API Gateway.
      if (gatewayBox.width && ticketX > gatewayX &&
          railY > ticketY && railY > gatewayY) {
        const radius = Math.min(
          10,
          (ticketX - gatewayX) / 6,
          (railY - ticketY) / 3,
          (railY - gatewayY) / 3
        );

        returnRoute =
          `M ${ticketX} ${ticketY}` +
          ` V ${railY - radius}` +
          ` Q ${ticketX} ${railY} ` +
          `${ticketX - radius} ${railY}` +
          ` H ${gatewayX + radius}` +
          ` Q ${gatewayX} ${railY} ` +
          `${gatewayX} ${railY - radius}` +
          ` V ${gatewayY}`;

        // Branch from the return rail into the bottom center
        // of Response Validation.
        if (validationX > gatewayX &&
            validationX < ticketX &&
            railY > validationY) {
          validationRoute =
            `M ${validationX} ${railY}` +
            ` V ${validationY}`;
        }
      }

      auditReturnPath.setAttribute('d', returnRoute);
      validationReturnPath.setAttribute('d', validationRoute);
    }

    let pending = false;

    function schedule() {
      if (pending) return;
      pending = true;
      requestAnimationFrame(() => {
        pending = false;
        draw();
      });
    }

    if (typeof ResizeObserver !== 'undefined') {
      const observer = new ResizeObserver(schedule);
      [host, source, target, fallback, operator, usage, gateway].forEach(
        node => observer.observe(node)
      );
    }

    document.querySelectorAll('[data-target="architecture-map"]')
      .forEach(button => button.addEventListener('click', schedule));

    window.addEventListener('resize', schedule);
    schedule();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, {
      once: true
    });
  } else {
    init();
  }
})();

// AM6 ARCHITECTURE DETAILS — SINGLE MODAL OWNER
(function () {
  'use strict';

  var nodeDetails = {
    'a-application-server': 'Receives support tickets and coordinates application operations. Integrates the support workflow with internal services and the commercial API gateway.',
    'a-secrets-manager': 'Stores and manages API credentials and keys. Prevents secrets from being exposed in application code and supports key rotation and revocation.',
    'a-egress-policy': 'Controls which information may leave the internal environment, including personal data handling and outbound policies for the external provider.',
    'a-api-gateway': 'Centralizes commercial API requests, enforcing authentication, policies, rate limits and routing. The gateway does not replace response validation.',
    'a-knowledge-store': 'Maintains procedures and policies used to support ticket resolution. Provides the document sources for context retrieval.',
    'a-index-retrieval': 'Retrieves relevant knowledge through vector search. Retrieval quality depends on indexing, source documents and query design.',
    'a-prompt-builder': 'Combines instructions, retrieved context and ticket information to prepare requests for the commercial LLM.',
    'a-external-provider-api': 'Runs model inference through an external commercial provider. Costs depend on the model, request volume and input/output token consumption.',
    'a-usage-meter': 'Tracks token consumption, estimated costs and latency. These measurements are necessary to compare projected ROI with actual operating expenses.',
    'a-fallback-gate': 'Defines how the system responds to provider failures, rate limits and service outages while preserving support continuity.',
    'a-response-validation': 'Evaluates generated responses before delivery, considering supporting evidence, quality, safety and support policies.',
    'a-operator-review': 'Allows support operators to approve, correct or reject AI suggestions. Review frequency and duration must be measured to validate ROI.',
    'a-ticket-audit': 'Records support outcomes and audit trails, providing traceability for suggestions, human reviews and decisions.',
    'b-application-server': 'Coordinates support tickets and the operational user interface within the private environment.',
    'b-knowledge-store': 'Stores procedures and policies locally for contextual knowledge retrieval.',
    'b-index-pipeline': 'Processes source documents and builds or updates search indexes, including embedding generation.',
    'b-local-retrieval': 'Retrieves relevant information from the local index without relying on a commercial API for the retrieval operation.',
    'b-model-artifact-registry': 'Manages model artifacts and open-weight model versions within the private environment, supporting traceability and controlled updates.',
    'b-cpu-first-inference-node': 'Runs an open-weight model with a CPU-first approach. Feasibility depends on benchmarks for latency, memory, concurrency and output quality.',
    'b-capacity-queue-control': 'Manages processing queues and capacity to prevent overload and maintain predictable inference throughput.',
    'b-response-validation': 'Applies safety and quality checks to responses generated within the private environment.',
    'b-operator-review': 'Maintains human approval and correction when required. Review frequency directly influences operating costs.',
    'b-ticket-audit': 'Preserves results and operation lineage for investigation, governance and traceability.',
    'b-telemetry-maintenance': 'Consolidates operational metrics, logs and model health information to support monitoring, diagnostics and private infrastructure maintenance.'
  };

  var flows = [
    ['blue', 'Blue', 'Primary data, request and result flows.'],
    ['orange', 'Orange', 'Preparation, policies, configuration and controlled routing.'],
    ['purple', 'Purple', 'Return paths, validation, auditing and feedback.']
  ];

  function text(element, selector) {
    var found = element.querySelector(selector);
    return found ? found.textContent.trim().replace(/\s+/g, ' ') : '';
  }

  function make(tag, className, value) {
    var el = document.createElement(tag);
    if (className) el.className = className;
    if (value) el.textContent = value;
    return el;
  }

  function init() {
    var map = document.getElementById('architecture-map');
    if (!map || map.getAttribute('data-am6-detail-ready') === '1') return;

    var legend = map.querySelector('.am6-legend');
    var core = map.querySelector('.am6-core-svg');
    var optionA = map.querySelector('.am6-option.am6-api');
    var optionB = map.querySelector('.am6-option.am6-private');
    var roiA = map.querySelector('[data-am6-roi-view="a"]');
    var roiB = map.querySelector('[data-am6-roi-view="b"]');
    if (!legend || !core || !optionA || !optionB || !roiA || !roiB) return;

    var key = make('div', 'am6-flow-key');
    key.setAttribute('aria-label', 'Flow line color legend');

    flows.forEach(function (item) {
      var group = make('span', 'am6-flow-key-item');
      var line = make('span', 'am6-flow-key-line am6-flow-key-' + item[0]);
      line.setAttribute('aria-hidden', 'true');
      group.appendChild(line);
      group.appendChild(make('span', '', item[1] + ' — ' + item[2]));
      key.appendChild(group);
    });
    legend.appendChild(key);

    // AM6 HORIZONTAL NAVIGATION — SINGLE OWNER
    function initHorizontalNav() {
      if (document.getElementById('am6-horizontal-nav-left')) return;

      var style = document.createElement('style');
      style.id = 'am6-horizontal-nav-style';

      style.textContent = [
        '.am6-horizontal-nav{position:fixed;top:50%;transform:translateY(-50%);z-index:40;width:34px;height:320px;border:0;border-radius:0;background:transparent;color:#245478;box-shadow:none;display:flex;align-items:center;justify-content:center;font:400 0/1 Arial,sans-serif;cursor:pointer;padding:0;appearance:none;-webkit-appearance:none;}',
        '.am6-horizontal-nav::before{content:"‹";display:inline-block;font:800 52px/1 Arial,sans-serif;transform:scaleY(2.6);transform-origin:center;pointer-events:none;}',
        '.am6-horizontal-nav-right::before{content:"›";animation:am6-nav-direction-pulse .9s ease-in-out 3;}',
        '@keyframes am6-nav-direction-pulse{0%,100%{opacity:1;transform:scaleY(2.6) translateX(0);}50%{opacity:.28;transform:scaleY(2.6) translateX(3px);}}',
        '@media(prefers-reduced-motion:reduce){.am6-horizontal-nav-right::before{animation:none;}}',
        '.am6-horizontal-nav:hover{background:transparent;color:#116dab;}',
        '.am6-horizontal-nav:focus-visible{outline:3px solid #1477c7;outline-offset:2px;}',
        '.am6-horizontal-nav[hidden]{display:none!important;}',
        '.am6-horizontal-nav-right{right:7px;}',
        '@media(max-width:700px){.am6-horizontal-nav{width:29px;height:120px;font-size:0;}.am6-horizontal-nav::before{font-size:42px;font-weight:800;transform:scaleY(2);}}'
      ].join('');

      document.head.appendChild(style);

      var left = make(
        'button',
        'am6-horizontal-nav am6-horizontal-nav-left',
        '‹'
      );

      var right = make(
        'button',
        'am6-horizontal-nav am6-horizontal-nav-right',
        '›'
      );

      left.id = 'am6-horizontal-nav-left';
      right.id = 'am6-horizontal-nav-right';

      left.type = 'button';
      right.type = 'button';

      left.setAttribute(
        'aria-label',
        'Scroll Architecture Map left'
      );

      right.setAttribute(
        'aria-label',
        'Scroll Architecture Map right'
      );

      left.title = 'Move map left';
      right.title = 'Move map right';

      document.body.appendChild(left);
      document.body.appendChild(right);

      function visible() {
        if (!map.getClientRects().length) return false;

        var rect = map.getBoundingClientRect();

        return rect.top < 0 &&
          rect.bottom > 0 &&
          rect.right > 0 &&
          rect.left < window.innerWidth;
      }

      function position() {
        var sidebar = document.querySelector('aside');
        var sidebarRight = sidebar ?
          sidebar.getBoundingClientRect().right : 0;

        var contentLeft = Math.max(
          sidebarRight,
          map.getBoundingClientRect().left - 40
        );

        left.style.left =
          Math.round(Math.max(7, contentLeft + 7)) + 'px';
      }

      function sync() {
        position();

        var show = visible();

        left.hidden = !show;
        right.hidden = !show;
      }

      function move(direction) {
        if (!visible()) return;

        // Navigate the existing Architecture Map scroller,
        // never the page/window horizontal scroll.
        var candidates = Array.prototype.filter.call(
          map.querySelectorAll('div'),
          function (node) {
            if (!node.className ||
                typeof node.className !== 'string' ||
                node.className.indexOf('am6-sc') === -1) {
              return false;
            }

            var css = window.getComputedStyle(node);
            return /(auto|scroll)/.test(css.overflowX) &&
              node.scrollWidth - node.clientWidth > 100;
          }
        );

        // Fail closed: do not move an ambiguous scroll target.
        if (candidates.length !== 1) {
          console.warn(
            'AM6_HORIZONTAL_NAV_TARGET_MISMATCH',
            candidates.length
          );
          return;
        }

        var scroller = candidates[0];
        var amount = Math.max(
          300,
          Math.round(scroller.clientWidth * 0.65)
        );

        scroller.scrollBy({
          left: direction * amount,
          behavior: 'smooth'
        });
      }

      left.addEventListener('click', function (event) {
        event.preventDefault();
        event.stopPropagation();
        move(-1);
      });

      right.addEventListener('click', function (event) {
        event.preventDefault();
        event.stopPropagation();
        move(1);
      });

      window.addEventListener('scroll', sync, {
        passive: true
      });

      window.addEventListener('resize', sync, {
        passive: true
      });

      document.addEventListener('click', function () {
        window.setTimeout(sync, 80);
      });

      sync();
    }

    initHorizontalNav();

    var overlay = make('div', 'am6-detail-overlay');
    overlay.hidden = true;
    var dialog = make('div', 'am6-detail-dialog');
    dialog.setAttribute('role', 'dialog');
    dialog.setAttribute('aria-modal', 'true');
    dialog.setAttribute('aria-labelledby', 'am6-detail-title');
    dialog.setAttribute('aria-describedby', 'am6-detail-body');

    var close = make('button', 'am6-detail-close', '×');
    close.type = 'button';
    close.setAttribute('aria-label', 'Close details');
    var title = make('h2', '', '');
    title.id = 'am6-detail-title';
    var category = make('p', 'am6-detail-category');
    var body = make('div', 'am6-detail-body');
    body.id = 'am6-detail-body';
    var note = make('p', 'am6-detail-note');

    dialog.appendChild(close);
    dialog.appendChild(title);
    dialog.appendChild(category);
    dialog.appendChild(body);
    dialog.appendChild(note);
    overlay.appendChild(dialog);
    document.body.appendChild(overlay);

    var previousFocus = null;

    function hide() {
      if (overlay.hidden) return;
      overlay.hidden = true;
      document.body.classList.remove('am6-detail-open');
      if (previousFocus && previousFocus.focus) previousFocus.focus();
    }

    function show(name, kind, description, footnote, source) {
      previousFocus = source || document.activeElement;
      title.textContent = name;
      category.textContent = kind;
      body.textContent = description;
      note.textContent = footnote ||
        'Architecture planning documentation. Validate against implementation evidence.';
      overlay.hidden = false;
      document.body.classList.add('am6-detail-open');
      close.focus();
    }

    close.addEventListener('click', hide);
    overlay.addEventListener('click', function (event) {
      if (event.target === overlay) hide();
    });

    document.addEventListener('keydown', function (event) {
      if (overlay.hidden) return;
      if (event.key === 'Escape') {
        event.preventDefault();
        hide();
      }
      if (event.key === 'Tab') {
        // The modal contains one focusable control: its close button.
        event.preventDefault();
        close.focus();
      }
    });

    var macroDetails = {
      a: 'Commercial API LLM. The application prepares context, enforces outbound data controls, calls the external provider and validates the response before human review and audit.\n\nProjected recurring costs at 3 API calls per ticket: US$108.00/month for tokens, US$416.67/month for human review and US$160.00/month for infrastructure and maintenance. Total: approximately US$684.67/month. Token-cost sensitivity across 1 to 5 calls per ticket: US$36.00 to US$180.00/month.\n\nThe projection uses 2,500 tickets/month derived from the annual briefing volume, not an observed monthly workload. One-time implementation costs are excluded.',
      b: 'Private Open-weight · CPU-first. The application uses local knowledge retrieval and inference within a private environment, with capacity controls, human review and telemetry.\n\nProjected recurring costs: US$200.00/month for CPU inference capacity, US$416.67/month for human review and US$160.00/month for auxiliary infrastructure and maintenance. Total: approximately US$776.67/month.\n\nInference capacity requires hardware and model-specific benchmarking. One-time implementation costs are excluded.'
    };


    // Existing dynamic SVG paths are the only flow-modal targets.
    // No new visible paths or separate modal controllers.
    var flowGroups = {
  "data-am6-orange-flow": {
    "option": "A",
    "items": [
      [
        "Secrets Manager → API Gateway",
        "Credential and secret-management control path."
      ],
      [
        "Egress Policy → API Gateway",
        "Outbound data-control path."
      ],
      [
        "Security Control Junction → API Gateway",
        "Shared junction combining the two control branches."
      ]
    ]
  },
  "data-am6-blue-rag": {
    "option": "A",
    "items": [
      [
        "API Gateway → Index / Retrieval",
        "Request path toward knowledge retrieval."
      ],
      [
        "API Gateway → Knowledge Store",
        "Connection to the source knowledge environment."
      ],
      [
        "Knowledge Store → Index / Retrieval",
        "Knowledge indexing and retrieval relationship."
      ],
      [
        "Index / Retrieval → Prompt Builder",
        "Retrieved context used for prompt construction."
      ],
      [
        "Context Preparation → Prompt Builder",
        "Context preparation branch toward the prompt builder."
      ]
    ]
  },
  "data-am6-provider-flow": {
    "option": "A",
    "items": [
      [
        "Knowledge Store → Context Junction",
        "Knowledge-context input into the shared collector."
      ],
      [
        "Index / Retrieval → Context Junction",
        "Retrieved-context input into the shared collector."
      ],
      [
        "Prompt Builder → Context Junction",
        "Prepared-prompt input into the shared collector."
      ],
      [
        "Context Junction",
        "Shared collector connecting the three context branches."
      ],
      [
        "Context Junction → External Provider API",
        "Combined inference request sent to the external provider."
      ]
    ]
  },
  "data-am6-purple-flow": {
    "option": "A",
    "items": [
      [
        "External Provider API → Usage Meter",
        "Provider activity forwarded to usage measurement."
      ],
      [
        "External Provider API → Response Validation",
        "Provider output forwarded for validation."
      ],
      [
        "External Provider API → Fallback Gate",
        "Provider integration connected to failure and availability handling."
      ],
      [
        "External Provider API → Usage Meter",
        "Additional controlled metering route."
      ],
      [
        "External Provider API → Response Validation",
        "Additional controlled validation route."
      ]
    ]
  },
  "data-am6-audit-link": {
    "option": "A",
    "items": [
      [
        "Response Validation → Ticket + Audit",
        "Validated result forwarded toward audit recording."
      ],
      [
        "Operational Control Route",
        "Additional control branch in the output workflow."
      ],
      [
        "Review Route",
        "Human-review branch of the output workflow."
      ],
      [
        "Operator Review → Ticket + Audit",
        "Reviewed result forwarded for traceable recording."
      ],
      [
        "Ticket + Audit → API Gateway",
        "Return bus from the audit stage toward the gateway."
      ],
      [
        "Return Bus → Response Validation",
        "Branch connecting the return path to validation."
      ]
    ]
  },
  "data-am6-b-application-flow": {
    "option": "B",
    "items": [
      [
        "Application Server → Knowledge / Index",
        "Application requests distributed to private knowledge processing."
      ],
      [
        "Local Preparation Flow",
        "Private knowledge processing and preparation branch."
      ],
      [
        "Operational Telemetry Return",
        "Return branch toward private operational monitoring."
      ],
      [
        "Knowledge / Retrieval → CPU-first Inference Node",
        "Locally retrieved context forwarded for inference."
      ],
      [
        "Local Retrieval → Model Artifact Registry",
        "Connection to locally managed model artifacts."
      ],
      [
        "Model Execution Chain",
        "Model artifact, inference and capacity-control relationship."
      ],
      [
        "Capacity / Queue Control → Ticket + Audit",
        "Capacity-control information routed toward auditing."
      ],
      [
        "CPU-first Inference Node → Validation / Review",
        "Locally generated output routed into output controls."
      ],
      [
        "Validation / Review → Ticket + Audit",
        "Validated or reviewed results forwarded for recording."
      ],
      [
        "Validation / Review → Telemetry",
        "Operational information returned to monitoring."
      ],
      [
        "Model Artifact Registry → Operator Review",
        "Model-version information available for operator review."
      ]
    ]
  }
};

    var flowSelector = Object.keys(flowGroups).map(function (key) {
      return 'svg[' + key + ']';
    }).join(', ');

    var flowDescriptions = {
      '#168ed0': 'Blue flow: primary movement of data, context, requests or results.',
      '#e58c17': 'Orange flow: preparation, policies or controlled routing.',
      '#986cdb': 'Purple flow: return paths, validation, auditing or feedback.'
    };


    function flowPaths(svg) {
      return Array.prototype.slice.call(
        svg.querySelectorAll('path:not([data-am6-flow-hit])')
      );
    }

    function findFlowDetail(element) {
      if (!element || !element.closest) return null;

      var selected = element.closest('path');
      if (!selected) return null;

      var svg = selected.closest(flowSelector);
      if (!svg || !map.contains(svg)) return null;

      var groupKey = Object.keys(flowGroups).find(function (key) {
        return svg.hasAttribute(key);
      });
      if (!groupKey) return null;

      var paths = flowPaths(svg);
      var path = selected;

      if (selected.hasAttribute('data-am6-flow-hit')) {
        var hitIndex = Number(
          selected.getAttribute('data-am6-flow-hit')
        );
        if (!Number.isInteger(hitIndex)) return null;
        path = paths[hitIndex];
      }

      if (!path || !(path.getAttribute('d') || '').trim()) {
        return null;
      }

      var index = paths.indexOf(path);
      var group = flowGroups[groupKey];
      if (index < 0 || index >= group.items.length) return null;

      var item = [
        path.getAttribute('data-am6-route-title'),
        path.getAttribute('data-am6-route-purpose')
      ];
      var partKey = selected.getAttribute('data-am6-flow-part');
      var rawParts = path.getAttribute('data-am6-route-parts');

      if (partKey !== null) {
        if (!rawParts) return null;

        var details = JSON.parse(rawParts);
        var partIndex = Number(partKey);

        if (!Number.isInteger(partIndex) ||
            partIndex < 0 || !details[partIndex]) {
          return null;
        }

        item = details[partIndex];
      }

      if (!item[0] || !item[1]) return null;
      var stroke = (path.getAttribute('stroke') || '')
        .trim().toLowerCase();

      var colorMeaning = flowDescriptions[stroke] ||
        'Specialized architecture connection.';

      return {
        title: item[0],
        category: 'Option ' + group.option + ' · Architecture flow',
        description:
          colorMeaning +
          '\n\nConnection: ' + item[0] +
          '\n\nFunction: ' + item[1],
        footnote:
          'Proposed logical architecture. This connection does not ' +
          'represent measured live traffic.',
        source: svg
      };
    }

    function activateFlowPaths() {
      Array.prototype.forEach.call(
        map.querySelectorAll(flowSelector),
        function (svg) {
          var key = Object.keys(flowGroups).find(function (name) {
            return svg.hasAttribute(name);
          });
          if (!key) return;

          var originals = flowPaths(svg);
          var expected = flowGroups[key].items.length;

          // Prevent mislabeling when a drawing owner changes
          // the number or order of connections.
          if (originals.length !== expected) {
            svg.setAttribute('data-am6-flow-count-mismatch', '1');
            Array.prototype.forEach.call(
              svg.querySelectorAll('[data-am6-flow-hit]'),
              function (node) { node.remove(); }
            );
            return;
          }

          svg.removeAttribute('data-am6-flow-count-mismatch');

          originals.forEach(function (path, index) {
            var geometry = path.getAttribute('d') || '';
            var stroke = (path.getAttribute('stroke') || '')
              .trim().toLowerCase();

            var supported =
              Object.prototype.hasOwnProperty.call(
                flowDescriptions, stroke
              ) || stroke === '#dc5079';

            var rawParts = path.getAttribute('data-am6-route-parts');
            var parts = rawParts ? JSON.parse(rawParts) : null;

            var segments = parts
              ? (geometry.match(/[Mm][^Mm]*/g) || [])
              : [geometry];

            var existing = Array.prototype.slice.call(
              svg.querySelectorAll(
                'path[data-am6-flow-hit="' + index + '"]'
              )
            );

            if (parts && parts.length !== segments.length) {
              svg.setAttribute(
                'data-am6-flow-parts-mismatch', '1'
              );
              existing.forEach(function (node) {
                node.remove();
              });
              path.style.pointerEvents = 'none';
              return;
            }

            svg.removeAttribute('data-am6-flow-parts-mismatch');

            // Rebuild only when subpath identity or count changes.
            // This preserves the SVG visual path and its controller.
            existing.forEach(function (node) {
              node.remove();
            });

            segments.forEach(function (segment, partIndex) {
              var hit = document.createElementNS(
                'http://www.w3.org/2000/svg', 'path'
              );

              hit.setAttribute(
                'data-am6-flow-hit', String(index)
              );

              if (parts) {
                hit.setAttribute(
                  'data-am6-flow-part', String(partIndex)
                );
              }

              hit.setAttribute('d', segment);
              hit.setAttribute('fill', 'none');
              hit.setAttribute('stroke', 'transparent');
              hit.setAttribute('stroke-width', '16');
              hit.setAttribute('stroke-dasharray', 'none');
              hit.setAttribute('stroke-linecap', 'round');
              hit.setAttribute('stroke-linejoin', 'round');

              hit.style.pointerEvents = 'stroke';
              hit.style.cursor = 'pointer';

              path.parentNode.insertBefore(
                hit, path.nextSibling
              );
            });

            // The transparent hit stroke receives the click.
            path.style.pointerEvents = 'none';
          });
        }
      );
    }

    activateFlowPaths();

    var flowObserver = new MutationObserver(function (records) {
      var changed = records.some(function (record) {
        if (record.type === 'attributes') {
          return record.attributeName === 'd' &&
            record.target.tagName &&
            record.target.tagName.toLowerCase() === 'path' &&
            !record.target.hasAttribute('data-am6-flow-hit');
        }

        if (record.type === 'childList') {
          return Array.prototype.some.call(
            record.addedNodes,
            function (node) {
              return node.nodeType === 1 &&
                !(node.hasAttribute &&
                  node.hasAttribute('data-am6-flow-hit'));
            }
          ) || Array.prototype.some.call(
            record.removedNodes,
            function (node) {
              return node.nodeType === 1 &&
                !(node.hasAttribute &&
                  node.hasAttribute('data-am6-flow-hit'));
            }
          );
        }

        return false;
      });

      if (changed) activateFlowPaths();
    });

    flowObserver.observe(map, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['d']
    });

    function detailsFor(element) {
      var flow = findFlowDetail(element);
      if (flow) return flow;

      var staticFlow = element.closest('[data-am6-static-flow]');
      if (staticFlow && map.contains(staticFlow) &&
          staticFlow.getAttribute('data-am6-static-flow') ===
            'a-application-secrets') {
        return {
          title: 'Application Server → Secrets Manager',
          category: 'Option A · Credential Management',
          description: 'The application requests authorized credentials through the Secrets Manager rather than embedding API keys in application code. The secrets-management boundary supports credential retrieval, rotation and revocation. The application should use only the permissions required for the operation.',
          footnote: 'Proposed architecture flow; this diagram does not establish that a credential-management integration is deployed.',
          source: staticFlow
        };
      }

      var node = element.closest('[data-am6-node]');
      if (node && map.contains(node)) {
        var id = node.getAttribute('data-am6-node');
        var name = text(node, 'strong') || id;
        return {
          title: name,
          category: id.charAt(0) === 'a' ? 'Option A · Architecture component'
            : 'Option B · Architecture component',
          description: nodeDetails[id] || text(node, 'small') ||
            'Component description pending technical validation.',
          footnote: 'Architecture role and proposed responsibilities; not proof of production deployment.',
          source: node
        };
      }

      var financial = element.closest('[data-am6-roi-financial]');
      if (financial && map.contains(financial)) {
        var option = financial.getAttribute('data-am6-roi-financial');
        var status = text(financial, 'small');
        return {
          title: text(financial, 'strong'),
          category: 'Option ' + option.toUpperCase() + ' · ROI Methodology',
          description: 'Displayed value: ' + status + '\n\n' +
            (financial.getAttribute('title') || 'Calculation details unavailable.'),
          footnote: 'Estimates are planning scenarios, not verified savings. The analyzed sample and annual projection have different denominators.',
          source: financial
        };
      }

      var header = element.closest('.am6-option > header');
      if (header && map.contains(header)) {
        var which = header.closest('.am6-api') ? 'a' : 'b';
        return {
          title: which === 'a' ? 'Option A · External API LLM'
            : 'Option B · Private Open-weight · CPU-first',
          category: 'Architecture overview',
          description: macroDetails[which],
          footnote: 'Figures are estimates based on the 30,000-ticket annual briefing baseline and require operational validation.',
          source: header
        };
      }

      var svgText = element.closest('text');
      if (svgText && core.contains(svgText)) {
        if (
          svgText.classList.contains('am6-center-title') ||
          svgText.classList.contains('am6-center-desc')
        ) {
          return {
            title: 'AI Automation Core',
            category: 'Shared operational architecture',
            description:
              'Shared automation and orchestration core. ' +
              'Coordinates decisions, context, knowledge and the ' +
              'operational workflow represented by the circular sectors.',
            footnote:
              'Planned architectural responsibility. This does not imply ' +
              'that all components have been deployed.',
            source: core
          };
        }

        // Descriptive text belongs to the corresponding title.
        if (
          svgText.classList.contains('am6-sector-desc') ||
          svgText.classList.contains('am6-satellite-desc')
        ) {
          var titleClass = svgText.classList.contains('am6-sector-desc')
            ? '.am6-sector-title'
            : '.am6-satellite-title';

          var descriptionBox = svgText.getBoundingClientRect();
          var dx = descriptionBox.left + descriptionBox.width / 2;
          var dy = descriptionBox.top + descriptionBox.height / 2;
          var nearestTitle = null;
          var nearestDistance = Infinity;

          Array.prototype.forEach.call(
            core.querySelectorAll(titleClass),
            function (candidate) {
              var box = candidate.getBoundingClientRect();
              var x = box.left + box.width / 2;
              var y = box.top + box.height / 2;
              var distance = Math.hypot(x - dx, y - dy);

              if (distance < nearestDistance) {
                nearestDistance = distance;
                nearestTitle = candidate;
              }
            }
          );

          if (!nearestTitle) return null;
          svgText = nearestTitle;
        }

        var label = svgText.textContent.trim().replace(/\s+/g, ' ');
        if (!label) return null;
        return {
          title: label,
          category: 'Shared operational architecture · Circular view',
          description: 'Element represented in the shared operational architecture: ' +
            label + '.\n\nThe circular diagram presents the shared operational responsibilities across the proposed architectures. This element must be interpreted together with its connections and neighboring components.',
          footnote: 'The modal identifies the label displayed in the SVG. Detailed implementation evidence is not established by the diagram alone.',
          source: core
        };
      }
      return null;
    }

    // Circular card/icon hit detection without changing SVG geometry.
    function circularDetailAt(event) {
      if (!core.contains(event.target)) return null;

      var labels = core.querySelectorAll(
        '.am6-satellite-title, .am6-sector-title, .am6-center-title'
      );
      var nearest = null;
      var distance = Infinity;

      Array.prototype.forEach.call(labels, function (label) {
        var name = (label.textContent || '').trim();
        if (!name) return;

        var box = label.getBoundingClientRect();
        if (!box.width || !box.height) return;

        var dx = Math.max(
          box.left - event.clientX, 0,
          event.clientX - box.right
        );
        var dy = Math.max(
          box.top - event.clientY, 0,
          event.clientY - box.bottom
        );
        var current = Math.sqrt(dx * dx + dy * dy);

        if (current < distance) {
          distance = current;
          nearest = label;
        }
      });

      // Avoid opening a random modal when clicking empty orbit space.
      if (!nearest || distance > 90) return null;

      var detail = detailsFor(nearest);
      if (!detail) return null;
      detail.source = core;
      return detail;
    }

    map.addEventListener('click', function (event) {
      if (event.target.closest('button')) return;
      var detail = detailsFor(event.target);
      if (!detail) detail = circularDetailAt(event);
      if (detail) show(detail.title, detail.category,
        detail.description, detail.footnote, detail.source);
    });

    var selectable = map.querySelectorAll(
      '[data-am6-node], [data-am6-static-flow], .am6-option > header, .am6-roi-grid > div[data-am6-roi-financial], .am6-core-svg text'
    );

    Array.prototype.forEach.call(selectable, function (element) {
      if (!element.hasAttribute('tabindex')) element.setAttribute('tabindex', '0');
      element.setAttribute('role', 'button');
      element.addEventListener('keydown', function (event) {
        if (event.key !== 'Enter' && event.key !== ' ') return;
        event.preventDefault();
        var detail = detailsFor(element);
        if (detail) show(detail.title, detail.category,
          detail.description, detail.footnote, element);
      });
    });

    map.setAttribute('data-am6-detail-ready', '1');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();


// AM6 OPTION A ROI BI OWNER
(function () {
  'use strict';

  function initialize(option) {
    var map = document.getElementById('architecture-map');
    if (!map || map.dataset['am6RoiBiReady' + option] === '1') return;

    var button = map.querySelector(
      '.am6-' + (option === 'a' ? 'api' : 'private') + ' [data-am6-roi-bi-open]'
    );
    var source = map.querySelector('#am6-roi-option-' + option);

    if (!button || !source) return;

    var cards = source.querySelectorAll(
      '.am6-roi-grid > div[data-am6-roi-financial="' + option + '"]'
    );

    if (cards.length !== 6) return;

    var ns = 'http://www.w3.org/2000/svg';
    var overlay = document.createElement('div');
    overlay.className = 'am6-roi-bi-overlay';
    overlay.hidden = true;

    var dialog = document.createElement('div');
    dialog.className = 'am6-roi-bi-dialog';
    dialog.setAttribute('role', 'dialog');
    dialog.setAttribute('aria-modal', 'true');
    dialog.setAttribute('aria-labelledby', 'am6-roi-bi-title-' + option);

    var header = document.createElement('div');
    header.className = 'am6-roi-bi-head';

    var heading = document.createElement('div');

    var kicker = document.createElement('div');
    kicker.className = 'am6-roi-bi-kicker';
    kicker.textContent = option === 'a'
      ? 'OPTION A · EXTERNAL API LLM'
      : 'OPTION B · PRIVATE OPEN-WEIGHT · CPU-FIRST';

    var title = document.createElement('h2');
    title.id = 'am6-roi-bi-title-' + option;
    title.textContent = 'ROI Analysis · Business Intelligence';

    var subtitle = document.createElement('p');
    subtitle.textContent =
      'Financial indicators, cost composition and scenario sensitivity.';

    heading.append(kicker, title, subtitle);

    var close = document.createElement('button');
    close.type = 'button';
    close.className = 'am6-roi-bi-close';
    close.setAttribute('aria-label', 'Close ROI analysis');
    close.textContent = '×';

    header.append(heading, close);

    var content = document.createElement('div');
    content.className = 'am6-roi-bi-content';

    dialog.append(header, content);
    overlay.appendChild(dialog);
    document.body.appendChild(overlay);

    function element(tag, cls, value) {
      var node = document.createElement(tag);
      if (cls) node.className = cls;
      if (value !== undefined) node.textContent = value;
      return node;
    }

    function svg(tag, attrs, parent) {
      var node = document.createElementNS(ns, tag);

      Object.keys(attrs).forEach(function (key) {
        node.setAttribute(key, String(attrs[key]));
      });

      if (parent) parent.appendChild(node);
      return node;
    }

    function money(value) {
      return 'US$ ' + value.toLocaleString((window.AIMASTER_I18N_LANG === 'pt-BR' ? 'pt-BR' : 'en-US'), {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      });
    }

    function parseUSD(value) {
      var match = String(value).match(
        /US\$\s*([\d,]+(?:\.\d{1,2})?)/i
      );

      if (!match) return null;

      var number = Number(match[1].replace(/,/g, ''));
      return Number.isFinite(number) ? number : null;
    }

    function readCards() {
      return Array.prototype.map.call(cards, function (card) {
        var strong = card.querySelector('strong');
        var small = card.querySelector('small');

        return {
          name: strong ? strong.textContent.trim() : '',
          value: small ? small.textContent.trim() : '',
          methodology: card.getAttribute('title') || ''
        };
      });
    }

    function metric(items, pattern) {
      return items.find(function (item) {
        return pattern.test(item.name);
      });
    }

    function panel(titleText, subtitleText) {
      var node = element('section', 'am6-roi-bi-panel');

      node.append(
        element('h3', '', titleText),
        element('p', '', subtitleText)
      );

      return node;
    }

    function renderPie(host, series) {
      var total = series.reduce(function (sum, item) {
        return sum + item.value;
      }, 0);

      if (total <= 0) return;

      var colors = ['#168ed0', '#e58c17', '#986cdb'];
      var wrap = element('div', 'am6-roi-bi-pie');

      var graph = svg('svg', {
        viewBox: '0 0 240 240',
        role: 'img',
        'aria-label': 'Estimated monthly cost composition'
      });

      var angle = -Math.PI / 2;

      series.forEach(function (item, index) {
        if (item.value <= 0) return;

        var delta = item.value / total * Math.PI * 2;
        var start = angle;
        var end = angle + delta;
        var radius = 85;

        var x1 = 120 + radius * Math.cos(start);
        var y1 = 120 + radius * Math.sin(start);
        var x2 = 120 + radius * Math.cos(end);
        var y2 = 120 + radius * Math.sin(end);

        svg('path', {
          d: 'M 120 120 L ' + x1 + ' ' + y1 +
             ' A 85 85 0 ' + (delta > Math.PI ? 1 : 0) +
             ' 1 ' + x2 + ' ' + y2 + ' Z',
          fill: colors[index]
        }, graph);

        angle = end;
      });

      svg('circle', {
        cx: 120, cy: 120, r: 49, fill: '#fff'
      }, graph);

      var label = svg('text', {
        x: 120, y: 116,
        'text-anchor': 'middle',
        'font-size': 11,
        fill: '#648097'
      }, graph);
      label.textContent = 'TOTAL / MONTH';

      var value = svg('text', {
        x: 120, y: 138,
        'text-anchor': 'middle',
        'font-size': 17,
        'font-weight': 800,
        fill: '#18496c'
      }, graph);
      value.textContent = money(total);

      var legend = element('div', 'am6-roi-bi-legend');

      series.forEach(function (item, index) {
        var row = element('div');
        var swatch = element('i');
        swatch.style.background = colors[index];

        row.append(
          swatch,
          document.createTextNode(
            item.name + ': ' + money(item.value) +
            ' (' + (item.value / total * 100).toFixed(1) + '%)'
          )
        );

        legend.appendChild(row);
      });

      wrap.append(graph, legend);
      host.appendChild(wrap);
    }

    function renderLine(host, fixed, variable, minutes) {
      var width = 610;
      var height = 270;
      var left = 68;
      var right = 23;
      var top = 18;
      var bottom = 42;

      var volumes = [
        500, 1000, 1500, 2000, 2500,
        3000, 3500, 4000, 4500
      ];

      var costs = volumes.map(function (volume) {
        return fixed + variable * volume / 2500;
      });

      var capacity = volumes.map(function (volume) {
        return volume * minutes / 60 * 20;
      });

      var ymax = Math.max.apply(
        null, costs.concat(capacity)
      ) * 1.12;

      function x(index) {
        return left + index *
          (width - left - right) / (volumes.length - 1);
      }

      function y(value) {
        return top + (height - top - bottom) *
          (1 - value / ymax);
      }

      var graph = svg('svg', {
        viewBox: '0 0 610 270',
        class: 'am6-roi-bi-line',
        role: 'img',
        'aria-label': 'Estimated cost and capacity by ticket volume'
      });

      for (var tick = 0; tick <= 4; tick++) {
        var amount = ymax * tick / 4;

        svg('line', {
          x1: left,
          y1: y(amount),
          x2: width - right,
          y2: y(amount),
          stroke: '#e1eaf1',
          'stroke-width': 1
        }, graph);

        var text = svg('text', {
          x: left - 8,
          y: y(amount) + 4,
          'text-anchor': 'end',
          'font-size': 11,
          fill: '#637e92'
        }, graph);

        text.textContent = 'US$ ' +
          Math.round(amount).toLocaleString((window.AIMASTER_I18N_LANG === 'pt-BR' ? 'pt-BR' : 'en-US'));
      }

      function draw(values, color) {
        var points = values.map(function (value, index) {
          return x(index) + ',' + y(value);
        }).join(' ');

        svg('polyline', {
          points: points,
          fill: 'none',
          stroke: color,
          'stroke-width': 3,
          'stroke-linecap': 'round',
          'stroke-linejoin': 'round'
        }, graph);

        values.forEach(function (value, index) {
          svg('circle', {
            cx: x(index),
            cy: y(value),
            r: 3.5,
            fill: color,
            stroke: '#fff',
            'stroke-width': 1.5
          }, graph);
        });
      }

      draw(costs, '#168ed0');
      draw(capacity, '#168657');

      volumes.forEach(function (volume, index) {
        if (index % 2 !== 0) return;

        var text = svg('text', {
          x: x(index),
          y: height - 20,
          'text-anchor': 'middle',
          'font-size': 11,
          fill: '#637e92'
        }, graph);

        text.textContent = volume.toLocaleString((window.AIMASTER_I18N_LANG === 'pt-BR' ? 'pt-BR' : 'en-US'));
      });

      host.appendChild(graph);

      var legend = element('div', 'am6-roi-bi-legend');

      legend.append(
        element('div', '', 'Blue: estimated recurring operating cost.'),
        element('div', '', 'Green: estimated labor capacity equivalent.'),
        element('div', '', 'Horizontal axis: tickets/month. Scenario, not historical data.')
      );

      host.appendChild(legend);
    }

    function renderCallSensitivity(host) {
      var monthlyTickets = 2500;
      var inputTokens = 4000;
      var outputTokens = 800;
      var inputPrice = 2;
      var outputPrice = 8;

      var costPerCall =
        (inputTokens * inputPrice +
         outputTokens * outputPrice) / 1000000;

      var costs = [1, 2, 3, 4, 5].map(function (calls) {
        return monthlyTickets * calls * costPerCall;
      });

      var card = panel(
        'API Token Cost · 1–5 Calls per Ticket',
        'Planning sensitivity · 2,500 tickets/month · ' +
        'GPT-4.1 reference · 4,000 input + 800 output tokens/call.'
      );

      var graph = svg('svg', {
        viewBox: '0 0 610 280',
        role: 'img',
        'aria-label':
          'Estimated token costs for one to five calls per ticket. ' +
          'Three calls is the planning baseline.'
      });

      var left = 48;
      var top = 24;
      var bottom = 232;
      var max = 200;

      [0, 50, 100, 150, 200].forEach(function (value) {
        var y = bottom - value / max * (bottom - top);

        svg('line', {
          x1: left,
          y1: y,
          x2: 592,
          y2: y,
          stroke: '#e1eaf1',
          'stroke-width': 1
        }, graph);

        var label = svg('text', {
          x: left - 9,
          y: y + 4,
          'text-anchor': 'end',
          'font-size': 11,
          fill: '#637e92'
        }, graph);

        label.textContent = '$' + value;
      });

      costs.forEach(function (cost, index) {
        var x = 78 + index * 106;
        var barHeight = cost / max * (bottom - top);
        var baseline = index === 2;
        var color = baseline ? '#e58c17' : '#168ed0';

        svg('rect', {
          x: x,
          y: bottom - barHeight,
          width: 53,
          height: barHeight,
          rx: 4,
          fill: color
        }, graph);

        var amount = svg('text', {
          x: x + 26.5,
          y: bottom - barHeight - 9,
          'text-anchor': 'middle',
          'font-size': 13,
          'font-weight': baseline ? 800 : 600,
          fill: '#18496c'
        }, graph);

        amount.textContent = '$' + cost.toFixed(0);

        var callLabel = svg('text', {
          x: x + 26.5,
          y: bottom + 19,
          'text-anchor': 'middle',
          'font-size': 12,
          fill: '#637e92'
        }, graph);

        callLabel.textContent = (index + 1) + ' calls';
      });

      card.appendChild(graph);

      card.appendChild(element(
        'p', '',
        'BASELINE: 3 calls/ticket = 7,500 calls/month. ' +
        'Input: 30M tokens × US$2/M = US$60. ' +
        'Output: 6M tokens × US$8/M = US$48. ' +
        'Total: US$108/month. ' +
        'Sensitivity: US$36–180/month. ' +
        'These are planning estimates, not measured usage.'
      ));

      host.appendChild(card);
    }

    function render() {
      content.replaceChildren();

      var items = readCards();

      var inference = metric(items, /inference cost/i);
      var review = metric(items, /review effort/i);
      var infrastructure = metric(items, /infrastructure cost/i);
      var savings = metric(items, /handling time savings/i);

      var tokenCost = inference ? parseUSD(inference.value) : null;
      var reviewCost = review ? parseUSD(review.value) : null;
      var infrastructureCost = infrastructure ?
        parseUSD(infrastructure.value) : null;

      var minutesMatch = savings ?
        savings.value.match(/(\d+(?:\.\d+)?)\s*min/i) : null;
      var minutes = minutesMatch ? Number(minutesMatch[1]) : NaN;

      content.appendChild(element(
        'div',
        'am6-roi-bi-notice',
        'PLANNING BASELINE · 30,000 tickets/year from the briefing, ' +
        'equivalent to 2,500/month as an annual average. ' +
        'Time savings, costs and projected ROI are assumptions, ' +
        'not verified operational results.'
      ));

      var kpis = element('section', 'am6-roi-bi-kpis');

      items.forEach(function (item) {
        var card = element('article', 'am6-roi-bi-kpi');

        card.append(
          element('span', '', item.name),
          element('strong', '', item.value),
          element(
            'small', '',
            'Source: current Option A ROI Methodology.'
          )
        );

        kpis.appendChild(card);
      });

      content.appendChild(kpis);

      var valid = [
        tokenCost, reviewCost, infrastructureCost
      ].every(function (number) {
        return Number.isFinite(number) && number >= 0;
      });

      if (!valid) {
        content.appendChild(element(
          'div',
          'am6-roi-bi-notice',
          'Cost values could not be validated against the ' +
          'current ROI cards. Charts have been withheld.'
        ));
        return;
      }

      var total = tokenCost + reviewCost + infrastructureCost;

      var charts = element('section', 'am6-roi-bi-charts');

      var pie = panel(
        'Monthly Cost Composition',
        'Estimated recurring costs in the Option A scenario.'
      );

      renderPie(pie, [
        {name: 'Inference / tokens', value: tokenCost},
        {name: 'Human review', value: reviewCost},
        {name: 'Infrastructure + maintenance', value: infrastructureCost}
      ]);

      var line = panel(
        'Volume Sensitivity',
        'Projected monthly costs versus labor capacity equivalent.'
      );

      if (Number.isFinite(minutes) && minutes > 0) {
        renderLine(
          line,
          infrastructureCost,
          tokenCost + reviewCost,
          minutes
        );
      } else {
        line.appendChild(element(
          'div', 'am6-roi-bi-notice',
          'Handling-time assumption unavailable. Line chart withheld.'
        ));
      }

      charts.append(pie, line);
      if (option === 'a') renderCallSensitivity(charts);
      content.appendChild(charts);

      var reading = element('section', 'am6-roi-bi-reading');

      var finance = panel(
        'Financial Interpretation',
        'Recurring cost composition.'
      );

      finance.appendChild(element(
        'p', '',
        'Estimated monthly recurring cost: ' + money(total) +
        '. Human review represents ' +
        (reviewCost / total * 100).toFixed(1) +
        '% of operating cost; inference tokens represent ' +
        (tokenCost / total * 100).toFixed(1) + '%.'
      ));

      var limitations = panel(
        'Evidence and Limitations',
        'What must be measured in production.'
      );

      limitations.appendChild(element(
        'p', '',
        'Handling-time savings, review frequency, actual provider ' +
        'pricing and workload patterns remain unverified. ' +
        'Theoretical capacity savings are not realized cash savings. ' +
        'One-time implementation costs are excluded.'
      ));

      reading.append(finance, limitations);
      content.appendChild(reading);

      if (Number.isFinite(minutes) && minutes > 0) {
        var grossCapacity = 2500 * minutes / 60 * 20;

        content.appendChild(element(
          'div',
          'am6-roi-bi-notice',
          'BASE SCENARIO · ' + money(grossCapacity) +
          '/month of estimated gross labor-capacity equivalent ' +
          'versus ' + money(total) +
          '/month of projected recurring operating costs. ' +
          'These figures do not establish realized financial ROI.'
        ));
      }

      var methods = element('section', 'am6-roi-bi-details');
      methods.appendChild(element(
        'h3', '',
        'Detailed Methodology · Six Source Indicators'
      ));

      items.forEach(function (item) {
        var details = element('details');

        details.append(
          element(
            'summary', '',
            item.name + ' — ' + item.value
          ),
          element(
            'p', '',
            item.methodology ||
            'No detailed methodology recorded in the source.'
          )
        );

        methods.appendChild(details);
      });

      content.appendChild(methods);
    }

    var previousFocus = null;

    function hide() {
      if (overlay.hidden) return;

      overlay.hidden = true;
      document.body.classList.remove('am6-roi-bi-open');
      button.setAttribute('aria-expanded', 'false');

      if (previousFocus && previousFocus.focus) {
        previousFocus.focus();
      }
    }

    button.addEventListener('click', function (event) {
      event.preventDefault();
      event.stopPropagation();

      previousFocus = document.activeElement;
      render();

      overlay.hidden = false;
      document.body.classList.add('am6-roi-bi-open');
      button.setAttribute('aria-expanded', 'true');

      close.focus();
    });

    close.addEventListener('click', hide);

    overlay.addEventListener('click', function (event) {
      if (event.target === overlay) hide();
    });

    document.addEventListener('keydown', function (event) {
      if (overlay.hidden) return;

      if (event.key === 'Escape') {
        event.preventDefault();
        hide();
      }

      if (event.key === 'Tab') {
        var focusable = Array.prototype.slice.call(
          dialog.querySelectorAll(
            'button,summary,[tabindex]:not([tabindex="-1"])'
          )
        ).filter(function (node) {
          return node.getClientRects().length > 0;
        });

        if (!focusable.length) return;

        var first = focusable[0];
        var last = focusable[focusable.length - 1];

        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last.focus();
        } else if (
          !event.shiftKey && document.activeElement === last
        ) {
          event.preventDefault();
          first.focus();
        }
      }
    });

    map.dataset['am6RoiBiReady' + option] = '1';
  }

  function initializeBoth() {
    initialize('a');
    initialize('b');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeBoth);
  } else {
    initializeBoth();
  }
})();

// AM6 ROI OPTION SWITCH OWNER
(function () {
  'use strict';

  function initializeRoiSwitch() {
    const roi = document.querySelector('#architecture-map .am6-roi');
    if (!roi || roi.dataset.am6RoiViewsReady === '1') return;

    const button = roi.querySelector('[data-am6-roi-switch]');
    const description = roi.querySelector('[data-am6-roi-description]');
    const optionA = roi.querySelector('[data-am6-roi-view="a"]');
    const optionB = roi.querySelector('[data-am6-roi-view="b"]');

    if (!button || !description || !optionA || !optionB) return;

    if (optionA.querySelectorAll('.am6-roi-grid > div').length !== 6 ||
        optionB.querySelectorAll('.am6-roi-grid > div').length !== 6) {
      return;
    }

    const descriptions = {
      a: '(Planning) External API LLM operating costs and ROI assumptions.',
      b: '(Planning) Private CPU-first operating costs and ROI assumptions.'
    };

    let active = 'a';

    function render() {
      optionA.hidden = active !== 'a';
      optionB.hidden = active !== 'b';

      description.textContent = descriptions[active];

      const next = active === 'a' ? 'Option B' : 'Option A';
      button.textContent = next;
      button.setAttribute('aria-label', 'Switch to ' + next);
      button.setAttribute('aria-controls',
        'am6-roi-option-a am6-roi-option-b');
      button.setAttribute('aria-pressed', String(active === 'b'));

      roi.setAttribute('data-am6-roi-active', active);
    }

    button.addEventListener('click', function () {
      active = active === 'a' ? 'b' : 'a';
      render();
    });

    roi.dataset.am6RoiViewsReady = '1';
    render();

    // Read both ROI scenarios from the canonical Architecture Map.
    // No duplicate formulas and no additional event listener.
    ['a', 'b'].forEach(function (option) {
      var sourceView = option === 'a' ? optionA : optionB;
      var cards = sourceView.querySelectorAll(
        '.am6-roi-grid > div[data-am6-roi-financial="' + option + '"]'
      );
      var targets = document.querySelectorAll(
        '#automation-reports [data-ar-roi-option="' + option + '"]'
      );
      if (cards.length !== 6 || targets.length !== 6) return;

      var values = Array.from(cards, function (card) {
        var small = card.querySelector('small');
        return small ? small.textContent.trim() : '';
      });
      if (!values.every(Boolean)) return;

      targets.forEach(function (target, i) {
        var group = target.closest('[data-ar-roi-estimated]');
        var localized = group &&
          group.getAttribute('data-ar-roi-estimated');
        target.textContent = values[i].replace(
          /\bEstimated$/,
          localized || 'Estimated'
        );
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeRoiSwitch);
  } else {
    initializeRoiSwitch();
  }
})();

// AM6 OPTION B BLUE FLOW: APPLICATION TO KNOWLEDGE AND INDEX
(() => {
  function init() {
    const option = document.querySelector(
      '#architecture-map .am6-option.am6-private'
    );
    if (!option) return;

    const host = option.querySelector('.am6-topology');
    const application = option.querySelector(
      '[data-am6-node="b-application-server"]'
    );
    const knowledge = option.querySelector(
      '[data-am6-node="b-knowledge-store"]'
    );
    const index = option.querySelector(
      '[data-am6-node="b-index-pipeline"]'
    );
    const localRetrieval = option.querySelector(
      '[data-am6-node="b-local-retrieval"]'
    );
    const telemetry = option.querySelector(
      '[data-am6-node="b-telemetry-maintenance"]'
    );
    const ticketAudit = option.querySelector(
      '[data-am6-node="b-ticket-audit"]'
    );
    const inference = option.querySelector(
      '[data-am6-node="b-cpu-first-inference-node"]'
    );
    const modelRegistry = option.querySelector(
      '[data-am6-node="b-model-artifact-registry"]'
    );
    const capacityControl = option.querySelector(
      '[data-am6-node="b-capacity-queue-control"]'
    );
    const responseValidation = option.querySelector(
      '[data-am6-node="b-response-validation"]'
    );
    const operatorReview = option.querySelector(
      '[data-am6-node="b-operator-review"]'
    );

    if (!host || !application || !knowledge || !index || !localRetrieval || !telemetry || !ticketAudit || !inference || !modelRegistry || !capacityControl || !responseValidation || !operatorReview) return;
    if (host.querySelector('[data-am6-b-application-flow]')) return;

    // One SVG owns both branches; no duplicate behavior controller.
    const ns = 'http://www.w3.org/2000/svg';
    const svg = document.createElementNS(ns, 'svg');
    svg.setAttribute('data-am6-b-application-flow', '');
    svg.setAttribute('aria-hidden', 'true');
    svg.style.position = 'absolute';
    svg.style.inset = '0';
    svg.style.width = '100%';
    svg.style.height = '100%';
    svg.style.pointerEvents = 'none';
    svg.style.overflow = 'visible';
    svg.style.zIndex = '2';

    const path = document.createElementNS(ns, 'path');
    path.setAttribute('fill', 'none');
    path.setAttribute('stroke', '#168ed0');
    path.setAttribute('stroke-width', '2.5');
    path.setAttribute('stroke-dasharray', '6 5');
    path.setAttribute('stroke-linecap', 'round');
    path.setAttribute('stroke-linejoin', 'round');

    svg.appendChild(path);

    // Option B: Application Server -> Local Retrieval.
    const orangePath = document.createElementNS(ns, 'path');
    orangePath.setAttribute('fill', 'none');
    orangePath.setAttribute('stroke', '#e58c17');
    orangePath.setAttribute('stroke-width', '2.5');
    orangePath.setAttribute('stroke-dasharray', '6 5');
    orangePath.setAttribute('stroke-linecap', 'round');
    orangePath.setAttribute('stroke-linejoin', 'round');
    svg.appendChild(orangePath);

    // Option B: lower return flow to Telemetry + Maintenance.
    const returnPath = document.createElementNS(ns, 'path');
    returnPath.setAttribute('fill', 'none');
    returnPath.setAttribute('stroke', '#986cdb');
    returnPath.setAttribute('stroke-width', '2.5');
    returnPath.setAttribute('stroke-dasharray', '6 5');
    returnPath.setAttribute('stroke-linecap', 'round');
    returnPath.setAttribute('stroke-linejoin', 'round');
    svg.appendChild(returnPath);

    // Option B: Knowledge Store + Index Pipeline -> CPU inference.
    const inferencePath = document.createElementNS(ns, 'path');
    inferencePath.setAttribute('fill', 'none');
    inferencePath.setAttribute('stroke', '#168ed0');
    inferencePath.setAttribute('stroke-width', '2.5');
    inferencePath.setAttribute('stroke-dasharray', '6 5');
    inferencePath.setAttribute('stroke-linecap', 'round');
    inferencePath.setAttribute('stroke-linejoin', 'round');
    svg.appendChild(inferencePath);

    // Option B: Local Retrieval -> Model Artifact Registry.
    const registryPath = document.createElementNS(ns, 'path');
    registryPath.setAttribute('fill', 'none');
    registryPath.setAttribute('stroke', '#e58c17');
    registryPath.setAttribute('stroke-width', '2.5');
    registryPath.setAttribute('stroke-dasharray', '6 5');
    registryPath.setAttribute('stroke-linecap', 'round');
    registryPath.setAttribute('stroke-linejoin', 'round');
    svg.appendChild(registryPath);

    // Option B: vertical purple model execution chain.
    const modelChainPath = document.createElementNS(ns, 'path');
    modelChainPath.setAttribute('fill', 'none');
    modelChainPath.setAttribute('stroke', '#986cdb');
    modelChainPath.setAttribute('stroke-width', '2.5');
    modelChainPath.setAttribute('stroke-dasharray', '6 5');
    modelChainPath.setAttribute('stroke-linecap', 'round');
    modelChainPath.setAttribute('stroke-linejoin', 'round');
    svg.appendChild(modelChainPath);

    // Option B: Capacity / Queue Control -> Ticket + Audit.
    const capacityAuditPath = document.createElementNS(ns, 'path');
    capacityAuditPath.setAttribute('fill', 'none');
    capacityAuditPath.setAttribute('stroke', '#dc5079');
    capacityAuditPath.setAttribute('stroke-width', '2.5');
    capacityAuditPath.setAttribute('stroke-dasharray', '6 5');
    capacityAuditPath.setAttribute('stroke-linecap', 'round');
    capacityAuditPath.setAttribute('stroke-linejoin', 'round');
    svg.appendChild(capacityAuditPath);

    // Option B: CPU inference -> Validation + Operator Review.
    const cpuOutputPath = document.createElementNS(ns, 'path');
    cpuOutputPath.setAttribute('fill', 'none');
    cpuOutputPath.setAttribute('stroke', '#168ed0');
    cpuOutputPath.setAttribute('stroke-width', '2.5');
    cpuOutputPath.setAttribute('stroke-dasharray', '6 5');
    cpuOutputPath.setAttribute('stroke-linecap', 'round');
    cpuOutputPath.setAttribute('stroke-linejoin', 'round');
    svg.appendChild(cpuOutputPath);

    // Option B: Validation -> Review -> Ticket + Audit.
    const validationAuditPath = document.createElementNS(ns, 'path');
    validationAuditPath.setAttribute('fill', 'none');
    validationAuditPath.setAttribute('stroke', '#168ed0');
    validationAuditPath.setAttribute('stroke-width', '2.5');
    validationAuditPath.setAttribute('stroke-dasharray', '6 5');
    validationAuditPath.setAttribute('stroke-linecap', 'round');
    validationAuditPath.setAttribute('stroke-linejoin', 'round');
    svg.appendChild(validationAuditPath);

    // Option B: Validation + Review -> Telemetry.
    const telemetryInputPath = document.createElementNS(ns, 'path');
    telemetryInputPath.setAttribute('fill', 'none');
    telemetryInputPath.setAttribute('stroke', '#168ed0');
    telemetryInputPath.setAttribute('stroke-width', '2.5');
    telemetryInputPath.setAttribute('stroke-dasharray', '6 5');
    telemetryInputPath.setAttribute('stroke-linecap', 'round');
    telemetryInputPath.setAttribute('stroke-linejoin', 'round');
    svg.appendChild(telemetryInputPath);

    // Option B: model version metadata -> operator review.
    const modelReviewPath = document.createElementNS(ns, 'path');
    modelReviewPath.setAttribute('fill', 'none');
    modelReviewPath.setAttribute('stroke', '#e58c17');
    modelReviewPath.setAttribute('stroke-width', '2.5');
    modelReviewPath.setAttribute('stroke-dasharray', '6 5');
    modelReviewPath.setAttribute('stroke-linecap', 'round');
    modelReviewPath.setAttribute('stroke-linejoin', 'round');
    svg.appendChild(modelReviewPath);

    // The SVG is an overlay and does not participate in the grid.
    if (window.getComputedStyle(host).position === 'static') {
      host.style.position = 'relative';
    }
    path.setAttribute('data-am6-route-title', "Application Server → Knowledge Processing");
    path.setAttribute('data-am6-route-purpose', "Application branch entering local knowledge processing.");
    path.setAttribute('data-am6-route-parts', "[[\"Application Server → Shared Junction\", \"The application initiates approved knowledge and indexing operations through a common junction.\"], [\"Shared Junction → Knowledge Store\", \"This branch delivers approved source information to private knowledge storage.\"], [\"Shared Junction → Index Pipeline\", \"This branch prepares source information for indexing and subsequent retrieval.\"]]");
    orangePath.setAttribute('data-am6-route-title', "Application Server → Local Retrieval");
    orangePath.setAttribute('data-am6-route-purpose', "Application branch connected to private retrieval.");
    returnPath.setAttribute('data-am6-route-title', "Operational Telemetry Return");
    returnPath.setAttribute('data-am6-route-purpose', "Private operational return connection.");
    returnPath.setAttribute('data-am6-route-parts', "[[\"Application Server → Telemetry + Maintenance\", \"Application health and runtime signals enter the private monitoring route.\"], [\"Ticket + Audit → Telemetry + Maintenance\", \"Ticket and audit events join the monitoring route for operational investigation.\"]]");
    inferencePath.setAttribute('data-am6-route-title', "Knowledge / Retrieval → CPU-first Inference Node");
    inferencePath.setAttribute('data-am6-route-purpose', "Retrieved context routed into local inference.");
    inferencePath.setAttribute('data-am6-route-parts', "[[\"Knowledge Store → Inference Collector\", \"Approved source knowledge contributes controlled context for local inference.\"], [\"Index Pipeline → Inference Collector\", \"Indexed information contributes retrieval-ready context to the inference request.\"], [\"Inference Collector → CPU-first Inference Node\", \"The combined context reaches the private CPU-first inference runtime.\"]]");
    registryPath.setAttribute('data-am6-route-title', "Local Retrieval → Model Artifact Registry");
    registryPath.setAttribute('data-am6-route-purpose', "Connection to model artifact management.");
    modelChainPath.setAttribute('data-am6-route-title', "Model Execution Chain");
    modelChainPath.setAttribute('data-am6-route-purpose', "Connection among model artifacts, inference and capacity control.");
    modelChainPath.setAttribute('data-am6-route-parts', "[[\"Model Artifact Registry → CPU-first Inference Node\", \"The approved model artifact and its version are made available to the private CPU-first inference runtime. This connection establishes which model is executed.\"], [\"CPU-first Inference Node → Capacity / Queue Control\", \"Inference workload is coordinated with queue and capacity controls to manage concurrency, resource consumption and processing limits.\"]]");
    capacityAuditPath.setAttribute('data-am6-route-title', "Capacity / Queue Control → Ticket + Audit");
    capacityAuditPath.setAttribute('data-am6-route-purpose', "Capacity management information connected to auditing.");
    cpuOutputPath.setAttribute('data-am6-route-title', "CPU-first Inference Node → Validation / Review");
    cpuOutputPath.setAttribute('data-am6-route-purpose', "Local inference output enters validation and review.");
    cpuOutputPath.setAttribute('data-am6-route-parts', "[[\"CPU-first Inference → Shared Output\", \"The local runtime forwards generated output to a controlled distribution junction.\"], [\"Shared Output → Response Validation\", \"Generated output enters the response acceptance and policy checks.\"], [\"Shared Output → Operator Review\", \"Generated output is available for human assessment where oversight is required.\"]]");
    validationAuditPath.setAttribute('data-am6-route-title', "Validation / Review → Ticket + Audit");
    validationAuditPath.setAttribute('data-am6-route-purpose', "Validated responses move through human review and audit recording.");
    validationAuditPath.setAttribute('data-am6-route-parts', "[[\"Response Validation → Operator Review\", \"Responses requiring human judgment are submitted for operator correction or approval.\"], [\"Operator Review → Ticket + Audit\", \"The operator decision and rationale are recorded in the ticket audit history.\"]]");
    telemetryInputPath.setAttribute('data-am6-route-title', "Validation / Review → Telemetry + Maintenance");
    telemetryInputPath.setAttribute('data-am6-route-purpose', "Separate validation and operator signals reach private monitoring.");
    telemetryInputPath.setAttribute('data-am6-route-parts', "[[\"Response Validation → Telemetry + Maintenance\", \"Validation outcomes, policy checks and diagnostic signals are routed to private monitoring.\"], [\"Operator Review → Telemetry + Maintenance\", \"Operator review events and correction activity are routed to private monitoring.\"]]");
    modelReviewPath.setAttribute('data-am6-route-title', "Model Artifact Registry → Operator Review");
    modelReviewPath.setAttribute('data-am6-route-purpose', "Model version context connected to human review.");
    host.appendChild(svg);

    function draw() {
      const base = host.getBoundingClientRect();
      const a = application.getBoundingClientRect();
      const k = knowledge.getBoundingClientRect();
      const i = index.getBoundingClientRect();
      const l = localRetrieval.getBoundingClientRect();
      const t = telemetry.getBoundingClientRect();
      const audit = ticketAudit.getBoundingClientRect();
      const cpu = inference.getBoundingClientRect();
      const registryBox = modelRegistry.getBoundingClientRect();
      const capacityBox = capacityControl.getBoundingClientRect();
      const validationBox = responseValidation.getBoundingClientRect();
      const reviewBox = operatorReview.getBoundingClientRect();

      svg.setAttribute(
        'viewBox', `0 0 ${base.width} ${base.height}`
      );

      if (!base.width || !base.height ||
          !a.width || !k.width || !i.width) {
        path.setAttribute('d', '');
        return;
      }

      const ax = a.right - base.left;
      const ay = a.top + a.height / 2 - base.top;
      const kx = k.left - base.left;
      const ky = k.top + k.height / 2 - base.top;
      const ix = i.left - base.left;
      const iy = i.top + i.height / 2 - base.top;

      // Shared trunk centered inside the gap between columns.
      const leftTarget = Math.min(kx, ix);
      if (leftTarget <= ax + 16) {
        path.setAttribute('d', '');
        return;
      }

      const trunkX = (ax + leftTarget) / 2;
      // Application Server feeds a shared, connected junction.
      // Both branches turn right through real quadratic curves.
      function arm(targetX, targetY) {
        const dy = targetY - ay;
        const direction = Math.sign(dy);
        const radius = Math.min(
          9,
          Math.abs(dy) / 2,
          (targetX - trunkX) / 2
        );

        if (!direction || radius <= 0) {
          return ` M ${trunkX} ${ay} H ${targetX}`;
        }

        return (
          ` M ${trunkX} ${ay}` +
          ` V ${targetY - direction * radius}` +
          ` Q ${trunkX} ${targetY} ` +
          `${trunkX + radius} ${targetY}` +
          ` H ${targetX}`
        );
      }

      // Both arms start at the same junction: no detached branch.
      const route =
        `M ${ax} ${ay} H ${trunkX}` +
        arm(kx, ky) +
        arm(ix, iy);

      path.setAttribute('d', route);

      // Lower orange exit, independent of the blue junction.
      const orangeStartX = ax;
      const orangeStartY = ay + 18;
      const orangeTargetX = l.left - base.left;
      const orangeTargetY =
        l.top + l.height / 2 - base.top;

      let orangeRoute = '';

      if (l.width && orangeTargetX > orangeStartX + 20) {
        const turnX =
          orangeStartX + (orangeTargetX - orangeStartX) / 2;
        const dy = orangeTargetY - orangeStartY;
        const direction = Math.sign(dy);
        const radius = Math.min(
          9,
          (turnX - orangeStartX) / 3,
          (orangeTargetX - turnX) / 3,
          Math.abs(dy) / 3
        );

        if (!direction || radius <= 0) {
          orangeRoute =
            `M ${orangeStartX} ${orangeStartY}` +
            ` H ${turnX}` +
            ` V ${orangeTargetY}` +
            ` H ${orangeTargetX}`;
        } else {
          orangeRoute =
            `M ${orangeStartX} ${orangeStartY}` +
            ` H ${turnX - radius}` +
            ` Q ${turnX} ${orangeStartY} ` +
            `${turnX} ${orangeStartY + direction * radius}` +
            ` V ${orangeTargetY - direction * radius}` +
            ` Q ${turnX} ${orangeTargetY} ` +
            `${turnX + radius} ${orangeTargetY}` +
            ` H ${orangeTargetX}`;
        }
      }

      orangePath.setAttribute('d', orangeRoute);

      // Bottom-center of Application Server -> below every
      // microcard -> bottom-center of Telemetry + Maintenance.
      const sx = a.left + a.width / 2 - base.left;
      const sy = a.bottom - base.top;
      const tx = t.left + t.width / 2 - base.left;
      const ty = t.bottom - base.top;

      const cardBottoms = Array.from(
        host.querySelectorAll('.am6-unit')
      ).map(card => card.getBoundingClientRect().bottom - base.top);

      const lowestCard = Math.max(sy, ty, ...cardBottoms);
      const railY = lowestCard + 34;
      let returnRoute = '';

      // Keep the horizontal return below all microcards.
      // Do not draw over a card if the topology lacks clearance.
      if (a.width && t.width &&
          tx > sx + 30 &&
          railY < base.height + 24 &&
          railY > sy + 12 &&
          railY > ty + 12) {
        const radius = Math.min(
          10,
          (railY - sy) / 3,
          (railY - ty) / 3,
          (tx - sx) / 5
        );

        returnRoute =
          `M ${sx} ${sy}` +
          ` V ${railY - radius}` +
          ` Q ${sx} ${railY} ${sx + radius} ${railY}` +
          ` H ${tx - radius}` +
          ` Q ${tx} ${railY} ${tx} ${railY - radius}` +
          ` V ${ty}`;
      }

      // Ticket + Audit joins the existing lower purple rail.
      // The branch is part of the same SVG path.
      if (returnRoute && audit.width) {
        const auditX =
          audit.left + audit.width / 2 - base.left;
        const auditBottom = audit.bottom - base.top;

        if (auditX > sx && auditX < tx &&
            railY > auditBottom + 2) {
          returnRoute +=
            ` M ${auditX} ${auditBottom} V ${railY}`;
        }
      }

      returnPath.setAttribute('d', returnRoute);

      // Two source arms join one vertical collector.
      // The collector feeds the CPU-first Inference Node.
      const kRight = k.right - base.left;
      const iRight = i.right - base.left;
      const kCenter = k.top + k.height / 2 - base.top;
      const iCenter = i.top + i.height / 2 - base.top;
      const cpuLeft = cpu.left - base.left;
      const cpuCenter = cpu.top + cpu.height / 2 - base.top;

      let inferenceRoute = '';

      const sourceRight = Math.max(kRight, iRight);
      const gap = cpuLeft - sourceRight;

      if (k.width && i.width && cpu.width && gap > 24) {
        const collectorX = sourceRight + gap * 0.42;
        const collectorTop = Math.min(kCenter, iCenter);
        const collectorBottom = Math.max(kCenter, iCenter);
        const collectorCenter =
          (collectorTop + collectorBottom) / 2;

        const radius = Math.min(
          9,
          gap / 6,
          Math.abs(cpuCenter - collectorCenter) / 3
        );

        // Both inputs curve into one shared vertical collector.
        const joinY = (kCenter + iCenter) / 2;

        function roundedInput(sourceX, sourceY) {
          const direction = Math.sign(joinY - sourceY);
          const radius = Math.min(
            9,
            (collectorX - sourceX) / 3,
            Math.abs(joinY - sourceY) / 3
          );

          if (!direction || radius <= 0) {
            return (
              `M ${sourceX} ${sourceY}` +
              ` H ${collectorX} V ${joinY}`
            );
          }

          return (
            `M ${sourceX} ${sourceY}` +
            ` H ${collectorX - radius}` +
            ` Q ${collectorX} ${sourceY} ` +
            `${collectorX} ${sourceY + direction * radius}` +
            ` V ${joinY}`
          );
        }

        // Shared output starts at the actual convergence point.
        const outputDirection = Math.sign(cpuCenter - joinY);
        const bendX = (collectorX + cpuLeft) / 2;
        const outputRadius = Math.min(
          9,
          (bendX - collectorX) / 3,
          (cpuLeft - bendX) / 3,
          Math.abs(cpuCenter - joinY) / 3
        );

        let outputRoute = '';

        if (!outputDirection || outputRadius <= 0) {
          outputRoute =
            `M ${collectorX} ${joinY}` +
            ` H ${cpuLeft}`;
        } else {
          outputRoute =
            `M ${collectorX} ${joinY}` +
            ` H ${bendX - outputRadius}` +
            ` Q ${bendX} ${joinY} ` +
            `${bendX} ${joinY + outputDirection * outputRadius}` +
            ` V ${cpuCenter - outputDirection * outputRadius}` +
            ` Q ${bendX} ${cpuCenter} ` +
            `${bendX + outputRadius} ${cpuCenter}` +
            ` H ${cpuLeft}`;
        }

        inferenceRoute =
          roundedInput(kRight, kCenter) +
          ' ' + roundedInput(iRight, iCenter) +
          ' ' + outputRoute;
      }

      inferencePath.setAttribute('d', inferenceRoute);

      // Local Retrieval -> Model Artifact Registry.
      const rx1 = l.right - base.left;
      const ry1 = l.top + l.height / 2 - base.top;
      const rx2 = registryBox.left - base.left;
      const ry2 = registryBox.top + registryBox.height / 2 - base.top;

      let registryRoute = '';

      if (l.width && registryBox.width && rx2 > rx1 + 16) {
        const midX = (rx1 + rx2) / 2;
        const direction = Math.sign(ry2 - ry1);
        const radius = Math.min(
          9,
          (midX - rx1) / 3,
          (rx2 - midX) / 3,
          Math.abs(ry2 - ry1) / 3
        );

        if (!direction || radius <= 0) {
          registryRoute = `M ${rx1} ${ry1} H ${rx2}`;
        } else {
          registryRoute =
            `M ${rx1} ${ry1}` +
            ` H ${midX - radius}` +
            ` Q ${midX} ${ry1} ${midX} ${ry1 + direction * radius}` +
            ` V ${ry2 - direction * radius}` +
            ` Q ${midX} ${ry2} ${midX + radius} ${ry2}` +
            ` H ${rx2}`;
        }
      }

      registryPath.setAttribute('d', registryRoute);

      // Source bottom-center -> target top-center.
      function modelChainSegment(sourceBox, targetBox) {
        if (!sourceBox.width || !targetBox.width) return '';

        const x1 = sourceBox.left + sourceBox.width / 2 - base.left;
        const y1 = sourceBox.bottom - base.top;
        const x2 = targetBox.left + targetBox.width / 2 - base.left;
        const y2 = targetBox.top - base.top;
        const height = y2 - y1;

        if (height <= 3) return '';

        if (Math.abs(x2 - x1) <= 1) {
          return `M ${x1} ${y1} V ${y2}`;
        }

        const radius = Math.min(
          9, height / 5, Math.abs(x2 - x1) / 3
        );
        const middleY = (y1 + y2) / 2;
        const direction = Math.sign(x2 - x1);

        return (
          `M ${x1} ${y1}` +
          ` V ${middleY - radius}` +
          ` Q ${x1} ${middleY} ${x1 + direction * radius} ${middleY}` +
          ` H ${x2 - direction * radius}` +
          ` Q ${x2} ${middleY} ${x2} ${middleY + radius}` +
          ` V ${y2}`
        );
      }

      const registryToInference =
        modelChainSegment(registryBox, cpu);
      const inferenceToCapacity =
        modelChainSegment(cpu, capacityBox);

      modelChainPath.setAttribute(
        'd',
        [registryToInference, inferenceToCapacity]
          .filter(Boolean).join(' ')
      );

      // Capacity / Queue Control -> Ticket + Audit.
      // Connect both cards through their facing horizontal edges.
      const cx1 = capacityBox.right - base.left;
      const cy1 = capacityBox.top + capacityBox.height / 2 - base.top;
      const cx2 = audit.left - base.left;
      const cy2 = audit.top + audit.height / 2 - base.top;

      let capacityAuditRoute = '';

      if (capacityBox.width && audit.width && cx2 > cx1 + 16) {
        const middleX = (cx1 + cx2) / 2;
        const direction = Math.sign(cy2 - cy1);
        const radius = Math.min(
          9,
          (middleX - cx1) / 3,
          (cx2 - middleX) / 3,
          Math.abs(cy2 - cy1) / 3
        );

        if (!direction || radius <= 0) {
          capacityAuditRoute = `M ${cx1} ${cy1} H ${cx2}`;
        } else {
          capacityAuditRoute =
            `M ${cx1} ${cy1}` +
            ` H ${middleX - radius}` +
            ` Q ${middleX} ${cy1} ` +
            `${middleX} ${cy1 + direction * radius}` +
            ` V ${cy2 - direction * radius}` +
            ` Q ${middleX} ${cy2} ` +
            `${middleX + radius} ${cy2}` +
            ` H ${cx2}`;
        }
      }

      capacityAuditPath.setAttribute('d', capacityAuditRoute);

      // A single shared blue trunk branches to both targets.
      const outX = cpu.right - base.left;
      const outY = cpu.top + cpu.height / 2 - base.top;

      const validationX = validationBox.left - base.left;
      const validationY =
        validationBox.top + validationBox.height / 2 - base.top;

      const reviewX = reviewBox.left - base.left;
      const reviewY =
        reviewBox.top + reviewBox.height / 2 - base.top;

      let cpuOutputRoute = '';

      const availableGap =
        Math.min(validationX, reviewX) - outX;

      if (cpu.width && validationBox.width && reviewBox.width &&
          availableGap > 24) {
        const splitX = outX + availableGap * 0.38;

        // Common segment: CPU-first Inference Node -> split.
        cpuOutputRoute = `M ${outX} ${outY} H ${splitX}`;

        function outputArm(targetX, targetY) {
          const delta = targetY - outY;
          const direction = Math.sign(delta);

          if (!direction || Math.abs(delta) < 2) {
            return ` M ${splitX} ${outY} H ${targetX}`;
          }

          const radius = Math.min(
            9,
            Math.abs(delta) / 3,
            (targetX - splitX) / 3
          );

          return (
            ` M ${splitX} ${outY}` +
            ` V ${targetY - direction * radius}` +
            ` Q ${splitX} ${targetY} ` +
            `${splitX + radius} ${targetY}` +
            ` H ${targetX}`
          );
        }

        cpuOutputRoute += outputArm(validationX, validationY);
        cpuOutputRoute += outputArm(reviewX, reviewY);
      }

      cpuOutputPath.setAttribute('d', cpuOutputRoute);

      // Bottom-center -> top-center within Validation & Output.
      function validationAuditSegment(fromBox, toBox) {
        if (!fromBox.width || !toBox.width) return '';

        const x1 = fromBox.left + fromBox.width / 2 - base.left;
        const y1 = fromBox.bottom - base.top;
        const x2 = toBox.left + toBox.width / 2 - base.left;
        const y2 = toBox.top - base.top;
        const gap = y2 - y1;

        if (gap <= 3) return '';

        if (Math.abs(x2 - x1) <= 1) {
          return `M ${x1} ${y1} V ${y2}`;
        }

        const direction = Math.sign(x2 - x1);
        const radius = Math.min(
          9, gap / 5, Math.abs(x2 - x1) / 3
        );
        const midY = (y1 + y2) / 2;

        return (
          `M ${x1} ${y1}` +
          ` V ${midY - radius}` +
          ` Q ${x1} ${midY} ${x1 + direction * radius} ${midY}` +
          ` H ${x2 - direction * radius}` +
          ` Q ${x2} ${midY} ${x2} ${midY + radius}` +
          ` V ${y2}`
        );
      }

      const validationToReview =
        validationAuditSegment(validationBox, reviewBox);
      const reviewToAudit =
        validationAuditSegment(reviewBox, audit);

      validationAuditPath.setAttribute(
        'd',
        [validationToReview, reviewToAudit].filter(Boolean).join(' ')
      );

      // Independent geometry names prevent collisions with existing flows.
      const tvRight = validationBox.right - base.left;
      const tvY = validationBox.top + validationBox.height / 2 - base.top;
      const trRight = reviewBox.right - base.left;
      const trY = reviewBox.top + reviewBox.height / 2 - base.top;
      const ttLeft = t.left - base.left;
      const ttY = t.top + t.height / 2 - base.top;

      let telemetryInputRoute = '';

      const telemetrySourceRight = Math.max(tvRight, trRight);
      const telemetryCorridor = ttLeft - telemetrySourceRight;

      if (validationBox.width && reviewBox.width && t.width &&
          telemetryCorridor > 34) {
        const validationLaneX =
          telemetrySourceRight + telemetryCorridor * 0.30;
        const reviewLaneX =
          telemetrySourceRight + telemetryCorridor * 0.65;
        const validationEntryY =
          t.top + t.height * 0.36 - base.top;
        const reviewEntryY =
          t.top + t.height * 0.64 - base.top;

        function directTelemetryRoute(sourceX, sourceY, laneX, targetY) {
          return (
            `M ${sourceX} ${sourceY}` +
            ` H ${laneX}` +
            ` V ${targetY}` +
            ` H ${ttLeft}`
          );
        }

        telemetryInputRoute =
          directTelemetryRoute(
            tvRight, tvY, validationLaneX, validationEntryY
          ) + ' ' +
          directTelemetryRoute(
            trRight, trY, reviewLaneX, reviewEntryY
          );
      }

      telemetryInputPath.setAttribute('d', telemetryInputRoute);

      // Separate orange route above Operator Review, away from
      // the blue CPU input and the blue vertical validation link.
      const mrStartX = registryBox.right - base.left;
      const mrStartY =
        registryBox.top + registryBox.height / 2 - base.top;
      const mrReviewLeft = reviewBox.left - base.left;
      const mrReviewTop = reviewBox.top - base.top;
      const mrValidationBottom = validationBox.bottom - base.top;
      const mrGap = mrReviewLeft - mrStartX;

      let modelReviewRoute = '';

      if (registryBox.width && reviewBox.width &&
          validationBox.width && mrGap > 30) {
        const mrCorridorX = mrStartX + Math.min(30, mrGap * 0.4);
        const mrEntryX = mrReviewLeft + Math.min(
          30, reviewBox.width * 0.22
        );
        const mrLaneY =
          (Math.max(mrValidationBottom, mrStartY) +
           mrReviewTop) / 2;

        const mrRadius = Math.min(
          7,
          (mrCorridorX - mrStartX) / 2,
          (mrEntryX - mrCorridorX) / 4,
          (mrLaneY - mrStartY) / 3,
          (mrReviewTop - mrLaneY) / 3
        );

        // Do not draw through microcards or reuse the blue
        // validation-to-review center-top entry.
        if (mrLaneY > mrStartY + 12 &&
            mrLaneY > mrValidationBottom + 4 &&
            mrLaneY < mrReviewTop - 5 &&
            mrRadius > 1) {
          modelReviewRoute =
            `M ${mrStartX} ${mrStartY}` +
            ` H ${mrCorridorX - mrRadius}` +
            ` Q ${mrCorridorX} ${mrStartY} ` +
            `${mrCorridorX} ${mrStartY + mrRadius}` +
            ` V ${mrLaneY - mrRadius}` +
            ` Q ${mrCorridorX} ${mrLaneY} ` +
            `${mrCorridorX + mrRadius} ${mrLaneY}` +
            ` H ${mrEntryX - mrRadius}` +
            ` Q ${mrEntryX} ${mrLaneY} ` +
            `${mrEntryX} ${mrLaneY + mrRadius}` +
            ` V ${mrReviewTop}`;
        }
      }

      modelReviewPath.setAttribute('d', modelReviewRoute);
    }

    const observer = new ResizeObserver(draw);
    [host, application, knowledge, index, localRetrieval, telemetry, ticketAudit, inference, modelRegistry, capacityControl, responseValidation, operatorReview].forEach(
      element => observer.observe(element)
    );
    window.addEventListener('resize', draw, {passive: true});
    draw();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, {once: true});
  } else {
    init();
  }
})();

// OWNER: process.evidence.viewer
(() => {
  function init() {
    const gallery = document.querySelector('#process .process-evidence');
    if (!gallery || typeof HTMLDialogElement === 'undefined' ||
        document.querySelector('.process-evidence-viewer')) return;

    const links = Array.from(
      gallery.querySelectorAll('.process-evidence-grid a[href]')
    );
    if (links.length !== 7) return;

    const dialog = document.createElement('dialog');
    dialog.className = 'process-evidence-viewer';
    dialog.setAttribute('aria-label', 'Process Log evidence image');
    dialog.innerHTML =
      '<button type="button" data-process-action="close" aria-label="Close image">×</button>' +
      '<button type="button" data-process-action="previous" aria-label="Previous image">‹</button>' +
      '<figure><img alt=""><figcaption></figcaption></figure>' +
      '<button type="button" data-process-action="next" aria-label="Next image">›</button>';
    document.body.appendChild(dialog);

    const image = dialog.querySelector('img');
    const caption = dialog.querySelector('figcaption');
    let index = 0;

    function show(next) {
      index = (next + links.length) % links.length;
      const link = links[index];
      image.src = link.href;
      image.alt = link.querySelector('img').alt;
      caption.textContent =
        link.closest('figure').querySelector('figcaption').textContent;
    }

    gallery.addEventListener('click', event => {
      const link = event.target.closest('.process-evidence-grid a[href]');
      const target = links.indexOf(link);
      if (target === -1) return;
      event.preventDefault();
      show(target);
      dialog.showModal();
    });

    dialog.addEventListener('click', event => {
      const button = event.target.closest('button[data-process-action]');
      if (button) {
        const action = button.dataset.processAction;
        if (action === 'close') dialog.close();
        if (action === 'previous') show(index - 1);
        if (action === 'next') show(index + 1);
      } else if (event.target === dialog) {
        dialog.close();
      }
    });

    dialog.addEventListener('keydown', event => {
      if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
      event.preventDefault();
      show(index + (event.key === 'ArrowRight' ? 1 : -1));
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, {once: true});
  } else {
    init();
  }
})();
