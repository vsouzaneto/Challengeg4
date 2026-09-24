import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { HttpResponse, http } from 'msw';
import { axe } from 'vitest-axe';
import { artifactsMissing } from '../mocks/handlers';
import { server } from '../mocks/server';
import { renderApp } from './utils';

// axe-core in jsdom cannot compute real colours, so contrast is proven in design-tokens.md §2.
const options = { rules: { 'color-contrast': { enabled: false } } };

describe('axe', () => {
  it('queue with data has no violations', async () => {
    const { container } = renderApp('/?as_of=2017-12-31&agent=Darcel%20Schlecht');
    await screen.findByRole('list', { name: 'Deals por prioridade' });
    expect(await axe(container, options)).toHaveNoViolations();
  });

  it('open drawer has no violations', async () => {
    const user = userEvent.setup();
    const { baseElement } = renderApp('/?as_of=2017-12-31&agent=Darcel%20Schlecht');
    await user.click(await screen.findByRole('button', { name: /Abrir detalhe de Konex/ }));
    await screen.findByRole('dialog');
    expect(await axe(baseElement, options)).toHaveNoViolations();
  });

  it('empty and artifacts-missing states have no violations', async () => {
    const a = renderApp('/?as_of=2017-12-31&agent=Ningu%C3%A9m');
    await screen.findByText('Nenhum deal aberto neste recorte.');
    expect(await axe(a.container, options)).toHaveNoViolations();
    a.unmount();
    server.use(
      http.get('*/api/v1/deals', () => HttpResponse.json(artifactsMissing, { status: 503 })),
    );
    const b = renderApp('/?as_of=2017-12-31');
    await screen.findByText('Ainda não há scores gerados.');
    expect(await axe(b.container, options)).toHaveNoViolations();
  });

  it('team and quality screens have no violations', async () => {
    const a = renderApp('/time?as_of=2017-12-31&manager=Melvin%20Marxen');
    await screen.findByRole('table', { name: /Por vendedor/ });
    expect(await axe(a.container, options)).toHaveNoViolations();
    a.unmount();
    const b = renderApp('/qualidade?as_of=2017-12-31');
    await screen.findByText('1. Ela acerta mais quem vai fechar?');
    expect(await axe(b.container, options)).toHaveNoViolations();
  });
});
