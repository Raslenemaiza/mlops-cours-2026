"""Schémas du Lab 4 (PNG) : flux du lab, couches d'une image, percentiles de latence, sécurité.

Régénérer (depuis la racine du repo) :
    uv run --no-project --with matplotlib python tools/diagrams/lab4_diagrams.py
Sortie : labs/m4-packaging/img/*.png
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lab0_diagrams import (  # noqa: E402
    LIGHT,
    MUTED,
    NAVY,
    ORANGE,
    PALE_NAVY,
    PALE_ORANGE,
    PALE_TEAL,
    TEAL,
    WHITE,
    arrow,
    box,
    canvas,
    plt,
    title,
)

OUT = Path(__file__).resolve().parents[2] / "labs" / "m4-packaging" / "img"
RED = "#DC2626"
PALE_RED = "#FDECEC"
INK = "#0F172A"


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / name, dpi=150, facecolor=WHITE)
    plt.close(fig)


# 0. Le Lab 4 en un coup d'œil ---------------------------------------------------------------
def flux_lab4():
    fig, ax = canvas(16, 7)
    title(
        ax,
        "Le Lab 4 en un coup d'œil",
        "Le modèle du Registry MLflow devient une image Docker autonome, mesurée, scannée et "
        "publiée dans le registry du cours.",
    )
    steps = [
        ("1", "ONNX", "export depuis\nMLflow, vérifié\n= scikit-learn"),
        ("2", "API", "FastAPI :\n/health, /metadata,\n/predict"),
        ("3", "Image naïve", "la baseline :\nlourde, root,\nsecrets copiés"),
        ("4", "Multi-stage", "slim, non-root,\nhealthcheck,\n< 500 Mo"),
        ("5", "Benchmark", "P50 / P95 / P99 :\nscikit-learn\ncontre ONNX"),
        ("6", "BentoML", "la même API\navec un\nframework"),
        ("7", "Scans", "Trivy (image)\nModelScan\n(modèle)"),
        ("8", "Registry", "push sur\nlocalhost:5001,\npuis pull"),
    ]
    for k, (num, name, sub) in enumerate(steps):
        x = 2 + k * 19.7
        sec = name in ("Scans", "Image naïve")
        box(
            ax,
            x,
            12,
            17,
            34,
            name,
            sub,
            fill=PALE_ORANGE if sec else (PALE_TEAL if k % 2 == 0 else PALE_NAVY),
            edge=ORANGE if sec else (TEAL if k % 2 == 0 else NAVY),
            ssize=8.5,
            tsize=11.5,
        )
        ax.text(x + 8.5, 49, f"étape {num}", ha="center", fontsize=10, color=MUTED)
        if k:
            arrow(ax, x - 2.6, 29, x, 29, "", color=NAVY, lw=1.4)
    ax.text(
        80,
        4,
        "Une image = une version du modèle : elle démarre sans MLflow, sans réseau, "
        "et ce qu'on scanne est exactement ce qui tourne.",
        ha="center",
        fontsize=11.5,
        color=NAVY,
        fontweight="bold",
    )
    save(fig, "00-lab4-flux.png")


# 1. Une image, ce sont des couches ---------------------------------------------------------
def couches():
    fig, ax = canvas(16, 8)
    title(
        ax,
        "Une image Docker est une pile de couches",
        "Chaque instruction du Dockerfile ajoute une couche. On paie toutes les couches, "
        "même celles qu'on « supprime » plus tard.",
    )

    def stack(x, name, total, layers, edge):
        y = 8
        for label, h, fill, col in layers:
            box(ax, x, y, 46, h, label, "", fill=fill, edge=col, tsize=10.5, lw=1.3, radius=0.6)
            y += h + 0.6
        ax.text(x + 23, y + 2, name, ha="center", fontsize=14, color=edge, fontweight="bold")
        ax.text(x + 23, y + 6.5, total, ha="center", fontsize=12, color=MUTED)

    stack(
        10,
        "Dockerfile naïf",
        "1,3 à 1,6 Go · root",
        [
            ("FROM python:3.12 (complète) ≈ 1 Go", 30, PALE_NAVY, NAVY),
            ("pip install sans version, cache pip conservé", 9, PALE_NAVY, NAVY),
            ("COPY . : .git, data/, … et .env (secrets !)", 9, PALE_RED, RED),
        ],
        RED,
    )
    stack(
        86,
        "Dockerfile multi-stage",
        "≈ 330 Mo · utilisateur 10001",
        [
            ("FROM python:3.12-slim ≈ 125 Mo", 9, PALE_TEAL, TEAL),
            ("/deps copié du builder ≈ 206 Mo", 11, PALE_TEAL, TEAL),
            ("dataset.yaml, src/, serve.py : quelques ko", 3.5, PALE_ORANGE, ORANGE),
            ("model.onnx + metadata.json (dernière couche)", 3.5, PALE_ORANGE, ORANGE),
        ],
        TEAL,
    )
    ax.text(
        147,
        14,
        "Dans /deps :\nONNX Runtime ≈ 62 Mo\nnumpy ≈ 57 Mo\npandas ≈ 45 Mo\n…",
        ha="center",
        fontsize=10.5,
        color=MUTED,
    )
    arrow(ax, 60, 25, 84, 25, "≈ 4 × plus petite", color=TEAL, lw=2.2, lsize=12)
    ax.text(
        80,
        2,
        "Schéma : hauteurs approximatives. Le stage builder (pip, cache) reste hors de l'image finale.",
        ha="center",
        fontsize=10,
        color=MUTED,
        style="italic",
    )
    save(fig, "01-couches.png")


# 2. Lire une latence : P50, P95, P99 -------------------------------------------------------
def latence():
    fig, ax = canvas(16, 8)
    title(
        ax,
        "Lire une latence : P50, P95, P99",
        "On mesure 1 000 appels, on les trie du plus rapide au plus lent, et on lit des rangs : "
        "la moyenne cache les requêtes lentes.",
    )
    rng = np.random.default_rng(4)
    ms = np.concatenate([rng.lognormal(np.log(4.0), 0.18, 960), rng.lognormal(np.log(7.5), 0.25, 40)])
    p50, p95, p99 = np.percentile(ms, [50, 95, 99])
    x0, y0, w, h = 6, 12, 100, 52
    ax.add_patch(plt.Rectangle((x0, y0), w, h, facecolor=WHITE, edgecolor=MUTED, lw=1))
    lo, hi = 2.0, 12.0
    counts, edges = np.histogram(ms, bins=40, range=(lo, hi))
    for c, a, b in zip(counts, edges[:-1], edges[1:]):
        px = x0 + (a - lo) / (hi - lo) * w
        pw = (b - a) / (hi - lo) * w
        ax.add_patch(
            plt.Rectangle((px, y0 + 1), pw * 0.92, c / counts.max() * (h - 10), color=NAVY, alpha=0.75)
        )
    for val, lab, col in ((p50, "P50", TEAL), (p95, "P95", ORANGE), (p99, "P99", RED)):
        px = x0 + (val - lo) / (hi - lo) * w
        ax.plot([px, px], [y0, y0 + h - 4], color=col, lw=2.2, ls="--")
        ax.text(px, y0 + h - 3, f"{lab}\n{val:.1f} ms", ha="center", fontsize=10.5, color=col, fontweight="bold")
    ax.text(x0 + w / 2, y0 - 5, "durée d'un appel (ms) · exemple fictif", ha="center", fontsize=10, color=MUTED)
    box(ax, 112, 12, 45, 52, "", "", fill=LIGHT, edge=NAVY)
    lines = [
        ("P50 (médiane)", "la moitié des appels\nsont plus rapides", TEAL),
        ("P95", "95 appels sur 100\nsont plus rapides", ORANGE),
        ("P99", "le 1 % le plus lent\ncommence ici", RED),
    ]
    for i, (head, body, col) in enumerate(lines):
        yy = 57 - i * 15
        ax.text(115, yy, head, fontsize=12, color=col, fontweight="bold")
        ax.text(115, yy - 2.2, body, fontsize=10.5, color=INK, va="top", linespacing=1.3)
    ax.text(
        80,
        2,
        "Un engagement de service s'écrit en percentile : « P95 < 50 ms », pas « moyenne < 50 ms ».",
        ha="center",
        fontsize=11.5,
        color=NAVY,
        fontweight="bold",
    )
    save(fig, "02-latence.png")


# 3. Sécurité : trois formats, deux scanners -------------------------------------------------
def securite():
    fig, ax = canvas(16, 8)
    title(
        ax,
        "Ce qu'on charge, ce qu'on scanne",
        "Charger un modèle peut exécuter du code. Le format compte autant que l'image qui le contient.",
    )
    cols = [
        ("pickle / joblib", "Au chargement, pickle peut\nappeler n'importe quelle\nfonction (os.system…).",
         "Danger si l'origine\nn'est pas maîtrisée", PALE_RED, RED),
        ("skops (MLflow 3)", "Reconstruit des objets\nPython, mais seulement\nles types autorisés.",
         "Compromis : liste\nde confiance", PALE_ORANGE, ORANGE),
        ("ONNX", "Un graphe d'opérations\ndéclaratif (protobuf) :\naucun code Python.",
         "Sûr par construction", PALE_TEAL, TEAL),
    ]
    for k, (name, body, verdict, fill, edge) in enumerate(cols):
        x = 6 + k * 50
        box(ax, x, 30, 46, 26, name, body, fill=fill, edge=edge, tsize=13, ssize=10)
        ax.text(x + 23, 26, verdict, ha="center", va="top", fontsize=11, color=edge, fontweight="bold")
    box(ax, 6, 3, 72, 13, "Trivy → l'image", "CVE des paquets Debian et Python\n(version épinglée : v0.75.0)",
        fill=LIGHT, edge=NAVY, tsize=12, ssize=10)
    box(ax, 84, 3, 72, 13, "ModelScan → le modèle", "lit les pickles et signale les appels\ndangereux ; ignore ONNX et skops",
        fill=LIGHT, edge=NAVY, tsize=12, ssize=10)
    save(fig, "03-securite.png")


if __name__ == "__main__":
    flux_lab4()
    couches()
    latence()
    securite()
    print("ok", sorted(p.name for p in OUT.glob("*.png")))
