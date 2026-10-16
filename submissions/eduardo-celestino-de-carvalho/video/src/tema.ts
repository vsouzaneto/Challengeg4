// Identidade do Lead Kanban (a mesma do app): navy e dourado do G4, cores das três colunas.
import {loadFont as manrope} from '@remotion/google-fonts/Manrope';
import {loadFont as baskerville} from '@remotion/google-fonts/LibreBaskerville';

export const fonte = manrope('normal', {weights: ['400', '500', '600', '700', '800'], subsets: ['latin', 'latin-ext']}).fontFamily;
export const fonteMarca = baskerville('normal', {weights: ['700'], subsets: ['latin']}).fontFamily;

export const cor = {
  navy: '#031a26',
  navy2: '#0b2a3b',
  ouro: '#b9915b',
  ouroClaro: '#d9bd8f',
  papel: '#f5f4f3',
  tinta: '#0f2230',
  suave: '#5b6b76',
  negociar: '#2E6DA4',
  qualificar: '#C99436',
  encerrar: '#B5452F',
};

export const LARGURA = 1920;
export const ALTURA = 1080;
