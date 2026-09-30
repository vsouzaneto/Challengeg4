/**
 * Helpers de DOM.
 *
 * Regra do modulo: nada vindo da API entra na pagina via `innerHTML`.
 * `el()` so aceita nos de texto, entao nomes de canal, assuntos de ticket e
 * trechos de documento indexado nao podem injetar marcacao.
 */

/**
 * Cria um elemento.
 * @param {string} tag
 * @param {object} [attrs] atributos; `class`, `dataset`, `style`, `on*` e `aria-*` sao tratados
 * @param {Array|string|Node} [children]
 */
export function el(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);

  for (const [key, value] of Object.entries(attrs)) {
    if (value === null || value === undefined || value === false) continue;

    if (key === "class") node.className = value;
    else if (key === "dataset") Object.assign(node.dataset, value);
    else if (key === "style") node.setAttribute("style", value);
    else if (key === "text") node.textContent = String(value);
    else if (key.startsWith("on") && typeof value === "function") {
      node.addEventListener(key.slice(2).toLowerCase(), value);
    } else if (value === true) node.setAttribute(key, "");
    else node.setAttribute(key, String(value));
  }

  append(node, children);
  return node;
}

export function append(parent, children) {
  const list = Array.isArray(children) ? children : [children];
  for (const child of list) {
    if (child === null || child === undefined || child === false) continue;
    parent.appendChild(child instanceof Node ? child : document.createTextNode(String(child)));
  }
  return parent;
}

export function clear(node) {
  while (node.firstChild) node.removeChild(node.firstChild);
  return node;
}

/** Substitui o conteudo de um container de uma vez so. */
export function render(container, children) {
  clear(container);
  append(container, children);
  return container;
}

export const $ = (selector, scope = document) => scope.querySelector(selector);
export const $$ = (selector, scope = document) => Array.from(scope.querySelectorAll(selector));

/* -- Blocos de estado ---------------------------------------------------- */

export function emptyState(title, body, action = null) {
  return el("div", { class: "state state-center" }, [
    el("h3", { text: title }),
    body ? el("p", { text: body }) : null,
    action,
  ]);
}

export function loadingState(title, body) {
  return el("div", { class: "state state-center", role: "status", "aria-live": "polite" }, [
    el("div", { class: "spinner" }),
    el("h3", { text: title }),
    body ? el("p", { text: body }) : null,
  ]);
}

/**
 * Bloco de erro. `error.detail` so aparece quando traz algo alem da mensagem
 * ja exibida, para nao repetir o mesmo texto duas vezes.
 */
export function errorState(error, retry = null) {
  const extra =
    error?.detail && typeof error.detail === "string" && error.detail !== error.message
      ? error.detail
      : null;

  return el("div", { class: "state state-error" }, [
    el("h3", { text: "Nao deu para carregar" }),
    el("p", { text: error?.message || "Erro desconhecido." }),
    extra ? el("code", { text: extra }) : null,
    error?.status ? el("p", { class: "card-note", text: `HTTP ${error.status}` }) : null,
    retry ? el("button", { class: "btn btn-ghost", type: "button", onClick: retry }, "Tentar de novo") : null,
  ]);
}

/* -- Toast --------------------------------------------------------------- */

export function toast(message, kind = "info") {
  const host = document.getElementById("toasts");
  if (!host) return;
  const node = el("div", { class: "toast", dataset: { kind }, text: message });
  host.appendChild(node);
  setTimeout(() => node.remove(), kind === "error" ? 7000 : 4000);
}

