"""Carregamentos em cache e utilidades compartilhadas pelas telas."""

from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from motor import classificador, config, eventos, pipeline
from motor.logs import registrar

ORDEM_ROTA_D2 = {"sensivel": 0, "triagem": 1, "detalhes": 2, "auto": 3}


def checar_dados(parar: bool = True) -> bool:
    faltam = config.dados_faltando()
    if not faltam:
        return True
    registrar("ERROR", "dados", "dataset_ausente", arquivos=[p.name for p in faltam])
    st.error("Dataset ausente: " + ", ".join(p.name for p in faltam))
    st.markdown(
        f"Baixe os datasets do Kaggle (licença CC0) e salve na pasta `{config.dados_dir()}`:\n\n"
        f"- Customer Support Ticket Dataset → `support_tickets.csv` ({config.KAGGLE_D1})\n"
        f"- IT Service Ticket Classification → `it_tickets.csv` ({config.KAGGLE_D2})")
    if parar:
        st.stop()
    return False


@st.cache_resource(show_spinner="Carregando o modelo (na primeira execução ele é treinado, ≈ 1 min)...")
def modelo():
    return classificador.carregar_ou_treinar()


@st.cache_data(show_spinner=False)
def d1() -> pd.DataFrame:
    return pd.read_csv(config.csv_d1())


@st.cache_resource(show_spinner="Triando os 8.469 tickets do suporte ao cliente...")
def fila_d1() -> list:
    return [pipeline.triar_d1(r) for r in d1().to_dict("records")]


@st.cache_resource(show_spinner="Triando os 9.568 tickets de teste do service desk...")
def fila_d2() -> list:
    m, _ = modelo()
    return pipeline.triar_d2_lote(list(m.X_te), m, [f"T{i}" for i in range(len(m.X_te))])


@st.cache_resource(show_spinner=False)
def avaliacao_d2() -> dict:
    m, _ = modelo()
    return classificador.avaliar_teste(m)


@st.cache_data(show_spinner=False)
def ler_json(caminho: str) -> dict | None:
    try:
        with open(caminho, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def registro() -> eventos.Registro:
    if "registro" not in st.session_state:
        st.session_state.registro = eventos.Registro()
    return st.session_state.registro


def gravar(tipo: str, **dados) -> None:
    if registro().gravar(tipo, **dados):
        st.success(f"Registrado: {tipo} (vira dado para a IA aprender)")
    else:
        st.warning("Não consegui gravar no disco; o evento ficou guardado nesta sessão e será gravado na próxima ação.")


def rastro_df(d) -> pd.DataFrame:
    return pd.DataFrame([{"etapa": e.nome, "resultado": e.resultado, "motivo": e.motivo, "ms": e.ms} for e in d.rastro])


def pct(x, casas: int = 1) -> str:
    return f"{x * 100:.{casas}f}%".replace(".", ",")


def num(x) -> str:
    return f"{x:,}".replace(",", ".")
