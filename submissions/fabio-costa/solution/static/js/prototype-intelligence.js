// BEGIN: prototype.intelligence
(() => {
  'use strict';

  const KEY = 'aimaster.prototype.operational-tickets.v1';

  const RULES = [
    {
      category: 'Billing',
      terms: ['billing', 'invoice', 'payment', 'refund', 'charge',
              'pagamento', 'cobranca', 'reembolso', 'fatura'],
      priority: 'High',
      response: 'Thank you for reporting the billing issue. We will review the available transaction information. Any refund or adjustment requires verification and authorization.'
    },
    {
      category: 'Technical',
      terms: ['technical', 'error', 'broken', 'failure', 'crash',
              'bug', 'not working', 'problem', 'problema', 'erro',
              'falha', 'nao funciona', 'defeito'],
      priority: 'Medium',
      response: 'Thank you for reporting this issue. Could you confirm when it started, which product or environment is affected, and any error messages? Please avoid sharing passwords or sensitive credentials.'
    },
    {
      category: 'Access',
      terms: ['login', 'access', 'account locked', 'password',
              'acesso', 'senha', 'conta bloqueada'],
      priority: 'High',
      response: 'We can help investigate the access problem. Please describe the error and affected account without sharing passwords, security codes or recovery tokens.'
    },
    {
      category: 'Product',
      terms: ['feature', 'product', 'setup', 'installation',
              'configuration', 'produto', 'instalacao', 'recurso'],
      priority: 'Low',
      response: 'Thank you for contacting support. Please tell us which product or feature you are using and what result you expected, so we can determine the next step.'
    }
  ];

  const STOP = new Set([
    'the', 'and', 'for', 'with', 'that', 'this', 'from',
    'have', 'your', 'about', 'ticket', 'test', 'please',
    'uma', 'para', 'com', 'que', 'por', 'dos', 'das',
    'esse', 'essa', 'sobre', 'teste', 'cliente'
  ]);

  function el(tag, value, cls) {
    const item = document.createElement(tag);
    if (value != null) item.textContent = value;
    if (cls) item.className = cls;
    return item;
  }

  function tokens(value) {
    return new Set(
      String(value || '').toLowerCase()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .split(/[^a-z0-9]+/)
        .filter(word => word.length > 3 && !STOP.has(word))
    );
  }

  function readTickets() {
    try {
      const raw = localStorage.getItem(KEY);
      const data = raw === null ? [] : JSON.parse(raw);

      if (
        !Array.isArray(data) ||
        data.length > 500 ||
        data.some(t =>
          !t ||
          typeof t.id !== 'string' ||
          typeof t.subject !== 'string' ||
          t.source !== 'Local prototype'
        ) ||
        new Set(data.map(t => t.id)).size !== data.length
      ) return null;

      return data;
    } catch (_) {
      return null;
    }
  }

  function analyze(ticket, records) {
    const text = [
      ticket.subject || '',
      ticket.description || '',
      ticket.type || '',
      ticket.ticketType || ''
    ].join(' ').toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '');

    const found = RULES.map(rule => ({
      rule,
      matches: rule.terms.filter(term => text.includes(term))
    })).filter(candidate => candidate.matches.length);

    found.sort((a, b) => b.matches.length - a.matches.length);

    const winner = found[0];
    const ambiguous =
      found.length > 1 &&
      found[0].matches.length === found[1].matches.length;

    const evidence = winner && !ambiguous
      ? 'Matched terms: ' + winner.matches.join(', ')
      : 'No sufficiently distinctive classification evidence.';

    let priority = null;

    // Suggest critical only when explicit operational severity
    // is present. A ticket title saying "Critical" alone is not
    // sufficient evidence of real-world impact.
    const urgent = [
      'outage', 'system down', 'data loss',
      'security breach', 'indisponibilidade',
      'perda de dados', 'vazamento de dados'
    ];

    if (urgent.some(term => text.includes(term))) {
      priority = 'Critical';
    } else if (winner && !ambiguous) {
      priority = winner.rule.priority;
    }

    const baseTokens = tokens(
      (ticket.subject || '') + ' ' + (ticket.description || '')
    );

    const similar = [];

    for (const other of records) {
      if (other.id === ticket.id) continue;

      const compare = tokens(
        (other.subject || '') + ' ' + (other.description || '')
      );

      if (!baseTokens.size || !compare.size) continue;

      let common = 0;
      for (const word of baseTokens) {
        if (compare.has(word)) common++;
      }

      if (common < 2) continue;

      const score = common / (
        baseTokens.size + compare.size - common
      );

      if (score >= 0.25) {
        similar.push({
          id: other.id,
          subject: other.subject || 'Untitled',
          overlap: common,
          score
        });
      }
    }

    similar.sort((a, b) => b.score - a.score);

    return {
      category: winner && !ambiguous
        ? winner.rule.category
        : null,
      evidence,
      priority,
      response: winner && !ambiguous
        ? winner.rule.response
        : null,
      similar: similar.slice(0, 3),
      sampleSize: records.length
    };
  }

  function init() {
    const list = document.getElementById('pc-create-list');
    if (!list || list.dataset.intelligenceReady === 'true') return;

    list.dataset.intelligenceReady = 'true';

    function decorate(card, ticket, records) {
      const management = card.querySelector(
        '.pc-create-management[data-ticket-id]'
      );

      if (!management ||
          management.querySelector('.pc-intelligence')) return;

      const analysis = analyze(ticket, records);

      const panel = el('details', null, 'pc-intelligence');
      panel.append(
        el('summary', 'AI-assisted guidance · Review suggestions')
      );

      const body = el('div', null, 'pc-intelligence-body');

      body.append(
        el('p',
          'Rule-based prototype · No connected LLM · No automatic decisions',
          'pc-intelligence-disclaimer'
        )
      );

      const category = analysis.category || 'Insufficient evidence';

      body.append(
        el('h4', 'Suggested classification'),
        el('p', category),
        el('p', analysis.evidence, 'pc-intelligence-evidence')
      );

      body.append(
        el('h4', 'Priority recommendation'),
        el(
          'p',
          analysis.priority
            ? analysis.priority +
              ' · Proposal only; verify business impact before saving.'
            : 'Insufficient evidence to recommend priority.'
        )
      );

      if (analysis.priority && ticket.status !== 'Closed') {
        const apply = el(
          'button',
          'Use suggested priority in form',
          'pc-intelligence-action'
        );
        apply.type = 'button';

        const feedback = el('span', '', 'pc-intelligence-feedback');

        apply.addEventListener('click', () => {
          const select = management.querySelector(
            '[data-field="priority"]'
          );

          if (!select || select.disabled) {
            feedback.textContent = 'Priority field unavailable.';
            return;
          }

          select.value = analysis.priority;
          feedback.textContent =
            'Form updated. Save changes / note to confirm.';
        });

        body.append(apply, feedback);
      }

      body.append(el('h4', 'Suggested customer reply'));

      const draft = el('textarea', null, 'pc-intelligence-draft');
      draft.rows = 4;
      draft.maxLength = 3000;
      draft.placeholder = 'No grounded response available.';

      if (analysis.response) {
        draft.value = analysis.response;
      }

      body.append(draft);

      const copy = el(
        'button',
        'Copy reviewed response',
        'pc-intelligence-action'
      );
      copy.type = 'button';

      const copyMessage = el(
        'span', '', 'pc-intelligence-feedback'
      );

      copy.addEventListener('click', async () => {
        if (!draft.value.trim()) {
          copyMessage.textContent = 'No response to copy.';
          return;
        }

        try {
          await navigator.clipboard.writeText(draft.value);
          copyMessage.textContent =
            'Copied. No message has been sent.';
        } catch (_) {
          draft.focus();
          draft.select();
          copyMessage.textContent =
            'Select and copy manually. No message was sent.';
        }
      });

      body.append(copy, copyMessage);

      body.append(el('h4', 'Similar operational tickets'));

      if (analysis.similar.length) {
        const ul = el('ul');

        for (const match of analysis.similar) {
          ul.append(
            el(
              'li',
              match.subject + ' · ' + match.id +
              ' · ' + match.overlap + ' shared terms'
            )
          );
        }

        body.append(ul);
      } else {
        body.append(el(
          'p',
          'No sufficiently similar local ticket found among ' +
          analysis.sampleSize + ' operational records.'
        ));
      }

      body.append(el(
        'p',
        'Evidence boundary: suggestions use ticket text and ' +
        'locally created records only. Historical Dataset 1 and ' +
        'Dataset 2 have not been used by this component.',
        'pc-intelligence-evidence'
      ));

      panel.append(body);
      management.append(panel);

      // OWNER: prototype.intelligence.quick-actions
      // BEGIN: prototype.intelligence.quick-actions
      // Expose existing tools at the beginning of each ticket.
      // No duplicated panels or lifecycle handlers.
      const quickActions = el(
        'div',
        null,
        'pc-ticket-quick-actions'
      );

      const aiButton = el(
        'button',
        'AI Assistance',
        'pc-ticket-quick-ai'
      );
      aiButton.type = 'button';
      aiButton.setAttribute('aria-expanded', 'false');

      const toolsButton = el(
        'button',
        'Operator Tools',
        'pc-ticket-quick-tools'
      );
      toolsButton.type = 'button';
      toolsButton.setAttribute('aria-expanded', 'false');

      function openExistingPanel(selector, button) {
        const target = management.querySelector(selector);

        if (!target) return;

        target.open = true;
        button.setAttribute('aria-expanded', 'true');

        // Expand only when requested, keeping the existing panel.
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'nearest'
        });
      }

      aiButton.addEventListener('click', () => {
        openExistingPanel('.pc-intelligence', aiButton);
      });

      toolsButton.addEventListener('click', () => {
        openExistingPanel(
          '.pc-productivity-detail',
          toolsButton
        );
      });

      quickActions.append(aiButton, toolsButton);
      management.before(quickActions);
      // END: prototype.intelligence.quick-actions
    }

    function sync() {
      const tickets = readTickets();
      if (!tickets) return;

      const byId = new Map(tickets.map(ticket => [
        ticket.id, ticket
      ]));

      for (const card of Array.from(list.children)) {
        const management = card.querySelector(
          '.pc-create-management[data-ticket-id]'
        );

        if (!management) continue;

        const ticket = byId.get(management.dataset.ticketId);

        if (ticket) decorate(card, ticket, tickets);
      }
    }

    // Observe only direct card additions and replacements.
    // Never write to or alter the lifecycle storage owner.
    let scheduled = false;

    const observer = new MutationObserver(() => {
      if (scheduled) return;
      scheduled = true;

      queueMicrotask(() => {
        scheduled = false;
        sync();
      });
    });

    observer.observe(list, { childList: true });

    window.addEventListener('storage', event => {
      if (event.key === KEY) sync();
    });

    sync();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, { once: true });
  } else {
    init();
  }
})();
// END: prototype.intelligence

// BEGIN: prototype.intelligence.historical-loader
(() => {
  const script = document.createElement('script');
  script.src = '/static/js/prototype-historical-evidence.js?v=176719f01a57b941';
  script.defer = true;
  document.head.append(script);
})();
// END: prototype.intelligence.historical-loader

// BEGIN: prototype.intelligence.modal-loader
(() => {
  const script = document.createElement('script');
  script.src = '/static/js/prototype-modal-assistance.js?v=58fc323d30c3cd63';
  script.defer = true;
  document.head.append(script);
})();
// END: prototype.intelligence.modal-loader

// BEGIN: prototype.intelligence.inbox-loader
(() => {
  const script = document.createElement('script');
  script.src = '/static/js/prototype-inbox-assistance.js?v=dae4fb770431cb21';
  script.defer = true;
  document.head.append(script);
})();
// END: prototype.intelligence.inbox-loader

// BEGIN: prototype.automation.selective.loader
(() => {
  const script = document.createElement('script');
  script.src =
    '/static/js/prototype-selective-automation.js?v=ab0886e244d9a48b';
  script.defer = true;
  document.head.append(script);
})();
// END: prototype.automation.selective.loader

// BEGIN: prototype.automation.monitoring.loader
(() => {
  const script = document.createElement('script');
  script.src =
    '/static/js/prototype-automation-monitoring.js?v=c95c455ce9764da1';
  script.defer = true;
  document.head.append(script);
})();
// END: prototype.automation.monitoring.loader
