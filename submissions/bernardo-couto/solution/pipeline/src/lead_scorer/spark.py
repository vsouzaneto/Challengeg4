"""Single entry point for SparkSession creation, including JAVA_HOME resolution.

Spark 3.5 runs on JDK 17 or 21 only. On this machine the system default is JDK 23, which
fails at startup with an opaque error, so we resolve a compatible JDK explicitly:
``JAVA_HOME`` env -> ``/usr/libexec/java_home -v 21`` -> ``-v 17`` -> plain ``java`` on PATH.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from pyspark.sql import SparkSession

SUPPORTED_MAJORS = (17, 21)
MAX_SUPPORTED_MAJOR = 21
_JAVA_HOME_TOOL = "/usr/libexec/java_home"


class UnsupportedJdkError(RuntimeError):
    """Raised when no JDK compatible with Spark 3.5 can be found."""


def _java_major(java_home: Path) -> int | None:
    """Return the major version of the JDK at ``java_home`` (parses ``java -version``)."""
    java = java_home / "bin" / "java"
    if not java.exists():
        return None
    try:
        out = subprocess.run(
            [str(java), "-version"], capture_output=True, text=True, timeout=20, check=False
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    match = re.search(r'version "(\d+)(?:\.(\d+))?', out.stderr + out.stdout)
    if not match:
        return None
    major = int(match.group(1))
    # Legacy "1.8.0" scheme: the second component is the real major.
    return int(match.group(2) or 0) if major == 1 else major


def _candidate_homes() -> list[Path]:
    homes: list[Path] = []
    env = os.environ.get("JAVA_HOME")
    if env:
        homes.append(Path(env))
    if sys.platform == "darwin" and Path(_JAVA_HOME_TOOL).exists():
        for version in ("21", "17"):
            try:
                res = subprocess.run(
                    [_JAVA_HOME_TOOL, "-v", version],
                    capture_output=True,
                    text=True,
                    timeout=20,
                    check=False,
                )
            except (OSError, subprocess.TimeoutExpired):
                continue
            if res.returncode == 0 and res.stdout.strip():
                homes.append(Path(res.stdout.strip()))
    java_on_path = shutil.which("java")
    if java_on_path:
        homes.append(Path(java_on_path).resolve().parent.parent)
    return homes


def resolve_java_home() -> Path:
    """Find a JDK 17/21, export it as ``JAVA_HOME`` and return it; raise with a pt-BR hint."""
    seen: dict[Path, int | None] = {}
    for home in _candidate_homes():
        if home in seen:
            continue
        major = _java_major(home)
        seen[home] = major
        # ``java_home -v 17`` means "17 or newer" on macOS, so we must check the real major.
        if major is not None and major in SUPPORTED_MAJORS:
            os.environ["JAVA_HOME"] = str(home)
            return home

    found = ", ".join(f"{h} (JDK {m})" for h, m in seen.items() if m is not None) or "nenhum"
    raise UnsupportedJdkError(
        "Nenhum JDK compativel com o Spark 3.5 foi encontrado. Sao suportados JDK 17 ou 21 "
        f"(JDK 23+ nao funciona). Encontrados: {found}.\n"
        "Como resolver:\n"
        "  - instale o Amazon Corretto 21 ou o Temurin 17 e exporte JAVA_HOME, ex.:\n"
        "      export JAVA_HOME=$(/usr/libexec/java_home -v 21)\n"
        "  - ou rode o pipeline pelo Docker: `docker compose --profile pipeline run --rm pipeline`."
    )


def get_spark(app_name: str = "lead-scorer", for_tests: bool = False) -> SparkSession:
    """Create (or reuse) the local SparkSession with the project defaults.

    ``for_tests`` lowers shuffle partitions and disables the UI so the pytest fixture starts fast.
    """
    resolve_java_home()
    builder = (
        SparkSession.builder.appName(app_name)
        .master("local[*]")
        .config("spark.sql.shuffle.partitions", "4" if for_tests else "8")
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.driver.memory", "1g" if for_tests else "2g")
        .config("spark.ui.enabled", "false" if for_tests else "true")
        .config("spark.ui.showConsoleProgress", "false")
        .config("spark.sql.adaptive.enabled", "false" if for_tests else "true")
    )
    return builder.getOrCreate()
