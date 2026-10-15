const $ = id => document.getElementById(id);
const formatCount = n => new Intl.NumberFormat('pt-BR').format(n);
const formatMoney = n => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(n);
const panelState = { deals: [], salesByAgent: {}, asOf: '' };
function el(parent, tag, cls, value) { const child = document.createElement(tag); if (cls) child.className = cls; if (value !== undefined) child.textContent = String(value); parent.append(child); return child; }
function link(parent, text, href, cls = '') { const child = el(parent, 'a', cls, text); child.href = href; return child; }
function queueText(group) { return `Avançar ${group.queues['Avançar'] || 0} · Revisar ${group.queues.Revisar || 0} · Qualificar ${group.queues.Qualificar || 0}`; }
function dealLink(params = {}) { return '/?' + new URLSearchParams(params).toString(); }
function card(parent, title, quantity, detail, href, metric) { const box = el(parent, 'article', 'business-card'); el(box, 'h3', '', title); el(box, 'strong', 'business-number', metric === undefined ? formatCount(quantity) : metric); el(box, 'p', '', detail); if (href) link(box, 'Abrir fila →', href, 'business-link'); return box; }
function sections() { const value = location.hash.replace('#', '').split('/')[0]; return ['vendedor', 'gerente', 'regiao', 'preco'].includes(value) ? value : 'gerente'; }
function selection() { try { return decodeURIComponent(location.hash.split('/').slice(1).join('/')); } catch { return ''; } }
function avatar(parent, name, size = '', role = 'seller') {
  const tone = [...name].reduce((sum, letter) => sum + letter.charCodeAt(0), 0) % 5;
  const art = el(parent, 'div', 'seller-avatar ' + size + ' avatar-tone-' + tone + (role === 'manager' ? ' manager-avatar' : ''));
  art.setAttribute('role', 'img'); art.setAttribute('aria-label', 'Avatar ilustrado de ' + name);
  el(art, 'span', 'avatar-head'); el(art, 'span', 'avatar-body');
  el(art, 'span', 'avatar-initials', avatarInitials(name));
  return art;
}
function managerHref(name) { return '#gerente/' + encodeURIComponent(name); }
function sellerHref(name) { return '#vendedor/' + encodeURIComponent(name); }
function mapHref(name) { return '#regiao/seller/' + encodeURIComponent(name); }
function sellerCard(parent, group) {
  const box = el(parent, 'article', 'business-card seller-id-card');
  const details = el(box, 'div', 'seller-id-copy');
  el(details, 'h3', '', group.name);
  el(details, 'strong', 'business-number', formatCount(group.deals.length));
  el(details, 'p', '', queueText(group));
  avatar(box, group.name, 'avatar-card');
  link(box, 'Ver vendedor →', sellerHref(group.name), 'seller-id-action');
  return box;
}
function queueCards(root, group, params) {
  const grid = el(root, 'div', 'business-grid');
  card(grid, 'Carteira aberta', group.deals.length, 'Oportunidades deste recorte', dealLink(params));
  for (const queue of ['Avançar', 'Revisar', 'Qualificar']) {
    card(grid, queue, group.queues[queue] || 0, 'Itens da fila operacional');
  }
}
function renderSeller(root) {
  const groups = groupDeals(panelState.deals, 'agent'); const selected = groups.find(group => group.name === selection());
  if (selected) {
    link(root, '← Todos os vendedores', '#vendedor', 'back-link');
    const profile = sellerProfile(panelState.deals, selected.name);
    const pair = el(root, 'div', 'identity-pair');
    const rg = el(pair, 'section', 'seller-rg');
    avatar(rg, selected.name, 'avatar-large');
    const identity = el(rg, 'div', 'rg-identity');
    el(identity, 'span', 'eyebrow', 'VENDEDOR · AVATAR ILUSTRADO');
    el(identity, 'h2', '', selected.name);
    el(identity, 'p', '', 'Região: ' + profile.region);
    el(identity, 'strong', '', formatCount(selected.deals.length) + ' oportunidades abertas');
    el(identity, 'span', 'rg-queues', queueText(selected));
    link(identity, 'Ver no mapa →', mapHref(selected.name), 'business-link');
    const manager = el(pair, 'section', 'seller-rg');
    avatar(manager, profile.manager, 'avatar-large', 'manager');
    const leader = el(manager, 'div', 'rg-identity');
    el(leader, 'span', 'eyebrow', 'GERENTE RESPONSÁVEL');
    el(leader, 'h2', '', profile.manager);
    el(leader, 'p', '', 'Equipe deste vendedor');
    link(leader, 'Ver gerente →', managerHref(profile.manager), 'business-link');
    el(root, 'p', 'business-intro', `${formatCount(selected.deals.length)} oportunidades abertas · ${queueText(selected)}`);
    const summary = el(root, 'div', 'business-grid'); card(summary, 'Fila deste vendedor', selected.deals.length, 'Ordenada pelo índice operacional', dealLink({ agent: selected.name }));
    card(summary, 'Preço de catálogo somado', selected.deals.length, 'Soma unitária; não representa vendas realizadas', '', formatMoney(selected.priceTotal));
    const sales = panelState.salesByAgent[selected.name] || { won: 0, lost: 0, won_value: 0 };
    el(root, 'h3', 'business-subhead', 'Vendas históricas deste vendedor');
    el(root, 'p', 'business-intro', 'Negócios fechados no conjunto histórico. Este resumo não participa do índice nem da fila aberta.');
    const history = el(root, 'div', 'business-grid');
    card(history, 'Vendas ganhas', sales.won, 'Oportunidades com desfecho Won');
    card(history, 'Valor fechado ganho', sales.won, 'Soma de close_value dos negócios ganhos, em USD', '', formatMoney(sales.won_value));
    card(history, 'Negócios perdidos', sales.lost, 'Oportunidades com desfecho Lost');
    const list = el(root, 'div', 'business-list'); el(list, 'h3', '', 'Primeiras oportunidades da fila');
    for (const deal of selected.deals.slice(0, 12)) { const row = el(list, 'div', 'business-row'); el(row, 'strong', '', deal.account || 'Conta não informada'); el(row, 'span', '', `${deal.product} · ${deal.queue} · ${deal.priority}/100`); }
    link(root, 'Ver toda a fila deste vendedor →', dealLink({ agent: selected.name }), 'business-link'); return;
  }
  el(root, 'h2', '', 'Vendedores'); el(root, 'p', 'business-intro', 'Abra uma página individual para ver a fila e o contexto de cada vendedor.');
  const grid = el(root, 'div', 'business-grid');
  for (const group of groups) sellerCard(grid, group);
}
function managerCard(parent, group) {
  const box = el(parent, 'article', 'business-card seller-id-card');
  const details = el(box, 'div', 'seller-id-copy');
  el(details, 'h3', '', group.name);
  el(details, 'strong', 'business-number', formatCount(group.deals.length));
  el(details, 'p', '', groupDeals(group.deals, 'agent').length + ' vendedores · ' + queueText(group));
  avatar(box, group.name, 'avatar-card', 'manager');
  link(box, 'Ver gerente →', managerHref(group.name), 'seller-id-action');
  return box;
}
function renderManager(root) {
  const groups = groupDeals(panelState.deals, 'manager'); const selected = groups.find(group => group.name === selection());
  if (selected) {
    link(root, '← Todos os gerentes', '#gerente', 'back-link');
    const profile = el(root, 'section', 'seller-rg');
    avatar(profile, selected.name, 'avatar-large', 'manager');
    const identity = el(profile, 'div', 'rg-identity');
    el(identity, 'span', 'eyebrow', 'DETALHES DO GERENTE · AVATAR ILUSTRADO');
    el(identity, 'h2', '', selected.name);
    el(identity, 'p', '', groupDeals(selected.deals, 'agent').length + ' vendedores na equipe');
    el(identity, 'strong', '', formatCount(selected.deals.length) + ' oportunidades abertas');
    el(identity, 'span', 'rg-queues', queueText(selected));
    queueCards(root, selected, { manager: selected.name });
    el(root, 'h3', 'business-subhead', 'Equipe'); const grid = el(root, 'div', 'business-grid');
    for (const seller of groupDeals(selected.deals, 'agent')) sellerCard(grid, seller);
    return;
  }
  el(root, 'h2', '', 'Gerentes e equipes'); el(root, 'p', 'business-intro', 'Selecione um gerente para ver a carteira e os vendedores da equipe.');
  const grid = el(root, 'div', 'business-grid'); for (const group of groups) managerCard(grid, group);
}
function renderRegion(root) {
  el(root, 'h2', '', 'Mapa de regiões');
  el(root, 'p', 'business-intro', 'Mapa ilustrativo. Formas e posições representam agrupamentos da base, sem coordenadas reais.');
  const groups = groupDeals(panelState.deals, 'region');
  const parts = location.hash.split('/');
  let value = ''; try { value = decodeURIComponent(parts.slice(2).join('/')); } catch {}
  const seller = parts[1] === 'seller' && groupDeals(panelState.deals, 'agent').some(group => group.name === value) ? value : '';
  const sellerRegion = seller ? sellerProfile(panelState.deals, seller).region : '';
  const region = sellerRegion || (parts[1] === 'region' && groups.some(group => group.name === value) ? value : '');
  const controls = el(root, 'div', 'map-controls');
  const regionLabel = el(controls, 'label', '', 'Escolher região');
  const regionSelect = el(regionLabel, 'select'); regionSelect.setAttribute('aria-label', 'Escolher região');
  const allRegions = el(regionSelect, 'option', '', 'Selecione uma região'); allRegions.value = '';
  for (const group of groups) { const option = el(regionSelect, 'option', '', group.name); option.value = group.name; }
  regionSelect.value = region;
  regionSelect.addEventListener('change', () => { location.hash = regionSelect.value ? '#regiao/region/' + encodeURIComponent(regionSelect.value) : '#regiao'; });
  if (region) {
    const sellerLabel = el(controls, 'label', '', 'Vendedor da região');
    const sellerSelect = el(sellerLabel, 'select'); sellerSelect.setAttribute('aria-label', 'Selecionar vendedor no mapa');
    const all = el(sellerSelect, 'option', '', 'Todos os vendedores'); all.value = '';
    const current = regionSummary(panelState.deals, region, seller);
    for (const person of current.sellers) { const option = el(sellerSelect, 'option', '', person.name); option.value = person.name; }
    sellerSelect.value = seller;
    sellerSelect.addEventListener('change', () => { location.hash = sellerSelect.value ? mapHref(sellerSelect.value) : '#regiao/region/' + encodeURIComponent(region); });
  }
  const layout = el(root, 'div', 'map-layout');
  const mapBox = el(layout, 'div', 'map-box' + (region ? ' map-region-detail' : ''));
  el(mapBox, 'span', 'map-stamp', 'MAPA ILUSTRATIVO · SEM COORDENADAS REAIS');
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('viewBox', '0 0 720 420'); svg.setAttribute('role', 'img');
  svg.setAttribute('aria-label', region ? 'Mapa ampliado da região ' + region : 'Mapa ilustrativo das três regiões');
  mapBox.append(svg);
  function node(tag, attrs, content, parent = svg) { const item = document.createElementNS('http://www.w3.org/2000/svg', tag); for (const [key,val] of Object.entries(attrs)) item.setAttribute(key,String(val)); if (content !== undefined) item.textContent = content; parent.append(item); return item; }
  const shapes = [
    'M42 85 Q115 22 249 45 Q330 59 376 141 Q338 231 239 248 Q91 240 42 177 Z',
    'M280 70 Q403 21 558 64 Q666 91 676 185 Q610 250 464 258 Q349 235 280 153 Z',
    'M154 224 Q260 175 375 205 Q473 185 568 242 Q618 324 537 381 Q322 400 169 364 Q93 300 154 224 Z'
  ];
  const centers = [[175,143],[502,145],[350,306]];
  if (!region) {
    groups.forEach((group,index) => {
      const path = node('path', {d: shapes[index],class:'map-region',tabindex:'0',role:'button','aria-label':'Abrir região '+group.name});
      const go = () => { location.hash = '#regiao/region/' + encodeURIComponent(group.name); };
      path.addEventListener('click',go); path.addEventListener('keydown',event => { if(event.key==='Enter'||event.key===' '){event.preventDefault();go();} });
      const [x,y] = centers[index];
      node('text',{x,y:y-9,class:'map-region-name','text-anchor':'middle'},group.name);
      node('text',{x,y:y+18,class:'map-region-count','text-anchor':'middle'},formatCount(group.deals.length)+' oportunidades');
    });
  } else {
    node('path',{d:'M75 71 Q276 12 563 65 Q664 119 645 263 Q608 379 379 391 Q180 376 75 294 Q24 173 75 71 Z',class:'map-region-outline'});
    node('text',{x:360,y:92,class:'map-region-name','text-anchor':'middle'},region);
    const current = regionSummary(panelState.deals,region,seller);
    current.sellers.forEach((person,index) => {
      const columns = 4, col = index % columns, row = Math.floor(index / columns);
      const x = 150 + col*138 + (row%2)*18, y = 122 + row*76;
      const marker = node('circle',{cx:x,cy:y,r:person.name===seller?14:11,class:'map-seller'+(person.name===seller?' active':''),tabindex:'0',role:'button','aria-label':'Selecionar '+person.name});
      const go = () => { location.hash = mapHref(person.name); };
      marker.addEventListener('click',go); marker.addEventListener('keydown',event => {if(event.key==='Enter'||event.key===' '){event.preventDefault();go();}});
      node('text',{x,y:y+32,class:'map-region-count','text-anchor':'middle'},person.name.split(' ')[0]);
    });
  }
  const side = el(layout, 'section', 'map-side');
  el(side, 'span', 'eyebrow', region ? 'REGIÃO SELECIONADA' : 'ESCOLHA UMA REGIÃO');
  el(side, 'h3', '', region || 'Visão geral');
  if (!region) el(side, 'p', 'business-intro map-overview-copy', 'Selecione uma área do mapa ou use o menu para abrir seus vendedores e oportunidades.');
  else { const current = regionSummary(panelState.deals,region,seller); el(side, 'p', 'business-intro',formatCount(current.deals.length)+' oportunidades · '+current.sellers.length+' vendedores'); }
  const max = Math.max(...groups.map(group => group.deals.length),1);
  for (const group of groups) {
    const row = el(side,'a','map-region-row'+(group.name===region?' active':''));
    row.href='#regiao/region/'+encodeURIComponent(group.name);
    el(row,'strong','',group.name); el(row,'span','',formatCount(group.deals.length));
    const track=el(row,'span','region-track'); el(track,'span','region-bar').style.width=(group.deals.length/max*100)+'%';
  }
  if (!region) return;
  const current = regionSummary(panelState.deals,region,seller);
  el(root,'h3','business-subhead',seller?'Vendedor no mapa: '+seller:'Vendedores da região');
  const people=el(root,'div','map-people');
  for(const person of current.sellers){const row=el(people,'div','map-person'+(seller===person.name?' selected':'')); avatar(row,person.name); const copy=el(row,'div'); el(copy,'strong','',person.name); el(copy,'span','',formatCount(person.deals.length)+' oportunidades · '+queueText(person)); link(row,seller===person.name?'Ver vendedor →':'Ver no mapa →',seller===person.name?sellerHref(person.name):mapHref(person.name),'business-link');}
  if(seller){el(root,'h3','business-subhead','Oportunidades deste vendedor'); const list=el(root,'div','business-list'); for(const deal of current.selected.slice(0,12)){const row=el(list,'div','business-row');el(row,'strong','',deal.account||'Conta não informada');el(row,'span','',deal.product+' · '+deal.queue+' · '+deal.priority+'/100');}link(root,'Abrir toda a fila →',dealLink({agent:seller}),'business-link');}
  else link(root,'Abrir fila da região →',dealLink({region}),'business-link');
}
function renderPrice(root) {
  el(root, 'h2', '', 'Preços de catálogo'); el(root, 'p', 'business-intro', 'Distribuição das oportunidades abertas pelo preço do produto. A soma dos preços não é receita potencial ou realizada.');
  const values = panelState.deals.map(deal => Number(deal.catalog_price)).filter(Number.isFinite).sort((a, b) => a - b);
  const grid = el(root, 'div', 'business-grid'); card(grid, 'Oportunidades', panelState.deals.length, 'Somente negócios abertos');
  const middle = Math.floor(values.length / 2);
  const median = values.length ? (values[middle] + values[Math.floor((values.length - 1) / 2)]) / 2 : 0;
  card(grid, 'Preço mediano', values.length, 'Preço unitário do produto, em USD', '', formatMoney(median));
  const bands = priceBands(panelState.deals); const max = Math.max(...bands.map(band => band.deals.length), 1);
  const list = el(root, 'div', 'price-bands'); for (const band of bands) { const row = el(list, 'div', 'price-band'); el(row, 'strong', '', band.label); const track = el(row, 'div', 'region-track'); el(track, 'div', 'region-bar').style.width = `${band.deals.length / max * 100}%`; el(row, 'span', '', `${formatCount(band.deals.length)} oportunidades`); }
}
function render() {
  const current = sections(); for (const tab of document.querySelectorAll('[data-panel]')) { const active = tab.dataset.panel === current; tab.classList.toggle('active', active); if (active) tab.setAttribute('aria-current', 'page'); else tab.removeAttribute('aria-current'); }
  const root = $('panel-content'); root.replaceChildren(); if (!panelState.deals.length) { el(root, 'p', '', 'Não há oportunidades abertas para mostrar.'); return; }
  ({ vendedor: renderSeller, gerente: renderManager, regiao: renderRegion, preco: renderPrice })[current](root);
}
window.addEventListener('hashchange', render);
fetch('/api/deals').then(response => { if (!response.ok) throw Error(`HTTP ${response.status}`); return response.json(); }).then(data => { panelState.deals = data.deals; panelState.salesByAgent = data.sales_by_agent || {}; panelState.asOf = data.as_of; $('snapshot').textContent = `Referência histórica: ${data.as_of.split('-').reverse().join('/')}`; render(); }).catch(error => { $('snapshot').textContent = 'Dados indisponíveis'; $('panel-content').textContent = `Não foi possível carregar os painéis: ${error.message}`; });
