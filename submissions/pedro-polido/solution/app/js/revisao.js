import { scenario, breakeven } from './roi.js';

const $ = (sel) => document.querySelector(sel);
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const int = (n) => Math.round(n).toLocaleString('pt-BR');
const dec = (n, d = 1) => n.toLocaleString('pt-BR', { minimumFractionDigits: d, maximumFractionDigits: d });
const pct = (v, d = 1) => `${dec(100 * v, d)}%`;
const brl = (n) => `R$ ${int(n)}`;
const pval = (p) => (p < 0.001 ? '< 0,001' : `= ${dec(p, p < 0.1 ? 3 : 2)}`);
const TAG = { FATO: 'fato', INFERÊNCIA: 'inf', PREMISSA: 'prem' };
const tag = (t) => `<span class="tag ${TAG[t]}">${t}</span>`;
const table = (el, head, rows) => {
  el.innerHTML = `<thead><tr>${head.map((h) => `<th>${h}</th>`).join('')}</tr></thead><tbody>${
    rows.map((r) => `<tr>${r.map((c) => `<td>${c}</td>`).join('')}</tr>`).join('')}</tbody>`;
};

const r = await (await fetch('data/revisao.json')).json();
const e1 = r.etapa1;
const rec = e1.registros;
const N = rec.pandas_padrao;
const k = r.automatizar;
const d = r.descartadas;
const na = r.nao_automatizar;
const roi = r.roi;

// ------------------------------------------------------------------------------------------------ Etapa 1
$('#e1-title').textContent = `O arquivo tem ${int(N)} registros, não 30 mil`;
$('#e1-lead').innerHTML = `As descrições têm quebras de linha dentro das aspas: quase 3 em cada 4 tickets (${pct(e1.registros_multilinha_pct)}) ocupam várias linhas do arquivo. ${tag('INFERÊNCIA')} Os "~30.000 registros" que o brief atribui a este dataset batem com as ${int(e1.linhas_fisicas)} linhas físicas. O brief também fala em "~30.000 tickets por ano" para a operação; esse é um número de contexto, que o CSV não confirma nem desmente.`;
const c = e1.compra;
table($('#e1-table'), ['Passo', 'Resultado', ''], [
  ['1. Arquivo', `${int(e1.bytes)} bytes · UTF-8 (decodificação estrita ok, ${e1.bom ? 'com' : 'sem'} BOM; ${int(e1.nao_ascii)} bytes não-ASCII; ${e1.substituicao} caracteres "�" já gravados no arquivo) · separador <code>${esc(e1.separador)}</code> · fim de linha ${e1.fim_de_linha} · SHA-256 <code>${e1.sha256.slice(0, 16)}…</code>`, tag('FATO')],
  ['2. Linhas físicas', `<b>${int(e1.linhas_fisicas)}</b> (equivale a <code>wc -l</code>)`, tag('FATO')],
  ['3. Registros', `Leitor CSV do Python: <b>${int(rec.csv_reader)}</b> · pandas padrão: <b>${int(rec.pandas_padrao)}</b> · pandas <code>engine="python"</code> com aspas: <b>${int(rec.pandas_python_aspas)}</b> · <code>on_bad_lines="warn"</code>: <b>${int(rec.pandas_on_bad_lines_warn)}</b>, ${rec.descartadas} linhas descartadas · lendo <i>sem</i> respeitar as aspas: ${int(rec.sem_respeitar_aspas)} "registros" quebrados, depois de descartar ${int(rec.sem_aspas_linhas_malformadas)} linhas malformadas e ${int(e1.linhas_em_branco_fisicas)} em branco`, tag('FATO')],
  ['Reconciliação', `1 cabeçalho + ${int(N)} registros + <b>${int(e1.quebras_dentro_de_campos)} quebras de linha dentro de <code>${esc(e1.coluna_das_quebras.join(', '))}</code></b> = ${int(1 + N + e1.quebras_dentro_de_campos)}. ${int(e1.registros_multilinha)} descrições (${pct(e1.registros_multilinha_pct)}) ocupam várias linhas; até ${e1.max_quebras_num_registro} quebras num registro.`, tag('FATO')],
  ['4. IDs e vazios', `${int(e1.ids_unicos)} IDs únicos · ${e1.ids_duplicados} duplicados · ${e1.ids_contiguos ? `<b>contíguos de ${e1.id_min} a ${int(e1.id_max)}, sem buracos</b>` : 'com buracos'} · ${e1.registros_vazios} registros vazios (as ${int(e1.linhas_em_branco_fisicas)} linhas em branco estão dentro das descrições) · ${e1.registros_repetidos} registros repetidos`, tag('FATO')],
  ['5. Datas', `Compra: ${c.de} a ${c.ate}; há registros em ${c.meses} de ${c.meses_no_intervalo} meses, e ${c.dias_sem_registro} de ${c.dias_no_intervalo} dias ficam sem registro (${c.por_mes_min} a ${c.por_mes_max} por mês) · 1ª resposta: ${e1.primeira_resposta.de} a ${e1.primeira_resposta.ate} · resolução: ${e1.resolucao.de} a ${e1.resolucao.ate} · coluna com data de abertura: <b>${e1.coluna_data_abertura.length ? esc(e1.coluna_data_abertura.join(', ')) : 'nenhuma'}</b>`, tag('FATO')],
]);
$('#e1-conclusao').innerHTML = `<b>O arquivo tem de fato apenas ${int(N)} registros; faltam cerca de ${int(e1.faltam_para_30mil)} em relação aos 30 mil.</b>
  ${tag('INFERÊNCIA')} Os "~30 mil" batem com as ${int(e1.linhas_fisicas)} linhas físicas. A contagem anterior, ${int(N)}, estava certa.`;
table($('#e1-colunas'), ['Coluna', 'Tipo', 'Nulos', '%'], e1.colunas.map((col) => [
  `<code>${esc(col.coluna)}</code>`, esc(col.tipo), int(col.nulos), pct(col.pct),
]));
const st = e1.nulos_por_status;
$('#e1-colunas').insertAdjacentHTML('afterend', `<p class="tiny muted" style="margin-top:8px">Os nulos seguem o status: fechados ${pct(st.Closed.Resolution, 0)} sem resolução; abertos ${pct(st.Open['First Response Time'], 0)} sem 1ª resposta; pendentes ${pct(st['Pending Customer Response']['First Response Time'], 0)} sem 1ª resposta e ${pct(st['Pending Customer Response'].Resolution, 0)} sem resolução.</p>`);
$('#e1-erros').innerHTML = [
  'Chamei este arquivo de "o de 30 mil tickets" antes de medir.',
  `O ROI da página principal usa 2.500 tickets/mês (os 30 mil/ano do brief) sem avisar que é premissa. O CSV não informa o volume: não tem data de abertura.`,
  'Os percentuais de automação da página principal (60% automático, 32% assistido, 8% humano) foram medidos na outra base (IT Service Tickets, 47.837 tickets). Não valem para este CSV, e nada nesta página usa aquela base.',
  'Escrevi "independentes" onde o correto é "sem associação detectável": p alto não prova independência.',
  'Descrevi a diferença entre resolução e 1ª resposta como uniforme de ±24 h. Ela é triangular.',
  `Na revisão por chat, juntei duas medidas de urgência: a frase de urgência (${int(d.urgencia.frase)} tickets, p ${pval(d.urgencia.frase_p)}) e a lista ampla de palavras (${int(d.urgencia.palavras)} tickets, p ${pval(d.urgencia.palavras_p)}, ${d.urgencia.palavras_low} marcados Low). Aqui aparecem separadas.`,
  `Na revisão por chat, tratei as ${int(k.abertura_generica)} descrições que abrem com a frase genérica como "sem detalhes". Nenhuma termina nela: todas continuam, com mediana de ${int(k.palavras_apos_abertura_mediana)} palavras. O único sinal medido de informação faltante é o {error_message} vazio (${int(k.erro_vazio)}).`,
  'Na revisão por chat, o ROI contou como elegíveis ao pedido de detalhes tickets que o próprio fluxo manda direto para uma pessoa (C1–C6). Refeito seguindo o fluxo, o ROI provável caiu.',
  'Na revisão por chat, chamei os 19 casos de C6 de "sem falsos alarmes" sem lê-los. Na leitura, 4 são falsos positivos.',
  'Rotulei o proxy de volume (registros ÷ meses de compra) como INFERÊNCIA. É PREMISSA: data de compra não é data de abertura do ticket.',
].map((t) => `<li>${esc(t)}</li>`).join('');

// ------------------------------------------------------------------------------------------------ 2.1
table($('#e21-mantidas'), ['Automação', 'Evidência nos dados', 'Nível', 'Métrica de sucesso', 'Risco se errar'], [
  ['Acuse de recebimento',
    `${tag('FATO')} ${int(k.abertos_sem_resposta)} tickets abertos (${pct(k.abertos_pct, 2)}) sem nenhuma 1ª resposta, ${int(k.abertos_critical)} deles Critical. ${tag('INFERÊNCIA')} É uma fotografia do momento; numa operação contínua, o acuse vale para 100% dos tickets novos.`,
    '🤖', `% de tickets sem resposta 5 min após a abertura chegando perto de 0% (prazo: ${tag('PREMISSA')}); 1ª resposta humana medida à parte`,
    `Se contar como 1ª resposta, esconde os ${int(k.abertos_critical)} Critical sem atendimento humano`],
  ['Lembrete ao cliente',
    `${tag('FATO')} ${int(k.pendentes)} (${pct(k.pendentes_pct, 2)}) aguardando o cliente. Não existe data da última interação: tempo de espera não calculado.`,
    '🤖', '% de pendentes que respondem ou fecham em N dias; queda do estoque de pendentes', 'Lembrar quem já respondeu. Nunca fechar sozinho um ticket de C1–C6.'],
  ['Pedido de detalhes',
    `${tag('FATO')} ${int(k.erro_vazio)} tickets (${pct(k.erro_vazio_pct, 2)}) trazem <code>{error_message}</code> vazio: a mensagem de erro que o cliente queria mostrar não está no texto. ${int(k.erro_vazio_em_c1_c6)} deles já vão para uma pessoa (C1–C6); pelo fluxo, o pedido automático alcança <b>${int(k.pedir_detalhes_fluxo)}</b>. ${tag('FATO')} Os ${int(k.abertura_generica)} que abrem com <i>"I'm having an issue with the {product_purchased}. Please assist."</i> <b>não contam</b>: todos continuam com mais texto (mediana de ${int(k.palavras_apos_abertura_mediana)} palavras).`,
    '🤝', `Detector com ≥ 90% de acerto em auditoria (${tag('PREMISSA')}); taxa de resposta do cliente; rascunhos aprovados sem edição`,
    'Pedir o que o cliente já informou; atrasar um caso urgente com mais uma rodada'],
]);
const p = d.predicao;
const ts = d.tipo_x_assunto;
const rs = d.resolucoes;
const dup = d.duplicatas;
const u = d.urgencia;
const predText = (x, nome) => `${nome}: ${pct(x.modelo, 2)} de acerto contra ${pct(x.majoritaria, 2)} chutando a classe mais comum e ${pct(x.acaso, 2)} ao acaso`;
table($('#e21-descartadas'), ['Automação', 'Por que descartar'], [
  ['Classificação automática pelo texto', `${tag('FATO')} Validação cruzada com 5 partições (TF-IDF + regressão logística; o tipo foi previsto com assunto + descrição). ${predText(p.tipo, 'Tipo')}. ${predText(p.assunto, 'Assunto')}. ${tag('INFERÊNCIA')} O modelo testado não encontrou sinal no texto; outra família de modelo não foi testada.`],
  ['Roteamento aprendido', `${tag('FATO')} ${d.colunas_de_roteamento.length} de ${d.total_colunas} colunas indicam fila, equipe, agente ou responsável. Não há o que aprender.`],
  ['Roteamento por regra (campos preenchidos)', `${tag('FATO')} Tipo × assunto sem associação detectável (p ${pval(ts.p)}, V de Cramér ${dec(ts.v, 3)}). Nos ${int(ts.assunto_com_nome_de_tipo)} tickets cujo assunto tem nome de tipo, os dois concordam em ${int(ts.concordam)} (${pct(ts.concordam / ts.assunto_com_nome_de_tipo)}). A regra aplicaria essa contradição.`],
  ['Respostas sugeridas pelo histórico', `${tag('FATO')} ${int(rs.n)} resoluções, de ${rs.palavras_min} a ${rs.palavras_max} palavras, ${int(rs.distintas)} diferentes entre si, <b>${rs.com_acao_tecnica} com ação técnica</b>. Semelhança resolução × descrição do mesmo ticket: ${dec(rs.similaridade_mesmo_ticket, 4)}, contra ${dec(rs.similaridade_aleatoria, 4)} em pares sorteados (diferença desprezível).`],
  ['Respostas prontas por assunto', `${tag('FATO')} A frase de abertura não tem associação detectável com o assunto (p ${pval(d.abertura_x_assunto_p)}). ${tag('INFERÊNCIA')} Uma resposta escolhida pelo assunto tenderia a não casar com o texto do ticket.`],
  ['Triagem de prioridade', `${tag('FATO')} ${predText(p.prioridade, 'Prioridade')}. A frase de urgência (${int(u.frase)} tickets) tem associação fraca com a prioridade (p ${pval(u.frase_p)}; Low em ${pct(u.frase_low)} contra ${pct(u.sem_frase_low)}). A lista ampla de palavras de urgência (${int(u.palavras)} tickets) não tem associação detectável (p ${pval(u.palavras_p)}), e ${u.palavras_low} desses estão como Low.`],
  ['Detecção de duplicatas por texto', `${tag('FATO')} Com semelhança ≥ 0,8: ${int(dup.pares_08)} pares (${int(dup.por_mil)} alertas a cada 1.000 tickets, ${int(dup.tickets_envolvidos)} tickets envolvidos), <b>${dup.mesmo_email} do mesmo e-mail</b>; mesmo assunto em ${pct(dup.mesmo_assunto)} dos pares, contra ${pct(dup.assunto_acaso)} ao acaso. ${tag('INFERÊNCIA')} Sem identificador confiável de cliente, não dá para medir duplicata real; o volume de alertas já inviabiliza o uso.`],
  ['Agrupar tickets do mesmo cliente', `${tag('FATO')} ${d.emails_repetidos} e-mails se repetem (${d.tickets_email_repetido} tickets), mas o nome muda em ${d.grupos_nome_diferente} dos ${d.emails_repetidos} grupos. O e-mail não identifica o cliente.`],
]);

// ------------------------------------------------------------------------------------------------ 2.2
$('#e22-title').innerHTML = `${pct(na.uniao_humano_pct)} dos tickets iriam para decisão humana, se os rótulos forem usados como gatilho ${tag('PREMISSA')}`;
$('#e22-bar').innerHTML = [
  ['human', na.uniao_humano_pct, `🧑 ${pct(na.uniao_humano_pct)}`],
  ['hitl', na.so_assistido_pct, `🤝 ${pct(na.so_assistido_pct)}`],
  ['none', na.nenhuma_pct, `sem categoria ${pct(na.nenhuma_pct)}`],
].map(([cls, v, label]) => `<div class="${cls}" style="flex-basis:${100 * v}%">${label}</div>`).join('');
const ex = (e) => `<div class="ex"><b>#${e.id}</b> <span class="muted">(${esc(e.tipo)} · ${esc(e.assunto)} · ${esc(e.prioridade)})</span><br>“${esc(e.trecho)}”</div>`;
const catRow = (cat) => [`<b>${cat.codigo} ${esc(cat.nome)}</b>`, esc(cat.criterio), `${int(cat.volume)}<br><span class="muted">${pct(cat.pct, 2)}</span>`, cat.exemplos.map(ex).join(''), esc(cat.risco)];
table($('#e22-humano'), ['Tipo 🧑', 'Critério objetivo', 'Volume', 'Exemplos reais', 'Por que a IA não decide'], na.categorias.filter((x) => x.nivel === '🧑').map(catRow));
table($('#e22-assistido'), ['Tipo 🤝', 'Critério objetivo', 'Volume', 'Exemplos reais', 'Por quê'], na.categorias.filter((x) => x.nivel === '🤝').map(catRow));
const leitura = na.c5_casos.map((x) => `#${x.id} (${na.c5_leitura[String(x.id)]})`).join(', ');
const tp = na.frase_template_p;
const c6 = na.c6_leitura;
$('#e22-nota').innerHTML = `<b>De onde vem o número:</b> ${int(na.so_por_rotulo_c1_c3)} tickets (${pct(na.so_por_rotulo_pct)}) entram só pelos campos tipo e assunto (C1–C3), que a Etapa 2.1 mostra não serem confiáveis. É um gatilho conservador: um alarme falso só manda o ticket para uma pessoa, e não decide nada. O texto (C4–C6) acrescenta ${int(na.texto_acrescenta)} tickets.
  C4 junta ${int(na.c4_assunto)} tickets pelo assunto e ${int(na.c4_texto)} pelo texto (${na.c4_ambos} pelos dois).
  Leitura dos ${na.c5_casos.length} casos de C5 ${tag('INFERÊNCIA')}: ${leitura}.
  A frase-padrão "I'm concerned about the security of my…" (${int(na.frase_template_seguranca)} tickets) ficou fora de C5: é uma preocupação genérica, sem relato de incidente, e não tem associação detectável com assunto (p ${pval(tp['Ticket Subject'])}), tipo (p ${pval(tp['Ticket Type'])}) ou prioridade (p ${pval(tp['Ticket Priority'])}).
  Leitura dos ${Object.values(c6).flat().length} casos de C6 ${tag('INFERÊNCIA')}: ${c6['emoção'].length} de emoção, ${c6.queixa.length} de queixa, ${c6['jurídico'].length} de contexto jurídico e <b>${c6['falso positivo'].length} falsos positivos</b> (#${c6['falso positivo'].join(', #')}).`;

// ------------------------------------------------------------------------------------------------ Etapa 3
const NOMES = ['conservador', 'provável', 'otimista'];
const prov = roi.cenarios['provável'];
$('#e3-title').textContent = prov.payback_meses === null
  ? `Com o volume proxy, a automação não se paga no cenário provável (ROI de 12 meses ${pct(prov.roi_12m)})`
  : `Com o volume proxy, o ROI de 12 meses é ${pct(prov.roi_12m)} no cenário provável (payback de ${dec(prov.payback_meses, 1)} meses)`;
$('#e3-lead').textContent = `A partir de ${int(prov.equilibrio)} tickets/mês o ROI de 12 meses fica positivo no cenário provável. O volume real decide o caso, e o CSV não o informa.`;
$('#e3-volume').innerHTML = [
  `${tag('FATO')} Não há data de abertura: o volume mensal não pode ser calculado diretamente.`,
  `${tag('PREMISSA')} Proxy de volume: supondo que os ${int(N)} registros sejam todos os tickets dos ${roi.meses} meses de datas de compra, <b>${dec(roi.volume_mes, 1)} tickets/mês</b>. O brief fala em 2.500/mês (30 mil/ano), também premissa.`,
  `${tag('FATO')} Tempo médio de tratamento: <b>não calculado</b> (${pct(roi.tempo_negativo_pct)} das diferenças são negativas). Os minutos poupados são ${tag('PREMISSA')}.`,
  `Elegíveis por mês: acuse ${dec(roi.volume_mes * roi.elegivel.acuse, 1)} (100%) · lembrete ${dec(roi.volume_mes * roi.elegivel.lembrete, 1)} (${pct(roi.elegivel.lembrete, 2)}) · pedido de detalhes ${dec(roi.volume_mes * roi.elegivel.pedir_detalhes, 1)} (${pct(roi.elegivel.pedir_detalhes, 2)})`,
].map((t) => `<li>${t}</li>`).join('');
const P = roi.premissas;
const A = roi.automacoes;
const tri = (arr, f) => arr.map(f).join(' / ');
const cen = NOMES.map((n) => roi.cenarios[n]);
table($('#e3-cenarios'), ['', 'Conservador', 'Provável', 'Otimista'], [
  ['Custo/hora do atendente', ...P.custo_hora.map((v) => brl(v))],
  ['Minutos poupados: acuse · lembrete · pedido', ...[0, 1, 2].map((i) => `${dec(A.acuse.min[i])} · ${dec(A.lembrete.min[i])} · ${dec(A.pedir_detalhes.min[i])}`)],
  ['Taxa de acerto: acuse · lembrete · pedido', ...[0, 1, 2].map((i) => `${pct(A.acuse.acerto[i], 0)} · ${pct(A.lembrete.acerto[i], 0)} · ${pct(A.pedir_detalhes.acerto[i], 0)}`)],
  ['Revisão humana por rascunho', ...A.pedir_detalhes.revisao.map((v) => `${dec(v, 2)} min`)],
  ['Implantação', ...[0, 1, 2].map((i) => `${P.impl_horas[i]} h × ${brl(P.impl_custo_hora[i])}`)],
  ['Manutenção', ...P.manut_horas_mes.map((v) => `${v} h/mês`)],
  ['API por rascunho', ...P.api_reais_por_rascunho.map((v) => `R$ ${dec(v, 3)}`)],
  ['<b>Horas economizadas/mês</b>', ...cen.map((x) => dec(x.horas_total, 1))],
  ['<b>Benefício/mês</b>', ...cen.map((x) => brl(x.beneficio_mes))],
  ['<b>Custo/mês</b> (manutenção + API + revisão)', ...cen.map((x) => `${brl(x.custo_mes)}<br><span class="tiny muted">${brl(x.manutencao_mes)} + ${brl(x.api_mes)} + ${brl(x.revisao_mes)}</span>`)],
  ['<b>Implantação</b>', ...cen.map((x) => brl(x.implantacao))],
  ['<b>ROI em 12 meses</b>', ...cen.map((x) => `<b class="${x.roi_12m < 0 ? 'neg' : 'pos'}">${pct(x.roi_12m)}</b>`)],
  ['<b>Payback</b>', ...cen.map((x) => (x.payback_meses === null ? 'não se paga' : `${dec(x.payback_meses, 1)} meses`))],
  ['Volume de equilíbrio (ROI 12m = 0)', ...cen.map((x) => `${int(x.equilibrio)}/mês`)],
  [`Com 2.500 tickets/mês ${tag('PREMISSA')} do brief (o CSV não informa o volume)`, ...cen.map((x) => `ROI ${pct(x.com_2500.roi_12m, 0)} · payback ${x.com_2500.payback_meses === null ? '—' : `${dec(x.com_2500.payback_meses, 1)} m`}`)],
]);

// Simulador
const FIELDS = [
  { id: 'cen', label: 'Cenário base', type: 'select' },
  // Valor exato do proxy (8.469 ÷ 24 = 352,875): arredondar mudaria o payback em relação à tabela
  { id: 'vol', label: `Tickets por mês (proxy: ${int(N)} ÷ ${roi.meses})`, step: 'any', get: () => roi.volume_mes },
  { id: 'custo_hora', label: 'Custo/hora do atendente (R$)', step: 1, get: (i) => P.custo_hora[i] },
  { id: 'impl_horas', label: 'Horas de implantação', step: 5, get: (i) => P.impl_horas[i] },
  { id: 'manut_horas_mes', label: 'Manutenção (h/mês)', step: 1, get: (i) => P.manut_horas_mes[i] },
  { id: 'pedir_detalhes.min', label: 'Min. poupados no pedido de detalhes', step: 0.5, get: (i) => A.pedir_detalhes.min[i] },
];
$('#e3-inputs').innerHTML = FIELDS.map((f) => (f.type === 'select'
  ? `<div><label for="s-cen">${f.label}</label><select id="s-cen">${NOMES.map((n, i) => `<option value="${i}" ${i === 1 ? 'selected' : ''}>${n}</option>`).join('')}</select></div>`
  : `<div><label for="s-${f.id}">${f.label}</label><input id="s-${f.id}" type="number" min="0" step="${f.step}"></div>`)).join('');
const fill = (i) => FIELDS.filter((f) => f.get).forEach((f) => { document.getElementById(`s-${f.id}`).value = f.get(i); });
function simulate() {
  const i = Number($('#s-cen').value);
  const val = (id) => Math.max(0, parseFloat(document.getElementById(`s-${id}`).value) || 0);
  const over = { custo_hora: val('custo_hora'), impl_horas: val('impl_horas'), manut_horas_mes: val('manut_horas_mes'), 'pedir_detalhes.min': val('pedir_detalhes.min') };
  const res = scenario(roi, i, { vol: val('vol'), over });
  const eq = breakeven(roi, i, over);
  $('#e3-sim').innerHTML = `
    <div class="kpi ${res.roi_12m < 0 ? 'bad' : 'good'}"><div class="kpi-label">ROI em 12 meses</div><div class="kpi-value">${pct(res.roi_12m)}</div></div>
    <div class="kpi"><div class="kpi-label">Payback</div><div class="kpi-value">${res.payback_meses === null ? '—' : `${dec(res.payback_meses, 1)} m`}</div><div class="kpi-sub">${res.payback_meses === null ? 'custo mensal maior que o benefício' : 'meses'}</div></div>
    <div class="kpi"><div class="kpi-label">Benefício − custo/mês</div><div class="kpi-value">${brl(res.beneficio_mes - res.custo_mes)}</div><div class="kpi-sub">${dec(res.horas_total, 1)} h/mês economizadas</div></div>
    <div class="kpi"><div class="kpi-label">Equilíbrio</div><div class="kpi-value">${int(eq)}</div><div class="kpi-sub">tickets/mês para ROI 12m = 0</div></div>`;
}
$('#s-cen').addEventListener('change', () => { fill(Number($('#s-cen').value)); simulate(); });
$('#e3-inputs').addEventListener('input', simulate);
fill(1);
simulate();

// Sensibilidade: faixa do ROI provável quando cada premissa vai do valor conservador ao otimista
const LABEL = {
  volume: 'Volume (metade → dobro)', impl_horas: 'Horas de implantação', custo_hora: 'Custo/hora do atendente',
  impl_custo_hora: 'Custo/hora de quem implanta', 'pedir_detalhes.min': 'Min. poupados no pedido de detalhes',
  manut_horas_mes: 'Horas de manutenção', 'acuse.min': 'Min. poupados no acuse', 'lembrete.min': 'Min. poupados no lembrete',
  'pedir_detalhes.acerto': 'Acerto do pedido de detalhes', 'lembrete.acerto': 'Acerto do lembrete',
  api_reais_por_rascunho: 'Custo de API por rascunho', 'acuse.acerto': 'Acerto do acuse',
};
const lo = Math.min(...roi.sensibilidade.map((s) => Math.min(s.pior, s.melhor)), -1);
const hi = Math.max(...roi.sensibilidade.map((s) => Math.max(s.pior, s.melhor)), 0.2);
const x = (v) => (100 * (v - lo)) / (hi - lo);
$('#e3-sens').innerHTML = roi.sensibilidade.slice(0, 8).map((s) => {
  const a = Math.min(s.pior, s.melhor);
  const b = Math.max(s.pior, s.melhor);
  return `<div class="sens-row"><span class="small">${esc(LABEL[s.premissa] || s.premissa)}</span>
    <div class="sens-track"><div class="sens-zero" style="left:${x(0)}%"></div><div class="sens-base" style="left:${x(prov.roi_12m)}%"></div>
      <div class="sens-bar" style="left:${x(a)}%;width:${Math.max(0.6, x(b) - x(a))}%"></div></div>
    <span class="tiny num">${pct(s.pior)} → ${pct(s.melhor)}</span></div>`;
}).join('') + `<p class="tiny muted" style="margin-top:8px">Linha tracejada: ROI zero. Traço escuro: ROI provável (${pct(prov.roi_12m)}). A manutenção consome ${pct(prov.manutencao_mes / prov.beneficio_mes, 0)} do benefício no cenário provável.</p>`;

$('#e3-ganhos').innerHTML = [
  `<b>Tickets sem nenhuma resposta:</b> hoje ${int(k.abertos_sem_resposta)} (${pct(k.abertos_pct, 2)}) ${tag('FATO')}. Com o acuse, nenhum fica sem pelo menos um acuse de recebimento ${tag('INFERÊNCIA')}. Tempo até a 1ª resposta: <b>não calculado</b> (os horários do CSV são inválidos).`,
  `<b>SLA:</b> não calculado; não há SLA nem tempo válido no CSV.`,
  `<b>Retrabalho evitado por duplicatas:</b> não calculado; a detecção foi descartada (${dup.mesmo_email} dos ${int(dup.pares_08)} pares parecidos são do mesmo e-mail, e o e-mail não identifica o cliente).`,
  `<b>Idas e vindas evitadas pelo pedido de detalhes:</b> não calculado (não há histórico de mensagens). Alcance pelo fluxo: ${int(k.pedir_detalhes_fluxo)} tickets (${pct(k.pedir_detalhes_fluxo / N, 2)}).`,
].map((t) => `<li>${t}</li>`).join('');

$('#pend').innerHTML = [
  `<b>Volume mensal real e data de abertura dos tickets.</b> O resultado financeiro depende disso: no cenário provável, o ponto de virada é ${int(prov.equilibrio)} tickets/mês.`,
  '<b>Tempo real de tratamento</b> por tipo de ticket, hoje premissa.',
  '<b>Custos:</b> custo/hora do atendente e de quem implanta; horas de implantação na ferramenta de atendimento.',
  '<b>Campos que faltam:</b> fila, equipe, agente ou código de cliente em algum sistema. Sem eles, roteamento e agrupamento por cliente continuam descartados.',
  '<b>Quem preenche tipo, assunto e prioridade?</b> Tipo e assunto não têm associação detectável: o formulário precisa ser revisto.',
  '<b>Esta base é uma amostra da operação real?</b> Placeholders em 100% das descrições, nenhuma resolução técnica e tempos negativos são típicos de dados gerados. Com uma base real, a análise é refeita.',
  '<b>Alçadas para reembolso, cancelamento e cobrança:</b> definem se algum desses casos pode passar de 🧑 para 🤝.',
  '<b>Prazos do acuse e do lembrete</b>, hoje premissas.',
].map((t) => `<li>${t}</li>`).join('');

// ------------------------------------------------------------------------------------------------ Mermaid
const dark = matchMedia('(prefers-color-scheme: dark)').matches;
try {
  const { default: mermaid } = await import('https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs');
  mermaid.initialize({ startOnLoad: false, securityLevel: 'strict', theme: dark ? 'dark' : 'default', flowchart: { htmlLabels: true } });
  await mermaid.run({ nodes: [document.getElementById('fluxo')] });
} catch (err) {
  document.getElementById('fluxo').insertAdjacentHTML('beforebegin', '<p class="tiny muted">Sem conexão com o CDN do Mermaid: abaixo está o código do fluxograma.</p>');
}
