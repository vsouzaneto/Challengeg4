# Tiny helper to author notebooks as Python lists of markdown/code cells.
import nbformat as nbf

SETUP = '''
# Setup: make solution/src importable and load the posts with derived features.
import sys
from pathlib import Path
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "solution" / "src").exists())
sys.path.insert(0, str(ROOT / "solution" / "src"))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display, Markdown
from social_insights import data, top_performers as tp, clustering as cl, drivers as dr, audience as au, nlp, validation as va, plots

plots.apply_style()
pd.set_option("display.float_format", "{:.4f}".format)
df = data.load_posts(ROOT)
print(f"{len(df):,} posts")
'''


class Notebook:
    def __init__(self):
        self.cells = []

    def md(self, text: str) -> None:
        self.cells.append(nbf.v4.new_markdown_cell(text.strip()))

    def code(self, text: str) -> None:
        self.cells.append(nbf.v4.new_code_cell(text.strip()))

    def save(self, path: str) -> None:
        meta = {"kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"}}
        nbf.write(nbf.v4.new_notebook(cells=self.cells, metadata=meta), path)
