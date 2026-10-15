(function () {
  const icons = { home: '📋', panels: '📊', method: '🎯', docs: '📚' };
  const panelIcons = { gerente: '🧑‍💼', vendedor: '🧑‍💻', regiao: '🗺️', preco: '💲' };

  document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.querySelector('.sidebar');
    if (!sidebar) return;

    const links = [
      ['a[href="/"]:not(.brand)', 'home'],
      ['a[href^="/panels.html"]:not(.brand)', 'panels'],
      ['a[href="/method.html"]', 'method'],
      ['a[href="/documentation.html"]', 'docs']
    ];
    links.forEach(([selector, name]) => {
      const link = sidebar.querySelector(selector);
      if (!link) return;
      const label = link.querySelector('span');
      if (!label) return;
      const icon = document.createElement('i');
      icon.setAttribute('aria-hidden', 'true');
      icon.setAttribute('class', 'nav-emoji');
      icon.textContent = icons[name];
      link.replaceChildren(icon, label);
    });

    const subnav = sidebar.querySelector('.sidebar-subnav');
    if (subnav && !subnav.querySelector('a[href="/panels.html#preco"]')) {
      const prices = document.createElement('a');
      prices.href = '/panels.html#preco';
      prices.textContent = 'Preços';
      prices.dataset.panel = 'preco';
      subnav.append(prices);
    }
    if (subnav) {
      subnav.querySelectorAll('a').forEach(link => {
        const section = link.hash.slice(1);
        const symbol = panelIcons[section];
        if (!symbol) return;
        const icon = document.createElement('i');
        icon.className = 'nav-emoji';
        icon.setAttribute('aria-hidden', 'true');
        icon.textContent = symbol;
        link.prepend(icon, ' ');
      });
    }
  });
})();
