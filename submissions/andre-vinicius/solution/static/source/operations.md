# Foco — execução, desenvolvimento e implantação

Como rodar o Foco, como uma mudança nova é feita, validada e integrada, e como voltar atrás. O Foco é um aplicativo **local**: não existe servidor de produção, pipeline de entrega contínua nem ambiente remoto neste repositório. “Implantar” significa integrar a mudança ao código e reiniciar o processo local.

## 1. Iniciar do zero

Requer Python 3.10 ou superior. Não há dependências `pip` nem conta de serviço. Execute **`python iniciar.py`** na pasta do projeto (no Windows, `iniciar-foco.cmd` também funciona por duplo clique). Se os CSVs públicos ainda não estiverem em `data/` (ignorada pelo Git), o início faz o download uma vez; nesse caso é necessária internet. O terminal informa a URL local e tenta abrir o navegador; `python iniciar.py --check` confere os dados sem abrir o servidor. Encerre com `Ctrl+C`. Para escolher pasta ou porta, use `python download_data.py` e `python app.py --data CAMINHO --port PORTA`. O programa não cria tarefas do sistema nem se instala como serviço.

Para revisão temporária num celular da mesma rede: `python app.py --host SEU_IP_LOCAL --port 8844`, e abra esse endereço no celular. Use o IP da interface local, nunca `0.0.0.0`; se o firewall pedir acesso, permita só a rede Privada. Não há autenticação nem TLS: não encaminhe a porta no roteador nem use este modo com dados sensíveis.

## 2. Ciclo de uma mudança

| # | Etapa | Quem | Evidência que fica |
| --- | --- | --- | --- |
| 1 | Definir o objetivo, o aceite e as frentes numa tarefa | Autor, com o agente que arquiteta | Brief da tarefa no quadro |
| 2 | Trabalhar numa cópia isolada (branch própria), sem tocar na pasta principal | Agente responsável pela frente | Branch e commits |
| 3 | Escrever ou ajustar testes junto com a mudança | Agente responsável | Arquivos em `tests/` no mesmo diff |
| 4 | Rodar a verificação da seção 4 com os CSVs reais | Agente responsável | Saída dos comandos na evidência da tarefa |
| 5 | Atualizar documentos afetados e `static/source/` | Agente responsável | `sync_docs.py --check` sem erro |
| 6 | Revisão cruzada por outro agente, contra o aceite | Outro agente | Veredito e o que foi (ou não) executado |
| 7 | Aprovação humana | Autor | Registro de aprovação da tarefa |
| 8 | Integrar a branch ao código principal e reiniciar o processo | Quem integra | Commit de integração; reinício do `app.py` |
| 9 | Conferir `/api/deals`, a referência histórica e uma tela | Quem integra | Observação na tarefa |

Duas observações do processo real: a aprovação de uma tarefa e a integração do código são registros diferentes; e quando o ambiente do agente impediu um comando (por exemplo, Python sem aprovação), o veredito da revisão registrou o que **não** rodou, em vez de assumir sucesso.

## 3. O que rodar conforme a mudança

| Mudança | Obrigatório rodar | Documentos a atualizar |
| --- | --- | --- |
| Peso, prazo ou fila em `scoring.py` | `test_rules.py`, `test_scoring.py`, `test_sales.py`; revisar `evaluate.py` se a hipótese histórica mudar | [Negócio](business-spec.md), [técnica](technical-spec.md), [funcional](functional-spec.md), `method.html` |
| Novo campo na API | `test_scoring.py` (HTTP), testes Node afetados | [Técnica](technical-spec.md) |
| Filtros, agrupamentos, anotações | `node --test` e roteiro manual de filtros | [Funcional](functional-spec.md) |
| Tela ou estilo | `node --check` do script alterado; roteiro manual em desktop e celular, claro e escuro | [Funcional](functional-spec.md), capturas |
| Novo CSV ou nova versão do dataset | `audit.py`, `evaluate.py`, suíte completa | [Auditoria](data-audit.md) |
| Só documentação | `python sync_docs.py --check` | O próprio documento |

Regra de ouro: mudança em `scoring.py` sem testes e sem texto atualizado não é integrada. Não altere peso nem prazo silenciosamente.

## 4. Verificação completa

```bash
python audit.py
python evaluate.py
python -m unittest discover -s tests -v
node --test tests/test_filters.cjs tests/test_business.cjs
python sync_docs.py --check
```

Mais `node --check` em cada script de `static/` alterado e o roteiro manual do [plano de testes](test-plan.md). Cole a saída real no plano de testes; não resuma sem contagem.

## 5. Atualizar os dados

1. Guardar uma cópia dos CSVs anteriores fora do repositório e baixar o novo conjunto em `data/`.
2. Executar `python audit.py` e comparar quantidades, esquema, datas, chaves e vazios. Uma data diferente muda a idade dos negócios; se a referência deve mudar, altere `DATASET_AS_OF` conscientemente, com teste.
3. Atualizar os números citados em [business-spec](business-spec.md), [data-audit](data-audit.md) e [test-plan](test-plan.md); os testes `test_real_data_joins_and_alias` e `test_open_deals_only_and_deterministic_order` fixam 8.800 e 2.089 e vão falhar de propósito.
4. Rodar a verificação completa e reiniciar `app.py`.

## 6. Voltar atrás

Como a entrega é código versionado, desfazer é um `git revert` do commit de integração (ou voltar a branch anterior) seguido de reiniciar `app.py`. Anotações dos usuários vivem no navegador de cada pessoa e não são afetadas por nenhuma mudança de servidor. O formato das anotações é identificado por `foco-opportunity-notes-v1`; mudá-lo exigiria migração.

## 7. Publicação do case

O [guia de submissão do G4](https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge/blob/main/submission-guide.md) deve ser conferido no momento de submeter. Antes de publicar: validar README e comandos numa cópia limpa; confirmar que `data/` e arquivos pessoais seguem fora do Git (`git ls-files`); revisar capturas por nomes, caminhos e segredos; anexar a saída real dos testes; explicar a AUC negativa e os limites do índice; revisar o diff do PR. **Fork, push e PR são feitos somente pelo autor. Este repositório ainda não foi enviado nem submetido.**

## 8. Acompanhar o trabalho

Quem quiser assistir ao desenvolvimento encontra, nesta ordem: `git log` (o que mudou e quando); [registro do processo](../PROCESS_LOG.md) (quem fez cada etapa, com o que se comprova); [como foi desenvolvido](case-development.md) (papéis e sequência de tarefas); e o [plano de testes](test-plan.md) (o que foi executado, por quem, com qual resultado). A página **Documentação** do aplicativo reúne os mesmos documentos.
