const assert = require('node:assert/strict');
const test = require('node:test');
const { groupDeals, priceBands, sellerProfile, regionSummary, avatarInitials } = require('../static/business.js');
const { readAnnotations, saveAnnotation } = require('../static/annotations.js');

const deals = [
  { id: 'A', agent: 'Ana', manager: 'Lia', region: 'Sul', queue: 'Avançar', priority: 85, catalog_price: 999 },
  { id: 'B', agent: 'Beto', manager: 'Lia', region: 'Norte', queue: 'Revisar', priority: 70, catalog_price: 1000 },
  { id: 'C', agent: 'Ana', manager: 'Lia', region: 'Sul', queue: 'Qualificar', priority: 55, catalog_price: 4000 },
];

test('painéis agrupam a mesma carteira sem mudar ordem nem índice', () => {
  const original = structuredClone(deals);
  const sellers = groupDeals(deals, 'agent');
  assert.equal(sellers[0].name, 'Ana');
  assert.deepEqual(sellers[0].deals.map(deal => deal.id), ['A', 'C']);
  assert.deepEqual(sellers[0].queues, { Avançar: 1, Revisar: 0, Qualificar: 1 });
  assert.equal(sellers[0].priceTotal, 4999);
  assert.equal(groupDeals(deals, 'manager')[0].deals.length, 3);
  assert.equal(groupDeals(deals, 'region')[0].deals.length, 2);
  assert.deepEqual(deals, original);
});

test('faixas de preço não perdem itens nas fronteiras', () => {
  assert.deepEqual(priceBands(deals).map(band => band.deals.map(deal => deal.id)), [['A'], ['B'], ['C']]);
});

test('RG e mapa usam gerente, região e oportunidades do vendedor selecionado', () => {
  const original = structuredClone(deals);
  const ana = sellerProfile(deals, 'Ana');
  assert.equal(ana.manager, 'Lia');
  assert.equal(ana.region, 'Sul');
  assert.deepEqual(ana.deals.map(deal => deal.id), ['A', 'C']);
  const sul = regionSummary(deals, 'Sul', 'Ana');
  assert.deepEqual(sul.sellers.map(group => group.name), ['Ana']);
  assert.deepEqual(sul.selected.map(deal => deal.id), ['A', 'C']);
  assert.equal(regionSummary(deals, 'Norte', 'Ana').selected.length, 0);
  assert.equal(avatarInitials('Ana Maria'), 'AM');
  assert.deepEqual(deals, original);
});

test('status e anotação sobrevivem à releitura local, sem tocar no score', () => {
  const values = new Map();
  const storage = { getItem: key => values.get(key) || null, setItem: (key, value) => values.set(key, value) };
  const original = structuredClone(deals);
  assert.equal(saveAnnotation(storage, 'A', { status: 'andando', note: 'Contato amanhã' }), true);
  assert.deepEqual(readAnnotations(storage).A, { status: 'andando', note: 'Contato amanhã' });
  assert.equal(saveAnnotation(storage, 'A', { status: 'parado' }), true);
  assert.equal(readAnnotations(storage).A.note, 'Contato amanhã');
  assert.equal(saveAnnotation(storage, 'A', { status: '', note: '' }), true);
  assert.equal(readAnnotations(storage).A, undefined);
  assert.deepEqual(deals, original);
});

test('armazenamento inválido não quebra a leitura', () => {
  assert.deepEqual(readAnnotations({ getItem: () => '{' }), {});
  assert.equal(saveAnnotation({ getItem: () => null, setItem: () => { throw Error('sem espaço'); } }, 'A', { status: 'parado' }), false);
});
