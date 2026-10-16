// Composição: cenas encadeadas com transição sobreposta, narração por cena e barra de capítulos.
import React from 'react';
import {AbsoluteFill, Audio, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {CAPITULOS, CENAS, Cena} from './cenas';
import {cor, fonte} from './tema';
import narracao from './narracao.json';

const TRANSICAO = 12; // quadros em que a cena seguinte entra por cima da anterior

const Entrada: React.FC<{children: React.ReactNode; primeira: boolean}> = ({children, primeira}) => {
  const frame = useCurrentFrame();
  const v = primeira ? 1 : interpolate(frame, [0, TRANSICAO], [0, 1], {extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{opacity: v, transform: `scale(${1.03 - 0.03 * v})`}}>{children}</AbsoluteFill>;
};

const Capitulo: React.FC<{cenas: Cena[]}> = ({cenas}) => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const atual = [...cenas].reverse().find((c) => frame >= c.deQuadro) ?? cenas[0];
  const indice = cenas.indexOf(atual);
  if (indice === 0 || indice === cenas.length - 1) return null;
  return (
    <>
      <div style={{position: 'absolute', left: 40, bottom: 34, padding: '12px 22px', borderRadius: 999, background: 'rgba(3,26,38,.88)',
        color: 'white', fontFamily: fonte, fontSize: 24, fontWeight: 700, display: 'flex', gap: 14, alignItems: 'center'}}>
        <span style={{color: cor.ouro}}>{indice}/{cenas.length - 2}</span>
        <span>{CAPITULOS[atual.id]}</span>
      </div>
      <div style={{position: 'absolute', left: 0, bottom: 0, height: 6, width: `${(frame / durationInFrames) * 100}%`, background: cor.ouro}} />
    </>
  );
};

export const Tutorial: React.FC<{semAudio?: boolean}> = ({semAudio}) => {
  const {fps} = useVideoConfig();
  const cenas = narracao.cenas as Cena[];
  return (
    <AbsoluteFill style={{backgroundColor: cor.navy}}>
      {cenas.map((c, i) => {
        const Componente = CENAS[c.id];
        return (
          <Sequence key={c.id} from={c.deQuadro} durationInFrames={c.quadros + TRANSICAO} name={c.id}>
            <Entrada primeira={i === 0}><Componente c={c} /></Entrada>
          </Sequence>
        );
      })}
      {!semAudio && cenas.map((c) => (
        <Sequence key={`voz-${c.id}`} from={Math.round(c.fala * fps)} name={`voz ${c.id}`}>
          <Audio src={staticFile(c.audio)} />
        </Sequence>
      ))}
      <Capitulo cenas={cenas} />
    </AbsoluteFill>
  );
};

export const DURACAO = narracao.quadros;
export const FPS = narracao.fps;
