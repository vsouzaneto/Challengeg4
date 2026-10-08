"""Interface Streamlit. Importação sem efeitos colaterais ou dependência da UI."""

from data import load_data
from scoring import score_open_opportunities


def load_portfolio():
    dataset = load_data()
    result = score_open_opportunities(dataset)
    # Enriquecimento exclusivamente para filtros, após o scoring global.
    rows = [dict(row, manager=dataset.sales_teams[row['sales_agent']]['manager'],
                 regional_office=dataset.sales_teams[row['sales_agent']]['regional_office'])
            for row in result.opportunities]
    return rows, result.reference_date


def filter_portfolio(rows, selections, watchlist_only=False, ordering='Balanced Priority'):
    """Não chama scoring, não altera linhas e preserva percentis globais."""
    filtered = [row for row in rows
                if all(not selected or row[field] in selected for field, selected in selections.items())
                and (not watchlist_only or row['watchlist'])]
    field = 'sales_price' if ordering == 'Price Only' else 'balanced_priority'
    return sorted(filtered, key=lambda row: (-row[field], row['opportunity_id']))


STAGES = {'Prospecting': 'Prospecção', 'Engaging': 'Em negociação'}
REGIONS = {'Central': 'Central', 'East': 'Leste', 'West': 'Oeste'}
LOW_EVIDENCE = '⚠ Pouco histórico disponível. Não descarte automaticamente. Revisão manual recomendada.'


def number(value, decimals=2):
    return f"{value:,.{decimals}f}".replace(',', '_').replace('.', ',').replace('_', '.')


def priority_label(score):
    if score >= 90:
        return 'Prioridade muito alta'
    if score >= 75:
        return 'Prioridade alta'
    if score >= 50:
        return 'Prioridade média'
    return 'Prioridade baixa'


def action_opportunities(rows):
    return sorted((r for r in rows if r['confidence'] in ('Alta', 'Média')),
                  key=lambda r: (-r['priority_score'], r['opportunity_id']))[:5]


def main_reason(row, strong_history_threshold):
    if row['watchlist']:
        return 'Alto valor, mas evidência histórica limitada.'
    if row['confidence'] == 'Baixa':
        return 'Evidência histórica limitada; revisão humana recomendada.'
    if row['historical_fit'] >= strong_history_threshold:
        return 'Combinação de valor econômico e histórico favorável do produto/vendedor.'
    return 'Valor econômico + histórico suficiente para apoiar a priorização.'


def explanation(row):
    reason = ('Alto valor + pouco histórico disponível.' if row['watchlist'] else
              'Combinação de valor econômico e histórico do produto e do vendedor.')
    return (f"Motivo principal: {reason} O histórico usa {row['n_product']:,} negócios "
            f"anteriores do produto e {row['n_sales_agent']:,} do vendedor. "
            f"A confiança da evidência é {row['confidence']}. "
            + (LOW_EVIDENCE if row['confidence'] == 'Baixa' else ''))


def table_rows(rows):
    return [{'Posição': i, 'Oportunidade': r['opportunity_id'],
             'Conta': r['account'] or 'Conta não informada', 'Vendedor': r['sales_agent'],
             'Produto': r['product'], 'Estágio': STAGES[r['deal_stage']],
             'Valor': number(r['sales_price']), 'Prioridade': number(r['priority_score']) + '/100',
             'Confiança': r['confidence'], 'Revisão manual': 'Sim' if r['watchlist'] else 'Não'}
            for i, r in enumerate(rows, 1)]


def main():
    import streamlit as st

    st.set_page_config(page_title='Prioridades de hoje', page_icon=':material/target:', layout='centered')
    st.title('Prioridades de hoje')
    st.write('Estas são as oportunidades que merecem sua atenção primeiro.')
    st.caption('Prioridade considera valor econômico e histórico disponível. Não representa chance de fechamento.')
    try:
        rows, reference_date = load_portfolio()
    except (ValueError, OSError) as error:
        st.error(f'Não foi possível carregar a carteira: {error}')
        st.stop()
        return

    with st.sidebar:
        st.header('Sua carteira')
        st.caption('Selecione seu nome na barra lateral para ver apenas sua carteira.')
        st.caption('Sem seleção, mostramos todos. Combine filtros para focar sua carteira.')
        selections = {}
        for field, label in [('sales_agent', 'Vendedor'), ('manager', 'Gerente'), ('regional_office', 'Região')]:
            selections[field] = st.multiselect(label, sorted({r[field] for r in rows}),
                placeholder='Selecionar', key=field,
                format_func=lambda value: REGIONS.get(value, value))
        selections['deal_stage'] = st.multiselect('Estágio', list(STAGES),
            format_func=lambda value: STAGES[value], placeholder='Selecionar', key='deal_stage')
        selections['confidence'] = st.multiselect('Confiança', ['Alta', 'Média', 'Baixa'],
            placeholder='Selecionar', key='confidence')
        manual_only = st.checkbox('Somente revisão manual', key='manual_only')
        st.caption(f'Demonstração histórica • {reference_date:%d/%m/%Y}. Os dados não são de hoje.')

    # Reserva a seção secundária após a carteira, mas lê a ordenação antes dos filtros.
    content = st.container()
    with st.expander('Como esta prioridade é calculada', expanded=False):
        label = st.radio('Ordenação', ['Prioridade Balanceada', 'Somente preço'], key='ordering')
        st.write('A Prioridade Balanceada combina preço e força do histórico. Somente preço é a comparação de referência.')
        st.caption('Nos testes históricos, a Prioridade Balanceada não demonstrou superioridade estatística confiável sobre preço sozinho.')
        st.caption('Força do histórico é um índice baseado em negócios anteriores parecidos. Não é probabilidade de compra.')
        st.caption(f'A prioridade de 0 a 100 indica posição relativa entre as {len(rows):,} oportunidades abertas originais. '
                   'Filtrar ou mudar a ordenação não recalcula esse número. Gerente e região servem apenas como filtros.')
    ordering = 'Price Only' if label == 'Somente preço' else 'Balanced Priority'
    filtered = filter_portfolio(rows, selections, manual_only, ordering)

    actions = action_opportunities(filtered)
    manual = [r for r in filtered if r['watchlist']]
    # Critério de linguagem apenas: quartil superior do índice na carteira global.
    fits = sorted(r['historical_fit'] for r in rows)
    strong_history_threshold = fits[int((len(fits) - 1) * 0.75)]

    with content:
        for col, (label, value) in zip(st.columns(3), [
            ('Prioridades exibidas', len(actions)),
            ('Para revisão manual', len(manual)),
            ('Total da carteira', len(filtered))]):
            col.metric(label, value)

        st.subheader('Foque nestas oportunidades hoje')
        st.caption('Até cinco maiores prioridades com confiança Alta ou Média, respeitando seus filtros. Valores de catálogo; moeda não confirmada.')
        if not actions:
            st.info('Não há oportunidades com confiança Alta ou Média nesta seleção. Confira a revisão manual ou amplie os filtros.')
        for position, row in enumerate(actions, 1):
            with st.container(border=True):
                title = row['account'] or f"Oportunidade {row['opportunity_id']}"
                st.markdown(f"**{position}. {title}**")
                st.write(priority_label(row['priority_score']))
                st.write(f"Valor: {number(row['sales_price'])} · Confiança: {row['confidence']}")
                st.caption(f"Vendedor: {row['sales_agent']} · Produto: {row['product']}")
                if not row['account']:
                    st.caption('Conta não informada no CRM')

        st.subheader('Revise estas oportunidades antes de agir')
        st.caption('São oportunidades valiosas, mas com pouco histórico. Merecem avaliação humana antes de serem priorizadas ou descartadas.')
        if manual:
            st.table([{**r, 'Prioridade': priority_label(source['priority_score'])}
                      for r, source in zip(table_rows(manual), manual)])
        else:
            st.caption('Nenhuma oportunidade para revisão manual nesta seleção.')

        with st.expander('Ver carteira completa', expanded=False):
            if filtered:
                st.table(table_rows(filtered))
            else:
                st.write('Não há oportunidades nesta seleção.')
            st.caption(f"Confiança média: {sum(r['confidence'] == 'Média' for r in filtered)} · "
                       f"Confiança baixa: {sum(r['confidence'] == 'Baixa' for r in filtered)}")

        if filtered:
            st.subheader('Por que esta oportunidade está aqui?')
            detail_rows = actions + [r for r in filtered if r not in actions]
            by_id = {r['opportunity_id']: r for r in detail_rows}
            selected = st.selectbox('Selecionar oportunidade', list(by_id), placeholder='Selecionar',
                format_func=lambda key: f"{by_id[key]['account'] or 'Oportunidade'} · {key}")
            row = by_id[selected]
            st.write(f"**{priority_label(row['priority_score'])}** · "
                     f"**Valor:** {number(row['sales_price'])} · **Confiança:** {row['confidence']}")
            st.write('**Motivo principal:** ' + main_reason(row, strong_history_threshold))
            if row['confidence'] == 'Baixa':
                st.warning(LOW_EVIDENCE)
            with st.expander('Ver detalhes do histórico', expanded=False):
                st.write(f"**Priority Score:** {number(row['priority_score'], 4)}/100")
                st.caption(f"Ranking relativo global de {number(len(rows), 0)} oportunidades abertas. Não é probabilidade de fechamento.")
                st.caption('Histórico favorável significa índice no quartil superior da carteira global. É apenas uma descrição relativa, sem alterar o score ou indicar causalidade.')
                st.write(f"**Força do histórico:** {number(row['historical_fit'], 4)}")
                st.caption('Força do histórico é um índice baseado em negócios anteriores parecidos. Não é probabilidade de compra.')
                st.write(f"Negócios anteriores do produto (n_product): **{row['n_product']}**")
                st.write(f"Negócios anteriores do vendedor (n_sales_agent): **{row['n_sales_agent']}**")
                st.caption('Os grupos se sobrepõem e não devem ser somados. Confiança indica volume de evidência, não garantia de acerto.')



if __name__ == '__main__':
    main()
