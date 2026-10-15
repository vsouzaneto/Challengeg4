# Foco — Lead Scorer, case G4 003

O **Foco** é uma aplicação local para o vendedor decidir qual oportunidade trabalhar em seguida. Ela usa os quatro CSVs reais indicados no [desafio 003](https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge/blob/main/challenges/build-003-lead-scorer/README.md), reúne 2.089 oportunidades abertas e as separa em **Avançar**, **Revisar** e **Qualificar**. O usuário pode filtrar por vendedor, gerente, região, conta, produto ou ID; cada item mostra o motivo da prioridade e uma próxima ação.

A interface oferece três formas de leitura dos mesmos dados: **Mesa comercial** (comparação rápida e detalhe lateral), **Fila de decisão** (próxima ação em destaque) e **Kanban** (filas calculadas lado a lado). A escolha de visualização, a largura dos painéis e o tema Automático/Claro/Escuro ficam salvos apenas neste navegador. No desktop, arraste a divisória entre lista e detalhe ou ajuste-a com as setas do teclado; no celular, tocar um item abre uma tela de detalhe com botão Voltar. As filas e o índice são calculados pelo mesmo código em todas as visualizações; alternar a tela não altera oportunidades.

**Painéis do negócio** reúne uma página por vendedor com sua carteira, fila e vendas históricas (quantidade ganha, perdida e valor fechado ganho), a estrutura por gerente, uma visão comparativa das regiões e a distribuição dos preços de catálogo. As vendas vêm dos negócios encerrados e aparecem somente como contexto; não participam do índice das oportunidades abertas. O dataset não traz coordenadas para um mapa geográfico preciso. Na oportunidade, é possível registrar uma anotação e um status visual de andamento. Esses registros ficam no armazenamento local do navegador, identificados pelo ID da oportunidade; não são enviados ao servidor nem alteram a fila ou o índice. Em outro navegador ou dispositivo, eles não aparecem.

Os **Painéis** têm subpáginas Gerente, Vendedor e Mapa de regiões. Cada vendedor aparece em um cartão de identificação com avatar ilustrado local, nome e fila; **Acessar detalhes** abre sua equipe, região, carteira e histórico. O mapa é ilustrativo, com áreas inventadas para comparar vendedores e oportunidades por `regional_office`; selecionar uma pessoa destaca sua região e suas oportunidades.

## Executar

Requer Python 3.10 ou superior e conexão à internet **somente na primeira execução**, para baixar o dataset público. Não há pacotes `pip` nem conta de serviço. Na pasta do projeto, use **um comando**:

```bash
python iniciar.py
```

O comando baixa os CSVs caso faltem, prepara a carteira, abre uma porta livre **somente neste computador** e mostra a URL no terminal. Ele também tenta abrir o navegador. Para encerrar, pressione `Ctrl+C`. No Windows, você também pode clicar duas vezes em `iniciar-foco.cmd`. Se os CSVs já estiverem em `data/`, o início funciona sem internet. Para conferir os dados sem iniciar a tela, use `python iniciar.py --check`.

Se preferir controlar manualmente a porta ou a pasta de dados, os comandos originais continuam disponíveis: `python download_data.py` e `python app.py`. Nesse modo manual, abra `http://127.0.0.1:8843`. O servidor escuta apenas `127.0.0.1`; encerre com `Ctrl+C`. Se já tiver os CSVs, coloque `accounts.csv`, `products.csv`, `sales_teams.csv` e `sales_pipeline.csv` em `data/` e pule o download. Para rodar `audit.py`, inclua também `metadata.csv`; o comando de download obtém os cinco arquivos. Use `python app.py --data CAMINHO --port 8843` para caminhos ou porta diferentes. A pasta `data/` é ignorada pelo Git.

Para validar no celular na **mesma rede local**, inicie uma segunda instância ligada somente ao IP local do computador: `python app.py --host SEU_IP_LOCAL --port 8844` e abra o endereço que o terminal imprime no celular. O IP pode mudar quando o roteador reconectar. Não use `0.0.0.0` para esta validação; o endereço específico restringe a escuta à interface escolhida. Se o Windows pedir autorização de firewall, permita apenas a rede **Privada**. O servidor não possui autenticação e não deve ser publicado na internet.

Para reproduzir a auditoria, a hipótese histórica e os testes:

```bash
python audit.py
python evaluate.py
python -m unittest discover -s tests -v
node --test tests/test_filters.cjs tests/test_business.cjs
```

## Como a prioridade funciona

Os negócios em `Engaging` com até 90 dias desde o engajamento entram em **Avançar**; os demais `Engaging`, em **Revisar**; `Prospecting` entra em **Qualificar**. Dentro de cada fila, um índice de 0 a 100 soma critérios observáveis: conta identificada, preço de catálogo como proxy de impacto e tempo desde o engajamento. O índice **não é probabilidade de fechamento**. A explicação aparece junto de cada oportunidade, e o [método completo](docs/data-audit.md) documenta os dados e a hipótese descartada.

Testamos primeiro uma taxa histórica suavizada por produto e setor, com corte cronológico. AUC de 0,4854 no conjunto de teste mostrou que ela não separa negócios ganhos dos perdidos neste dataset. Por isso essa taxa **não participa** da fila apresentada. Dados de `Won`/`Lost`, `close_value` e `close_date` não são usados para pontuar uma oportunidade aberta. A referência histórica é fixa em 31/12/2017 para este conjunto, sem ser recalculada a partir dos desfechos.

## Limites e próximos passos

O dataset é fictício, termina em 2017 e não registra mudanças anteriores de estágio, tarefas ou contatos. Não é possível validar retrospectivamente o efeito da regra de 90 dias sobre conversão. Antes de um piloto real, RevOps precisaria calibrar pesos e prazo com vendedores, capturar histórico de atividades e medir tempo até a próxima ação, atualização de negócios parados e avanço de estágio. Também seriam necessários autenticação, permissão por vendedor e integração ao CRM.

O Foco foi desenvolvido com apoio do **Demiurgo**, ambiente próprio de organização de tarefas, agentes, revisões e evidências. O avaliador só precisa deste repositório para executar o Foco. A [história de desenvolvimento](docs/case-development.md) e o [process log](PROCESS_LOG.md) explicam o método.

O menu **Documentação**, visível em todas as telas, abre a história do desenvolvimento e um leitor dos documentos, com acesso às cópias estáticas de seus arquivos fonte. Leia nesta ordem: [especificação de negócio](docs/business-spec.md) (problema, regras numeradas e rastreabilidade), [especificação funcional](docs/functional-spec.md) (telas, filtros, filas, índice, próxima ação), [especificação técnica](docs/technical-spec.md) (arquitetura, dados, cálculo, limites), [plano de testes](docs/test-plan.md) (o que testar, como, resultados reais e lacunas), [operação, desenvolvimento e implantação](docs/operations.md), [auditoria dos dados](docs/data-audit.md), [como foi desenvolvido](docs/case-development.md) e [registro do processo](PROCESS_LOG.md) (trabalho dos agentes com evidências). [Evoluções propostas](docs/product-roadmap.md) ficam separadas das funções prontas. Após editar qualquer documento, execute `python sync_docs.py` e confira com `python sync_docs.py --check`. O Git guarda apenas código e documentação do case; os CSVs públicos são obtidos à parte.
