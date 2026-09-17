<!-- Gerado por solution/analysis/05_report.py a partir de docs/templates/automacao.md.tmpl. Não edite à mão. -->

# Proposta de automação com IA

## Princípio

Automatizar **o que é repetitivo, mensurável e reversível**. Manter com pessoas **o que envolve dinheiro, acesso, risco ou um cliente insatisfeito**. Toda automação começa em modo sombra (sugere sem aplicar) e só passa a agir quando o acerto medido na própria operação justificar.

## O fluxo proposto

```
Ticket entra
  │
  ├─ 1. Sinal de risco/urgência?  ──sim──▶ ESCALAÇÃO: atendente sênior, sem rascunho de IA
  │
  ├─ 2. Classificador + explicação (categoria, confiança, termos que pesaram)
  │
  ├─ 3. Guarda de domínio: vocabulário conhecido?  ──não──▶ REVISÃO HUMANA
  ├─ 4. Confiança ≥ limiar?                         ──não──▶ REVISÃO HUMANA
  ├─ 5. Privilégio administrativo (previsto ou provável)? ──sim──▶ REVISÃO HUMANA com aprovação
  │
  └─ 6. ROTEAMENTO AUTOMÁTICO para a fila
         │
         ├─ Tickets similares já resolvidos exibidos ao agente
         ├─ Rascunho de resposta (IA generativa), sempre revisado antes de enviar
         └─ Agente corrige a categoria se preciso → a correção volta para o re-treino
```

No teste (7.176 tickets), esse fluxo mandou **65,3%** para roteamento automático (acerto de 94,9%), **28,1%** para revisão humana e **6,5%** para escalação.

## O que automatizar

| Automação | Por quê | Evidência |
|---|---|---|
| **Classificação e roteamento** | Maior ganho mensurável; erro é reversível (reatribuição) | 65,3% automáticos com 94,9% de acerto (IC 94,3%–95,6%); triagem recuperável ≈ 816 h/ano no cenário |
| **Follow-up de pendências** (lembrete e fechamento por inatividade) | 34,0% dos tickets aguardam o cliente; não exige julgamento | ≈ 816 h/ano no cenário (premissa a validar em piloto) |
| **Tickets similares** ao abrir o ticket | Ajuda o agente sem decidir por ele | Protótipo funcional |
| **Rascunho de resposta** (IA generativa) | Reduz o tempo de escrita; o humano aprova | ≈ 396 h/ano no cenário: menor que as anteriores, por isso vem depois |

## O que NÃO automatizar

| Situação | Tratamento | Por quê |
|---|---|---|
| **Termos de risco/urgência** (urgent, phishing, hacked, refund, cancel…) | Escalação, **sem rascunho de IA**, bloqueado também no servidor | Segurança e retenção: erro de tom ou de conteúdo custa caro |
| **Pedidos de privilégio administrativo** | Sempre aprovação humana, inclusive quando só a *probabilidade* é alta | É a classe que o modelo mais confunde (recall 66,3%); 5 de 264 ainda escaparam no teste |
| **Texto fora do padrão do treino** | Revisão humana | Fora do domínio o modelo erra com convicção: 91% dos tickets de e-commerce confiantes viraram "Hardware" |
| **Baixa confiança** | Revisão humana | 20,5% dos tickets no teste |
| **Reembolso e cancelamento** (tipos do Dataset 1) | Humano | Decisão financeira e de retenção |
| **Envio automático de respostas** | Nunca | O rascunho é sempre revisado |

### Exemplos reais dos dados

Tickets do conjunto de teste (nunca usados em treino ou seleção), escolhidos por regra fixa para não haver seleção a dedo: em cada situação, o ticket de menor id com 10 a 40 palavras. A rota é a que a API aplica.

| Situação | Ticket real (teste, texto já pré-processado) | Real → previsto | Confiança | Tratamento |
|---|---|---|---|---|
| **Termo de risco/urgência** | #174: _increase site increase site dear increase site storage quota invoicing site old asap work old assign directly best regards engineer_ | Storage → Storage | 86,5% | Termo(s) detectado(s): asap. Escalado para atendente sênior, sem rascunho de IA. |
| **Pedido de privilégio pego pela regra de risco** | #8396: _is down again down again keep getting communications problem thanks senior analyst north_ | Administrative rights → Hardware | 77,8% | O modelo previu outra categoria, mas a probabilidade de privilégio passou do limiar: aprovação humana. |
| **Pedido de privilégio que escapou** | #27574: _question guest wednesday october question guest hi issues guest wired issues connect client thank_ | Administrative rights → Hardware | 89,2% | Exemplo do vazamento residual: por isso conceder acesso nunca é automático, mesmo após o roteamento. |
| **Texto fora do padrão do treino** | #182: _card on saturdays card saturdays hi change regarding availability cards cleaning ladies namely saturdays cards available until please assist thanks_ | Access → Access | 99,3% | Vocabulário pouco conhecido pelo modelo: triagem humana. |
| **Baixa confiança** | #23: _badge access to be removed badge removed dear please badge since he working anymore best regards_ | Access → HR Support | 53,1% | O modelo não tem certeza suficiente: triagem humana confirma a categoria. |

**Leitura honesta dos exemplos:** nem todo ticket barrado estava errado.
- O exemplo de termo de risco é um pedido rotineiro de cota, escalado só por conter "asap".
- O de texto fora do padrão tinha a categoria certa e mesmo assim foi para humano.

Esse é o custo, medido e aceito, de uma política conservadora. Em produção, a lista de termos e os limiares devem ser calibrados com dados da operação. O exemplo de privilégio pego pela regra também sugere rótulos ruidosos no próprio dataset (o texto descreve uma falha de comunicação), outro motivo para re-treinar com dados rotulados pela própria equipe.

Automatizar 100% seria o erro: no teste, **28,1% + 6,5%** dos tickets seguem com pessoas, e isso é o desenho, não uma falha.

## ROI (cenário)

≈ **2.514 h/ano recuperáveis** (≈ 1,4 agente; ≈ R$ 113.152/ano) para 30.000 tickets/ano, já descontadas a conferência, a revisão e os erros residuais. Os detalhes e a sensibilidade estão em [diagnostico.md](diagnostico.md).

## Implantação sugerida

1. **Semanas 1–4 (modo sombra):** classificador re-treinado com o histórico da operação sugere a fila sem aplicar. Medir cobertura, acerto e vazamento de privilégio no domínio real.
2. **Semanas 5–8:** ligar o roteamento automático só nas categorias com acerto ≥ meta. Ligar o follow-up automático.
3. **Depois:** rascunho de resposta em teste A/B (tempo de resposta e CSAT, com e sem rascunho).
4. **Sempre:** painel com taxa de reatribuição, vazamento de privilégio e deriva de domínio (fração de tickets barrados pelo guarda).
