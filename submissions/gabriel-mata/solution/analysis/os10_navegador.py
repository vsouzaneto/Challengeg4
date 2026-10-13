"""OS-10 - checagens do decisor.html no navegador (Playwright + Chrome local).

Modos (itens da parte 6 da OS):
  linguagem   validacao 2: varredura de palavras proibidas e frases longas
  efeito      validacao 3: base com efeito conhecido -> resumo com Priorize/Evite
  planejar    validacao 4: botao travado, exemplos, mais opcoes, comparativo
  tema        validacao 5: 4 capturas a 1.440 px, contraste e escolha salva
  ajuda       validacao 6: botao "?" no clique, no Enter e fechando com Esc
  tudo        todos os modos acima
"""

import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
FERRAMENTA = REPO_ROOT / "solution" / "tool" / "decisor.html"
SAIDA = REPO_ROOT / "solution" / "outputs" / "os10"
FIXTURES = REPO_ROOT / "solution" / "outputs" / "os09" / "fixtures"
REF_SIM = REPO_ROOT / "solution" / "outputs" / "os09" / "d_referencia_simulador.csv"

# secao 1.5 da OS: proibidas na tela (liberadas so em "Como calculamos")
PROIBIDAS = [
    ("IC", r"\bIC\b", False),
    ("intervalo de confianca", r"intervalos? de confian", True),
    ("Bonferroni", r"bonferroni", True),
    ("segmento", r"\bsegmento", True),
    ("recorte", r"\brecorte", True),
    ("estrato", r"\bestrato", True),
    ("indice", r"\bíndice|\bindice", True),
    ("lift", r"\blift\b", True),
    ("variancia", r"variânci|varianci", True),
    ("desvio", r"\bdesvio", True),
    ("margem relevante", r"margem relevante", True),
    ("teste A/B", r"teste\s+A/B", True),
    ("base", r"\bbases?\b", True),
    ("combinacoes", r"combinaç|combinac", True),
    ("k", r"\bk\b", True),
    ("n", r"\bn\b", True),
]

# innerText = texto como aparece na tela: pula o que esta dentro de recolhivel
# fechado (Como calculamos) e preserva a quebra entre blocos
JS_TEXTO = """(sel) => {
  const n = document.querySelector(sel);
  const baloes = [...n.querySelectorAll(".balao")].map(b => b.textContent.trim());
  return (n.innerText + "\\n" + baloes.join("\\n")).replace(/[ \\t]+/g, " ").trim();
}"""


def abrir(p, largura=1440, altura=900):
    nav = p.chromium.launch(channel="chrome")
    pg = nav.new_page(viewport={"width": largura, "height": altura})
    pg.on("pageerror", lambda e: print(f"  ERRO JS: {e}"))
    pg.on("console", lambda m: print(f"  console.{m.type}: {m.text}") if m.type == "error" else None)
    pg.goto(FERRAMENTA.as_uri())
    pg.wait_for_selector("#secao-resumo", timeout=30000)
    return nav, pg


def subir_csv(pg, caminho):
    pg.set_input_files("#arquivo", str(caminho))
    pg.wait_for_function(
        "() => document.getElementById('dados-info').textContent.includes('"
        + caminho.name + "')", timeout=60000)
    pg.wait_for_timeout(300)


def abrir_recolhiveis(pg):
    """Abre todos os <details>, menos o de Como calculamos."""
    pg.evaluate("""() => {
      document.querySelectorAll("details").forEach(d => {
        const s = d.querySelector("summary");
        if (s && s.textContent.includes("Como calculamos")) { d.open = false; return; }
        d.open = true;
      });
    }""")
    pg.wait_for_timeout(200)


def preparar_planejar(pg):
    """Deixa a aba Planejar com uma ideia avaliada e um mes calculado."""
    pg.click("#aba-plan")
    pg.select_option("#i-plataforma", "TikTok")
    pg.select_option("#i-formato", "video")
    pg.click("#btn-ideia")
    pg.fill("#s-org", "30")
    pg.fill("#s-pat", "10")
    pg.fill("#s-valor", "2000")
    pg.click("#btn-simular")
    pg.wait_for_timeout(400)


def frases_longas(texto, limite=25):
    saida = []
    for f in re.split(r"(?<=[.!?:])\s+|\n+", texto):
        f = f.strip()
        palavras = [p for p in re.split(r"\s+", f) if p]
        if len(palavras) > limite:
            saida.append((len(palavras), f))
    saida.sort(reverse=True)
    return saida


def achados(texto):
    res = []
    for nome, padrao, ignora_caixa in PROIBIDAS:
        flags = re.IGNORECASE if ignora_caixa else 0
        for m in re.finditer(padrao, texto, flags):
            ini, fim = max(0, m.start() - 35), min(len(texto), m.end() + 35)
            res.append((nome, texto[ini:fim]))
    return res


# ---------------------------------------------------------------- modos

def modo_linguagem(pg):
    print("validacao 2 - varredura de linguagem (Como calculamos fechado)")
    abrir_recolhiveis(pg)
    preparar_planejar(pg)
    alvos = [("barra superior", "header.topo"),
             ("Diagnostico", "#painel-diag"),
             ("Planejar campanha", "#painel-plan")]
    pg.click("#aba-diag")
    abrir_recolhiveis(pg)
    total = 0
    guardar = []
    for nome, sel in alvos:
        if sel == "#painel-plan":
            pg.click("#aba-plan")
            pg.wait_for_timeout(200)
        texto = pg.evaluate(JS_TEXTO, sel)
        guardar.append("=== " + nome + " ===\n" + texto)
        enc = achados(texto)
        total += len(enc)
        print(f"  {nome}: {len(texto)} caracteres, {len(enc)} palavra(s) proibida(s)")
        for palavra, trecho in enc[:12]:
            print(f"    PROIBIDA \"{palavra}\" em: ...{trecho}...")
        longas = frases_longas(texto)
        print(f"    frases com mais de 25 palavras: {len(longas)}")
        for qtd, f in longas[:6]:
            print(f"      {qtd} palavras: {f[:150]}")
    print(f"  total de palavras proibidas na tela: {total}")
    SAIDA.mkdir(parents=True, exist_ok=True)
    destino = SAIDA / "texto_tela.txt"
    destino.write_text("\n\n".join(guardar) + "\n", encoding="utf-8")
    print(f"  texto conferido salvo em {destino.name}")


def modo_efeito(pg):
    print("validacao 3 - base com efeito conhecido (video com likes x 1,3)")
    subir_csv(pg, FIXTURES / "base_efeito_conhecido.csv")
    print("  " + pg.eval_on_selector("#dados-info", "e => e.textContent"))
    frase = pg.eval_on_selector("#secao-resumo .frase-principal",
                                "e => e.textContent.replace(/\\s+/g,' ').trim()")
    print(f"  frase principal: {frase}")
    for linha in pg.eval_on_selector_all(
            "#secao-resumo .linha-resumo",
            "ns => ns.map(n => n.textContent.replace(/\\s+/g,' ').trim())"):
        print("  | " + linha)
    txt = pg.eval_on_selector("#secao-resumo", "e => e.textContent.replace(/\\s+/g,' ')")
    for esperado in ["Priorize: Vídeo", "Evite: Imagem, Texto, Misto"]:
        print(f"  {'ok ' if esperado in txt else 'NAO'} contém \"{esperado}\"")


def modo_planejar(pg):
    print("validacao 4 - aba Planejar campanha")
    pg.click("#aba-plan")
    travado = pg.eval_on_selector("#btn-ideia", "e => e.disabled")
    dica = pg.eval_on_selector("#dica-ideia", "e => e.hidden ? '' : e.textContent.trim()")
    print(f"  {'ok ' if travado else 'NAO'} botao travado com tudo em Qualquer")
    print(f"  dica visivel: \"{dica}\"")

    print("  exemplos prontos:")
    exemplos = pg.eval_on_selector_all("#exemplos-ideia button",
                                       "ns => ns.map(n => n.textContent.trim())")
    for i, nome in enumerate(exemplos):
        pg.eval_on_selector_all("#exemplos-ideia button", f"ns => ns[{i}].click()")
        pg.wait_for_timeout(350)
        campos = pg.evaluate("""() => {
          const o = {};
          document.querySelectorAll("#campos-ideia select, #mais-opcoes-caixa select")
            .forEach(s => { if (s.value) o[s.id] = s.value; });
          return o;
        }""")
        selo = pg.eval_on_selector_all("#res-ideia .selo", "ns => ns.map(n => n.textContent.trim())")
        print(f"  | {nome}: {campos} -> selo {selo}, botao travado="
              f"{pg.eval_on_selector('#btn-ideia', 'e => e.disabled')}")

    print("  mais opcoes:")
    estado = pg.evaluate("""() => {
      const b = document.querySelector("#mais-opcoes-caixa button");
      const caixa = document.querySelector("#mais-opcoes-caixa .form-campos");
      const antes = { rotulo: b.textContent.trim(), escondido: caixa.hidden };
      b.click();
      const depois = { rotulo: b.textContent.trim(), escondido: caixa.hidden,
                       campos: caixa.querySelectorAll("select").length };
      b.click();
      const fim = { rotulo: b.textContent.trim(), escondido: caixa.hidden };
      return { antes, depois, fim };
    }""")
    print(f"  | antes: {estado['antes']}")
    print(f"  | aberto: {estado['depois']}")
    print(f"  | fechado de novo: {estado['fim']}")

    print("  comparativo do mes (30 organicos + 10 pagos a R$ 2.000):")
    pg.reload()
    pg.wait_for_selector("#secao-resumo", timeout=30000)
    pg.click("#aba-plan")
    pg.fill("#s-org", "30")
    pg.fill("#s-pat", "10")
    pg.fill("#s-valor", "2000")
    pg.click("#btn-simular")
    pg.wait_for_timeout(400)
    for linha in pg.eval_on_selector_all(
            "#res-plano table.comparativo tr",
            "ns => ns.map(n => [...n.children].map(c => c.textContent.replace(/\\s+/g,' ').trim()).join(' | '))"):
        print("  | " + linha)
    for p in pg.eval_on_selector_all("#res-plano p",
                                     "ns => ns.map(n => n.textContent.replace(/\\s+/g,' ').trim())"):
        print("  " + p)
    print("  conta a mao (os09/d_referencia_simulador.csv):")
    ref = {}
    for l in REF_SIM.read_text(encoding="utf-8").strip().split("\n")[1:]:
        campos = l.split(",")
        ref[campos[0]] = float(campos[1]) if campos[1] else float("nan")
    for met in ["views", "interacoes"]:
        total = ref[f"total no mes (40 posts) - {met}"]
        ganho = ref[f"ganho do patrocinio (10 posts) - {met}"]
        print(f"  | {met}: plano {total:.2f} -> {round(total / 1000)} mil; "
              f"sem pagar {total - ganho:.2f} -> {round((total - ganho) / 1000)} mil")
    print("  | posts no mes 40; investimento R$ 20.000 vs R$ 0")


TEMAS = [("claro", "Claro"), ("escuro", "Escuro")]
ABAS_TEMA = [("aba-diag", "painel-diag", "diagnostico"), ("aba-plan", "painel-plan", "planejar")]

JS_CONTRASTE = """(sel) => {
  const lum = c => {
    const [r,g,b] = c.match(/\\d+(\\.\\d+)?/g).slice(0,3).map(Number)
      .map(v => { v /= 255; return v <= 0.03928 ? v/12.92 : Math.pow((v+0.055)/1.055, 2.4); });
    return 0.2126*r + 0.7152*g + 0.0722*b;
  };
  const fundo = n => {
    for (let e = n; e; e = e.parentElement) {
      const bg = getComputedStyle(e).backgroundColor;
      if (bg && !bg.startsWith("rgba(0, 0, 0, 0)")) return bg;
    }
    return getComputedStyle(document.body).backgroundColor;
  };
  const res = [];
  document.querySelectorAll(sel + " *").forEach(n => {
    const txt = [...n.childNodes].filter(c => c.nodeType === 3)
      .map(c => c.textContent.trim()).join(" ").trim();
    if (!txt) return;
    const r = n.getBoundingClientRect();
    if (!r.width || !r.height) return;
    const cs = getComputedStyle(n);
    const a = lum(cs.color), b = lum(fundo(n));
    const razao = (Math.max(a,b) + 0.05) / (Math.min(a,b) + 0.05);
    res.push({ razao: Math.round(razao*100)/100, cor: cs.color,
               fundo: fundo(n), tam: cs.fontSize, txt: txt.slice(0, 32) });
  });
  res.sort((x,y) => x.razao - y.razao);
  return res.slice(0, 5);
}"""


def escolher_tema(pg, valor):
    pg.click("#f-tema")
    pg.check(f"input[name=tema][value={valor}]")
    pg.wait_for_timeout(200)
    pg.keyboard.press("Escape")
    pg.wait_for_timeout(150)


def modo_tema(pg):
    print("validacao 5 - tema claro e escuro a 1.440 px")
    SAIDA.mkdir(parents=True, exist_ok=True)
    abrir_recolhiveis(pg)
    preparar_planejar(pg)
    for valor, nome in TEMAS:
        escolher_tema(pg, valor)
        attr = pg.evaluate("() => document.documentElement.getAttribute('data-tema')")
        for aba, painel, apelido in ABAS_TEMA:
            pg.click("#" + aba)
            if aba == "aba-diag":
                abrir_recolhiveis(pg)
            pg.wait_for_timeout(250)
            pg.evaluate("window.scrollTo(0, 0)")
            destino = SAIDA / f"captura_{apelido}_{valor}_1440.png"
            pg.screenshot(path=str(destino), full_page=True)
            altura = pg.evaluate("document.documentElement.scrollHeight")
            piores = pg.evaluate(JS_CONTRASTE, "#" + painel)
            abaixo = [p for p in piores if p["razao"] < 4.5]
            print(f"  {destino.name} (1440x{altura}, data-tema={attr}), "
                  f"pior contraste {piores[0]['razao']}:1")
            for p in abaixo:
                print(f"    ABAIXO {p['razao']}:1 {p['cor']} sobre {p['fundo']} "
                      f"{p['tam']} \"{p['txt']}\"")
    # a escolha precisa sobreviver ao recarregar
    escolher_tema(pg, "escuro")
    salvo = pg.evaluate("() => localStorage.getItem('decisor-tema')")
    pg.reload()
    pg.wait_for_selector("#secao-resumo", timeout=30000)
    depois = pg.evaluate("""() => ({
      attr: document.documentElement.getAttribute('data-tema'),
      radio: (document.querySelector('input[name=tema]:checked') || {}).value,
      fundo: getComputedStyle(document.body).backgroundColor
    })""")
    print(f"  localStorage decisor-tema = {salvo}; depois de recarregar: {depois}")
    pg.evaluate("() => localStorage.removeItem('decisor-tema')")


def modo_ajuda(pg):
    print("validacao 6 - ajuda \"?\"")
    for sel, nome in [("#painel-diag", "Diagnostico"), ("#painel-plan", "Planejar")]:
        print(f"  botoes \"?\" em {nome}: "
              + str(pg.eval_on_selector_all(sel + " button.ajuda", "ns => ns.length")))
    # clique
    pg.eval_on_selector_all("button.ajuda", "ns => ns[0].scrollIntoView()")
    pg.wait_for_timeout(150)
    pg.eval_on_selector_all("button.ajuda", "ns => ns[0].click()")
    pg.wait_for_timeout(150)
    print("  clique: " + pg.evaluate("""() => {
      const b = document.querySelectorAll('button.ajuda')[0];
      const bal = b.parentElement.querySelector('.balao');
      return `aberto=${!bal.hidden} aria-expanded=${b.getAttribute('aria-expanded')} "${bal.textContent}"`;
    }"""))
    # fecha com Esc
    pg.keyboard.press("Escape")
    pg.wait_for_timeout(150)
    print("  Esc: " + pg.evaluate("""() => {
      const bal = document.querySelectorAll('.balao')[0];
      return `aberto=${!bal.hidden}`;
    }"""))
    # abre pelo teclado (foco + Enter)
    pg.eval_on_selector_all("button.ajuda", "ns => ns[0].focus()")
    pg.keyboard.press("Enter")
    pg.wait_for_timeout(150)
    print("  Enter: " + pg.evaluate("""() => {
      const bal = document.querySelectorAll('.balao')[0];
      return `aberto=${!bal.hidden} foco=${document.activeElement.className}`;
    }"""))
    # fecha clicando fora
    pg.mouse.click(5, 5)
    pg.wait_for_timeout(150)
    print("  clique fora: " + pg.evaluate("""() => {
      const bal = document.querySelectorAll('.balao')[0];
      return `aberto=${!bal.hidden}`;
    }"""))
    # textos dos quatro termos
    textos = pg.evaluate("""() => {
      const o = {};
      document.querySelectorAll('.termo').forEach(t => {
        const b = t.querySelector('button.ajuda');
        if (b) o[b.getAttribute('aria-label')] = t.querySelector('.balao').textContent;
      });
      return o;
    }""")
    for rot, frase in textos.items():
        print(f"  | {rot}: {frase}")
    preparar_planejar(pg)
    print("  botoes \"?\" em Planejar depois de usar a aba: "
          + str(pg.eval_on_selector_all("#painel-plan button.ajuda", "ns => ns.length")))


def modo_barras(pg):
    """Confere as barras de patrocinio contra a mesma conta feita em pandas.
    O ui.js repete a separacao por estratos do motor para ter medias por post."""
    import pandas as pd

    print("extra - barras de 'Vale a pena pagar influenciador?' contra o pandas")
    tela = pg.eval_on_selector_all(
        "#painel-diag .barras .barra-valor",
        "ns => ns.map(n => n.textContent.replace(/\\s+/g,' ').trim())")
    usados = pg.eval_on_selector_all(
        "#painel-diag .secao",
        """ns => ns.filter(n => n.textContent.includes('Vale a pena pagar'))
                    .map(n => (n.textContent.match(/analisamos ([\\d.]+) posts/) || [])[1])""")
    print(f"  tela: {tela}; posts na tela: {usados}")

    caminho = REPO_ROOT / "datasets" / "social_media_dataset.csv"
    df = pd.read_csv(caminho)
    df["interacoes"] = df["likes"] + df["shares"] + df["comments_count"]
    # o motor usa limite superior fechado (seguidores <= limite)
    limites = [-float("inf"), 50000, 100000, 500000, 1000000, float("inf")]
    df["faixa"] = pd.cut(df["follower_count"], bins=limites, right=True)
    pat = df["is_sponsored"].astype(str).str.strip().str.upper() == "TRUE"
    df["pat"] = pat
    chaves = ["platform", "content_category", "content_type", "faixa"]
    partes = []
    for _, g in df.groupby(chaves, observed=True):
        if (g["pat"]).sum() >= 30 and (~g["pat"]).sum() >= 30:
            partes.append(g)
    usado = pd.concat(partes)
    print(f"  pandas: {len(usado)} posts em {len(partes)} grupos comparaveis")
    for met in ["interacoes", "views"]:
        po = usado[usado["pat"]][met].mean()
        og = usado[~usado["pat"]][met].mean()
        print(f"  | {met}: sem pagar {og:.1f} por post; pago {po:.1f} por post")


MODOS = {
    "linguagem": modo_linguagem,
    "barras": modo_barras,
    "efeito": modo_efeito,
    "planejar": modo_planejar,
    "tema": modo_tema,
    "ajuda": modo_ajuda,
}


def main():
    pedidos = sys.argv[1:] or ["tudo"]
    if pedidos == ["tudo"]:
        pedidos = list(MODOS)
    with sync_playwright() as p:
        for nome in pedidos:
            nav, pg = abrir(p)
            MODOS[nome](pg)
            nav.close()


if __name__ == "__main__":
    main()
