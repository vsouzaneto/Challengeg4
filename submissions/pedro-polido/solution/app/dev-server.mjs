// Servidor local: arquivos estáticos + /api/assist com a mesma função que roda na Vercel.
// Uso: node dev-server.mjs   (lê GEMINI_API_KEY do .env da raiz do repositório, se existir)
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { existsSync, readFileSync } from 'node:fs';
import { extname, join, normalize, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = dirname(fileURLToPath(import.meta.url));
const PORT = Number(process.env.PORT) || 5173;
const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png' };

// .env: procura subindo a partir da pasta do app (a raiz do repo fica 4 níveis acima)
for (let dir = ROOT, i = 0; i < 6; i += 1, dir = resolve(dir, '..')) {
  const file = join(dir, '.env');
  if (existsSync(file)) {
    for (const line of readFileSync(file, 'utf8').split(/\r?\n/)) {
      const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/);
      if (m && !process.env[m[1]]) process.env[m[1]] = m[2].replace(/^["']|["']$/g, '');
    }
    break;
  }
}

const { default: assist } = await import('./api/assist.js');

createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  if (url.pathname === '/api/assist') {
    // Mesmos helpers que a Vercel injeta: req.body já parseado, res.status().json()
    let raw = '';
    for await (const chunk of req) raw += chunk;
    try { req.body = raw ? JSON.parse(raw) : {}; } catch { req.body = {}; }
    res.status = (code) => { res.statusCode = code; return res; };
    res.json = (obj) => { res.setHeader('Content-Type', 'application/json'); res.end(JSON.stringify(obj)); return res; };
    return assist(req, res);
  }
  const path = normalize(join(ROOT, url.pathname === '/' ? 'index.html' : decodeURIComponent(url.pathname)));
  if (!path.startsWith(ROOT) || path.includes(`${ROOT}\\api`) || path.includes(`${ROOT}/api`)) {
    res.statusCode = 404;
    return res.end('not found');
  }
  try {
    const body = await readFile(path);
    res.setHeader('Content-Type', MIME[extname(path)] || 'application/octet-stream');
    res.end(body);
  } catch {
    res.statusCode = 404;
    res.end('not found');
  }
}).listen(PORT, () => console.log(`http://localhost:${PORT}  (Gemini ${process.env.GEMINI_API_KEY ? 'configurado' : 'não configurado'})`));
