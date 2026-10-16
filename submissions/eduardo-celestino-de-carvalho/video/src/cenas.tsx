// As dez cenas do tutorial. Cada uma recebe sua entrada de narracao.json e marca eventos pelas frases narradas.
import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {
  Caixa, Captura, Contador, Destaque, FundoMarca, Plano, Rotulo, TextoRevela, camera, caixa, mola, naTela, surge,
} from './kit';
import {ALTURA, LARGURA, cor, fonte, fonteMarca} from './tema';

export type Cena = {
  id: string; texto: string; audio: string; fala: number; duracaoFala: number; inicio: number; duracao: number;
  deQuadro: number; quadros: number; legendas: {inicio: number; fim: number; texto: string}[];
};

/** Quadro (relativo à cena) em que começa a frase `k`; `fracao` avança dentro dela. */
const useMarcas = (c: Cena) => {
  const {fps} = useVideoConfig();
  const q = (t: number) => Math.round(t * fps) - c.deQuadro;
  return (k: number, fracao = 0) => {
    const l = c.legendas[Math.min(k, c.legendas.length - 1)];
    return q(l.inicio + (l.fim - l.inicio) * fracao);
  };
};

/** 1 dentro de [de, ate), com entrada e saída suaves. */
const janela = (frame: number, de: number, ate = Infinity) =>
  surge(frame, de, 10) * (Number.isFinite(ate) ? 1 - surge(frame, ate, 10) : 1);

const Cursor: React.FC<{de: [number, number]; para: [number, number]; inicio: number; clique: number}> = ({de, para, inicio, clique}) => {
  const frame = useCurrentFrame();
  const t = interpolate(frame, [inicio, clique - 4], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const e = 1 - Math.pow(1 - t, 3);
  const x = de[0] + (para[0] - de[0]) * e;
  const y = de[1] + (para[1] - de[1]) * e;
  const onda = interpolate(frame, [clique, clique + 18], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const aperto = frame >= clique && frame < clique + 6 ? 0.86 : 1;
  if (frame < inicio) return null;
  return (
    <>
      {frame >= clique && onda < 1 && (
        <div style={{position: 'absolute', left: x - 40 * onda, top: y - 40 * onda, width: 80 * onda, height: 80 * onda,
          borderRadius: '50%', border: `4px solid ${cor.ouro}`, opacity: 1 - onda}} />
      )}
      <svg width="46" height="46" viewBox="0 0 24 24" style={{position: 'absolute', left: x - 6, top: y - 3, transform: `scale(${aperto})`,
        filter: 'drop-shadow(0 4px 8px rgba(0,0,0,.4))'}}>
        <path d="M4 2 L4 19 L8.5 14.8 L11.6 21.5 L14.4 20.3 L11.4 13.8 L17.5 13.8 Z" fill="white" stroke={cor.navy} strokeWidth="1.3" strokeLinejoin="round" />
      </svg>
    </>
  );
};

const centro = (b: Caixa): [number, number] => [b[0] + b[2] / 2, b[1] + b[3] / 2];

// ------------------------------------------------------------------ 1. abertura
export const Abertura: React.FC<{c: Cena}> = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const colunas: [string, string][] = [['Negociar', cor.negociar], ['Qualificar', cor.qualificar], ['Confirmar ou encerrar', cor.encerrar]];
  return (
    <FundoMarca>
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 28}}>
        <div style={{display: 'flex', alignItems: 'center', gap: 34, transform: `scale(${0.9 + 0.1 * mola(frame, fps)})`, opacity: mola(frame, fps)}}>
          <span style={{fontFamily: fonteMarca, fontSize: 120, color: cor.ouro, fontWeight: 700}}>G4</span>
          <span style={{width: 3, height: 110, background: 'rgba(255,255,255,.25)'}} />
          <TextoRevela texto="Lead Kanban" de={8} tamanho={124} passo={6} />
        </div>
        <div style={{fontFamily: fonte, fontSize: 36, color: cor.ouroClaro, fontWeight: 600, letterSpacing: 6,
          textTransform: 'uppercase', opacity: surge(frame, 30, 20)}}>Tutorial de uso · 2 minutos</div>
        <div style={{display: 'flex', gap: 24, marginTop: 40}}>
          {colunas.map(([nome, tinta], i) => {
            const v = mola(frame, fps, 44 + i * 7);
            return (
              <div key={nome} style={{width: 330, opacity: v, transform: `translateY(${(1 - v) * 30}px)`}}>
                <div style={{height: 10, borderRadius: 5, background: tinta, transform: `scaleX(${v})`, transformOrigin: 'left'}} />
                <div style={{fontFamily: fonte, fontSize: 30, color: 'white', fontWeight: 700, marginTop: 14}}>{nome}</div>
              </div>
            );
          })}
        </div>
      </AbsoluteFill>
    </FundoMarca>
  );
};

// ------------------------------------------------------------------ 2. problema
export const Problema: React.FC<{c: Cena}> = ({c}) => {
  const frame = useCurrentFrame();
  const m = useMarcas(c);
  const pergunta = m(1);
  const colunas = 22;
  const linhas = 13;
  return (
    <FundoMarca>
      <div style={{position: 'absolute', left: 130, top: 300, width: 700}}>
        <Contador ate={2089} de={4} dur={50} estilo={{fontFamily: fonte, fontSize: 230, fontWeight: 800, color: 'white', letterSpacing: -6}} />
        <div style={{fontFamily: fonte, fontSize: 52, color: cor.ouroClaro, fontWeight: 600, opacity: surge(frame, 20)}}>oportunidades abertas</div>
        <div style={{fontFamily: fonte, fontSize: 34, color: 'rgba(255,255,255,.7)', marginTop: 26, opacity: surge(frame, m(0, 0.6))}}>
          e o tempo de cada vendedor é limitado
        </div>
      </div>
      <div style={{position: 'absolute', left: 900, top: 190, display: 'grid', gridTemplateColumns: `repeat(${colunas}, 34px)`, gap: 9,
        opacity: 1 - 0.75 * surge(frame, pergunta, 16)}}>
        {Array.from({length: colunas * linhas}, (_, i) => {
          const ordem = (i * 37) % (colunas * linhas);
          const v = surge(frame, 6 + ordem / 7, 8);
          const tinta = [cor.negociar, cor.qualificar, cor.encerrar][(i * 7) % 10 < 2 ? 0 : (i * 7) % 10 < 5 ? 1 : 2];
          return <div key={i} style={{width: 34, height: 46, borderRadius: 6, background: 'white', opacity: v * 0.9,
            borderTop: `5px solid ${tinta}`, transform: `scale(${0.6 + 0.4 * v})`}} />;
        })}
      </div>
      <div style={{position: 'absolute', left: 900, top: 470, width: 900, textAlign: 'center'}}>
        <TextoRevela texto="Por qual negócio *começar?*" de={pergunta} tamanho={86} passo={5} />
      </div>
    </FundoMarca>
  );
};

// ------------------------------------------------------------------ 3. prazo de 138 dias
export const Prazo: React.FC<{c: Cena}> = ({c}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const m = useMarcas(c);
  const x0 = 160;
  const x1 = 1760;
  const maxDias = 400;
  const px = (d: number) => x0 + ((x1 - x0) * d) / maxDias;
  const fecharam = mola(frame, fps, m(1), 60);
  const parado = surge(frame, m(2), 24);
  const y = 560;
  return (
    <FundoMarca>
      <div style={{position: 'absolute', left: x0, top: 130, width: 1600}}>
        <TextoRevela texto="O histórico ajuda a responder" tamanho={64} />
      </div>
      {/* eixo */}
      <div style={{position: 'absolute', left: x0, top: y + 70, width: x1 - x0, height: 3, background: 'rgba(255,255,255,.3)'}} />
      {[0, 100, 200, 300, 400].map((d) => (
        <div key={d} style={{position: 'absolute', left: px(d) - 60, top: y + 86, width: 120, textAlign: 'center',
          fontFamily: fonte, fontSize: 26, color: 'rgba(255,255,255,.6)'}}>{d} dias</div>
      ))}
      {/* vendas concluídas até 138 dias */}
      <div style={{position: 'absolute', left: x0, top: y, height: 60, width: (px(138) - x0) * fecharam, borderRadius: '10px 0 0 10px',
        background: cor.negociar}} />
      <div style={{position: 'absolute', left: x0, top: y - 74, fontFamily: fonte, fontSize: 34, fontWeight: 700, color: 'white',
        opacity: surge(frame, m(1) + 14)}}>
        <Contador ate={6711} de={m(1)} dur={36} /> vendas fecharam aqui
      </div>
      {/* marco de 138 dias */}
      <div style={{position: 'absolute', left: px(138) - 2, top: y - 120, width: 4, height: 200, background: cor.ouro, opacity: surge(frame, m(1) + 20)}} />
      <div style={{position: 'absolute', left: px(138) - 120, top: y - 190, width: 240, textAlign: 'center', fontFamily: fonte,
        fontSize: 56, fontWeight: 800, color: cor.ouro, opacity: surge(frame, m(1) + 20)}}>138 dias</div>
      <div style={{position: 'absolute', left: px(138) + 30, top: y + 6, fontFamily: fonte, fontSize: 34, fontWeight: 700,
        color: cor.ouroClaro, opacity: surge(frame, m(1, 0.6)) * (1 - parado)}}>nenhuma venda depois</div>
      {/* parados */}
      <div style={{position: 'absolute', left: px(138) + 6, top: y, height: 60, width: (x1 - px(138) - 6) * parado, borderRadius: '0 10px 10px 0',
        background: `repeating-linear-gradient(135deg, ${cor.encerrar}, ${cor.encerrar} 14px, #8f3424 14px, #8f3424 28px)`}} />
      <div style={{position: 'absolute', left: px(220), top: y + 160, width: 760, fontFamily: fonte, color: 'white', opacity: surge(frame, m(2) + 18)}}>
        <div style={{fontSize: 96, fontWeight: 800, color: '#e58a73'}}><Contador ate={81} de={m(2) + 18} dur={30} sufixo="%" /></div>
        <div style={{fontSize: 34, fontWeight: 600}}>dos negócios em negociação já passaram do prazo: <span style={{color: '#e58a73'}}>estão parados</span></div>
      </div>
    </FundoMarca>
  );
};

// ------------------------------------------------------------------ 4. as três colunas
export const Colunas: React.FC<{c: Cena}> = ({c}) => {
  const frame = useCurrentFrame();
  const m = useMarcas(c);
  const t = camera(frame, [{de: 0, alvo: 'tudo'}]);
  const lanes: [string, string, string, number][] = [
    ['negociar', cor.negociar, 'Negociar: dentro do prazo, com chance real de fechar', 1],
    ['qualificar', cor.qualificar, 'Qualificar: em prospecção, precisa provar necessidade, decisor e prazo', 2],
    ['encerrar', cor.encerrar, 'Confirmar ou encerrar: passou do prazo, pede uma decisão', 3],
  ];
  return (
    <AbsoluteFill>
      <Captura tela="pipeline" t={t} />
      {/* primeira frase: as três colunas juntas */}
      {lanes.map(([nome, tinta]) => (
        <div key={nome} style={{position: 'absolute', ...posicao(naTela(caixa('pipeline', nome), t)), border: `5px solid ${tinta}`,
          borderRadius: 18, opacity: janela(frame, 6, m(1))}} />
      ))}
      {lanes.map(([nome, tinta, texto, k]) => {
        const b = naTela(caixa('pipeline', nome), t);
        const v = janela(frame, m(k), k < 3 ? m(k + 1) : Infinity);
        return (
          <React.Fragment key={nome}>
            <Destaque b={b} visivel={v} cor={tinta} raio={18} />
            <Rotulo b={[b[0], 560, b[2], 10]} visivel={v} texto={texto} lado="baixo" largura={Math.min(520, b[2])} />
          </React.Fragment>
        );
      })}
    </AbsoluteFill>
  );
};

const posicao = (b: Caixa) => ({left: b[0] - 8, top: b[1] - 8, width: b[2] + 16, height: b[3] + 16});

// ------------------------------------------------------------------ 5. ordem e cartão
export const Cartao: React.FC<{c: Cena}> = ({c}) => {
  const frame = useCurrentFrame();
  const m = useMarcas(c);
  const topoNegociar: Caixa = [112, 152, 555, 600];
  const planos: Plano[] = [
    {de: 0, alvo: 'tudo'},
    {de: 4, alvo: topoNegociar, margem: 1.15},
    {de: m(2), alvo: caixa('pipeline', 'cartao'), margem: 1.7},
  ];
  const t = camera(frame, planos);
  const cartao = naTela(caixa('pipeline', 'cartao'), t);
  const prazo = naTela(caixa('pipeline', 'prazo'), t);
  return (
    <AbsoluteFill>
      <Captura tela="pipeline" t={t} />
      <Rotulo b={naTela(topoNegociar, t)} visivel={janela(frame, m(0, 0.4), m(1))} texto="Os cartões já estão em ordem: maior valor primeiro" lado="direita" largura={520} />
      <Destaque b={cartao} visivel={janela(frame, m(1), m(2, 0.45))} />
      <Rotulo b={cartao} visivel={janela(frame, m(1) + 6, m(2))} texto="Comece pelo número 1" lado="direita" largura={420} />
      <Rotulo b={cartao} visivel={janela(frame, m(2) + 26, m(2, 0.45))} texto="Produto, empresa e valor" lado="cima" largura={500} />
      <Destaque b={prazo} visivel={janela(frame, m(2, 0.5))} raio={10} />
      <Rotulo b={prazo} visivel={janela(frame, m(2, 0.5) + 6)} texto="Barra de prazo: quanto mais cheia, mais perto do limite" lado="baixo" largura={640} />
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ 6. filtros
export const Filtros: React.FC<{c: Cena}> = ({c}) => {
  const frame = useCurrentFrame();
  const m = useMarcas(c);
  const barra: Caixa = [920, 0, 1000, 64];
  const t = camera(frame, [{de: 0, alvo: barra, margem: 1.05}, {de: m(1) - 6, alvo: 'tudo'}]);
  const clique = m(0, 0.55);
  // Com filtro ativo aparece o botão "Limpar" e o campo muda de lugar: cada momento usa a sua captura.
  const alvoCursor = naTela(caixa('pipeline', 'vendedor'), t);
  const vendedor = frame < clique ? alvoCursor : naTela(caixa('filtrado', 'vendedor'), t);
  return (
    <AbsoluteFill>
      <Captura tela={frame < clique ? 'pipeline' : 'filtrado'} t={t} />
      <Destaque b={vendedor} visivel={janela(frame, m(0, 0.25), m(1))} raio={10} />
      <Rotulo b={vendedor} visivel={janela(frame, m(0, 0.3), m(1))} texto="Escolha o seu nome" lado="baixo" largura={380} />
      <Cursor de={[1500, 700]} para={centro(alvoCursor)} inicio={m(0, 0.2)} clique={clique} />
      {['negociar', 'qualificar', 'encerrar'].map((nome, i) => (
        <Destaque key={nome} b={naTela(caixa('filtrado', nome), t)} visivel={janela(frame, m(1) + 22 + i * 4) * 0.9}
          cor={[cor.negociar, cor.qualificar, cor.encerrar][i]} escuro={0.12} raio={18} />
      ))}
      <Rotulo b={[700, 820, 520, 10]} visivel={janela(frame, m(1) + 30)} texto="Só a sua carteira, em todas as telas" lado="baixo" largura={560} />
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ 7. detalhe
export const Detalhe: React.FC<{c: Cena}> = ({c}) => {
  const frame = useCurrentFrame();
  const m = useMarcas(c);
  const clique = m(0, 0.55);
  const abre = surge(frame, clique + 4, 16);
  const cartao = caixa('pipeline', 'cartao');
  const t = camera(frame, [{de: 0, alvo: 'tudo'}]);
  const partes: [string, string][] = [['acoes', 'O que fazer agora, com ações para marcar'], ['motivo', 'Por que está nesta coluna'], ['tempo', 'Tempo em negociação']];
  return (
    <AbsoluteFill>
      <Captura tela="pipeline" t={t} />
      <Destaque b={cartao} visivel={janela(frame, 4, clique + 8)} />
      <Cursor de={[900, 800]} para={centro(cartao)} inicio={6} clique={clique} />
      <AbsoluteFill style={{opacity: abre, transform: `scale(${0.94 + 0.06 * abre})`, transformOrigin: `${centro(cartao)[0]}px ${centro(cartao)[1]}px`}}>
        <Captura tela="detalhe" t={t} />
        {partes.map(([nome, texto], i) => {
          const de = m(1, i / 3);
          const ate = i < 2 ? m(1, (i + 1) / 3) : Infinity;
          const b = caixa('detalhe', nome);
          return (
            <React.Fragment key={nome}>
              <Destaque b={b} visivel={janela(frame, de, ate)} />
              <Rotulo b={b} visivel={janela(frame, de + 6, ate)} texto={texto} lado={nome === 'tempo' ? 'baixo' : 'esquerda'} largura={400} />
            </React.Fragment>
          );
        })}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ 8. dashboard
export const Dashboard: React.FC<{c: Cena}> = ({c}) => {
  const frame = useCurrentFrame();
  const m = useMarcas(c);
  const troca = m(1);
  const t = camera(frame, [{de: 0, alvo: 'tudo'}]);
  const evid = surge(frame, troca - 4, 14);
  const composicao = caixa('dashboard', 'composicao');
  const rankings = caixa('dashboard', 'rankings');
  const fatos = caixa('evidencias', 'fatos');
  return (
    <AbsoluteFill>
      <Captura tela="dashboard" t={t} />
      <Destaque b={composicao} visivel={janela(frame, m(0, 0.15), m(0, 0.62))} />
      <Rotulo b={composicao} visivel={janela(frame, m(0, 0.2), m(0, 0.62))} texto="Onde está o valor: por regional, manager ou vendedor" lado="baixo" largura={700} />
      <Destaque b={rankings} visivel={janela(frame, m(0, 0.66), troca)} />
      <Rotulo b={rankings} visivel={janela(frame, m(0, 0.7), troca)} texto="Rankings: quem precisa de apoio" lado="cima" largura={560} />
      <AbsoluteFill style={{opacity: evid, transform: `translateY(${(1 - evid) * 60}px)`}}>
        <Captura tela="evidencias" t={t} />
        <Destaque b={fatos} visivel={janela(frame, troca + 10)} />
        <Rotulo b={fatos} visivel={janela(frame, troca + 16)} texto="Os números que sustentam as regras" lado="baixo" largura={600} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ 9. ajuda
export const Ajuda: React.FC<{c: Cena}> = ({c}) => {
  const frame = useCurrentFrame();
  const m = useMarcas(c);
  const canto: Caixa = [1440, 0, 480, 64];
  const t = camera(frame, [{de: 0, alvo: 'tudo'}, {de: 4, alvo: canto, margem: 1.0}]);
  const botao = naTela(caixa('pipeline', 'ajuda'), t);
  const clique = m(1, 0.3);
  const abre = surge(frame, clique + 4, 18);
  const pulso = 1 + 0.08 * Math.sin(frame / 4);
  const tAjuda = camera(frame, [{de: 0, alvo: 'tudo'}]);
  return (
    <AbsoluteFill>
      <Captura tela="pipeline" t={t} />
      <Destaque b={[botao[0] - 6 * pulso, botao[1] - 6 * pulso, botao[2] + 12 * pulso, botao[3] + 12 * pulso]} visivel={janela(frame, m(0, 0.3), clique + 6)} raio={60} />
      <Rotulo b={botao} visivel={janela(frame, m(0, 0.4), clique + 6)} texto="Procedimento completo, regras e glossário" lado="esquerda" largura={520} />
      <Cursor de={[1000, 900]} para={centro(botao)} inicio={m(0, 0.5)} clique={clique} />
      <AbsoluteFill style={{opacity: abre, transform: `scale(${0.6 + 0.4 * abre})`, transformOrigin: '1790px 30px'}}>
        <Captura tela="ajuda" t={tAjuda} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ 10. rotina da semana
export const Rotina: React.FC<{c: Cena}> = ({c}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const m = useMarcas(c);
  const passos: [string, string, string][] = [
    ['1', 'Decida os parados', cor.encerrar],
    ['2', 'Negocie em ordem', cor.negociar],
    ['3', 'Qualifique as novas', cor.qualificar],
  ];
  const fim = m(4);
  const sai = surge(frame, fim, 16);
  return (
    <FundoMarca>
      <AbsoluteFill style={{alignItems: 'center', paddingTop: 150, opacity: 1 - sai}}>
        <TextoRevela texto="A rotina da *semana*" tamanho={84} />
        <div style={{display: 'flex', gap: 40, marginTop: 90}}>
          {passos.map(([n, texto, tinta], i) => {
            const v = mola(frame, fps, m(i + 1));
            return (
              <div key={n} style={{width: 470, height: 300, borderRadius: 24, background: 'white', padding: 40, opacity: v,
                transform: `translateY(${(1 - v) * 60}px)`, borderTop: `14px solid ${tinta}`, boxShadow: '0 24px 60px rgba(0,0,0,.35)'}}>
                <div style={{fontFamily: fonte, fontSize: 90, fontWeight: 800, color: tinta}}>{n}</div>
                <div style={{fontFamily: fonte, fontSize: 48, fontWeight: 800, color: cor.tinta, lineHeight: 1.1}}>{texto}</div>
              </div>
            );
          })}
        </div>
      </AbsoluteFill>
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 30, opacity: sai}}>
        <div style={{display: 'flex', alignItems: 'center', gap: 34}}>
          <span style={{fontFamily: fonteMarca, fontSize: 110, color: cor.ouro, fontWeight: 700}}>G4</span>
          <span style={{width: 3, height: 100, background: 'rgba(255,255,255,.25)'}} />
          <span style={{fontFamily: fonte, fontSize: 112, color: 'white', fontWeight: 800, letterSpacing: -1}}>Lead Kanban</span>
        </div>
        <div style={{fontFamily: fonte, fontSize: 38, color: cor.ouroClaro, fontWeight: 600}}>Bom trabalho! Dúvidas? Clique em <b>?</b> no topo do app.</div>
      </AbsoluteFill>
    </FundoMarca>
  );
};

export const CENAS: Record<string, React.FC<{c: Cena}>> = {
  abertura: Abertura, problema: Problema, prazo: Prazo, colunas: Colunas, cartao: Cartao,
  filtros: Filtros, detalhe: Detalhe, dashboard: Dashboard, ajuda: Ajuda, rotina: Rotina,
};

export const CAPITULOS: Record<string, string> = {
  abertura: 'Lead Kanban', problema: 'O desafio', prazo: 'O prazo de 138 dias', colunas: 'As três colunas',
  cartao: 'Ordem e cartão', filtros: 'Sua carteira', detalhe: 'Detalhe do negócio', dashboard: 'Dashboard',
  ajuda: 'Ajuda', rotina: 'Rotina da semana',
};

export {LARGURA, ALTURA};
