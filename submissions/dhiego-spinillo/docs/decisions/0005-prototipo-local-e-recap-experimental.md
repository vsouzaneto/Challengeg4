# ADR0005 — Protótipo local e recap experimental

**Status:** vigente no protótipo. **Data:**21/09/2026.

## Decisão e contexto

Entregar FastAPI, Jinja e JavaScript nativo, com modelo local incluído, SQLite para decisões e Docker para reprodução. O usuário sugeriu FastAPI/Jinja/HTMX/PostgreSQL/Docker; escolhemos as peças necessárias ao fluxo demonstrado. Classificação funciona sem chave externa. Persistência mantém sugestão, escolha, motivo e horário; exportação omite o texto original. Execução vinculada a127.0.0.1, sem autenticação de produção.

O recap via OpenRouter permanece opcional, experimental e desligado por padrão. A integração retornou15/16saídas com esquema/citações válidos após corrigir um invólucro Markdown. Porém o revisor automatizado aprovou fidelidade em6/15. Isso não sustenta adoção operacional. Não esconder a avaliação nem tratar presença de citação como garantia semântica.

## Alternativas consideradas

- **PostgreSQL e n8n:** adiados; não há concorrência operacional, múltiplos sistemas ou workflow externo que exija essas dependências na demonstração.
- **HTMX:** substituído por poucos handlers de fetch/DOM nativos; entrada editável, estado de análise e destaque de citação cabem nesse escopo.
- **Recap como núcleo aprovado:** não adotado; evidência de qualidade insuficiente. Mantido como experimento identificado para discussão.
- **Protótipo apenas estático:** rejeitado; a classificação executa sobre entrada nova e a confirmação é persistida. O diagnóstico visual permanece uma análise estática reproduzível.

## Consequências

O contêiner copia somente o modelo em artifacts; banco e chaves não entram na imagem. O volume persiste apenas o banco runtime. A imagem usa usuário sem privilégios. Uma publicação externa exigirá controle de acesso e tratamento dos dados adequados à operação; o pacote atual demonstra execução local. Nenhuma ação real é enviada a sistemas de atendimento.
