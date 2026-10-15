// Filtros puros para manter o mesmo recorte nas três visualizações.
function filterDeals(deals, { agent = '', manager = '', region = '', query = '' } = {}) {
  const needle = String(query).trim().toLocaleLowerCase('pt-BR');
  return deals.filter(deal =>
    (!agent || deal.agent === agent) &&
    (!manager || deal.manager === manager) &&
    (!region || deal.region === region) &&
    (!needle || [deal.id, deal.account, deal.product].some(value =>
      String(value ?? '').toLocaleLowerCase('pt-BR').includes(needle)))
  );
}

if (typeof module !== 'undefined') module.exports = { filterDeals };
