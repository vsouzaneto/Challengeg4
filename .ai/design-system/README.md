# Design system — G4 Scale (deste git)

Fonte visual: `Identidade-Visual-G4-Scale-2026-09-21-14_30_59.pdf` (export Behance, 7 páginas, sem texto extraível). Hex amostrados do raster 2× em 2026-09-21.

Este git **não** instala Angular, React, Vue nem `@infrab4a/components`. O DS aqui é **contrato de marca** para UIs que o candidato (ou um maintainer) construir — em especial o challenge **003**. Tokens entram via CSS custom properties em [tokens.css](tokens.css).

| Arquivo | Papel |
|---------|-------|
| [SPEC-REVERSE.md](SPEC-REVERSE.md) | O que o PDF **mostra** (e o que não mostra) |
| [SPEC-DRIVEN.md](SPEC-DRIVEN.md) | Como aplicar sem inventar token |
| [G4-SCALE-TOKENS.md](G4-SCALE-TOKENS.md) | Paleta, tipo, raio, elevação |
| [GUIDANCE.md](GUIDANCE.md) | Componentes Angular / React / Vue |
| [tokens.css](tokens.css) | Variáveis `--g4s-*` para copiar ao app |
| PDF | Fonte canônica de cor + logo + grafismo |
| `_pdf-pages/` | Raster local (gitignored; regenerável) |

## Qual DS usar

| Superfície | Tokens | Onde |
|------------|--------|------|
| UI de submissão (003, proto 002, dashboard 001/004) | **G4 Scale** (`#32445A`, `#466381`, gelo/cinza) | este diretório |
| Brief / GitHub markdown | sem tema | não estilizar README com CSS de marca |
| glam / Bfluence | rosa `#fe357b` | **proibido** neste git |
| Rebrand institucional G4 2026 (esfera armilar, dourado) | outro sistema | **não** está neste PDF — não misturar |
| Chrome Behance (págs. 6–7) | azul Adobe / preto footer | **não** é marca G4 Scale |

## Regras

- Cor via token `--g4s-*`. Sem hex solto em componente novo.
- Sem acento rosa, dourado editorial, roxo Material ou azul Behance.
- Família do wordmark **não é nomeada** no PDF. Fallback de implementação está marcado como **derivado**.
- Brand do desafio: **G4 Scale** / **G4**. Empresa fictícia do 001: **RavenStack** (não aplicar este DS como se fosse produto RavenStack — o DS é da plataforma G4).
