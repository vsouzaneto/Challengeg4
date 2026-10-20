"""FastAPI server: content pages, the Power BI-style explorer and the prediction API.

Run (from submissions/rafael): .venv/bin/social-web            → http://127.0.0.1:8000
                               .venv/bin/social-web --rebuild  → retrain models and rebuild content after new data
"""
import argparse
import math
from functools import lru_cache
import re
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from social_insights import audience_segments
from social_insights.site_export import _clean

from . import explore
from .schemas import AudienceQuery, ExploreQuery, PostInput
from .state import AppState, load_state

HERE = Path(__file__).resolve().parent
PAGES = {"/": ("inicio.html", "Resumo"), "/perguntas": ("perguntas.html", "As 4 perguntas"), "/estrategia": ("estrategia.html", "Estratégia"),
         "/descobertas": ("descobertas.html", "Descobertas"), "/explorar": ("explorar.html", "Explorar dados"),
         "/simular": ("simular.html", "Simular post"), "/audiencia": ("audiencia.html", "Agrupamento de audiência"),
         "/auditorias": ("auditorias.html", "Auditorias"), "/metodo": ("metodo.html", "Como chegamos lá")}
MAIN_PAGES = ["/", "/explorar", "/simular", "/audiencia"]
DEEP_PAGES = ["/perguntas", "/estrategia", "/descobertas", "/auditorias", "/metodo"]
TIME_NOTE = "Horários assumem um relógio único (a base não informa fuso horário)."
LABELS = {"platform": "Plataforma", "content_type": "Formato", "content_category": "Tema", "language": "Idioma", "follower_tier": "Tamanho do creator",
          "is_sponsored": "Patrocinado", "sponsor_category": "Setor do patrocinador", "daypart": "Período do dia", "weekday": "Dia da semana",
          "length_bin": "Duração", "n_hashtags": "Nº de hashtags", "month_name": "Mês", "hour": "Hora",
          "audience_gender_distribution": "Gênero do público", "audience_age_distribution": "Idade do público", "audience_location": "País do público"}
VALUES = {"video": "vídeo", "image": "imagem", "text": "texto", "mixed": "misto", "English": "inglês", "Spanish": "espanhol", "Chinese": "chinês",
          "Hindi": "hindi", "Japanese": "japonês", "True": "sim", "False": "não", "Monday": "segunda", "Tuesday": "terça", "Wednesday": "quarta",
          "Thursday": "quinta", "Friday": "sexta", "Saturday": "sábado", "Sunday": "domingo", "female": "feminino", "male": "masculino",
          "non-binary": "não binário", "unknown": "não identificado", "views": "views", "likes": "likes", "comments_count": "comentários",
          "January": "janeiro", "February": "fevereiro", "March": "março", "April": "abril", "May": "maio", "June": "junho", "July": "julho",
          "August": "agosto", "September": "setembro", "October": "outubro", "November": "novembro", "December": "dezembro",
          "Portuguese": "português", "German": "alemão", "Russian": "russo", "French": "francês", "USA": "EUA", "UK": "Reino Unido",
          "India": "Índia", "Japan": "Japão", "Brazil": "Brasil", "Germany": "Alemanha", "Russia": "Rússia", "China": "China",
          "cosmetics": "cosméticos", "electronics": "eletrônicos", "fashion": "moda", "food": "alimentação", "gaming": "games", "travel": "viagem"}


def num(value, digits: int = 0) -> str:
    """pt-BR number: 12.345,6."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "—"
    text = f"{float(value):,.{digits}f}"
    return text.replace(",", "X").replace(".", ",").replace("X", ".")


def pt_text(text: str) -> str:
    """Convert numbers inside generated sentences ("1,234.5") to pt-BR ("1.234,5")."""
    return re.sub(r"(\d)([.,])(?=(\d+))", lambda m: m.group(1) + ("," if m.group(2) == "." else ("." if len(m.group(3)) == 3 else ",")), text)


MEDIA_WORDS = re.compile(r"\b(video|image|text|mixed)\b")


def media_words(text: str) -> str:
    """Translate raw media-type words inside generated sentences (whole words only)."""
    return MEDIA_WORDS.sub(lambda m: VALUES[m.group(1)], text)


VALUE_WORDS = re.compile(r"\b(" + "|".join(re.escape(k) for k in VALUES if k[0].isupper()) + r")\b")


def value_words(text: str) -> str:
    """Translate raw category values (languages, countries, weekdays...) inside generated sentences."""
    return VALUE_WORDS.sub(lambda m: VALUES[m.group(1)], media_words(text))


def create_app(state: AppState) -> FastAPI:
    app = FastAPI(title="G4 Marketing", description="Análise de social media, painel exploratório e previsão antes de postar.",
                  version="1.0.0")
    app.mount("/static", StaticFiles(directory=HERE / "static"), name="static")
    templates = Jinja2Templates(directory=HERE / "templates")
    templates.env.filters.update(num=num, pct=lambda v, d=1: "—" if v is None else f"{num(v, d)}%", pt=pt_text,
                                 label=lambda k: LABELS.get(k, k), val=lambda v: VALUES.get(str(v), str(v)), words=media_words,
                                 values=value_words)
    templates.env.globals.update(PAGES=PAGES, MAIN_PAGES=MAIN_PAGES, DEEP_PAGES=DEEP_PAGES, LABELS=LABELS, VALUES=VALUES,
                                 TIME_NOTE=TIME_NOTE)

    def page(path: str):
        template, title = PAGES[path]

        async def handler(request: Request) -> HTMLResponse:
            return templates.TemplateResponse(request, template, {"d": state.payload, "title": title, "path": path})
        return handler

    for path in PAGES:
        app.add_api_route(path, page(path), methods=["GET"], response_class=HTMLResponse, include_in_schema=False)

    @app.api_route("/favicon.ico", methods=["GET", "HEAD"], include_in_schema=False)
    def favicon() -> FileResponse:
        return FileResponse(HERE / "static" / "img" / "favicon.ico", media_type="image/x-icon")

    @app.get("/prever", include_in_schema=False)
    def old_predict_page() -> RedirectResponse:
        return RedirectResponse("/simular", status_code=301)

    @app.get("/api/health", tags=["sistema"])
    def health() -> dict:
        return {"status": "ok", "posts": len(state.posts)}

    @app.get("/api/options", tags=["explorar"])
    def options() -> dict:
        return _clean(explore.options(state.posts) | {"rotulos": LABELS, "valores": VALUES})

    @app.post("/api/explore", tags=["explorar"])
    def explore_data(query: ExploreQuery) -> dict:
        try:
            result = explore.explore(state.posts, query.filtros, query.dimensao, query.metrica, query.linha, query.coluna, query.de, query.ate,
                                     query.graficos)
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        return _clean(result)

    @lru_cache(maxsize=256)
    def audience(platform: str | None, content_type: str | None, content_category: str | None, k: int | None) -> dict:
        filtros = {"platform": platform, "content_type": content_type, "content_category": content_category}
        return _clean(audience_segments.segment(state.posts, filtros, k))

    @app.post("/api/audience", tags=["audiência"])
    def audience_segments_api(query: AudienceQuery) -> dict:
        return audience(query.platform, query.content_type, query.content_category, query.k)

    @app.post("/api/predict", tags=["prever"])
    def predict(post: PostInput) -> dict:
        data = post.model_dump()
        return _clean(state.predictor.predict(data, goal=data.pop("objetivo")))

    return app


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--rebuild", action="store_true", help="retreina os modelos e recalcula o conteúdo")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--build-only", action="store_true", help="só treina e grava modelos e conteúdo em solution/models (sem subir o site)")
    args = parser.parse_args()
    import uvicorn
    print("Carregando dados e modelos (a 1ª execução treina tudo e leva alguns minutos)…", flush=True)
    state = load_state(rebuild=args.rebuild)
    if args.build_only:
        print("Modelos e conteúdo gravados em solution/models.", flush=True)
        return
    app = create_app(state)
    print(f"Pronto: http://{args.host}:{args.port}  ·  API: http://{args.host}:{args.port}/docs", flush=True)
    uvicorn.run(app, host=args.host, port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
