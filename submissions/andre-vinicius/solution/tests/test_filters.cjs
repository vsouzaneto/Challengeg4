const assert = require('node:assert/strict');
const test = require('node:test');
const { filterDeals } = require('../static/filter.js');

const deals = [
  { id: 'A-1', account: 'Árvore', product: 'GTX Pro', agent: 'Ana', manager: 'Lia', region: 'Sul' },
  { id: 'B-2', account: 'Bela', product: 'GTX Basic', agent: 'Beto', manager: 'Lia', region: 'Norte' },
  { id: 'C-3', account: 'Conta não informada', product: 'GTX Pro', agent: 'Ana', manager: 'Rui', region: 'Sul' },
];

test('vendedor, gerente e região combinam sem alterar a ordem da fila', () => {
  assert.deepEqual(filterDeals(deals, { agent: 'Ana', region: 'Sul' }).map(d => d.id), ['A-1', 'C-3']);
  assert.deepEqual(filterDeals(deals, { agent: 'Ana', manager: 'Lia', region: 'Sul' }).map(d => d.id), ['A-1']);
  assert.deepEqual(filterDeals(deals, { agent: 'Beto', region: 'Sul' }), []);
});

test('busca ignora maiúsculas, espaços e acentos preservados', () => {
  assert.deepEqual(filterDeals(deals, { query: '  ÁRV  ' }).map(d => d.id), ['A-1']);
  assert.deepEqual(filterDeals(deals, { query: 'b-2' }).map(d => d.id), ['B-2']);
  assert.deepEqual(filterDeals(deals, { query: 'gtx pro' }).map(d => d.id), ['A-1', 'C-3']);
});
