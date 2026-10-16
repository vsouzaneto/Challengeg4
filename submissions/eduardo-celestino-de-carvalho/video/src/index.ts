import React from 'react';
import {Composition, registerRoot} from 'remotion';
import {DURACAO, FPS, Tutorial} from './Tutorial';
import {ALTURA, LARGURA} from './tema';

const Raiz: React.FC = () =>
  React.createElement(Composition, {
    id: 'Tutorial', component: Tutorial, durationInFrames: DURACAO, fps: FPS, width: LARGURA, height: ALTURA,
    defaultProps: {semAudio: false},
  });

registerRoot(Raiz);
