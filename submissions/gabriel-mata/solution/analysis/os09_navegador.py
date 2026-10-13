"""OS-09 - checagens do decisor.html no navegador (Playwright + Chrome local).

Modos:
  briefing6000  item 0.5.2: sobe a base com efeito conhecido e le o briefing
  template      validacao 2: sobe o template preenchido e le as metricas novas
  ideias        validacao 4: tres ideias na aba Planejar campanha
  simulador     validacao 3: cenario 30 organicos + 10 patrocinados, R$ 2.000
  capturas      validacao 5: as 3 abas a 1.280 e 1.440 px + Planejar usada
  acessibilidade validacao 6: navegacao por Tab, foco visivel e contraste
  tudo          todos os modos acima
"""

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
FERRAMENTA = REPO_ROOT / "solution" / "tool" / "decisor.html"
SAIDA = REPO_ROOT / "solution" / "outputs" / "os09"
FIXTURES = SAIDA / "fixtures"


def abrir(p, largura=1280, altura=900):
    nav = p.chromium.launch(channel="chrome")
    pg = nav.new_page(viewport={"width": largura, "height": altura})
    pg.on("pageerror", lambda e: print(f"  ERRO JS: {e}"))
    pg.on("console", lambda m: print(f"  console.{m.type}: {m.text}") if m.type == "error" else None)
    pg.goto(FERRAMENTA.as_uri())
    pg.wait_for_selector("#secao-briefing", timeout=30000)
    return nav, pg


def subir_csv(pg, caminho):
    pg.set_input_files("#arquivo", str(caminho))
    pg.wait_for_function(
        "() => document.getElementById('base-info').textContent.includes('" + caminho.name + "')",
        timeout=60000)
    pg.wait_for_timeout(300)


def texto_briefing(pg):
    return pg.eval_on_selector("#secao-briefing", "e => e.textContent")


# ---------------------------------------------------------------- modos

def modo_briefing6000(pg):
    print("0.5.2 - briefing da base com efeito conhecido")
    subir_csv(pg, FIXTURES / "base_efeito_conhecido.csv")
    print("  " + pg.eval_on_selector("#base-info", "e => e.textContent"))
    txt = texto_briefing(pg)
    for linha in pg.eval_on_selector_all(
            "#secao-briefing .linha-brief",
            "ns => ns.map(n => n.textContent.replace(/\\s+/g,' ').trim())"):
        print("  | " + linha)
    for esperado in ["Priorize: Vídeo", "Evite: Imagem", "Texto", "Misto"]:
        print(f"  {'ok ' if esperado in txt else 'NAO'} contém \"{esperado}\"")


def modo_template(pg):
    print("validacao 2 - template de ponta a ponta")
    pg.click("#aba-como")
    with pg.expect_download() as dl:
        pg.click("#btn-template")
    baixado = dl.value
    destino = SAIDA / "template_decisor.csv"
    baixado.save_as(str(destino))
    linhas = destino.read_text(encoding="utf-8-sig").strip().split("\n")
    print(f"  baixado: {destino.name}, {len(linhas) - 1} linhas de exemplo")
    cab_baixado = linhas[0].split(",")
    cab_fixture = (FIXTURES / "template_preenchido.csv").read_text(
        encoding="utf-8").split("\n")[0].strip().split(",")
    print(f"  {'ok ' if cab_baixado == cab_fixture else 'NAO'} cabecalho igual ao do arquivo preenchido")
    print("  colunas: " + ", ".join(cab_baixado))
    for l in linhas[1:]:
        campos = l.split(",")
        print(f"  | exemplo: {campos[1]} {campos[2]} patrocinado={campos[5]} custo={campos[-1]}")

    subir_csv(pg, FIXTURES / "template_preenchido.csv")
    print("  " + pg.eval_on_selector("#base-info", "e => e.textContent"))
    print("  secao Vale patrocinar:")
    for linha in pg.eval_on_selector_all(
            "#painel-diag .secao",
            """ns => ns.filter(n => n.textContent.includes('Vale patrocinar'))
                        .map(n => n.textContent.replace(/\\s+/g,' ').trim())"""):
        print("  | " + linha[:900])
    print("  tabela de custos:")
    for linha in pg.eval_on_selector_all(
            "#painel-diag table.tabela tr",
            "ns => ns.map(n => [...n.children].map(c => c.textContent.replace(/\\s+/g,' ').trim()).join(' | '))"):
        print("  | " + linha)
    conv = pg.eval_on_selector_all(
        "#painel-diag details.secao > summary",
        "ns => ns.map(n => n.textContent.replace(/\\s+/g,' ').trim())")
    for s in conv:
        if "Conversão" in s:
            print("  | " + s)


IDEIAS = [
    {"nome": "TikTok + video + tech", "sel": {"i-plataforma": "TikTok", "i-formato": "video", "i-categoria": "tech"}},
    {"nome": "qualquer + patrocinado", "sel": {"i-patrocinado": "sim"}},
    {"nome": "TikTok + image + tech + 500K-1M + 19-25 anos (menos de 100 posts)",
     "sel": {"i-plataforma": "TikTok", "i-formato": "image", "i-categoria": "tech",
             "i-faixa": "500K–1M", "i-idade": "19-25"}},
]


def modo_ideias(pg):
    print("validacao 4 - testar uma ideia")
    pg.click("#aba-plan")
    for ideia in IDEIAS:
        pg.reload()
        pg.wait_for_selector("#secao-briefing", timeout=30000)
        pg.click("#aba-plan")
        for campo, valor in ideia["sel"].items():
            pg.select_option("#" + campo, valor)
        pg.click("#btn-ideia")
        pg.wait_for_timeout(300)
        selo = pg.eval_on_selector_all("#res-ideia .selo",
                                       "ns => ns.map(n => n.textContent.trim())")
        frase = pg.eval_on_selector_all("#res-ideia .frase, #res-ideia .vazio, #res-ideia p",
                                        "ns => ns.map(n => n.textContent.replace(/\\s+/g,' ').trim())")
        print(f"  {ideia['nome']}: selo = {selo}")
        for f in frase:
            print("    " + f)


def modo_simulador(pg):
    print("validacao 3 - simulador: 30 organicos + 10 patrocinados, R$ 2.000 por patrocinado")
    pg.click("#aba-plan")
    pg.fill("#s-org", "30")
    pg.fill("#s-pat", "10")
    pg.fill("#s-valor", "2000")
    pg.fill("#s-custo-org", "0")
    pg.click("#btn-simular")
    pg.wait_for_timeout(300)
    for linha in pg.eval_on_selector_all(
            "#res-simulador table.tabela tr",
            "ns => ns.map(n => [...n.children].map(c => c.textContent.replace(/\\s+/g,' ').trim()).join(' | '))"):
        print("  | " + linha)
    for p in pg.eval_on_selector_all("#res-simulador p",
                                     "ns => ns.map(n => n.textContent.replace(/\\s+/g,' ').trim())"):
        print("  " + p)
    pg.click("#aba-diag")
    for linha in pg.eval_on_selector_all(
            "#secao-briefing .linha-brief",
            "ns => ns.map(n => n.textContent.replace(/\\s+/g,' ').trim())"):
        if linha.startswith("Plano de volume"):
            print("  briefing: " + linha)


ABAS = [("aba-diag", "painel-diag", "diagnostico"),
        ("aba-como", "painel-como", "como-usar"),
        ("aba-plan", "painel-plan", "planejar")]


def modo_capturas(pg):
    print("validacao 5 - capturas das 3 abas a 1.280 e 1.440 px")
    for largura in (1280, 1440):
        pg.set_viewport_size({"width": largura, "height": 900})
        for aba, painel, nome in ABAS:
            pg.click("#" + aba)
            pg.wait_for_timeout(250)
            destino = SAIDA / f"captura_{nome}_{largura}.png"
            pg.evaluate("window.scrollTo(0, 0)")
            pg.screenshot(path=str(destino), full_page=True)
            print(f"  {destino.name} ({largura}x"
                  f"{pg.evaluate('document.documentElement.scrollHeight')})")
    # Planejar depois de avaliar uma ideia e simular
    pg.set_viewport_size({"width": 1440, "height": 900})
    pg.click("#aba-plan")
    pg.select_option("#i-plataforma", "TikTok")
    pg.select_option("#i-formato", "video")
    pg.click("#btn-ideia")
    pg.fill("#s-org", "30")
    pg.fill("#s-pat", "10")
    pg.fill("#s-valor", "2000")
    pg.click("#btn-simular")
    pg.wait_for_timeout(400)
    destino = SAIDA / "captura_planejar_usada_1440.png"
    pg.evaluate("window.scrollTo(0, 0)")
    pg.screenshot(path=str(destino), full_page=True)
    print(f"  {destino.name} (1440x{pg.evaluate('document.documentElement.scrollHeight')})")
    # medidas da Parte 4
    med = pg.evaluate("""() => {
      const r = n => Math.round(parseFloat(n));
      const cs = s => {
        const n = document.querySelector(s);
        return n ? getComputedStyle(n) : new Proxy({}, { get: () => "(ausente)" });
      };
      const lg = s => Math.round(document.querySelector(s).getBoundingClientRect().width);
      return {
        larguraConteudo: lg(".conteudo") || lg("main"),
        corpo: cs("body").fontSize + " / " + cs("body").lineHeight,
        fonte: cs("body").fontFamily.slice(0, 40),
        numTabular: cs("body").fontVariantNumeric,
        tituloSecao: cs("#painel-diag .secao h2").fontSize + " / " + cs("#painel-diag .secao h2").fontWeight,
        subtituloSecao: cs(".secao h3").fontSize + " / " + cs(".secao h3").fontWeight,
        resumoSecao: cs("details.secao > summary").fontSize + " / " + cs("details.secao > summary").fontWeight,
        tituloBrief: cs("#secao-briefing h2").fontSize + " / " + cs("#secao-briefing h2").fontWeight,
        bordaSecao: cs("#painel-diag .secao").borderBottomWidth + " " + cs("#painel-diag .secao").borderBottomColor,
        sombraSecao: cs("#painel-diag .secao").boxShadow,
        raioBotao: cs("#btn-ideia").borderRadius,
        raioSecao: cs("#painel-diag .secao").borderRadius,
        alturaCampo: r(cs("#s-org").height) + parseFloat(cs("#s-org").paddingTop) * 0 + "px",
        topoBrief: cs("#secao-briefing").borderTopWidth + " " + cs("#secao-briefing").borderTopColor
      };
    }""")
    for k, v in med.items():
        print(f"  {k}: {v}")


def modo_acessibilidade(pg):
    print("validacao 6 - acessibilidade basica")
    for aba, painel, nome in ABAS:
        # troca de aba por JS e clica num ponto sem foco no topo, para que o
        # Tab recomece do inicio do documento
        pg.eval_on_selector("#" + aba, "e => e.click()")
        pg.wait_for_timeout(200)
        pg.evaluate("window.scrollTo(0, 0)")
        pg.mouse.click(5, 5)
        visitados = []
        for _ in range(60):
            pg.keyboard.press("Tab")
            info = pg.evaluate("""() => {
              const a = document.activeElement;
              if (!a || a === document.body) return null;
              const cs = getComputedStyle(a);
              const r = a.getBoundingClientRect();
              return { tag: a.tagName.toLowerCase(), id: a.id,
                       rotulo: (a.textContent || a.value || "").replace(/\\s+/g,' ').trim().slice(0,20),
                       contorno: cs.outlineWidth + " " + cs.outlineStyle,
                       visivel: r.width > 0 && r.height > 0 };
            }""")
            if info is None:
                break
            visitados.append(info)
        sem_foco = [v for v in visitados if v["contorno"].startswith("0px") or "none" in v["contorno"]]
        fora_tela = [v for v in visitados if not v["visivel"]]
        focaveis = pg.evaluate("""(sel) => {
          const q = "a[href], button, select, input, textarea, summary, [tabindex]";
          return [...document.querySelectorAll(q)]
            .filter(n => !n.disabled && n.offsetParent !== null
                         && n.getBoundingClientRect().width > 0
                         && !(n.tagName !== "SUMMARY" && n.closest("details:not([open])"))
                         && n.getAttribute("tabindex") !== "-1"
                         && (n.closest(".painel") === null || n.closest(".painel").id === sel))
            .map(n => n.id || n.tagName.toLowerCase() + ":"
                 + (n.textContent || "").replace(/\\s+/g,' ').trim().slice(0,20));
        }""", painel)
        vistos = set(v["id"] for v in visitados if v["id"])
        rotulos = set(v["rotulo"] for v in visitados)
        nao_vistos = [f for f in focaveis
                      if f not in vistos and f.split(":", 1)[-1] not in rotulos]
        print(f"  {nome}: {len(visitados)} paradas de Tab para {len(focaveis)} focaveis, "
              f"{len(sem_foco)} sem contorno de foco, {len(fora_tela)} invisiveis")
        if nao_vistos:
            print(f"    NAO ALCANCADOS: {nao_vistos}")
        for v in sem_foco[:5]:
            print(f"    SEM FOCO: {v['tag']}#{v['id']} {v['rotulo']}")
    selos = pg.evaluate("""() => {
      document.getElementById('aba-diag').click();
      return [...document.querySelectorAll('.selo')].map(n => n.textContent.trim());
    }""")
    vazios = [s for s in selos if not s]
    print(f"  selos com texto: {len(selos) - len(vazios)}/{len(selos)} (vazios: {len(vazios)})")
    print(f"  exemplos: {sorted(set(selos))[:6]}")

    print("  contraste (minimo exigido 4,5:1):")
    for aba, painel, nome in ABAS:
        pg.click("#" + aba)
        pg.wait_for_timeout(200)
        piores = pg.evaluate("""(sel) => {
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
            return "rgb(255,255,255)";
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
                       tam: cs.fontSize, txt: txt.slice(0, 32) });
          });
          res.sort((x,y) => x.razao - y.razao);
          return res.slice(0, 4);
        }""", "#" + painel)
        pior = piores[0]["razao"] if piores else None
        print(f"    {nome}: pior razao {pior}:1")
        for p in piores:
            if p["razao"] < 4.5:
                print(f"      ABAIXO {p['razao']}:1 {p['cor']} {p['tam']} \"{p['txt']}\"")


MODOS = {
    "briefing6000": modo_briefing6000,
    "template": modo_template,
    "simulador": modo_simulador,
    "ideias": modo_ideias,
    "capturas": modo_capturas,
    "acessibilidade": modo_acessibilidade,
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
