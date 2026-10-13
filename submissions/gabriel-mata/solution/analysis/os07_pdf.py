"""OS-07b - Converte os relatorios .md em PDF continuo de uma unica pagina.

markdown -> HTML -> Playwright (Chrome ja instalado, channel="chrome").
Cada PDF tem largura A4 e altura igual a do conteudo: sem paginacao.
Nao altera os .md. O HTML intermediario fica em pasta temporaria.
"""

import os
import re
import shutil
import sys
import tempfile

import markdown
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
REPORT_DIR = os.path.join(REPO, "solution", "report")
OUT_DIR = os.path.join(REPO, "solution", "outputs", "os07")

# 210mm em pixels CSS (96 dpi)
PAGE_W_PX = 794
SLACK_PX = 40

CSS = """
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }

body {
  width: 210mm;
  margin: 0;
  padding: 1.5cm 2cm;
  box-sizing: border-box;
  font-family: Helvetica, Arial, sans-serif;
  font-size: 10.5pt;
  line-height: 1.45;
  color: #222222;
  background: #FFFFFF;
}

body > *:first-child { margin-top: 0; }

h1, h2, h3, h4 {
  color: #222222;
  line-height: 1.25;
  break-after: avoid;
  page-break-after: avoid;
}

h1 {
  font-size: 18pt;
  margin: 32px 0 12px 0;
  padding-bottom: 4px;
  border-bottom: 1px solid #C0392B;
}

h2 { font-size: 14pt; margin: 28px 0 10px 0; }
h3 { font-size: 12pt; margin: 20px 0 8px 0; }
h4 { font-size: 10.5pt; margin: 16px 0 8px 0; }

p { margin: 0 0 10px 0; }
ul, ol { margin: 0 0 10px 0; padding-left: 1.4em; }
li { margin-bottom: 2px; }

hr {
  border: 0;
  border-top: 1px solid #DDDDDD;
  margin: 24px 0;
}

a { color: inherit; text-decoration: none; }

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 9.5pt;
  margin: 12px 0;
}

th, td {
  border: 0.5pt solid #DDDDDD;
  padding: 4pt 6pt;
  text-align: left;
  vertical-align: top;
}

th { background-color: #F2F2F2; font-weight: bold; }
tbody tr:nth-child(even) { background-color: #FAFAFA; }

img {
  width: 100%;
  height: auto;
  display: block;
  margin: 16px 0;
}

blockquote {
  border-left: 2.5pt solid #C0392B;
  background-color: #FAFAFA;
  margin: 12px 0;
  padding: 8px 12px;
}

blockquote p:last-child { margin-bottom: 0; }

code, pre { font-family: Menlo, Consolas, monospace; font-size: 9pt; }

pre {
  background-color: #FAFAFA;
  border: 0.5pt solid #DDDDDD;
  padding: 8px;
  margin: 12px 0;
}

.divisoria { margin: 40px 0; }
.divisoria-linha { border-top: 1px solid #C0392B; }
.divisoria-titulo { font-size: 18pt; font-weight: bold; margin-top: 12px; }
.divisoria + * { margin-top: 0; }
"""

PAGE_TMPL = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>{css}</style>
</head>
<body>
{body}
</body>
</html>
"""

DIVISORIA = (
    '<div class="divisoria">'
    '<div class="divisoria-linha"></div>'
    '<div class="divisoria-titulo">Relatório técnico</div>'
    "</div>"
)


def md_to_html_body(md_path):
    with open(md_path, encoding="utf-8") as fh:
        text = fh.read()
    return markdown.markdown(text, extensions=["tables", "fenced_code"])


def absolutize_images(body, base_dir):
    """Troca os src relativos das imagens por caminhos absolutos file://."""
    srcs = []

    def repl(match):
        prefix, src, suffix = match.group(1), match.group(2), match.group(3)
        if src.startswith(("http:", "https:", "file:", "data:")):
            srcs.append(src)
            return match.group(0)
        abs_path = os.path.normpath(os.path.join(base_dir, src))
        srcs.append(abs_path)
        return prefix + "file://" + abs_path + suffix

    body = re.sub(r'(<img[^>]*?\ssrc=")([^"]+)(")', repl, body)
    # tira o <p> que so embrulha a imagem, para nao somar margem
    body = re.sub(r"<p>\s*(<img[^>]*>)\s*</p>", r"\1", body)
    return body, srcs


def check_lists(body, probes):
    """Confere que cada texto citado e seguido por uma lista, nao por texto colado."""
    out = []
    for probe in probes:
        idx = body.find(probe)
        if idx < 0:
            out.append((probe, "TEXTO NAO ENCONTRADO"))
            continue
        trecho = body[idx : idx + 400]
        m = re.search(r"</p>\s*<(ul|ol)>", trecho)
        out.append((probe, "<%s> apos </p>" % m.group(1) if m else "SEM LISTA LOGO APOS"))
    # paragrafo que engoliu itens de lista
    coladas = [
        p[:60]
        for p in re.findall(r"<p>(.*?)</p>", body, re.S)
        if re.search(r"\n\s*[-*]\s+\S", p)
    ]
    return out, coladas


def pdf_info(pdf_path):
    with open(pdf_path, "rb") as fh:
        data = fh.read()
    n_pages = len(re.findall(rb"/Type\s*/Page[^s]", data))
    boxes = re.findall(rb"/MediaBox\s*\[\s*([\d.\-]+)\s+([\d.\-]+)\s+([\d.\-]+)\s+([\d.\-]+)\s*\]", data)
    w_mm = h_mm = None
    if boxes:
        w_pt = float(boxes[0][2]) - float(boxes[0][0])
        h_pt = float(boxes[0][3]) - float(boxes[0][1])
        w_mm = w_pt * 25.4 / 72.0
        h_mm = h_pt * 25.4 / 72.0
    graficos = 0
    for m in re.finditer(rb"/Subtype\s*/Image", data):
        seg = data[max(0, m.start() - 400) : m.start() + 400]
        w = re.search(rb"/Width\s+(\d+)", seg)
        if w and int(w.group(1)) == 1500:
            graficos += 1
    return n_pages, w_mm, h_mm, graficos


IMG_REPORT = """() => Array.from(document.images).map(i => {
  const r = i.getBoundingClientRect();
  return {
    arquivo: i.currentSrc.split('/').pop(),
    natural: i.naturalWidth + 'x' + i.naturalHeight,
    render: Math.round(r.width) + 'x' + Math.round(r.height),
    topo: Math.round(r.top + window.scrollY),
    ok: i.complete && i.naturalWidth > 0 && r.width > 0 && r.height > 0
  };
})"""

WAIT_ASSETS = """() => Promise.all([
  document.fonts.ready,
  ...Array.from(document.images).map(i => i.complete
    ? Promise.resolve()
    : new Promise(r => { i.onload = i.onerror = r; }))
])"""


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="os07b_")
    png_dir = os.path.join(tmp, "png")
    os.makedirs(png_dir, exist_ok=True)

    exec_body, exec_srcs = absolutize_images(
        md_to_html_body(os.path.join(REPORT_DIR, "relatorio_executivo.md")), REPORT_DIR
    )
    tec_body, tec_srcs = absolutize_images(
        md_to_html_body(os.path.join(REPORT_DIR, "relatorio_tecnico.md")), REPORT_DIR
    )

    docs = [
        ("relatorio_executivo", exec_body, exec_srcs),
        ("relatorio_tecnico", tec_body, tec_srcs),
        (
            "relatorio_completo",
            exec_body + DIVISORIA + tec_body,
            exec_srcs + tec_srcs,
        ),
    ]

    probes_exec = ["Com os dados reais, revisamos a estratégia se:"]
    probes_tec = [
        "<strong>Consequências para o método:</strong>",
        "<strong>Fora do escopo, por decisão:</strong>",
        "As recomendações estão no relatório executivo",
    ]

    print("### Listas (verificacao 3)")
    for label, body, probes in [
        ("executivo", exec_body, probes_exec),
        ("tecnico", tec_body, probes_tec),
    ]:
        res, coladas = check_lists(body, probes)
        for probe, status in res:
            print("  [%s] %-55s -> %s" % (label, probe[:55], status))
        print("  [%s] paragrafos com lista colada: %d %s" % (label, len(coladas), coladas))
    print("")

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(channel="chrome")
            for name, body, srcs in docs:
                html_path = os.path.join(tmp, name + ".html")
                with open(html_path, "w", encoding="utf-8") as fh:
                    fh.write(PAGE_TMPL.format(title=name, css=CSS, body=body))

                page = browser.new_page(viewport={"width": PAGE_W_PX, "height": 1200})
                page.goto("file://" + html_path, wait_until="load")
                page.evaluate(WAIT_ASSETS)
                height = page.evaluate("document.documentElement.scrollHeight")
                imgs = page.evaluate(IMG_REPORT)

                pdf_path = os.path.join(REPORT_DIR, name + ".pdf")
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
                page.pdf(
                    path=pdf_path,
                    width="210mm",
                    height="%dpx" % (height + SLACK_PX),
                    print_background=True,
                    margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
                )
                page.screenshot(
                    path=os.path.join(png_dir, name + ".png"), full_page=True
                )
                page.close()

                n_pages, w_mm, h_mm, graficos = pdf_info(pdf_path)
                print("=== %s ===" % name)
                print("  altura medida do conteudo: %d px" % height)
                print("  paginas: %d" % n_pages)
                print("  tamanho da pagina: %.1f x %.1f mm" % (w_mm, h_mm))
                print("  imagens referenciadas: %d" % len(srcs))
                print("  imagens renderizadas na pagina: %d (todas ok: %s)"
                      % (len(imgs), all(i["ok"] for i in imgs)))
                for i in imgs:
                    print("    - %s natural %s render %s topo y=%s ok=%s"
                          % (i["arquivo"], i["natural"], i["render"], i["topo"], i["ok"]))
                print("  objetos de imagem no pdf (1500px, Chrome deduplica): %d" % graficos)
                print("  pdf: %d bytes" % os.path.getsize(pdf_path))
                print("  png de conferencia: %s" % os.path.join(png_dir, name + ".png"))
                if n_pages != 1:
                    print("  FALHA: o PDF nao ficou com 1 pagina")
            browser.close()
    except Exception:
        shutil.rmtree(tmp, ignore_errors=True)
        raise

    print("\nPNG de conferencia em: %s" % png_dir)
    print("HTML temporario em: %s (apague depois da conferencia)" % tmp)


if __name__ == "__main__":
    main()
