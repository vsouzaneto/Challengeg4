import { screen, within } from '@testing-library/react';
import { HttpResponse, http } from 'msw';
import { modelMissing } from '../mocks/handlers';
import { server } from '../mocks/server';
import { renderApp } from './utils';

describe('Qualidade do modelo', () => {
  it('renders the four question blocks from metrics.json in business language', async () => {
    renderApp('/qualidade?as_of=2017-12-31');
    expect(await screen.findByRole('heading', { level: 1 })).toHaveTextContent(
      'Qualidade do modelo · versão 2017-12-31-lr-v1',
    );
    const main = screen.getByRole('main');
    const h2s = within(main)
      .getAllByRole('heading', { level: 2 })
      .map((h) => h.textContent);
    expect(h2s.slice(0, 4)).toEqual([
      '1. Ela acerta mais quem vai fechar?',
      '2. Quando diz 70 %, fecha 70 %?',
      '3. Quanto do pipeline ela cobre?',
      '4. Vale dinheiro?',
    ]);
    // Latest cut (2017-09-30): scorer 0.560 vs random 0.603 with overlapping CIs -> honest tie sentence.
    expect(
      screen.getByText(/^Não\. O score não prevê fechamento melhor que o acaso \(5,6 vs 6,0 de 10/),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { name: 'O que esta ferramenta não faz' }),
    ).toBeInTheDocument();
    expect(screen.getByRole('img', { name: /Lead Scorer 5,6 de 10/ })).toBeInTheDocument();
    expect(screen.getByText('Erro médio de calibração: 4 pontos.')).toBeInTheDocument();
    expect(
      screen.getByText(
        /capturado 36 % da receita fechada depois do corte \(aleatório: 21 %; ordenar só por preço: 46 %\)/,
      ),
    ).toBeInTheDocument();
    expect(screen.getByText(/dos 2\.089 deals abertos pontuados/)).toBeInTheDocument();
    expect(screen.queryByText(/AUC|Brier|precision@/)).not.toBeInTheDocument();
    const table = screen.getByRole('table');
    expect(within(table).getAllByRole('row')).toHaveLength(6);
  });

  it('shows the artifacts-missing state with the command when metrics are absent (503)', async () => {
    server.use(
      http.get('*/api/v1/model/metrics', () => HttpResponse.json(modelMissing, { status: 503 })),
    );
    renderApp('/qualidade?as_of=2017-12-31');
    expect(
      await screen.findByText('As métricas do backtest ainda não foram geradas.'),
    ).toBeInTheDocument();
    expect(screen.getByText('cd solution && make pipeline')).toBeInTheDocument();
  });
});
