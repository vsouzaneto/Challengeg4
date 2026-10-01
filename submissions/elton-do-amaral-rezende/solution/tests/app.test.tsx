import { beforeEach, afterEach, describe, expect, it, vi } from 'vitest';
import { render, screen, fireEvent, cleanup, act } from '@testing-library/react';
import type { ComponentType } from 'react';

let App: ComponentType;
beforeEach(async () => {
  cleanup(); localStorage.clear(); vi.resetModules();
  vi.useFakeTimers(); vi.setSystemTime(new Date('2026-09-30T15:00:00Z'));
  App = (await import('../src/App')).App;
});
afterEach(() => { cleanup(); vi.useRealTimers(); vi.restoreAllMocks(); });
const choose = (seller = 'Darcel Schlecht') => fireEvent.change(screen.getByLabelText('Sua carteira'), { target: { value: seller } });

describe('jornada integrada', () => {
  it('carteira sem oportunidades não inventa meta ou missão e permite trocar de vendedor', async () => {
    const { dataset } = await import('../src/data/dataset');
    const emptySeller = dataset.agents.find((a) => !dataset.opportunities.some((o) => o.salesAgent === a.name))!;
    render(<App />); choose(emptySeller.name);
    expect(screen.queryByTestId('expanded-mission')).not.toBeInTheDocument();
    expect(screen.getByText('Esta carteira não tem oportunidades abertas disponíveis hoje.')).toBeInTheDocument();
    expect(screen.getByText('Sem oportunidades, não há conquista de meta neste dia.')).toBeInTheDocument();
    choose();
    expect(screen.getAllByTestId('expanded-mission')).toHaveLength(1);
  });
  it('exporta somente a carteira selecionada com dados reais', async () => {
    const { dataset } = await import('../src/data/dataset');
    const createObjectURL = vi.fn().mockReturnValue('blob:test');
    const originalCreate = Object.getOwnPropertyDescriptor(URL, 'createObjectURL');
    const originalRevoke = Object.getOwnPropertyDescriptor(URL, 'revokeObjectURL');
    Object.defineProperty(URL, 'createObjectURL', { configurable: true, value: createObjectURL });
    Object.defineProperty(URL, 'revokeObjectURL', { configurable: true, value: vi.fn() });
    vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {});
    const blobs: unknown[][] = [];
    const OriginalBlob = globalThis.Blob;
    vi.stubGlobal('Blob', class extends OriginalBlob {
      constructor(parts: BlobPart[], options?: BlobPropertyBag) { super(parts, options); blobs.push(parts); }
    });
    try {
      render(<App />); choose();
      fireEvent.click(screen.getByText('Opções da equipe'));
      fireEvent.click(screen.getByRole('button', { name: 'Exportar carteira selecionada' }));
      const csv = String(blobs[0][0]);
      expect(csv).toContain('"opportunity_id"');
      const lines = csv.split('\r\n').slice(1);
      const expected = dataset.opportunities.filter((o) => o.salesAgent === 'Darcel Schlecht');
      expect(lines).toHaveLength(expected.length);
      for (const o of expected) expect(csv).toContain(`"${o.opportunityId}","Darcel Schlecht"`);
      expect(csv).not.toContain('"Zane Levy"');
      expect(createObjectURL).toHaveBeenCalledOnce();
    } finally {
      vi.unstubAllGlobals();
      if (originalCreate) Object.defineProperty(URL, 'createObjectURL', originalCreate); else Reflect.deleteProperty(URL, 'createObjectURL');
      if (originalRevoke) Object.defineProperty(URL, 'revokeObjectURL', originalRevoke); else Reflect.deleteProperty(URL, 'revokeObjectURL');
    }
  });
  it('abre a carteira inicial de Zane com dez prioridades e sem progresso inventado', () => {
    render(<App />);
    expect(screen.getByLabelText('Sua carteira')).toHaveValue('Zane Levy');
    expect(screen.queryByText('Uma boa rotina começa com prioridades claras.')).not.toBeInTheDocument();
    expect(screen.getByTestId('expanded-mission')).toHaveTextContent('The New York Inquirer');
    expect(screen.getAllByTestId('expanded-mission')).toHaveLength(1);
    expect(screen.getByText('0 concluídas hoje')).toBeInTheDocument();
    expect(screen.getAllByRole('button', { name: /^Abrir missão/ })).toHaveLength(9);
  });
  it('preserva a última carteira escolhida em vez de voltar à inicial', () => {
    const view = render(<App />);
    choose('Moses Frase');
    fireEvent.click(screen.getByRole('button', { name: 'Feito' }));
    view.unmount(); render(<App />);
    expect(screen.getByLabelText('Sua carteira')).toHaveValue('Moses Frase');
    expect(screen.getByText('1 concluída hoje')).toBeInTheDocument();
  });
  it('usa a carteira inicial quando a escolha salva não é um vendedor válido', async () => {
    const { dataset } = await import('../src/data/dataset');
    localStorage.setItem(`lead-scorer:selection:${dataset.datasetVersion}`, JSON.stringify('Vendedor inexistente'));
    render(<App />);
    expect(screen.getByLabelText('Sua carteira')).toHaveValue('Zane Levy');
    expect(screen.getAllByTestId('expanded-mission')).toHaveLength(1);
  });
  it('seleção mantém ordem, foco e compactos acima/abaixo sem concluir', () => {
    const { container } = render(<App />); choose();
    fireEvent.click(screen.getByRole('button', { name: /^Abrir missão 7:/ }));
    expect(container.querySelectorAll('.mission-above')).toHaveLength(6);
    expect(container.querySelectorAll('.mission-below')).toHaveLength(3);
    expect(screen.getAllByTestId('expanded-mission')).toHaveLength(1);
    expect(screen.getByText('0 concluídas hoje')).toBeInTheDocument();
    expect(document.activeElement?.id).toMatch(/^mission-/);
  });
  it('conclui, adia, desfaz e restaura após recarregar', () => {
    const view = render(<App />); choose();
    fireEvent.click(screen.getByRole('button', { name: 'Feito' }));
    expect(screen.getByText('1 concluída hoje')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Adiar para amanhã' }));
    expect(screen.getByText(/1 adiada para amanhã/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /^Desfazer$/ }));
    expect(screen.queryByText(/1 adiada para amanhã/)).not.toBeInTheDocument();
    view.unmount(); render(<App />);
    expect(screen.getByText('1 concluída hoje')).toBeInTheDocument();
    expect(screen.getAllByTestId('expanded-mission')).toHaveLength(1);
  });
  it('isola vendedores e carrega lote seguinte sem duplicar os IDs anteriores', () => {
    const { container } = render(<App />); choose();
    const oldIds = [...container.querySelectorAll('[data-opportunity-id]')].map((e) => e.getAttribute('data-opportunity-id'));
    for (let i = 0; i < 10; i++) fireEvent.click(screen.getByRole('button', { name: 'Feito' }));
    expect(screen.getByText('10 concluídas hoje')).toBeInTheDocument();
    expect(screen.getByText(/Mais 10 prioridades/)).toBeInTheDocument();
    expect(container.querySelectorAll('.compact-mission')).toHaveLength(9);
    expect([...container.querySelectorAll('[data-opportunity-id]')].every((e) => !oldIds.includes(e.getAttribute('data-opportunity-id')))).toBe(true);
    choose('Moses Frase'); expect(screen.getByText('0 concluídas hoje')).toBeInTheDocument();
    choose(); expect(screen.getByText('10 concluídas hoje')).toBeInTheDocument();
  });
  it('renova a fila no dia seguinte ao retornar à aba', () => {
    render(<App />); choose();
    fireEvent.click(screen.getByRole('button', { name: 'Feito' }));
    expect(screen.getByText('1 concluída hoje')).toBeInTheDocument();
    act(() => { vi.setSystemTime(new Date('2026-10-01T15:00:00Z')); window.dispatchEvent(new Event('focus')); });
    expect(screen.getByText('0 concluídas hoje')).toBeInTheDocument();
    expect(screen.getByText('31/12/2017')).toBeInTheDocument();
  });
  it('cópia não altera progresso e trata falha da área de transferência', async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, 'clipboard', { configurable: true, value: { writeText } });
    render(<App />); choose();
    await act(async () => { fireEvent.click(screen.getByRole('button', { name: 'Copiar orientação' })); });
    expect(writeText).toHaveBeenCalledOnce();
    expect(screen.getByText('0 concluídas hoje')).toBeInTheDocument();
    expect(screen.getByText(/A missão continua pendente/)).toBeInTheDocument();
    writeText.mockRejectedValueOnce(new Error('Bloqueado'));
    await act(async () => { fireEvent.click(screen.getByRole('button', { name: 'Copiar orientação' })); });
    expect(screen.getByText(/Não foi possível copiar automaticamente/)).toBeInTheDocument();
  });
  it('renova antes de agir se a data virou sem evento de retorno à aba', () => {
    render(<App />); choose();
    vi.setSystemTime(new Date('2026-10-01T03:00:00Z'));
    fireEvent.click(screen.getByRole('button', { name: 'Feito' }));
    expect(screen.getByText('0 concluídas hoje')).toBeInTheDocument();
    expect(screen.getByText(/O dia mudou/)).toBeInTheDocument();
  });
  it('mantém a jornada na sessão quando localStorage está bloqueado', () => {
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => { throw new Error('Bloqueado'); });
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => { throw new Error('Bloqueado'); });
    render(<App />); choose();
    fireEvent.click(screen.getByRole('button', { name: 'Feito' }));
    expect(screen.getByText('1 concluída hoje')).toBeInTheDocument();
    expect(screen.getByText(/apenas nesta sessão/)).toBeInTheDocument();
    choose('Moses Frase'); choose();
    expect(screen.getByText('1 concluída hoje')).toBeInTheDocument();
  });
  it('rejeita fila persistida que aponta para uma oportunidade desconhecida', async () => {
    const { dataset } = await import('../src/data/dataset');
    const { storageKey } = await import('../src/state/storage');
    localStorage.setItem(`lead-scorer:selection:${dataset.datasetVersion}`, JSON.stringify('Darcel Schlecht'));
    localStorage.setItem(storageKey(dataset.datasetVersion, 'Darcel Schlecht'), JSON.stringify({ schemaVersion: 1, datasetVersion: dataset.datasetVersion, salesAgent: 'Darcel Schlecht', days: { '2026-09-30': { dayKey: '2026-09-30', goal: 1, ranking: ['fake'], cursor: 1, batchNumber: 1, batch: ['fake'], active: 'fake', returns: [], actions: {} } } }));
    expect(localStorage.getItem(`lead-scorer:selection:${dataset.datasetVersion}`)).toBe(JSON.stringify('Darcel Schlecht'));
    render(<App />);
    expect(screen.getAllByTestId('expanded-mission')).toHaveLength(1);
    expect(screen.getByText(/apenas nesta sessão/)).toBeInTheDocument();
    expect(screen.getByText('0 concluídas hoje')).toBeInTheDocument();
  });
});
