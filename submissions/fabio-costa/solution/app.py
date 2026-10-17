from __future__ import annotations

from pathlib import Path
import hashlib
import hmac
import json

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

from src.data_audit import DataAudit
from src.dataset_explorer import DatasetExplorer
from src.dataset2_diagnostics import Dataset2Diagnostics
from src.diagnostics import OperationalDiagnostics
from src.cross_analysis import CrossAnalysis

# -----------------------------------------------------------------------------
# APPLICATION PATHS
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"

SESSION_SECRET_FILE = BASE_DIR.parents[1] / ".aimaster_session_secret"

AUTH_USERNAME = "admin"
AUTH_PASSWORD_SHA256 = "608ad597dc74db593048f73a85c1c5a92f9a4466b5c2a5024e872e324bafcff8"


# -----------------------------------------------------------------------------
# APPLICATION FACTORY AND HTTP ROUTES
# -----------------------------------------------------------------------------
def create_app() -> Flask:
    app = Flask(__name__)

    app.secret_key = SESSION_SECRET_FILE.read_text(
        encoding="utf-8"
    ).strip()

    app.config.update(
        JSON_SORT_KEYS=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )

    def get_ui_catalog():
        from configparser import ConfigParser
        catalog = ConfigParser(interpolation=None, delimiters=("=",), strict=True)
        catalog.optionxform = str
        with (BASE_DIR / "languages/pt-br/traducoes.ini").open(encoding="utf-8") as f:
            catalog.read_file(f)
        items = {}
        for section in catalog.sections():
            for english, portuguese in catalog.items(section):
                if english in items:
                    raise RuntimeError("Duplicate PT-BR key: " + english)
                items[english] = portuguese
        return items

    def get_ui_language():
        return 'pt-BR' if session.get('aimaster_language') == 'pt-BR' else 'en'

    @app.before_request
    def require_auth():
        requested_language = request.args.get('lang')
        if requested_language in ('en', 'pt-BR') and request.method == 'GET':
            session['aimaster_language'] = requested_language
        public_endpoints = {"login", "static", "health"}

        if request.endpoint in public_endpoints:
            return None

        if session.get("authenticated") is True:
            return None

        if request.path.startswith("/api/"):
            return jsonify({
                "status": "unauthorized",
                "message": "Authentication required.",
            }), 401

        return redirect(
            url_for(
                "login",
                next=request.path,
            )
        )

    @app.route("/login", methods=["GET", "POST"])
    def login():
        error = None
        next_url = request.args.get("next", "/")

        if (
            not next_url.startswith("/")
            or next_url.startswith("//")
        ):
            next_url = "/"

        if request.method == "POST":
            username = request.form.get(
                "username",
                "",
            )

            password = request.form.get(
                "password",
                "",
            )

            password_hash = hashlib.sha256(
                password.encode("utf-8")
            ).hexdigest()

            valid_username = hmac.compare_digest(
                username,
                AUTH_USERNAME,
            )

            valid_password = hmac.compare_digest(
                password_hash,
                AUTH_PASSWORD_SHA256,
            )

            if valid_username and valid_password:
                chosen_language = get_ui_language()
                session.clear()
                session["aimaster_language"] = chosen_language
                session["authenticated"] = True

                return redirect(next_url)

            error = "Invalid username or password."

        ui_lang = get_ui_language()
        labels = get_ui_catalog() if ui_lang == 'pt-BR' else {}
        return render_template(
            "login.html",
            error=error,
            next_url=next_url,
            ui_lang=ui_lang,
            tr=lambda english: labels.get(english, english),
        )

    @app.get("/logout")
    def logout():
        selected_lang = get_ui_language()
        session.clear()
        session["aimaster_language"] = selected_lang
        return redirect(url_for("login"))

    @app.get("/pt-br/_preview")
    @app.get("/")
    def dashboard():
        report_path = BASE_DIR / "artifacts/training/runs/20261009T030639-217a27c7/benchmark.json"
        expected_sha = "c19eb461280a3f9a6dcaee13f8e60a32633bdc31af6db016dbf6f05552f466a3"
        training_report = None
        if report_path.is_file():
            content = report_path.read_bytes()
            if hashlib.sha256(content).hexdigest() == expected_sha:
                training_report = json.loads(content)
        # BEGIN: i18n.pt_br.preview.dashboard
        ui_lang = ('pt-BR' if request.path == '/pt-br/_preview'
                   else get_ui_language())
        translated_labels = get_ui_catalog() if ui_lang == 'pt-BR' else {}
        return render_template(
            'index.html',
            training_report=training_report,
            ui_lang=ui_lang,
            ui_catalog=translated_labels,
            tr=lambda english: translated_labels.get(english, english),
        )
        # END: i18n.pt_br.preview.dashboard

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "service": "AI Master Support Intelligence"})

    @app.get("/api/audit")
    def audit():
        return jsonify(DataAudit(RAW_DIR).run())

    @app.get("/api/diagnostic")
    def diagnostic():
        return jsonify(OperationalDiagnostics(RAW_DIR).run())

    @app.get("/api/diagnostic/cross-analysis")
    def diagnostic_cross_analysis():
        result = CrossAnalysis(
            RAW_DIR
        ).analyze(
            scope=request.args.get(
                "scope",
                "open_pending",
            ),
            dimension_a=request.args.get(
                "dimension_a",
                "channel",
            ),
            dimension_b=request.args.get(
                "dimension_b",
                "ticket_type",
            ),
            metric=request.args.get(
                "metric",
                "ticket_count",
            ),
        )

        status_code = (
            200
            if result.get("status")
            == "ready"
            else 400
        )

        return jsonify(
            result
        ), status_code

    @app.get("/api/explorer/summary")
    def explorer_summary():
        return jsonify(DatasetExplorer(RAW_DIR).summary())

    @app.get("/api/dataset2/diagnostic")
    def dataset2_diagnostic():
        return jsonify(Dataset2Diagnostics(RAW_DIR).run())

    @app.get("/api/explorer/<dataset_id>/rows")
    def explorer_rows(dataset_id: str):
        result = DatasetExplorer(RAW_DIR).rows(
            dataset_id=dataset_id,
            page=request.args.get("page", default=1, type=int) or 1,
            page_size=request.args.get("page_size", default=25, type=int) or 25,
            query=request.args.get("q", default="", type=str) or "",
            filter_field=request.args.get("filter_field", default="", type=str) or "",
            filter_value=request.args.get("filter_value", default="", type=str) or "",
        )
        status = 400 if result.get("status") == "error" else 200
        return jsonify(result), status

    return app


# -----------------------------------------------------------------------------
# WSGI ENTRYPOINT
# -----------------------------------------------------------------------------
app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
