# Suporte ao cliente: diagnóstico, automação e protótipo

## O problema
A operação de suporte atende por email, chat, telefone e redes sociais, algo em torno de 30 mil tickets por ano segundo a área. Tempo de resolução subiu, satisfação caiu, time sobrecarregado. A diretoria quer três respostas: onde se perde tempo, com número; o que dá para automatizar com IA e o que não dá; e algo rodando que prove que funciona.

## Os dados
Dois arquivos em `solution/data/`, nunca alterados. Toda transformação gera arquivo novo em `solution/data/derived/`.

`customer_support_tickets.csv` é a extração do sistema de tickets: cliente, produto, tipo, assunto, descrição, status, resolução, prioridade, canal, tempos e nota de satisfação. `all_tickets_processed_improved_v3.csv` são tickets de TI já classificados em categorias, com texto e grupo. Serve para treinar e avaliar classificação.

O que a área diz sobre os dados é afirmação, não fato. Volume, período e o que cada coluna significa de verdade entram como hipótese a testar.

## Divisão de trabalho
Eu escolho as perguntas, leio as saídas e decido o que cada anomalia significa. O agente escreve o código, roda, refatora e faz a parte mecânica. O diário em `process-log/diario.md` é escrito por mim, durante o trabalho; o agente só confere número contra fonte quando eu pedir.

Antes de rodar qualquer teste eu escrevo o que espero. Depois comparo. Isso vai no diário.

## Regras que evitam erro conhecido
Scripts numerados em `solution/` na ordem de execução, cada um salvando a saída em texto ao lado. Semente fixa em tudo que sorteia. Nenhum número vai para documento sem ter saído de um script daqui ou sem ser premissa declarada com a fonte.

Antes de confiar numa coluna: texto com `{chave}` literal pode ser só falha de renderização, teste antes de descartar; nulo alinhado a um status é construção do sistema, não dado faltante; datas fora do período declarado ou fora de ordem se contam, não se apagam; distribuição uniforme em categórica de negócio é sinal de dado gerado. Cada anomalia termina em uma decisão escrita: recuperar, usar com ressalva ou descartar.

Quase-duplicata dividida entre treino e teste infla acurácia. Deduplicar antes do split.
Resultado bom demais quase sempre é vazamento.

Ambiente: Python 3.12, venv em `.venv`, dependências fixadas em `requirements.txt`.

Modelo externo: o protótipo roda ponta a ponta sem chave de API. Chave só por variável de ambiente lida de `.env` fora do repositório; nunca em argumento, log, prompt ou commit. Resposta de modelo externo fica cacheada em arquivo versionado. Um provedor, com o motivo escrito.

Nenhum caminho absoluto desta máquina em código, saída ou documento. Scripts resolvem caminhos a partir do próprio arquivo.

Git: só arquivos dentro desta pasta. A raiz do repositório ignora `submissions/`, então `git add .` não adiciona nada; usar `git add -f` caminho a caminho. Não fazer commit nem push sem eu pedir.