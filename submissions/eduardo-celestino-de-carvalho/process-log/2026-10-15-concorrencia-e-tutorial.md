# 15/10/2026 — Comparação com as outras submissões, exports e vídeo tutorial

## Pedido

Com o PR quase pronto, o candidato pediu duas coisas:
- investigar as soluções já enviadas para o mesmo case, para saber se a nossa se destaca;
- depois, deixar o processo transparente com o export das conversas e criar um vídeo tutorial em motion design, com narração, para usuários não técnicos. A referência era o estúdio de vídeo de um projeto pessoal dele.

## Comparação com as outras submissões

A IA leu os 86 PRs públicos do Challenge 003 (76 abertos, nenhum com merge) e as 176 reviews do avaliador. As reviews do 003 foram lidas na íntegra.

| Achado | Consequência |
|---|---|
| Pelo menos 18 submissões chegaram ao limite de 138 dias, várias com os mesmos números | O insight central não diferencia mais; o diferencial passa a ser rigor, produto e evidência |
| Um PR anterior (24/09) usa o mesmo nome de coluna, "Confirmar ou encerrar" | O candidato decidiu manter o nome: não houve cópia, e o export desta sessão mostra como o nome surgiu (revisão de termos, 15/10) |
| O motivo de reprovação mais comum é um process log só narrativo: sem export das conversas, sem capturas das sessões, com um único commit | Exports das duas sessões incluídos no repositório |
| São elogiados: hipóteses derrubadas por dados, backtest contra baseline, testes de vazamento, decisões humanas explícitas | Já presentes; mantidos em destaque no README |
| Deploy público e capturas do app aparecem como melhorias não bloqueadoras | Capturas incluídas; deploy fica como próximo passo opcional |

## Exports

- **Codex:** o export foi gerado pelo próprio Codex, a pedido do candidato.
- **Claude Code:** gerado a partir do log local da sessão, com mensagens, respostas e ações. Saídas brutas e raciocínio interno ficaram de fora.
- **Revisão de dados privados.** Antes de gravar, a IA procurou no texto final nomes de outros projetos do candidato, e-mail e caminhos locais.
  - A primeira versão ainda deixava passar variações em maiúsculas e um caminho cortado no meio.
  - A redação passou a ignorar maiúsculas e a respeitar os limites de palavra (para "naturais" não virar marcador), e a ser aplicada antes de truncar os comandos.

## Vídeo tutorial

O pipeline seguiu o do estúdio pessoal do candidato: roteiro → voz neural → cenas em Remotion → quadros pelo Chrome → codificação com PyAV. O PyAV é necessário porque o Controle de Aplicativo do Windows bloqueia o ffmpeg do Remotion nesta máquina.

- **Roteiro:** 10 cenas, cerca de 2 minutos, frases curtas e verbos de ação, sem jargão de CRM.
- **Telas reais.** As cenas usam capturas do app em 2×. Cada destaque é posicionado pelas coordenadas reais do elemento, medidas no navegador na hora da captura.
- **Sincronia.** Cada destaque entra na frase que o narra, usando os tempos de frase devolvidos pelo serviço de voz.
- **No app:** primeira seção do procedimento (botão **?**), com legendas ativadas, e botão "Assistir tutorial" no guia rápido. O servidor passou a responder a pedidos de intervalo (HTTP 206), sem os quais o player não consegue avançar e voltar o vídeo. A resposta tem teste próprio.

### Problemas encontrados no caminho

1. **Voz.** O `edge-tts` instalado na máquina recebia 403 do serviço. A versão 7.3.1, instalada num ambiente isolado em `video/.venv`, resolveu sem mexer no estúdio pessoal.
2. **O botão "?" parou de abrir no servidor de testes.** Ele tinha sido iniciado antes da renomeação das chaves do JSON de robustez, e o procedimento falhava inteiro.
   - O código publicado estava consistente.
   - Mesmo assim, o bloco de robustez passou a ser tolerante: com um JSON de outra versão, o procedimento abre sem ele.
3. **Destaque fora do lugar.** Na cena dos filtros, o destaque usava a posição do campo depois do filtro aplicado; ao filtrar, aparece o botão "Limpar" e o campo se desloca. Encontrado nos quadros de conferência e corrigido para usar a captura de cada momento.
4. **Erro de render** com intervalo infinito numa animação; corrigido antes do render final.
