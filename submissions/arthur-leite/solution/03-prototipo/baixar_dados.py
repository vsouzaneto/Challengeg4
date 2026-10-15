"""
Baixa os dois datasets públicos do Kaggle para submissions/arthur-leite/data/. Não precisa de login.

    python baixar_dados.py
"""
import shutil
from pathlib import Path

import kagglehub

RAIZ = Path(__file__).resolve().parents[2]
DATASETS = {
    "suraj520/customer-support-ticket-dataset": "data/ds1_customer_support",
    "adisongoh/it-service-ticket-classification-dataset": "data/ds2_it_tickets",
}

for ds, destino in DATASETS.items():
    origem = kagglehub.dataset_download(ds)
    shutil.copytree(origem, RAIZ / destino, dirs_exist_ok=True)
    print(f"ok  {ds} -> {RAIZ / destino}")
