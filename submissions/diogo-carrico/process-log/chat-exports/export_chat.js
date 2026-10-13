// Convert a Claude Code session transcript (.jsonl) into a readable, sanitized Markdown log.
// Keeps: user messages, assistant text, one line per tool call (name + its description).
// Drops: tool outputs, hidden reasoning, system reminders and other internal tags.
// Usage: node export_chat.js <session.jsonl> <out.md> "<title>"
const fs = require('fs');
const [, , input, output, title] = process.argv;

const SECRETS = [
  [/KGAT_[0-9A-Za-z]{8,}/g, 'KGAT_[removido]'],
  [/AIza[0-9A-Za-z_-]{20,}/g, 'AIza[removido]'],
  [/gh[opsu]_[A-Za-z0-9]{20,}/g, 'gh*_[removido]'],
  [/(^|[^A-Za-z0-9])sk-(ant-)?[A-Za-z0-9_-]{20,}/g, '$1sk-[removido]'],
  [/C:\\\\Users\\\\[^\\\s"']+/gi, '~'],
  [/C:\\Users\\[^\\\s"']+/gi, '~'],
  [/C:\/Users\/[^/\s"']+/gi, '~'],
  [/\/c\/Users\/[^/\s"']+/gi, '~'],
  [/DIOGOC~1/g, '~'],
  // Personal e-mail addresses; documentation and noreply addresses stay readable.
  [/[A-Za-z0-9._%+-]+@(?!example\.(com|org|net)\b|users\.noreply\.github\.com\b|anthropic\.com\b)[A-Za-z0-9.-]+\.[a-z]{2,}/gi, '[e-mail removido]'],
];
const INTERNAL_TAGS = [
  'system-reminder', 'command-name', 'command-message', 'command-args', 'local-command-stdout',
  'local-command-caveat', 'task-notification', 'artifact-view-context', 'skill-format',
];

function sanitize(text) {
  let t = text;
  for (const tag of INTERNAL_TAGS) t = t.replace(new RegExp(`<${tag}[^>]*>[\\s\\S]*?<\\/${tag}>`, 'g'), '');
  t = t.replace(/<pasted_content[^>]*>/g, '').replace(/<\/pasted_content[^>]*>/g, '');
  for (const [re, rep] of SECRETS) t = t.replace(re, rep);
  return t.replace(/\n{3,}/g, '\n\n').trim();
}

const lines = fs.readFileSync(input, 'utf8').split('\n').filter(Boolean);
const out = [`# ${title}`, '', '> Exportado do Claude Code e limpo automaticamente: chaves, tokens, e-mail e caminhos pessoais removidos; saídas de ferramentas, raciocínio interno e avisos do sistema omitidos. Cada ferramenta usada aparece numa linha, com a descrição que a IA deu ao chamá-la.', ''];
let last = null;
let turns = 0;
// Only results of the multiple-choice tool count as Diogo's answers.
const askIds = new Set();
for (const line of lines) {
  try {
    const j = JSON.parse(line);
    const c = j.message && j.message.content;
    if (j.type === 'assistant' && Array.isArray(c)) {
      for (const b of c) if (b.type === 'tool_use' && b.name === 'AskUserQuestion') askIds.add(b.id);
    }
  } catch {}
}
for (const line of lines) {
  let j;
  try { j = JSON.parse(line); } catch { continue; }
  // Messages Diogo sent while the assistant was working arrive as queued commands.
  if (j.type === 'attachment' && j.attachment && j.attachment.type === 'queued_command'
      && (!j.attachment.origin || j.attachment.origin.kind === 'human')) {
    const text = sanitize(String(j.attachment.prompt || ''));
    if (text) {
      out.push('', `## Diogo (enviada durante o trabalho)${j.timestamp ? ' · ' + j.timestamp.slice(0, 16).replace('T', ' ') : ''}`, '', text);
      last = 'user';
      turns++;
    }
    continue;
  }
  if (!j.message || j.isMeta) continue;
  const c = j.message.content;
  // Answers to multiple-choice questions come back as a tool result.
  if (j.type === 'user' && Array.isArray(c)) {
    const answer = c.find(b => b.type === 'tool_result' && askIds.has(b.tool_use_id));
    if (answer) {
      const raw = typeof answer.content === 'string' ? answer.content : answer.content.map(x => x.text || '').join('\n');
      out.push('', '## Diogo (respostas às perguntas de múltipla escolha)', '', sanitize(raw.replace(/ You can now continue.*$/s, '')));
      last = 'user';
      turns++;
      continue;
    }
  }
  const blocks = typeof c === 'string' ? [{ type: 'text', text: c }] : Array.isArray(c) ? c : [];
  if (j.type === 'user') {
    const text = sanitize(blocks.filter(b => b.type === 'text').map(b => b.text).join('\n'));
    if (!text) continue;
    out.push('', `## Diogo${j.timestamp ? ' · ' + j.timestamp.slice(0, 16).replace('T', ' ') : ''}`, '', text);
    last = 'user';
    turns++;
  } else if (j.type === 'assistant') {
    for (const b of blocks) {
      if (b.type === 'text') {
        const text = sanitize(b.text);
        if (!text) continue;
        if (last !== 'assistant') out.push('', '## Claude', '');
        out.push(text, '');
        last = 'assistant';
      } else if (b.type === 'tool_use') {
        const desc = b.input && (b.input.description || b.input.label || b.input.action || b.input.query || '');
        if (last !== 'assistant') out.push('', '## Claude', '');
        out.push(`- _ferramenta: ${b.name.replace(/^mcp__[^_]+__/, '')}${desc ? ' — ' + sanitize(String(desc)).replace(/\s+/g, ' ').slice(0, 160) : ''}_`);
        last = 'assistant';
      }
    }
  }
}
fs.writeFileSync(output, out.join('\n') + '\n');
console.log(`${output}: ${turns} mensagens do Diogo, ${(fs.statSync(output).size / 1e6).toFixed(2)} MB`);
