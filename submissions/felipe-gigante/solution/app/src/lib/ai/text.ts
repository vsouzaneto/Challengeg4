// Utilitários de texto compartilhados pelo pipeline.

/** Tokenização idêntica ao sklearn: token_pattern r"(?u)\b\w\w+\b" + lowercase. */
export function sklearnTokens(text: string): string[] {
  return text.toLowerCase().match(/[\p{L}\p{N}_]{2,}/gu) ?? [];
}

/**
 * Normalização PT→EN. O classificador foi treinado no Dataset 2 (inglês).
 * Em vez de traduzir com LLM a cada ticket (custo/latência), mapeamos os termos
 * de domínio mais frequentes. Se houver LLM configurado, ele é usado como cascata.
 */
const PT_EN: Record<string, string> = {
  senha: "password", senhas: "password", acesso: "access", acessar: "access", login: "login", logar: "login",
  entrar: "login", conta: "account", usuario: "user", usuário: "user", bloqueada: "locked", bloqueado: "locked",
  bloqueio: "locked", redefinir: "reset", resetar: "reset", trocar: "change", alterar: "change", esqueci: "forgot",
  notebook: "laptop", computador: "computer", tela: "screen", teclado: "keyboard", mouse: "mouse", monitor: "monitor",
  impressora: "printer", bateria: "battery", carregador: "charger", carregar: "charge", celular: "phone",
  quebrado: "broken", quebrou: "broken", ligar: "turn on", liga: "turn on", desliga: "turn off", travando: "freezing",
  trava: "freezing", lento: "slow", erro: "error", falha: "failure", instalar: "install", instalação: "installation",
  instalacao: "installation", configurar: "setup", configuração: "setup", configuracao: "setup", atualização: "update",
  atualizacao: "update", atualizar: "update", rede: "network", internet: "internet", wifi: "wifi", conexão: "connection",
  conexao: "connection", conectar: "connect", conecta: "connect", conecto: "connect", fones: "headphones", armazenamento: "storage", espaço: "space", espaco: "space", disco: "disk",
  pasta: "folder", arquivo: "file", arquivos: "files", compartilhada: "shared", backup: "backup", perdi: "lost",
  perdido: "lost", dados: "data", compra: "purchase", comprar: "buy", pedido: "order", cotação: "quote",
  cotacao: "quote", licença: "license", licenca: "license", permissão: "permission", permissao: "permission",
  administrador: "administrator", admin: "admin", direitos: "rights", projeto: "project", férias: "vacation",
  ferias: "vacation", salário: "salary", salario: "salary", contrato: "contract", entrega: "delivery",
  entregue: "delivered", chegou: "arrived", atrasado: "late", atraso: "delay", rastreio: "tracking",
  reembolso: "refund", estorno: "refund", devolução: "return", devolucao: "return", cancelar: "cancel",
  cancelamento: "cancellation", assinatura: "subscription", cobrança: "charge", cobranca: "charge", cobrado: "charged",
  pagamento: "payment", fatura: "invoice", boleto: "invoice", cartão: "card", cartao: "card", nota: "invoice",
  endereço: "address", endereco: "address", compatível: "compatible", compativel: "compatible",
  compatibilidade: "compatibility", recomendação: "recommendation", recomendacao: "recommendation",
  produto: "product", fone: "headphones", câmera: "camera", camera: "camera", relógio: "watch", relogio: "watch",
  imagem: "display", vídeo: "video", video: "video", aplicativo: "app", app: "app", bug: "bug",
  e: "and", meu: "my", minha: "my", não: "not", nao: "not", consigo: "can", funciona: "works", funcionando: "working",
};

export function normalizeToEnglish(text: string): string {
  return text
    .toLowerCase()
    .split(/(\s+|[.,;:!?()"'])/)
    .map((w) => PT_EN[w] ?? w)
    .join("");
}

const STOP = new Set(
  (
    "the a an and or but is are was were be been to of in on for with my your our i me we you it this that at from by as " +
    "have has had do does did can could would should will not no please hi hello thanks thank there here what how when " +
    "o a os as um uma de do da dos das em no na nos nas para por com meu minha que se eu voce você ele ela isso esse essa " +
    "estou esta está ser ter tem foi como mais mas ou ao aos pra pro oi ola olá obrigado obrigada dá da já ja é pode posso consigo vocês voces"
  ).split(" "),
);

/** Tokens para busca semântica leve (KB / clustering): normaliza, remove stopwords, stemming simples. */
export function searchTokens(text: string): string[] {
  return sklearnTokens(normalizeToEnglish(text))
    .filter((t) => !STOP.has(t) && !/^\d+$/.test(t))
    .map(stem);
}

function stem(w: string): string {
  if (w.length <= 4 || w.endsWith("ss")) return w;
  return w.replace(/(ings|ing|edly|ed|es|s)$/u, "") || w;
}

export function detectLanguage(text: string): "pt" | "en" {
  const t = ` ${text.toLowerCase()} `;
  const pt = (t.match(/\s(não|nao|meu|minha|você|voce|está|esta|para|com|uma|como|consigo|obrigad[oa]|olá|ola)\s/g) ?? []).length;
  const en = (t.match(/\s(the|my|is|can't|cannot|i'm|with|please|have|not|how|what)\s/g) ?? []).length;
  if (/[ãõçáéíóúâê]/.test(t)) return "pt";
  return pt >= en ? (pt === 0 && en === 0 ? "pt" : pt > en ? "pt" : "en") : "en";
}

export type SparseVec = Map<string, number>;

export function termFreq(tokens: string[]): SparseVec {
  const m: SparseVec = new Map();
  for (const t of tokens) m.set(t, (m.get(t) ?? 0) + 1);
  return m;
}

export function cosine(a: SparseVec, b: SparseVec): number {
  let dot = 0, na = 0, nb = 0;
  for (const [k, v] of a) {
    na += v * v;
    const w = b.get(k);
    if (w) dot += v * w;
  }
  for (const v of b.values()) nb += v * v;
  return na && nb ? dot / Math.sqrt(na * nb) : 0;
}

/** Limpa os placeholders de template do Dataset 1 ({product_purchased}, {error_message}...). */
export function cleanDatasetText(text: string, product: string): string {
  return text
    .replace(/\{product_purchased\}|\{product_name\}|\{product\}/g, product)
    .replace(/\{error_message\}/g, "an error")
    .replace(/\{[a-z_]+\}/g, "")
    .replace(/\s+\n/g, "\n")
    .trim();
}
