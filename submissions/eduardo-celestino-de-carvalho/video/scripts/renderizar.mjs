// Renderiza o tutorial sem o ffmpeg do Remotion (bloqueado pelo Controle de Aplicativo do Windows nesta máquina):
//   1) o Chrome do Remotion exporta os quadros em JPEG;
//   2) scripts/codificar.py mixa a narração e codifica H.264 + AAC com PyAV.
//
//   npm run video                       → out/tutorial.mp4 + out/tutorial-capa.jpg
//   npm run video -- --conferir [0.6]   → out/conferencia/<cena>.jpg (um quadro de cada cena, na fração indicada)
import {mkdirSync, readFileSync, rmSync} from 'node:fs';
import {dirname, join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
import {bundle} from '@remotion/bundler';
import {renderFrames, renderStill, selectComposition} from '@remotion/renderer';

const raiz = join(dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
const narracao = JSON.parse(readFileSync(join(raiz, 'src', 'narracao.json'), 'utf8'));
const serveUrl = await bundle({entryPoint: join(raiz, 'src', 'index.ts')});
const inputProps = {semAudio: true};
const composition = await selectComposition({serveUrl, id: 'Tutorial', inputProps});

if (args.includes('--conferir')) {
  const i = args.indexOf('--conferir');
  const fracoes = (args[i + 1] && !args[i + 1].startsWith('--') ? args[i + 1] : '0.3,0.75').split(',').map(Number);
  const pasta = join(raiz, 'out', 'conferencia');
  mkdirSync(pasta, {recursive: true});
  for (const c of narracao.cenas) {
    for (const f of fracoes) {
      const frame = Math.min(composition.durationInFrames - 1, c.deQuadro + Math.round(c.quadros * f));
      const output = join(pasta, `${String(c.deQuadro).padStart(5, '0')}-${c.id}-${Math.round(f * 100)}.jpg`);
      await renderStill({composition, serveUrl, frame, output, imageFormat: 'jpeg', jpegQuality: 80, scale: 0.5, inputProps});
      console.log(output);
    }
  }
  process.exit(0);
}

const pastaQuadros = join(raiz, '.cache', 'quadros');
rmSync(pastaQuadros, {recursive: true, force: true});
mkdirSync(pastaQuadros, {recursive: true});
const inicio = Date.now();
let ultimo = 0;
await renderFrames({
  composition, serveUrl, outputDir: pastaQuadros, imageFormat: 'jpeg', jpegQuality: 90, concurrency: 6, inputProps,
  onStart: () => console.log(`${composition.durationInFrames} quadros`),
  onFrameUpdate: (n) => {
    if (n - ultimo >= 600 || n === composition.durationInFrames) {
      ultimo = n;
      console.log(`  ${n}/${composition.durationInFrames} quadros · ${((Date.now() - inicio) / 1000).toFixed(0)} s`);
    }
  },
});
mkdirSync(join(raiz, 'out'), {recursive: true});
const python = process.platform === 'win32' ? join(raiz, '.venv', 'Scripts', 'python.exe') : join(raiz, '.venv', 'bin', 'python');
execFileSync(python, [join(raiz, 'scripts', 'codificar.py'), pastaQuadros, join(raiz, 'out', 'tutorial.mp4')], {
  stdio: 'inherit', env: {...process.env, PYTHONIOENCODING: 'utf-8'},
});
