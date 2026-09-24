import { screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { HttpResponse, delay, http } from 'msw';
import { artifactsMissing } from '../mocks/handlers';
import { server } from '../mocks/server';
import { location, renderApp } from './utils';

describe('Fila do vendedor', () => {
  it('renders the ordered rows and the three tiles from the loaded page', async () => {
    renderApp('/?as_of=2017-12-31&agent=Darcel%20Schlecht');
    const list = await screen.findByRole('list', { name: 'Deals por prioridade' });
    const rows = within(list).getAllByRole('listitem');
    expect(rows.length).toBeGreaterThan(1);
    expect(rows.length).toBeLessThanOrEqual(10);
    // First row = OpenAPI example pinned on top by the fixtures (priority 82.4 -> 82).
    expect(within(rows[0]!).getByText('82')).toBeInTheDocument();
    expect(
      within(rows[0]!).getByRole('button', { name: /Abrir detalhe de Konex · GTX Pro/ }),
    ).toBeInTheDocument();
    expect(within(rows[0]!).getByText(/^Ticket alto: R\$ 3\.412 esperados/)).toBeInTheDocument();
    expect(
      within(rows[0]!).getByText(/Ligar esta semana e propor data de fechamento/),
    ).toBeInTheDocument();
    expect(within(rows[0]!).getByText('Confiança alta')).toBeInTheDocument();
    expect(within(rows[0]!).getByText(/R\$\s?3\.413/)).toBeInTheDocument();
    expect(
      screen.getByText('Tier A: bom valor, dentro do ciclo, dados completos'),
    ).toBeInTheDocument();
    expect(screen.getByText(/esperados no top/)).toBeInTheDocument();
    expect(screen.getByText('esfriando (101–138 dias)')).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /Trabalhar/ })).toHaveAttribute('aria-selected', 'true');
    expect(screen.getByRole('tab', { name: /Confirmar ou encerrar/ })).toBeInTheDocument();
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Sua fila de hoje');
  });

  it('shows unknown accounts as muted text with a CTA, never hidden', async () => {
    renderApp('/?as_of=2017-12-31&n=50');
    await screen.findByRole('list', { name: 'Deals por prioridade' });
    expect(screen.getAllByText('Conta não informada').length).toBeGreaterThan(0);
    expect(screen.getAllByRole('button', { name: /Registrar conta de/ }).length).toBeGreaterThan(0);
  });

  it('writes filters to the URL and clears the hierarchy when the region changes', async () => {
    const user = userEvent.setup();
    renderApp('/?as_of=2017-12-31');
    await screen.findByRole('list', { name: 'Deals por prioridade' });
    const region = screen.getByLabelText('Região');
    await waitFor(() => expect(within(region).getAllByRole('option').length).toBeGreaterThan(1));
    await user.selectOptions(region, 'Central');
    expect(location()).toContain('region=Central');
    await user.selectOptions(screen.getByLabelText('Manager'), 'Melvin Marxen');
    expect(location()).toContain('manager=Melvin+Marxen');
    await user.selectOptions(screen.getByLabelText('Vendedor'), 'Darcel Schlecht');
    expect(location()).toContain('agent=Darcel+Schlecht');
    await user.selectOptions(region, 'East');
    expect(location()).toContain('region=East');
    expect(location()).not.toContain('manager=');
    expect(location()).not.toContain('agent=');
    await user.click(screen.getByRole('button', { name: 'Limpar filtros' }));
    expect(location()).toBe('/?as_of=2017-12-31');
  });

  it('writes default as_of into the URL when missing', async () => {
    renderApp('/');
    await waitFor(() => expect(location()).toContain('as_of=2017-12-31'));
  });

  it('opens the drawer with every reason, then closes with Esc and returns focus', async () => {
    const user = userEvent.setup();
    renderApp('/?as_of=2017-12-31&agent=Darcel%20Schlecht');
    const title = await screen.findByRole('button', { name: /Abrir detalhe de Konex · GTX Pro/ });
    await user.click(title);
    const dialog = await screen.findByRole('dialog');
    expect(location()).toContain('deal=Z063OYW0');
    expect(within(dialog).getByRole('heading', { name: /Konex · GTX Pro/ })).toHaveFocus();
    // Score factors (HIGH_TICKET, PRODUCT_BASE_RATE) apart from context; MODEL_CONTRIBUTION hidden (weight 0).
    const reasons = within(dialog).getByRole('list', { name: 'Razões do score' });
    expect(within(reasons).getAllByRole('listitem')).toHaveLength(2);
    expect(within(reasons).getByText('+9,0 pts')).toBeInTheDocument();
    expect(within(reasons).getByText('+0,6 pts')).toBeInTheDocument();
    expect(within(reasons).getByText(/Aumenta o score, \+9,0 pontos\./)).toBeInTheDocument();
    const context = within(dialog).getByRole('list', { name: 'Contexto do deal' });
    expect(within(context).getAllByRole('listitem')).toHaveLength(2);
    expect(within(context).getByText('Você fecha 74% dos GTX Pro (52 deals).')).toBeInTheDocument();
    expect(within(context).queryByText(/pts/)).not.toBeInTheDocument();
    expect(within(dialog).queryByText(/Modelo estatístico/)).not.toBeInTheDocument();
    expect(within(dialog).queryByText(/Prob\. de fechar/)).not.toBeInTheDocument();
    expect(within(dialog).getByText(/Fecham 71% dos GTX Pro/)).toBeInTheDocument();
    expect(within(dialog).getByText('Histórico da conta')).toBeInTheDocument();
    await user.keyboard('{Escape}');
    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument());
    expect(location()).not.toContain('deal=');
    expect(title).toHaveFocus();
  });

  it('hides the account section and shows the banner when the account is unknown', async () => {
    const user = userEvent.setup();
    renderApp('/?as_of=2017-12-31&n=50');
    await screen.findByRole('list', { name: 'Deals por prioridade' });
    await user.click(screen.getAllByRole('button', { name: /Registrar conta de/ })[0]!);
    const dialog = await screen.findByRole('dialog');
    expect(within(dialog).queryByText('Histórico da conta')).not.toBeInTheDocument();
    expect(within(dialog).getByText(/^Conta não informada no CRM/)).toBeInTheDocument();
    expect(within(dialog).getByRole('button', { name: 'Conta corrigida' })).toHaveFocus();
  });

  it('records feedback optimistically and confirms with the API time', async () => {
    const user = userEvent.setup();
    renderApp('/?as_of=2017-12-31&agent=Darcel%20Schlecht');
    await user.click(
      await screen.findByRole('button', { name: /Abrir detalhe de Konex · GTX Pro/ }),
    );
    const dialog = await screen.findByRole('dialog');
    await user.click(within(dialog).getByRole('button', { name: 'Contatado' }));
    expect(within(dialog).getByRole('button', { name: 'Contatado' })).toHaveAttribute(
      'aria-pressed',
      'true',
    );
    await waitFor(() =>
      expect(within(dialog).getByText(/Registrado "Contatado" às/)).toBeInTheDocument(),
    );
    await user.keyboard('{Escape}');
    expect(screen.getByText('Contatado hoje')).toBeInTheDocument();
  });

  it('rolls back the optimistic state and toasts when the POST fails', async () => {
    server.use(
      http.post('*/api/v1/feedback', async () => {
        await delay(150);
        return HttpResponse.json({ error: { code: 'INTERNAL', message: 'boom' } }, { status: 500 });
      }),
    );
    const user = userEvent.setup();
    renderApp('/?as_of=2017-12-31&agent=Darcel%20Schlecht');
    await user.click(
      await screen.findByRole('button', { name: /Abrir detalhe de Konex · GTX Pro/ }),
    );
    const dialog = await screen.findByRole('dialog');
    await user.click(within(dialog).getByRole('button', { name: 'Reunião marcada' }));
    expect(within(dialog).getByRole('button', { name: 'Reunião marcada' })).toHaveAttribute(
      'aria-pressed',
      'true',
    );
    await waitFor(() =>
      expect(within(dialog).getByRole('button', { name: 'Reunião marcada' })).toHaveAttribute(
        'aria-pressed',
        'false',
      ),
    );
    expect(
      screen
        .getAllByRole('alert')
        .some((a) => a.textContent?.includes('Não foi possível registrar a ação.')),
    ).toBe(true);
    expect(within(dialog).getByRole('button', { name: 'Tentar de novo' })).toBeInTheDocument();
    await user.keyboard('{Escape}');
    expect(screen.queryByText('Reunião marcada hoje')).not.toBeInTheDocument();
  });

  it('asks for confirmation before discarding and offers undo', async () => {
    const user = userEvent.setup();
    renderApp('/?as_of=2017-12-31&agent=Darcel%20Schlecht');
    const rowTitle = await screen.findByRole('button', {
      name: /Abrir detalhe de Konex · GTX Pro/,
    });
    await user.click(rowTitle);
    const dialog = await screen.findByRole('dialog');
    await user.click(within(dialog).getByRole('button', { name: 'Ocultar da minha fila' }));
    const confirm = within(dialog).getByRole('alertdialog');
    expect(within(confirm).getByRole('button', { name: 'Cancelar' })).toHaveFocus();
    await user.click(within(confirm).getByRole('button', { name: 'Confirmar' }));
    await user.keyboard('{Escape}');
    await waitFor(() =>
      expect(
        screen.queryByRole('button', { name: /Abrir detalhe de Konex · GTX Pro/ }),
      ).not.toBeInTheDocument(),
    );
    await user.click(screen.getByRole('button', { name: 'desfazer' }));
    expect(
      await screen.findByRole('button', { name: /Abrir detalhe de Konex · GTX Pro/ }),
    ).toBeInTheDocument();
  });

  it('shows the artifacts-missing card with the exact command on 503', async () => {
    server.use(
      http.get('*/api/v1/deals', () => HttpResponse.json(artifactsMissing, { status: 503 })),
    );
    renderApp('/?as_of=2017-12-31');
    expect(await screen.findByText('Ainda não há scores gerados.')).toBeInTheDocument();
    expect(screen.getByText('cd solution && make pipeline')).toBeInTheDocument();
    expect(screen.getByText('docker compose --profile pipeline up')).toBeInTheDocument();
    expect(screen.queryByRole('list', { name: 'Deals por prioridade' })).not.toBeInTheDocument();
  });

  it('shows the API error state with retry on 500', async () => {
    server.use(
      http.get('*/api/v1/deals', () =>
        HttpResponse.json({ error: { code: 'X', message: 'x' } }, { status: 500 }),
      ),
    );
    renderApp('/?as_of=2017-12-31');
    const alert = await screen.findByRole('alert', {}, { timeout: 5000 });
    expect(alert).toHaveTextContent('Não foi possível carregar os deals.');
    expect(alert).toHaveTextContent('erro 500');
    expect(within(alert).getByRole('button', { name: 'Tentar de novo' })).toHaveFocus();
  });

  it('shows the empty state for a filter with no deals', async () => {
    renderApp('/?as_of=2017-12-31&agent=Ningu%C3%A9m');
    expect(await screen.findByText('Nenhum deal aberto neste recorte.')).toBeInTheDocument();
    expect(
      within(screen.getByRole('main')).getByRole('button', { name: 'Limpar filtros' }),
    ).toBeInTheDocument();
  });

  it('keeps sort in the URL and warns that priority stays on the badge', async () => {
    const user = userEvent.setup();
    renderApp('/?as_of=2017-12-31');
    await screen.findByRole('list', { name: 'Deals por prioridade' });
    await user.selectOptions(screen.getByLabelText('Ordenar por'), 'value');
    expect(location()).toContain('sort=value');
    expect(await screen.findByText(/Ordenado por outro critério/)).toBeInTheDocument();
  });

  it('shows the "confirm or close" queue with age bands, quota and no tier badge', async () => {
    const user = userEvent.setup();
    renderApp('/?as_of=2017-12-31&manager=Melvin%20Marxen');
    await screen.findByRole('list', { name: 'Deals por prioridade' });
    await user.click(screen.getByRole('tab', { name: /Confirmar ou encerrar/ }));
    expect(location()).toContain('queue=confirm');
    const list = await screen.findByRole('list', { name: 'Confirmar ou encerrar' });
    const rows = within(list).getAllByRole('listitem');
    expect(rows.length).toBeGreaterThan(0);
    expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuemax', '5');
    expect(screen.getByText(/nominais fora do forecast até você confirmar/)).toBeInTheDocument();
    expect(within(list).getAllByText('fora do forecast').length).toBe(rows.length);
    expect(within(list).getAllByText('Sem histórico de fechamento nesta idade').length).toBe(
      rows.length,
    );
    expect(within(list).queryByLabelText(/^Tier [A-D] —/)).not.toBeInTheDocument();
    expect(screen.getAllByText(/Faixa de idade: 139–180 dias/).length).toBe(1);
    expect(document.body.textContent).not.toMatch(/zumbi/i);
  });

  it('records "Encerrado no CRM" as closed_in_crm', async () => {
    const user = userEvent.setup();
    let posted: unknown;
    server.use(
      http.post('*/api/v1/feedback', async ({ request }) => {
        posted = await request.json();
        return HttpResponse.json(
          {
            ...(posted as object),
            id: '1',
            recorded_at: '2026-09-23T10:00:00Z',
            as_of: '2017-12-31',
            model_version: 'v',
            priority_score: 1,
            note: null,
          },
          { status: 201 },
        );
      }),
    );
    renderApp('/?as_of=2017-12-31&agent=Darcel%20Schlecht');
    await user.click(
      await screen.findByRole('button', { name: /Abrir detalhe de Konex · GTX Pro/ }),
    );
    const dialog = await screen.findByRole('dialog');
    await user.click(within(dialog).getByRole('button', { name: 'Encerrado no CRM' }));
    await waitFor(() =>
      expect(within(dialog).getByText(/Registrado "Encerrado no CRM"/)).toBeInTheDocument(),
    );
    expect(posted).toMatchObject({ action: 'closed_in_crm', opportunity_id: 'Z063OYW0' });
  });
});
