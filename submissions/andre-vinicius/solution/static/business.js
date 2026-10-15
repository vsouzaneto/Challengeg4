// Agrupamentos da carteira aberta. Valores monetários aqui são preço de catálogo, não receita.
function groupDeals(deals, field) {
  const groups = new Map();
  for (const deal of deals) {
    const key = deal[field] || 'Não informado';
    if (!groups.has(key)) groups.set(key, { name: key, deals: [], queues: { Avançar: 0, Revisar: 0, Qualificar: 0 }, priceTotal: 0 });
    const group = groups.get(key);
    group.deals.push(deal);
    group.queues[deal.queue] = (group.queues[deal.queue] || 0) + 1;
    group.priceTotal += Number(deal.catalog_price) || 0;
  }
  return [...groups.values()].sort((a, b) => b.deals.length - a.deals.length || a.name.localeCompare(b.name, 'pt-BR'));
}

function priceBands(deals) {
  const bands = [
    { label: 'Até US$ 999', min: 0, max: 1000 },
    { label: 'US$ 1.000 a 3.999', min: 1000, max: 4000 },
    { label: 'US$ 4.000 ou mais', min: 4000, max: Infinity },
  ];
  return bands.map(band => ({ ...band, deals: deals.filter(deal => Number(deal.catalog_price) >= band.min && Number(deal.catalog_price) < band.max) }));
}

function sellerProfile(deals, name) {
  const own = deals.filter(deal => (deal.agent || 'Não informado') === name);
  const counts = field => groupDeals(own, field);
  return { name, deals: own, manager: counts('manager')[0]?.name || 'Não informado', region: counts('region')[0]?.name || 'Não informado' };
}

function regionSummary(deals, region, seller = '') {
  const regional = deals.filter(deal => (deal.region || 'Não informado') === region);
  return { region, deals: regional, sellers: groupDeals(regional, 'agent'), selected: seller ? regional.filter(deal => deal.agent === seller) : regional };
}

function avatarInitials(name) {
  return String(name || '?').trim().split(/\s+/).slice(0, 2).map(part => part[0]?.toLocaleUpperCase('pt-BR') || '').join('');
}

if (typeof module !== 'undefined') module.exports = { groupDeals, priceBands, sellerProfile, regionSummary, avatarInitials };
