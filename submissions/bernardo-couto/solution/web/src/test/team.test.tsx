import { screen, within } from '@testing-library/react';
import { fmtBRLCompact } from '../lib/format';
import { pipelineSummary, DEALS } from '../mocks/fixtures';
import { renderApp } from './utils';

describe('Visão do manager', () => {
  it('lists sellers ordered by zombie value, without a rank column, each linking to their queue', async () => {
    renderApp('/time?as_of=2017-12-31&manager=Melvin%20Marxen');
    expect(await screen.findByRole('heading', { level: 1 })).toHaveTextContent(
      'Saúde do pipeline · time de Melvin Marxen',
    );
    const table = await screen.findByRole('table', { name: /Por vendedor/ });
    const headers = within(table)
      .getAllByRole('columnheader')
      .map((h) => h.textContent);
    expect(headers).toEqual([
      'Vendedor',
      'Abertos',
      'Tier A',
      'Esperado',
      'Parado (R$ tabela)',
      'Parados',
      'Conta inf.',
      'Carga',
    ]);
    expect(headers.join(' ')).not.toMatch(/Posição|Rank|#/);
    const expected = pipelineSummary(
      'sales_agent',
      DEALS.filter((d) => d.manager === 'Melvin Marxen'),
    ).groups.sort((a, b) => b.zombie_value - a.zombie_value);
    const rows = within(table).getAllByRole('row').slice(1);
    expect(rows.map((r) => within(r).getByRole('rowheader').textContent)).toEqual(
      expected.map((g) => g.key),
    );
    const link = within(rows[0]!).getByRole('link', { name: `Abrir fila de ${expected[0]!.key}` });
    expect(link.getAttribute('href')).toContain(
      `agent=${encodeURIComponent(expected[0]!.key).replace(/%20/g, '+')}`,
    );
    expect(link.getAttribute('href')).toContain('manager=Melvin+Marxen');
    expect(rows[0]!).toHaveTextContent(
      fmtBRLCompact(expected[0]!.nominal_zombie_value ?? 0).replace(/\u00a0/g, ' '),
    );
    expect(document.body.textContent).not.toMatch(/zumbi/i);
    expect(
      within(rows[0]!).getByLabelText(
        /^carga (alta|normal|baixa) \(\d+ deals; mediana do time \d+\)$/,
      ),
    ).toBeInTheDocument();
  });

  it('renders the tier distribution as a labelled bar with a table alternative', async () => {
    renderApp('/time?as_of=2017-12-31');
    const img = await screen.findByRole('img', {
      name: /Distribuição de tiers: A \d+ %, B \d+ %, C \d+ %, D \d+ %/,
    });
    expect(img).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Ver como tabela' })).toBeInTheDocument();
    expect(screen.getByText(/Esfriando = 101–138 dias/)).toBeInTheDocument();
  });
});
