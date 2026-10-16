// Kit de animação: câmera sobre capturas reais, destaque com spotlight, rótulos, texto e números.
import React from 'react';
import {AbsoluteFill, Easing, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {ALTURA, LARGURA, cor, fonte} from './tema';
import caixas from './capturas.json';

export type Caixa = [number, number, number, number];
export type Tela = keyof typeof caixas;

export const caixa = (tela: Tela, nome: string): Caixa => {
  const b = (caixas[tela] as Record<string, number[]>)[nome];
  if (!b) throw new Error(`Caixa ausente: ${tela}.${nome}`);
  const [x, y, w, h] = b;
  return [x, y, w, Math.min(h, ALTURA - y - 8)]; // colunas longas: corta na borda da tela
};

/** Entrada com mola, de 0 a 1, a partir do quadro `de`. */
export const mola = (frame: number, fps: number, de = 0, rigidez = 120) =>
  spring({frame: frame - de, fps, config: {damping: 16, stiffness: rigidez, mass: 0.8}});

export const surge = (frame: number, de: number, dur = 14) =>
  interpolate(frame, [de, de + dur], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});

// ------------------------------------------------------------------ câmera
export type Plano = {de: number; alvo: Caixa | 'tudo'; margem?: number};
type Transform = {s: number; tx: number; ty: number};

const enquadrar = (alvo: Caixa | 'tudo', margem = 1.25): Transform => {
  if (alvo === 'tudo') return {s: 1, tx: 0, ty: 0};
  const [x, y, w, h] = alvo;
  const s = Math.min(3, Math.max(1, Math.min(LARGURA / (w * margem), ALTURA / (h * margem))));
  const cx = x + w / 2;
  const cy = y + h / 2;
  // Centraliza o alvo sem mostrar fora da captura.
  const tx = Math.min(0, Math.max(LARGURA - LARGURA * s, LARGURA / 2 - cx * s));
  const ty = Math.min(0, Math.max(ALTURA - ALTURA * s, ALTURA / 2 - cy * s));
  return {s, tx, ty};
};

export const camera = (frame: number, planos: Plano[], dur = 26): Transform => {
  let atual = enquadrar(planos[0].alvo, planos[0].margem);
  for (const p of planos.slice(1)) {
    const proximo = enquadrar(p.alvo, p.margem);
    const t = interpolate(frame, [p.de, p.de + dur], [0, 1], {
      extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic),
    });
    atual = {s: atual.s + (proximo.s - atual.s) * t, tx: atual.tx + (proximo.tx - atual.tx) * t, ty: atual.ty + (proximo.ty - atual.ty) * t};
  }
  // Câmera viva: deriva lenta e quase imperceptível.
  const deriva = 1 + 0.012 * Math.sin(frame / 90);
  return {s: atual.s * deriva, tx: atual.tx - (LARGURA * atual.s * (deriva - 1)) / 2, ty: atual.ty - (ALTURA * atual.s * (deriva - 1)) / 2};
};

export const naTela = (b: Caixa, t: Transform): Caixa => [b[0] * t.s + t.tx, b[1] * t.s + t.ty, b[2] * t.s, b[3] * t.s];

export const Captura: React.FC<{tela: Tela; t: Transform; escurecer?: number}> = ({tela, t, escurecer = 0}) => (
  <AbsoluteFill style={{backgroundColor: cor.papel}}>
    <Img
      src={staticFile(`capturas/${tela}.jpg`)}
      style={{position: 'absolute', width: LARGURA, height: ALTURA, transformOrigin: '0 0',
        transform: `translate(${t.tx}px, ${t.ty}px) scale(${t.s})`}}
    />
    {escurecer > 0 && <AbsoluteFill style={{backgroundColor: `rgba(3,26,38,${escurecer})`}} />}
  </AbsoluteFill>
);

/** Spotlight: escurece tudo fora da caixa (em coordenadas de tela) e contorna em dourado. */
export const Destaque: React.FC<{b: Caixa; visivel: number; raio?: number; cor?: string; escuro?: number}> = ({
  b, visivel, raio = 14, cor: borda = cor.ouro, escuro = 0.55,
}) => {
  if (visivel <= 0.001) return null;
  const pad = 8;
  return (
    <div style={{
      position: 'absolute', left: b[0] - pad, top: b[1] - pad, width: b[2] + pad * 2, height: b[3] + pad * 2,
      borderRadius: raio, border: `4px solid ${borda}`, opacity: visivel,
      boxShadow: `0 0 0 4000px rgba(3,26,38,${escuro * visivel}), 0 0 40px ${borda}88`,
    }} />
  );
};

/** Rótulo explicativo ancorado a uma caixa da tela. */
export const Rotulo: React.FC<{
  b: Caixa; visivel: number; texto: string; lado?: 'cima' | 'baixo' | 'direita' | 'esquerda'; largura?: number;
}> = ({b, visivel, texto, lado = 'baixo', largura = 460}) => {
  if (visivel <= 0.001) return null;
  const gap = 30;
  let left = b[0] + b[2] / 2 - largura / 2;
  let top = b[1] + b[3] + gap;
  if (lado === 'cima') top = b[1] - gap - 90;
  if (lado === 'direita') { left = b[0] + b[2] + gap; top = b[1] + b[3] / 2 - 45; }
  if (lado === 'esquerda') { left = b[0] - gap - largura; top = b[1] + b[3] / 2 - 45; }
  left = Math.max(40, Math.min(LARGURA - largura - 40, left));
  top = Math.max(40, Math.min(ALTURA - 140, top));
  return (
    <div style={{
      position: 'absolute', left, top, width: largura, padding: '20px 26px', borderRadius: 16,
      background: cor.navy, color: 'white', fontFamily: fonte, fontSize: 30, fontWeight: 600, lineHeight: 1.3,
      borderLeft: `6px solid ${cor.ouro}`, boxShadow: '0 18px 50px rgba(0,0,0,.35)',
      opacity: visivel, transform: `translateY(${(1 - visivel) * 18}px)`,
    }}>{texto}</div>
  );
};

/** Texto que entra palavra por palavra; trechos entre *asteriscos* ficam dourados. */
export const TextoRevela: React.FC<{texto: string; de?: number; tamanho?: number; cor?: string; passo?: number; peso?: number}> = ({
  texto, de = 0, tamanho = 72, cor: tinta = 'white', passo = 3, peso = 800,
}) => {
  const frame = useCurrentFrame();
  let destaque = false;
  return (
    <div style={{fontFamily: fonte, fontSize: tamanho, fontWeight: peso, color: tinta, lineHeight: 1.15, letterSpacing: -1}}>
      {texto.split(' ').map((palavra, i) => {
        const abre = palavra.startsWith('*');
        if (abre) destaque = true;
        const limpa = palavra.replace(/\*/g, '');
        const atual = destaque;
        if (palavra.endsWith('*')) destaque = false;
        const v = surge(frame, de + i * passo, 12);
        return (
          <span key={i} style={{display: 'inline-block', marginRight: '0.26em', opacity: v,
            transform: `translateY(${(1 - v) * 24}px)`, filter: `blur(${(1 - v) * 6}px)`, color: atual ? cor.ouro : tinta}}>
            {limpa}
          </span>
        );
      })}
    </div>
  );
};

/** Número que sobe até o valor, no formato brasileiro. */
export const Contador: React.FC<{ate: number; de?: number; dur?: number; estilo?: React.CSSProperties; sufixo?: string}> = ({
  ate, de = 0, dur = 40, estilo, sufixo = '',
}) => {
  const frame = useCurrentFrame();
  const v = interpolate(frame, [de, de + dur], [0, ate], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  return <span style={estilo}>{Math.round(v).toLocaleString('pt-BR')}{sufixo}</span>;
};

export const FundoMarca: React.FC<{children?: React.ReactNode}> = ({children}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const brilho = 0.5 + 0.5 * Math.sin(frame / fps / 3);
  return (
    <AbsoluteFill style={{background: `radial-gradient(1200px 700px at ${30 + brilho * 10}% 20%, ${cor.navy2}, ${cor.navy})`}}>
      <AbsoluteFill style={{
        backgroundImage: 'linear-gradient(rgba(255,255,255,.035) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.035) 1px, transparent 1px)',
        backgroundSize: '64px 64px',
      }} />
      {children}
    </AbsoluteFill>
  );
};
