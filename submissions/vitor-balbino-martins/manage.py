#!/usr/bin/env python
"""
manage.py - CLI interno de gerenciamento do projeto / Internal project management CLI.
Execute a partir da raiz do projeto / Run from the project root:

  python manage.py <comando> [opcoes]

Comandos disponiveis / Available commands:
  run            Inicia o servidor de desenvolvimento / Start dev server
  add-resource   Scaffold completo com banco de dados / Full resource with DB layer
  add-service    Apenas logica de negocio, sem banco / Business logic only, no DB
  add-middleware Scaffold de middleware customizado / Custom middleware scaffold
  add-proxy      Cliente HTTP para API externa / HTTP client for external API
  routes         Lista rotas registradas / List registered routes
  migrate        Gera e aplica migration Alembic / Generate and apply Alembic migration

Use  python manage.py <comando> --help  para detalhes de cada comando.
Use  python manage.py <command> --help  for details on each command.
"""
import sys
import subprocess
import typer
from pathlib import Path

app = typer.Typer(
    name="manage",
    help=(
        "CLI de gerenciamento do projeto FastAPI.\n\n"
        "FastAPI project management CLI.\n\n"
        "Execute 'python manage.py <comando> --help' para detalhes.\n"
        "Run 'python manage.py <command> --help' for details."
    ),
    add_completion=False,
    no_args_is_help=True,
)


def _ok(m):   typer.echo(typer.style("  [OK] " + str(m), fg=typer.colors.GREEN))
def _info(m): typer.echo(typer.style("  [i]  " + str(m), fg=typer.colors.CYAN))
def _warn(m): typer.echo(typer.style("  [!]  " + str(m), fg=typer.colors.YELLOW))
def _err(m):  typer.echo(typer.style("  [X]  " + str(m), fg=typer.colors.RED))
def _sec(t):  typer.echo(typer.style("\n  -- " + t, bold=True))


def _write(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _touch(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.touch()


def _to_class(name):
    return "".join(w.capitalize() for w in name.split("_"))


def _check_root():
    if not Path("main.py").exists():
        _err("main.py nao encontrado. Execute na raiz do projeto.")
        _err("main.py not found. Run from the project root.")
        raise typer.Exit(1)


# ----------------------------------------------------------------
# run
# ----------------------------------------------------------------

@app.command()
def run(
    port:    int  = typer.Option(8000,        "--port",   "-p",  help="Porta do servidor / Server port"),
    host:    str  = typer.Option("127.0.0.1", "--host",          help="Host do servidor / Server host"),
    reload:  bool = typer.Option(True,  "--reload/--no-reload",   help="Hot-reload ao salvar / Hot-reload on save"),
    workers: int  = typer.Option(1,     "--workers", "-w",        help="Numero de workers / Worker count"),
):
    """
    Inicia o servidor uvicorn de desenvolvimento.
    Start the uvicorn development server.

    \b
    Exemplos / Examples:
      python manage.py run
      python manage.py run --port 8080 --no-reload
      python manage.py run --workers 4 --host 0.0.0.0
    """
    cmd = [sys.executable, "-m", "uvicorn", "main:app",
           "--host", host, "--port", str(port), "--workers", str(workers)]
    if reload:
        cmd.append("--reload")
    _info("http://" + host + ":" + str(port) + "  (reload=" + str(reload) + ", workers=" + str(workers) + ")")
    subprocess.run(cmd)


# ----------------------------------------------------------------
# add-resource  (completo, com banco de dados)
# ----------------------------------------------------------------

@app.command()
def add_resource(
    name: str = typer.Argument(
        ...,
        help=(
            "Nome do recurso em snake_case singular. "
            "Resource name in singular snake_case. "
            "Ex: product, user_profile, sales_order"
        ),
    ),
    auth:      bool = typer.Option(False, "--auth/--no-auth",
        help="Protege as rotas com autenticacao / Protect routes with auth dependency"),
    dto:       bool = typer.Option(True,  "--dto/--no-dto",
        help="Gera schemas Pydantic (Create/Update/Response) / Generate Pydantic schemas"),
    repo:      bool = typer.Option(True,  "--repo/--no-repo",
        help="Gera Repository com acesso ao banco / Generate Repository with DB access"),
    proxy:     bool = typer.Option(False, "--proxy/--no-proxy",
        help="Gera cliente HTTP para API externa / Generate HTTP client for external API"),
    events:    bool = typer.Option(False, "--events/--no-events",
        help="Emite evento de dominio ao criar / Emit domain event on create"),
    paginated: bool = typer.Option(True,  "--paginated/--no-paginated",
        help="Retorna lista paginada / Return paginated list response"),
    version:   str  = typer.Option("v1",  "--version",
        help="Versao da API / API version prefix (ex: v1, v2)"),
):
    """
    Scaffold COMPLETO: model ORM + schema + repository + service + endpoint HTTP.
    FULL scaffold: ORM model + schema + repository + service + HTTP endpoint.

    \b
    Gerado / Generated:
      models/<name>.py                 -> SQLAlchemy ORM model
      schemas/<name>.py                -> Pydantic DTOs (Create / Update / Response)
      repositories/<name>_repository.py-> Repository Pattern com SQLAlchemy
      services/<name>_service.py       -> Regras de negocio / Business logic
      api/v1/endpoints/<name>.py       -> Rotas HTTP (GET/POST/PUT/DELETE)

    \b
    Use quando / Use when:
      - O recurso precisa persistir dados no banco de dados
      - The resource needs to persist data in the database

    \b
    Exemplos / Examples:
      python manage.py add-resource product
      python manage.py add-resource order --auth --events --paginated
      python manage.py add-resource payment --proxy
      python manage.py add-resource log_entry --no-dto --no-paginated
    """
    _check_root()
    base = Path(".")
    cap  = _to_class(name)
    typer.echo(typer.style("\nRecurso completo / Full resource: " + name + " (" + cap + ")\n", bold=True))

    if not repo:
        _err("--no-repo nao e suportado em add-resource: o endpoint gerado depende do repository.")
        _err("--no-repo is not supported here: the generated endpoint depends on the repository.")
        _info("Para logica de negocio sem banco use / For DB-less business logic use:")
        _info("  python manage.py add-service " + name)
        raise typer.Exit(1)

    if dto:
        _gen_schemas(base, name, cap)
        _ok("schemas/" + name + ".py")

    _gen_model(base, name, cap)
    _ok("models/" + name + ".py")
    _gen_repository(base, name, cap)
    _ok("repositories/" + name + "_repository.py")

    _gen_service(base, name, cap, dto, repo, events, paginated)
    _ok("services/" + name + "_service.py")

    if proxy:
        _gen_proxy(base, name, cap)
        _ok("infrastructure/http/" + name + "_client.py")

    _gen_endpoint(base, name, cap, auth, dto, paginated, version)
    _ok("api/" + version + "/endpoints/" + name + ".py")
    _register(base, name, version)
    _ok("Rota registrada / Route registered: /" + name + "s")

    typer.echo(typer.style("\n[OK] '" + name + "' pronto! / ready!\n", fg=typer.colors.GREEN, bold=True))
    _warn("Nao esqueca a migration / Do not forget the migration:")
    _warn('  python manage.py migrate -m "add ' + name + '"')


# ----------------------------------------------------------------
# add-service  (logica de negocio pura, sem banco)
# ----------------------------------------------------------------

@app.command()
def add_service(
    name: str = typer.Argument(
        ...,
        help=(
            "Nome do servico em snake_case singular. "
            "Service name in singular snake_case. "
            "Ex: pricing, notification, tax_calculator"
        ),
    ),
    dto:    bool = typer.Option(True,  "--dto/--no-dto",
        help="Gera schemas Pydantic de entrada/saida / Generate Pydantic input/output schemas"),
    events: bool = typer.Option(False, "--events/--no-events",
        help="Emite eventos de dominio / Emit domain events"),
    inject: str  = typer.Option("",   "--inject",
        help=(
            "Dependencias externas a injetar, separadas por virgula. "
            "External dependencies to inject, comma-separated. "
            "Ex: --inject order_service,product_service"
        )),
):
    """
    Scaffold LEVE: apenas schema + service com logica de negocio pura.
    LIGHTWEIGHT scaffold: schema + pure business logic service only.

    \b
    NAO gera / Does NOT generate:
      - Model ORM (sem acesso direto ao banco / no direct DB access)
      - Repository
      - Endpoint HTTP

    \b
    GERA / Generates:
      schemas/<name>.py          -> DTOs de entrada e saida / Input & output DTOs
      services/<name>_service.py -> Logica de negocio pura / Pure business logic

    \b
    Use quando / Use when:
      - Regra de negocio que consome dados de outros servicos/repositorios ja existentes
      - Calculos, validacoes, orquestracoes, notificacoes internas
      - Business rule that consumes data from existing services/repositories
      - Calculations, validations, orchestrations, internal notifications

    \b
    Como consumir / How to consume:
      # Em outro servico / In another service:
      from services.pricing_service import PricingService
      svc = PricingService(order_service=order_svc, product_service=product_svc)

      # Em um endpoint / In an endpoint:
      def _svc(order_svc=Depends(get_order_service)) -> PricingService:
          return PricingService(order_service=order_svc)

    \b
    Exemplos / Examples:
      python manage.py add-service pricing
      python manage.py add-service notification --events
      python manage.py add-service tax_calculator --inject order_service,product_service
      python manage.py add-service discount_engine --dto --events
    """
    _check_root()
    base = Path(".")
    cap  = _to_class(name)
    typer.echo(typer.style("\nServico leve / Lightweight service: " + name + " (" + cap + ")\n", bold=True))

    deps = [d.strip() for d in inject.split(",") if d.strip()] if inject else []

    if dto:
        _gen_service_schemas(base, name, cap)
        _ok("schemas/" + name + ".py")

    _gen_pure_service(base, name, cap, dto, events, deps)
    _ok("services/" + name + "_service.py")

    typer.echo(typer.style("\n[OK] '" + name + "' pronto! / ready!\n", fg=typer.colors.GREEN, bold=True))

    if deps:
        _info("Injetar no endpoint / Inject in endpoint:")
        for d in deps:
            _info("  from services." + d + "_service import " + _to_class(d) + "Service")
    _info("Importar onde precisar / Import wherever needed:")
    _info("  from services." + name + "_service import " + cap + "Service")


# ----------------------------------------------------------------
# add-middleware
# ----------------------------------------------------------------

@app.command()
def add_middleware(
    name: str = typer.Argument(
        ...,
        help="Nome do middleware em snake_case / Middleware name in snake_case. Ex: rate_limit, cors_custom"
    ),
):
    """
    Scaffold de middleware Starlette customizado.
    Scaffold a custom Starlette middleware.

    \b
    Gerado / Generated:
      middlewares/<name>.py -> Classe middleware pronta para implementar

    \b
    Apos criar, registre em main.py / After creating, register in main.py:
      app.add_middleware(<Name>Middleware)

    \b
    Exemplos / Examples:
      python manage.py add-middleware rate_limit
      python manage.py add-middleware request_id
      python manage.py add-middleware audit_log
    """
    _check_root()
    cap = _to_class(name)
    content = "\n".join([
        "import logging",
        "from fastapi import Request",
        "from starlette.middleware.base import BaseHTTPMiddleware",
        "",
        "logger = logging.getLogger(__name__)",
        "",
        "",
        "class " + cap + "Middleware(BaseHTTPMiddleware):",
        '    """',
        "    Middleware: " + name + ".",
        "    TODO: implemente a logica abaixo / implement logic below.",
        '    """',
        "",
        "    async def dispatch(self, request: Request, call_next):",
        "        # --- pre-processamento / pre-processing ---",
        "        response = await call_next(request)",
        "        # --- pos-processamento / post-processing ---",
        "        return response",
        "",
    ])
    _write(Path("middlewares") / (name + ".py"), content)
    _ok("middlewares/" + name + ".py")
    _warn("Registre em main.py / Register in main.py:  app.add_middleware(" + cap + "Middleware)")


# ----------------------------------------------------------------
# add-proxy
# ----------------------------------------------------------------

@app.command()
def add_proxy(
    name:     str = typer.Argument(
        ...,
        help="Nome do cliente em snake_case / Client name in snake_case. Ex: payment_gateway, erp_api"
    ),
    base_url: str = typer.Option(
        "https://api.example.com", "--url",
        help="URL base da API externa / Base URL of the external API"
    ),
):
    """
    Scaffold de cliente HTTP assincrono (httpx) para API externa.
    Scaffold an async httpx HTTP client for an external API.

    \b
    Gerado / Generated:
      infrastructure/http/<name>_client.py -> Cliente com metodos CRUD

    \b
    Exemplos / Examples:
      python manage.py add-proxy payment_gateway --url https://api.stripe.com
      python manage.py add-proxy erp_api --url https://erp.empresa.com/api
    """
    _check_root()
    _gen_proxy(Path("."), name, _to_class(name), base_url)
    _ok("infrastructure/http/" + name + "_client.py")


# ----------------------------------------------------------------
# routes
# ----------------------------------------------------------------

@app.command()
def routes(
    version: str = typer.Option("v1", "--version", help="Versao da API / API version. Ex: v1, v2"),
):
    """
    Lista todas as rotas HTTP registradas.
    List all registered HTTP routes.

    \b
    Exemplos / Examples:
      python manage.py routes
      python manage.py routes --version v2
    """
    init = Path("api") / version / "__init__.py"
    if not init.exists():
        _err("api/" + version + "/__init__.py nao encontrado / not found.")
        raise typer.Exit(1)
    typer.echo(typer.style("\nRotas registradas / Registered routes  (api/" + version + ")\n", bold=True))
    for line in init.read_text(encoding="utf-8").splitlines():
        if "include_router" in line:
            typer.echo("  " + line.strip())
    typer.echo()


# ----------------------------------------------------------------
# migrate
# ----------------------------------------------------------------

@app.command()
def migrate(
    msg:      str  = typer.Option("auto", "-m", "--msg", help="Mensagem da migration / Migration message"),
    init:     bool = typer.Option(False, "--init",       help="Reescreve a config do Alembic / Rewrite Alembic config"),
    only_gen: bool = typer.Option(False, "--only-gen",   help="So gera o arquivo, nao aplica / Only generate, do not apply"),
):
    """
    Gera e aplica migrations Alembic. Inicializa automaticamente se necessario.
    Generate and apply Alembic migrations. Auto-initializes if needed.

    \b
    O que faz / What it does:
      1. Garante que alembic.ini e env.py existem e estao atualizados
      2. Gera nova revision com --autogenerate
      3. Aplica com upgrade head (a menos que --only-gen)

    \b
    Equivalente a / Equivalent to:
      alembic revision --autogenerate -m <msg>
      alembic upgrade head

    \b
    Exemplos / Examples:
      python manage.py migrate
      python manage.py migrate -m "add product table"
      python manage.py migrate --init
      python manage.py migrate --only-gen -m "draft"
    """
    _check_root()
    ini_path  = Path("alembic.ini")
    mig_dir   = Path("infrastructure") / "database" / "migrations"
    env_path  = mig_dir / "env.py"
    mako_path = mig_dir / "script.py.mako"

    if init or not ini_path.exists():
        _info("Configurando Alembic / Configuring Alembic...")
        _write(ini_path, _ALEMBIC_INI)
        _ok("alembic.ini configurado / configured")

    if init or not env_path.exists():
        _write(env_path, _ALEMBIC_ENV_PY)
        _ok("migrations/env.py configurado / configured")
    else:
        env_txt = env_path.read_text(encoding="utf-8")
        if "run_async_migrations" not in env_txt:
            _warn("env.py desatualizado, atualizando / outdated, updating...")
            _write(env_path, _ALEMBIC_ENV_PY)
            _ok("env.py atualizado / updated")

    if not mako_path.exists():
        _write(mako_path, _ALEMBIC_SCRIPT_MAKO)
        _ok("migrations/script.py.mako configurado / configured")

    _touch(mig_dir / "versions" / ".gitkeep")

    _info('Gerando revision / Generating revision: "' + msg + '"')
    r = subprocess.run(
        [sys.executable, "-m", "alembic", "revision", "--autogenerate", "-m", msg],
    )
    if r.returncode != 0:
        _err("Falha ao gerar revision / Failed to generate revision")
        raise typer.Exit(1)

    if only_gen:
        _warn("--only-gen: migration gerada mas NAO aplicada / generated but NOT applied")
        return

    _info("Aplicando / Applying: upgrade head")
    subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"])


_ALEMBIC_INI = "[alembic]\nscript_location = infrastructure/database/migrations\nprepend_sys_path = .\nversion_path_separator = os\n# sqlalchemy.url gerenciado pelo env.py / managed by env.py\n\n[loggers]\nkeys = root,sqlalchemy,alembic\n\n[handlers]\nkeys = console\n\n[formatters]\nkeys = generic\n\n[logger_root]\nlevel = WARN\nhandlers = console\nqualname =\n\n[logger_sqlalchemy]\nlevel = WARN\nhandlers =\nqualname = sqlalchemy.engine\n\n[logger_alembic]\nlevel = INFO\nhandlers =\nqualname = alembic\n\n[handler_console]\nclass = StreamHandler\nargs = (sys.stderr,)\nlevel = NOTSET\nformatter = generic\n\n[formatter_generic]\n# fileConfig() reads these with raw=True, so '%' must NOT be doubled here.\nformat = %(levelname)-5.5s [%(name)s] %(message)s\ndatefmt = %H:%M:%S\n"


_ALEMBIC_ENV_PY = 'import asyncio\nimport sys\nimport os\nfrom logging.config import fileConfig\nfrom pathlib import Path\nfrom sqlalchemy import pool\nfrom sqlalchemy.engine import Connection\nfrom sqlalchemy.ext.asyncio import async_engine_from_config\nfrom alembic import context\n\n_root = Path(__file__).parent.parent.parent.parent\nif str(_root) not in sys.path:\n    sys.path.insert(0, str(_root))\n\n_env_file = _root / ".env"\nif _env_file.exists():\n    for _line in _env_file.read_text(encoding="utf-8").splitlines():\n        _line = _line.strip()\n        if _line and not _line.startswith("#") and "=" in _line:\n            _k, _, _v = _line.partition("=")\n            os.environ.setdefault(_k.strip(), _v.strip())\n\nfrom infrastructure.database.base import Base\nimport importlib\nimport pkgutil\n\n_models_dir = _root / "models"\nif _models_dir.exists():\n    for _mod in pkgutil.iter_modules([str(_models_dir)]):\n        importlib.import_module("models." + _mod.name)\n\nconfig = context.config\nif config.config_file_name is not None:\n    fileConfig(config.config_file_name)\n\ntarget_metadata = Base.metadata\n\n\ndef _get_url() -> str:\n    try:\n        from core.config import settings\n        return settings.DATABASE_URL\n    except Exception:\n        url = os.environ.get("DATABASE_URL", "")\n        if not url:\n            raise RuntimeError(\n                "DATABASE_URL nao encontrada. Defina no arquivo .env\\n"\n                "DATABASE_URL not found. Define it in the .env file"\n            )\n        return url\n\n\ndef run_migrations_offline() -> None:\n    context.configure(\n        url=_get_url(),\n        target_metadata=target_metadata,\n        literal_binds=True,\n        dialect_opts={"paramstyle": "named"},\n    )\n    with context.begin_transaction():\n        context.run_migrations()\n\n\ndef do_run_migrations(connection: Connection) -> None:\n    context.configure(connection=connection, target_metadata=target_metadata)\n    with context.begin_transaction():\n        context.run_migrations()\n\n\nasync def run_async_migrations() -> None:\n    cfg = config.get_section(config.config_ini_section, {})\n    cfg["sqlalchemy.url"] = _get_url()\n    engine = async_engine_from_config(\n        cfg, prefix="sqlalchemy.", poolclass=pool.NullPool,\n    )\n    async with engine.connect() as conn:\n        await conn.run_sync(do_run_migrations)\n    await engine.dispose()\n\n\ndef run_migrations_online() -> None:\n    asyncio.run(run_async_migrations())\n\n\nif context.is_offline_mode():\n    run_migrations_offline()\nelse:\n    run_migrations_online()\n'


_ALEMBIC_SCRIPT_MAKO = '"""${message}\n\nRevision ID: ${up_revision}\nRevises: ${down_revision | comma,n}\nCreate Date: ${create_date}\n"""\nfrom typing import Sequence, Union\nfrom alembic import op\nimport sqlalchemy as sa\n${imports if imports else ""}\n\nrevision: str = ${repr(up_revision)}\ndown_revision: Union[str, None] = ${repr(down_revision)}\nbranch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}\ndepends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}\n\n\ndef upgrade() -> None:\n    ${upgrades if upgrades else "pass"}\n\n\ndef downgrade() -> None:\n    ${downgrades if downgrades else "pass"}\n'


# ----------------------------------------------------------------
# Scaffold helpers - add-resource
# ----------------------------------------------------------------

def _gen_schemas(base, name, cap):
    out = [
        "from pydantic import BaseModel, Field, ConfigDict",
        "from typing import Optional",
        "from datetime import datetime",
        "",
        "",
        "class " + cap + "Base(BaseModel):",
        "    model_config = ConfigDict(from_attributes=True)",
        "    name:        str           = Field(..., min_length=1, max_length=255)",
        "    description: Optional[str] = Field(None, max_length=1000)",
        "",
        "",
        "class " + cap + "Create(" + cap + "Base):",
        "    pass",
        "",
        "",
        "class " + cap + "Update(BaseModel):",
        "    model_config = ConfigDict(from_attributes=True)",
        "    name:        Optional[str] = Field(None, min_length=1, max_length=255)",
        "    description: Optional[str] = Field(None, max_length=1000)",
        "",
        "",
        "class " + cap + "Response(" + cap + "Base):",
        "    id:         int",
        "    created_at: Optional[datetime] = None",
        "    updated_at: Optional[datetime] = None",
        "",
    ]
    _write(base / "schemas" / (name + ".py"), "\n".join(out))


def _gen_model(base, name, cap):
    out = [
        "from sqlalchemy import String, Text, Integer",
        "from sqlalchemy.orm import Mapped, mapped_column",
        "from infrastructure.database.base import Base, TimestampMixin",
        "",
        "",
        "class " + cap + "(Base, TimestampMixin):",
        '    __tablename__ = "' + name + 's"',
        "",
        "    id:          Mapped[int]        = mapped_column(Integer, primary_key=True, autoincrement=True)",
        "    name:        Mapped[str]        = mapped_column(String(255), nullable=False, index=True)",
        "    description: Mapped[str | None] = mapped_column(Text, nullable=True)",
        "",
        "    def __repr__(self) -> str:",
        '        return f"<' + cap + ' id={self.id} name={self.name!r}>"',
        "",
    ]
    _write(base / "models" / (name + ".py"), "\n".join(out))


def _gen_repository(base, name, cap):
    out = [
        "import logging",
        "from typing import Sequence",
        "from sqlalchemy import select, func",
        "from sqlalchemy.ext.asyncio import AsyncSession",
        "from models." + name + " import " + cap,
        "",
        "logger = logging.getLogger(__name__)",
        "",
        "",
        "class " + cap + "Repository:",
        "    def __init__(self, session: AsyncSession):",
        "        self._session = session",
        "",
        "    async def count(self) -> int:",
        "        r = await self._session.execute(select(func.count()).select_from(" + cap + "))",
        "        return r.scalar_one()",
        "",
        "    async def list(self, offset: int = 0, limit: int = 20) -> Sequence[" + cap + "]:",
        "        r = await self._session.execute(",
        "            select(" + cap + ").order_by(" + cap + ".id).offset(offset).limit(limit)",
        "        )",
        "        return r.scalars().all()",
        "",
        "    async def get(self, id: int) -> " + cap + " | None:",
        "        return await self._session.get(" + cap + ", id)",
        "",
        "    async def add(self, entity: " + cap + ") -> " + cap + ":",
        "        self._session.add(entity)",
        "        await self._session.flush()",
        "        await self._session.refresh(entity)",
        '        logger.info("Created ' + cap + ' id=%d", entity.id)',
        "        return entity",
        "",
        "    async def update(self, entity: " + cap + ", data: dict) -> " + cap + ":",
        "        for k, v in data.items():",
        "            if v is not None:",
        "                setattr(entity, k, v)",
        "        await self._session.flush()",
        "        await self._session.refresh(entity)",
        "        return entity",
        "",
        "    async def delete(self, entity: " + cap + ") -> None:",
        "        await self._session.delete(entity)",
        "        await self._session.flush()",
        '        logger.info("Deleted ' + cap + ' id=%d", entity.id)',
        "",
    ]
    _write(base / "repositories" / (name + "_repository.py"), "\n".join(out))


def _gen_service(base, name, cap, with_dto, with_repo, with_events, paginated):
    imports = [
        "import logging",
        "from core.exceptions import NotFoundException",
        "from core.responses import PaginatedResponse",
    ]
    if with_dto:
        imports.append("from schemas." + name + " import " + cap + "Create, " + cap + "Update")
    if with_repo:
        imports.append("from repositories." + name + "_repository import " + cap + "Repository")
    if with_events:
        imports.append("from infrastructure.events.bus import bus, DomainEvent")

    ct = cap + "Create" if with_dto else "dict"
    ut = cap + "Update" if with_dto else "dict"

    body = imports + [
        "",
        "logger = logging.getLogger(__name__)",
        "",
        "",
        "def _to_dict(obj) -> dict:",
        "    return {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}",
        "",
        "",
        "class " + cap + "Service:",
        "    def __init__(self, repository):",
        "        self._repo = repository",
        "",
        "    async def list(self, page: int = 1, page_size: int = 20) -> dict:",
        "        offset = (page - 1) * page_size",
        "        items  = await self._repo.list(offset=offset, limit=page_size)",
        "        total  = await self._repo.count()",
        "        return PaginatedResponse.build(",
        "            items=[_to_dict(i) for i in items],",
        "            total=total, page=page, page_size=page_size,",
        "        ).model_dump()",
        "",
        "    async def create(self, data: " + ct + ") -> dict:",
        "        from models." + name + " import " + cap,
        "        payload = data.model_dump() if hasattr(data, 'model_dump') else data",
        "        entity  = " + cap + "(**payload)",
        "        result  = await self._repo.add(entity)",
    ]
    if with_events:
        body.append(
            "        await bus.publish(DomainEvent('" + name + ".created', {'id': result.id}))"
        )
    body += [
        "        return _to_dict(result)",
        "",
        "    async def get(self, id: int) -> dict:",
        "        entity = await self._repo.get(id)",
        "        if not entity:",
        '            raise NotFoundException("' + cap + '", id)',
        "        return _to_dict(entity)",
        "",
        "    async def update(self, id: int, data: " + ut + ") -> dict:",
        "        entity = await self._repo.get(id)",
        "        if not entity:",
        '            raise NotFoundException("' + cap + '", id)',
        "        patch  = data.model_dump(exclude_unset=True) if hasattr(data, 'model_dump') else data",
        "        result = await self._repo.update(entity, patch)",
        "        return _to_dict(result)",
        "",
        "    async def delete(self, id: int) -> None:",
        "        entity = await self._repo.get(id)",
        "        if not entity:",
        '            raise NotFoundException("' + cap + '", id)',
        "        await self._repo.delete(entity)",
        "",
    ]
    _write(base / "services" / (name + "_service.py"), "\n".join(body))


# ----------------------------------------------------------------
# Scaffold helpers - add-service (logica pura / pure logic)
# ----------------------------------------------------------------

def _gen_service_schemas(base, name, cap):
    """DTOs simples de entrada/saida, sem from_attributes (nao mapeiam ORM)."""
    out = [
        "from pydantic import BaseModel, Field",
        "from typing import Optional, Any",
        "",
        "",
        "# --- Input / Entrada ---",
        "",
        "class " + cap + "Input(BaseModel):",
        '    """Dados de entrada para ' + name + ' / Input data for ' + name + '."""',
        "    # TODO: defina os campos de entrada / define input fields",
        "    payload: dict[str, Any] = Field(default_factory=dict)",
        "",
        "",
        "# --- Output / Saida ---",
        "",
        "class " + cap + "Output(BaseModel):",
        '    """Resultado do servico ' + name + ' / Output of ' + name + ' service."""',
        "    # TODO: defina os campos de saida / define output fields",
        "    result: dict[str, Any] = Field(default_factory=dict)",
        "    success: bool = True",
        "    message: Optional[str] = None",
        "",
    ]
    _write(base / "schemas" / (name + ".py"), "\n".join(out))


def _gen_pure_service(base, name, cap, with_dto, with_events, deps):
    imports = ["import logging"]
    if with_dto:
        imports.append("from schemas." + name + " import " + cap + "Input, " + cap + "Output")
    if with_events:
        imports.append("from infrastructure.events.bus import bus, DomainEvent")

    dep_args = []
    dep_assigns = []
    for d in deps:
        dep_args.append(d + "_service")
        dep_assigns.append("        self._" + d + " = " + d + "_service")

    init_params = ", ".join(dep_args)
    if init_params:
        init_params = ", " + init_params

    in_t  = cap + "Input"  if with_dto else "dict"
    out_t = cap + "Output" if with_dto else "dict"

    body = imports + [
        "",
        "logger = logging.getLogger(__name__)",
        "",
        "",
        "class " + cap + "Service:",
        '    """',
        "    Servico de logica de negocio: " + name + ".",
        "    Pure business logic service: " + name + ".",
        "",
        "    Nao acessa banco diretamente - consome outros servicos/repositorios.",
        "    Does not access DB directly - consumes other services/repositories.",
        '    """',
        "",
        "    def __init__(self" + init_params + "):",
    ]

    if dep_assigns:
        body += dep_assigns
    else:
        body.append("        pass  # injete dependencias conforme necessario / inject dependencies as needed")

    body += [
        "",
        "    async def execute(self, data: " + in_t + ") -> " + out_t + ":",
        '        """',
        "        Ponto de entrada principal do servico.",
        "        Main entry point of the service.",
        '        """',
        '        logger.info("Executing ' + name + ' service")',
        "",
        "        # TODO: implemente a logica de negocio / implement business logic",
        "        payload = data.payload if hasattr(data, 'payload') else data",
        "",
    ]

    if with_events:
        body += [
            "        # Emitir evento de dominio / Emit domain event",
            "        await bus.publish(DomainEvent('" + name + ".executed', {'payload': str(payload)}))",
            "",
        ]

    if with_dto:
        body += [
            "        return " + cap + "Output(result=payload, success=True)",
            "",
        ]
    else:
        body += [
            "        return {'result': payload, 'success': True}",
            "",
        ]

    _write(base / "services" / (name + "_service.py"), "\n".join(body))


# ----------------------------------------------------------------
# Scaffold helpers - proxy / http client
# ----------------------------------------------------------------

def _gen_proxy(base, name, cap, base_url="https://api.example.com"):
    _touch(base / "infrastructure" / "http" / "__init__.py")
    bc = base / "infrastructure" / "http" / "base_client.py"
    if not bc.exists():
        _write(bc, "\n".join([
            "import logging",
            "import httpx",
            "from typing import Any",
            "",
            "logger = logging.getLogger(__name__)",
            "",
            "",
            "class BaseHttpClient:",
            '    base_url: str  = ""',
            "    timeout: float = 10.0",
            "",
            "    def __init__(self):",
            "        self._client: httpx.AsyncClient | None = None",
            "",
            "    async def start(self):",
            "        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)",
            "",
            "    async def stop(self):",
            "        if self._client:",
            "            await self._client.aclose()",
            "",
            "    async def get(self, p, **kw):    return await self._req('GET',    p, **kw)",
            "    async def post(self, p, **kw):   return await self._req('POST',   p, **kw)",
            "    async def put(self, p, **kw):    return await self._req('PUT',    p, **kw)",
            "    async def delete(self, p, **kw): return await self._req('DELETE', p, **kw)",
            "",
            "    async def _req(self, method, path, **kw):",
            "        if self._client is None:",
            "            await self.start()",
            "        resp = await self._client.request(method, path, **kw)",
            "        resp.raise_for_status()",
            "        return resp.json()",
            "",
        ]))

    _write(base / "infrastructure" / "http" / (name + "_client.py"), "\n".join([
        "from infrastructure.http.base_client import BaseHttpClient",
        "",
        "",
        "class " + cap + "Client(BaseHttpClient):",
        '    base_url = "' + base_url + '"',
        "",
        "    async def list(self):",
        '        return await self.get("/' + name + 's")',
        "",
        "    async def get_one(self, id: int):",
        '        return await self.get(f"/' + name + 's/{id}")',
        "",
        "    async def create(self, data: dict):",
        '        return await self.post("/' + name + 's", json=data)',
        "",
        "    async def update(self, id: int, data: dict):",
        '        return await self.put(f"/' + name + 's/{id}", json=data)',
        "",
        "    async def remove(self, id: int):",
        '        return await self.delete(f"/' + name + 's/{id}")',
        "",
        "",
        name + "_client = " + cap + "Client()",
        "",
    ]))


# ----------------------------------------------------------------
# Scaffold helpers - endpoint + router registration
# ----------------------------------------------------------------

def _gen_endpoint(base, name, cap, use_auth, with_dto, paginated, version):
    lines = [
        "from fastapi import APIRouter, Depends, status",
        "from api." + version + ".dependencies.pagination import PaginationParams, get_pagination",
        "from infrastructure.database.session import get_db",
        "from repositories." + name + "_repository import " + cap + "Repository",
        "from services." + name + "_service import " + cap + "Service",
    ]
    if use_auth:
        lines.append("from api." + version + ".dependencies.auth import get_current_user")
    if with_dto:
        lines.append("from schemas." + name + " import " + cap + "Create, " + cap + "Update")

    ct = cap + "Create" if with_dto else "dict"
    ut = cap + "Update" if with_dto else "dict"
    auth_dep = ", current_user: dict = Depends(get_current_user)" if use_auth else ""

    lines += [
        "",
        "router = APIRouter()",
        "",
        "",
        "def _svc(db=Depends(get_db)) -> " + cap + "Service:",
        "    return " + cap + "Service(" + cap + "Repository(db))",
        "",
        "",
        '@router.get("/", summary="List ' + name + 's")',
        "async def list_" + name + "s(",
        "    pagination: PaginationParams = Depends(get_pagination),",
        "    svc: " + cap + "Service = Depends(_svc)" + auth_dep + ",",
        "):",
        "    return await svc.list(page=pagination.page, page_size=pagination.page_size)",
        "",
        "",
        '@router.post("/", status_code=status.HTTP_201_CREATED, summary="Create ' + name + '")',
        "async def create_" + name + "(data: " + ct + ", svc: " + cap + "Service = Depends(_svc)" + auth_dep + "):",
        "    return await svc.create(data)",
        "",
        "",
        '@router.get("/{id}", summary="Get ' + name + '")',
        "async def get_" + name + "(id: int, svc: " + cap + "Service = Depends(_svc)" + auth_dep + "):",
        "    return await svc.get(id)",
        "",
        "",
        '@router.put("/{id}", summary="Update ' + name + '")',
        "async def update_" + name + "(id: int, data: " + ut + ", svc: " + cap + "Service = Depends(_svc)" + auth_dep + "):",
        "    return await svc.update(id, data)",
        "",
        "",
        '@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete ' + name + '")',
        "async def delete_" + name + "(id: int, svc: " + cap + "Service = Depends(_svc)" + auth_dep + "):",
        "    await svc.delete(id)",
        "",
    ]
    _touch(base / "api" / version / "endpoints" / "__init__.py")
    _write(base / "api" / version / "endpoints" / (name + ".py"), "\n".join(lines))


def _register(base, name, version):
    init = base / "api" / version / "__init__.py"
    if not init.exists():
        _err("api/" + version + "/__init__.py nao encontrado / not found.")
        raise typer.Exit(1)
    content = init.read_text(encoding="utf-8")
    imp = "from api." + version + ".endpoints." + name + " import router as " + name + "_router\n"
    inc = 'router.include_router(' + name + '_router, prefix="/' + name + 's", tags=["' + name + '"])\n'
    if imp.strip() in content:
        _warn("'" + name + "' ja registrado / already registered.")
        return
    if not content.endswith("\n"):
        content += "\n"
    init.write_text(imp + content + inc, encoding="utf-8")


# ----------------------------------------------------------------
if __name__ == "__main__":
    app()
