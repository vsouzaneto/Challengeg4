(function () {
  'use strict';
  var lang = window.AIMASTER_I18N_LANG || 'en';
  var catalog = window.AIMASTER_I18N_CATALOG || {};
  var active = lang === 'pt-BR';
  var protectedSelector = [
    '#explorer-table-wrap', '#automation-d2-table-wrap',
    '#pc-ticket-list', '#pc-ticket-detail-content', '#pc-create-list',
    '.raw-table-wrap', '[contenteditable="true"]',
    'script', 'style', 'code', 'pre', 'textarea'
  ].join(',');
  var prefixes = [];
  var chunks = [];
  var scheduled = false;
  var queued = [];

  function translate(input) {
    if (!active || typeof input !== 'string') return input;
    var match = /^(\s*)([\s\S]*?)(\s*)$/.exec(input);
    if (!match) return input;
    var core = match[2];
    if (!core) return input;
    var output = Object.prototype.hasOwnProperty.call(catalog, core)
      ? catalog[core] : core;
    if (output === core && core.indexOf(' leads stalled channel volume;') !== -1) {
      var text = core.replace(/\s+/g, ' ').trim();
      var flow = /^(.+?) leads stalled channel volume; (.+?) has the highest channel rate\. (.+?) leads priority volume; (.+?) has the highest priority rate\.$/.exec(text);
      var template = '{channel_volume} leads stalled channel volume; {channel_rate} has the highest channel rate. {priority_volume} leads priority volume; {priority_rate} has the highest priority rate.';
      if (flow && Object.prototype.hasOwnProperty.call(catalog, template)) {
        output = catalog[template];
        ['channel_volume', 'channel_rate', 'priority_volume', 'priority_rate'].forEach(function (name, i) {
          output = output.replace('{' + name + '}', translate(flow[i + 1]));
        });
      }
    }
    if (output === core) {
      for (var i = 0; i < prefixes.length; i++) {
        var entry = prefixes[i];
        if (core.indexOf(entry[0]) === 0 && core.length > entry[0].length) {
          output = entry[1] + core.slice(entry[0].length);
          break;
        }
      }
    }
    if (output === core && core.length > 42) {
      for (var j = 0; j < chunks.length; j++) {
        var part = chunks[j];
        if (output.indexOf(part[0]) !== -1) {
          output = output.replace(part[0], part[1]);
        }
      }
    }
    return match[1] + output + match[3];
  }

  function isProtected(element) {
    return !!(element && element.closest && element.closest(protectedSelector));
  }

  function localize(element) {
    if (!element || element.nodeType !== 1 || isProtected(element)) return;
    var iterator = document.createTreeWalker(element, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT);
    var node = element;
    while (node) {
      if (node.nodeType === 3) {
        if (!isProtected(node.parentElement)) {
          var replacement = translate(node.nodeValue);
          if (replacement !== node.nodeValue) node.nodeValue = replacement;
        }
      } else if (node.nodeType === 1 && !isProtected(node)) {
        ['placeholder', 'title', 'aria-label'].forEach(function (attr) {
          if (node.hasAttribute(attr)) {
            var before = node.getAttribute(attr);
            var after = translate(before);
            if (before !== after) node.setAttribute(attr, after);
          }
        });
      }
      node = iterator.nextNode();
    }
  }

  function flush() {
    scheduled = false;
    var candidates = queued;
    queued = [];
    candidates.forEach(function (node) {
      if (node.nodeType === 3) {
        if (!isProtected(node.parentElement)) {
          var next = translate(node.nodeValue);
          if (next !== node.nodeValue) node.nodeValue = next;
        }
      } else if (node.nodeType === 1) {
        localize(node);
      }
    });
  }
  function enqueue(node) {
    queued.push(node);
    if (!scheduled) {
      scheduled = true;
      window.requestAnimationFrame(flush);
    }
  }

  function initFlags() {
    document.querySelectorAll('.brand-languages a[data-ai-locale]').forEach(function (link) {
      link.addEventListener('click', function (event) {
        var hash = window.location.hash;
        if (hash) {
          event.preventDefault();
          window.location.assign(link.href.split('#')[0] + hash);
        }
      });
    });
  }

  function init() {
    initFlags();
    if (!active) return;
    prefixes = Object.keys(catalog).filter(function (key) {
      return /[:：]$/.test(key) && key.length > 7;
    }).sort(function (a, b) { return b.length - a.length; }).map(function (key) {
      return [key, catalog[key]];
    });
    chunks = Object.keys(catalog).filter(function (key) {
      return key.length >= 36 && key.length <= 180 && key.indexOf('<') === -1;
    }).sort(function (a, b) { return b.length - a.length; }).map(function (key) {
      return [key, catalog[key]];
    });
    localize(document.body);
    new MutationObserver(function (mutations) {
      mutations.forEach(function (mutation) {
        if (mutation.type === 'characterData') enqueue(mutation.target);
        else mutation.addedNodes.forEach(enqueue);
      });
    }).observe(document.body, {subtree: true, childList: true, characterData: true});
    if (window.Chart && typeof window.Chart.register === 'function') {
      window.Chart.register({
        id: 'aimaster-pt-br',
        beforeUpdate: function (chart) {
          if (chart.data && Array.isArray(chart.data.labels)) {
            chart.data.labels = chart.data.labels.map(translate);
          }
          if (chart.data && Array.isArray(chart.data.datasets)) {
            chart.data.datasets.forEach(function (dataset) {
              if (typeof dataset.label === 'string') dataset.label = translate(dataset.label);
            });
          }
        }
      });
    }
  }
  window.aiMasterTranslate = translate;
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
}());
