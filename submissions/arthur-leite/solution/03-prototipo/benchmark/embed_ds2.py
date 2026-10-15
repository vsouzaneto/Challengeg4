"""Gera e salva os embeddings do Dataset 2 (classificador B). Roda uma vez; o resultado fica em cache."""
from pathlib import Path
import time
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parents[3]
CACHE = ROOT / "data/cache"
CACHE.mkdir(parents=True, exist_ok=True)
MODELO = "sentence-transformers/all-MiniLM-L6-v2"

d = pd.read_csv(ROOT / "data/ds2_it_tickets/all_tickets_processed_improved_v3.csv")
t = time.time()
emb = SentenceTransformer(MODELO, device="cpu").encode(
    d["Document"].tolist(), batch_size=128, show_progress_bar=False, normalize_embeddings=True)
np.save(CACHE / "ds2_minilm.npy", emb.astype(np.float32))
print(f"{emb.shape} em {time.time() - t:.0f}s -> {CACHE / 'ds2_minilm.npy'}")
