# Anotações para a ENTREGA (GitHub)

Tudo o que precisa existir no dia do PR, e o que registrar desde já para não perder evidências.

## Estrutura da submissão
```
submissions/emerson-souza/
├── README.md                 ← template oficial (Sobre mim, Executive Summary, Solução, Process Log, Evidências)
├── solution/
│   ├── app/                  ← código do sistema (núcleo + 4 módulos)
│   ├── relatorios/           ← relatório de cada desafio (PDF + MD), gerados pelo sistema
│   └── capturas/             ← prints das telas principais
├── process-log/
│   ├── 00-diario.md          ← rodadas (já começou)
│   ├── screenshots/          ← prints de conversas com IA e do sistema rodando
│   └── chat-exports/         ← exports das conversas
└── docs/
    ├── como_rodar.md         ← setup: executável + código-fonte + gerar .exe
    ├── arquitetura.md        ← núcleo sozinho + cooperativo, contratos, cruzamentos
    ├── desafio-001.md … 004  ← lógica, achados e limitações de cada módulo
    └── qualidade_dos_dados.md
```
- **Executável:** Release no fork (o zip passa de 100 MB). Link no README.
- **Título do PR:** `[Submission] Emerson Souza — Challenges 001, 002, 003 e 004`.
- **Branch:** `submission/emerson-souza`.
- **Dados:** não subir os datasets grandes (vêm do Kaggle); explicar onde baixar e onde colocar. Avaliar se sobe só a RavenStack (pequena) para o "usar dados do desafio" funcionar direto.

## O README precisa responder, por desafio
| Bloco do template | Conteúdo |
|---|---|
| Executive Summary | 3–5 frases: o sistema único, o núcleo cooperativo, o principal achado de cada desafio (inclusive "os dados do 002/004 não têm sinal, e nós provamos") |
| Abordagem | Entender os dados antes → planejamento em `.md` → contratos → módulos → cruzamentos |
| Resultados / Findings | Uma seção por desafio, com números |
| Recomendações | Priorizadas, por desafio |
| Limitações | Por desafio + dos cruzamentos (selos) |
| Process Log | Ferramentas, workflow, **onde a IA errou**, **o que o Emerson adicionou** |
| Evidências | Checklist marcado |

## O que o Emerson adicionou (registrar sempre, é o que eles mais valorizam)
- A ideia de **resolver os 4 desafios num sistema único**.
- O **núcleo sozinho + cooperativo** (sessão → módulo → resultado vira entrada de outro módulo).
- **Janela própria, como software**.
- **Foco nos obrigatórios** antes dos diferenciais.
- Planejar **tudo em `.md` antes de programar**.
- Correções feitas na IA (ver o diário).

## Evidências a coletar AO LONGO do trabalho (não deixar para o fim)
- [ ] Print desta conversa de planejamento (a regra do núcleo sendo definida)
- [ ] Print/export de cada rodada relevante com a IA
- [ ] Prints do sistema rodando (cada módulo + um cruzamento)
- [ ] Gravação curta (1–3 min) do fluxo: nova sessão → churn → "enviar para suporte"
- [ ] Histórico de commits (git) mostrando a evolução
- [ ] Testes de aceite marcados (ver `07-requisitos_obrigatorios.md`)

## Checklist final antes do PR
- [ ] Todos os 🔴 de `07-requisitos_obrigatorios.md` marcados
- [ ] `como_rodar.md` testado do zero numa máquina limpa (código e .exe)
- [ ] Nenhum dado pessoal ou histórico de teste no pacote
- [ ] Números do README batem com os relatórios gerados
- [ ] Nada fora de `submissions/emerson-souza/`
