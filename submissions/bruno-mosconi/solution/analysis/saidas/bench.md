# npm run bench

Núcleo (`src/core`) na data padrão, com os negócios multiplicados por k (cópias com ID novo; mesmos 35 vendedores e 7 produtos). Mediana de 5 rodadas depois de 1 de aquecimento, em milissegundos. Máquina: Apple M3 Pro, 11 núcleos; Node v22.23.2; Chromium 156.0.8078.4.

- **Tela:** o que o app calcula ao abrir a semana de um vendedor: curva, score de todos, a lista dele e a equipe do gestor.
- **Job:** o que um job diário calcularia: curva, score de todos e as listas dos 35 vendedores.
- **Foto:** os negócios em JSON, sem e com gzip.

| k | Negócios | Em andamento | Curva (Node) | Tela (Node) | Tela (Chromium) | Job (Node) | Job (Chromium) | Foto JSON | Foto gzip |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 8.800 | 1.589 | 1 | 2 | 2 | 9 | 6 | 1,3 MB | 0,2 MB |
| 10 | 88.000 | 15.890 | 10 | 18 | 13 | 62 | 54 | 13,2 MB | 1,6 MB |
| 100 | 880.000 | 158.900 | 112 | 216 | 143 | 690 | 616 | 133,3 MB | 16,6 MB |
