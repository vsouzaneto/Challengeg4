# Protótipos da direção de arte (portão visual do incremento 4)

**Rodada 3 (D41–D43):** protótipo único em `rodada-3/`, com o README próprio. O que segue abaixo é a rodada 2, reprovada na D41.

## Rodada 2

Páginas estáticas com dados reais (Zane Levy e a equipe da Summer Sewald, nas 4 datas com histórico suficiente), feitas para o Bruno escolher a direção antes do código de produção (D38).

| Arquivo | O que é |
|---|---|
| `direcao-de-arte.html` | princípios, o que veio de cada referência, as duas fontes, cores, espaço, componentes e movimento |
| `variacao-a.html` | "Agenda": uma coluna; "Comece por estes" com 3 negócios grandes; o detalhe numa folha que desliza |
| `variacao-b.html` | "Mesa": lista à esquerda, com os 5 primeiros maiores; o motivo sempre aberto à direita |
| `prints/` | 1280 e 390 px, vendedor e gestor, painel aberto, modo escuro e fonte B |
| `videos/` | gravação do Playwright: troca de data, painel e entrada da equipe |
| `dados.js` | gerado por `cd solution && node scripts/prototipos.ts` |

Para abrir (as fontes não carregam por `file://`):

```sh
cd process-log/prototipos && python3 -m http.server 8765
```

Depois, `http://127.0.0.1:8765/variacao-a.html`. Opções no endereço: `?fonte=b` (Mona Sans), `?tema=escuro`, `#equipe`.

Fontes: Onest e Mona Sans, SIL OFL 1.1 (licenças em `fontes/`).
