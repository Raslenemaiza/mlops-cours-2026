"""Schémas du Lab 5 (PNG) : flux du lab, ce que crée un InferenceService, test de charge, canary.

Régénérer (depuis la racine du repo) :
    uv run --no-project --with matplotlib python tools/diagrams/lab5_diagrams.py
Sortie : labs/m5-serving/img/*.png
"""

from __future__ import annotations

import math
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

OUT = Path(__file__).resolve().parents[2] / "labs" / "m5-serving" / "img"
RED = "#DC2626"
INK = "#0F172A"


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / name, dpi=150, facecolor=WHITE)
    plt.close(fig)


# 0. Le Lab 5 en un coup d'œil ---------------------------------------------------------------
def flux_lab5():
    fig, ax = canvas(16, 7)
    title(
        ax,
        "Le Lab 5 en un coup d'œil",
        "L'image du Lab 4 devient un service Kubernetes qui s'adapte à la charge et change de "
        "version sans coupure.",
    )
    steps = [
        ("1", "KServe", "make kserve :\nKnative, Kourier,\nKServe"),
        ("2", "Registry", "l'image 1.0.0\ndu Lab 4\nest là ?"),
        ("3", "Inference\nService", "un YAML :\nle service\nest créé"),
        ("4", "Appel", "curl sur\nlocalhost:30080\n+ en-tête Host"),
        ("5", "Autoscaling", "0 à 5 pods\nselon les\nrequêtes/s"),
        ("6", "Charge", "Locust :\n100, 500,\n1 000 users"),
        ("7", "Canary", "v2 à 10 %,\npuis 100 %\n(ou retour)"),
        ("8", "Rapport", "latences,\npods, canary\n(+ option 8)"),
    ]
    for k, (num, name, sub) in enumerate(steps):
        x = 2 + k * 19.7
        seance = k < 4
        box(
            ax,
            x,
            12,
            17,
            34,
            name,
            sub,
            fill=PALE_TEAL if seance else PALE_NAVY,
            edge=TEAL if seance else NAVY,
            ssize=8.5,
            tsize=11.5,
        )
        ax.text(x + 8.5, 49, f"étape {num if k < 7 else '9'}", ha="center", fontsize=10, color=MUTED)
        if k:
            arrow(ax, x - 2.6, 29, x, 29, "", color=NAVY, lw=1.4)
    ax.text(40, 4, "En séance : étapes 1 à 4", ha="center", fontsize=12, color=TEAL, fontweight="bold")
    ax.text(120, 4, "En autonomie : étapes 5 à 9 et la mission", ha="center", fontsize=12, color=NAVY,
            fontweight="bold")
    save(fig, "00-lab5-flux.png")


# 1. Ce que crée un InferenceService --------------------------------------------------------
def isvc():
    fig, ax = canvas(16, 9)
    title(
        ax,
        "Ce que crée un InferenceService",
        "Vous écrivez un YAML ; KServe et Knative créent le reste. Ici, pendant le canary de l'étape 7.",
    )
    box(ax, 2, 40, 22, 14, "Client", "curl, Locust\nen-tête Host", fill=LIGHT, edge=NAVY, tsize=12, ssize=9.5)
    box(ax, 32, 40, 26, 14, "Kourier", "passerelle (Envoy)\nlocalhost:30080", fill=PALE_ORANGE, edge=ORANGE,
        tsize=12, ssize=9.5)
    arrow(ax, 24, 47, 32, 47, "", color=NAVY, lw=1.6)
    box(ax, 66, 40, 26, 14, "Route", "répartit le trafic\nentre révisions", fill=PALE_NAVY, edge=NAVY,
        tsize=12, ssize=9.5)
    arrow(ax, 58, 47, 66, 47, "", color=NAVY, lw=1.6)
    # révisions
    for k, (rev, img, pct, col, fill) in enumerate(
        [("révision 00002", "image 1.0.0", "90 %", NAVY, PALE_NAVY),
         ("révision 00003", "image 2.0.0", "10 %", TEAL, PALE_TEAL)]
    ):
        y = 33 - k * 25
        box(ax, 104, y, 30, 20, rev, img, fill=fill, edge=col, tsize=11.5, ssize=10)
        arrow(ax, 92, 47, 104, y + 10, pct, color=col, lw=2.0, lsize=12)
        for j in range(2 if k == 0 else 1):
            box(ax, 138 + j * 10, y + 3, 9, 14, "pod", "", fill=WHITE, edge=col, tsize=9, lw=1.2, radius=0.4)
    ax.text(147, 55, "chaque pod :\nkserve-container\n+ queue-proxy", ha="center", fontsize=9.5, color=MUTED)
    box(ax, 32, 6, 26, 16, "Activator", "retient les requêtes\nquand il n'y a\naucun pod", fill=LIGHT,
        edge=MUTED, tsize=11.5, ssize=9.5)
    box(ax, 66, 6, 26, 16, "Autoscaler (KPA)", "lit les requêtes/s\nmesurées par\nqueue-proxy", fill=LIGHT,
        edge=MUTED, tsize=11.5, ssize=9.5)
    arrow(ax, 92, 14, 104, 14, "ajuste\nle nombre\nde pods", color=MUTED, lw=1.4, lsize=9)
    ax.text(14, 30, "Une révision =\nune image +\nsa configuration,\nimmuable", ha="center", fontsize=10.5,
            color=NAVY, fontweight="bold")
    save(fig, "01-isvc.png")


# 2. Lire un test de charge ----------------------------------------------------------------
def charge():
    fig, ax = canvas(16, 8)
    title(
        ax,
        "Lire un test de charge",
        "On augmente le nombre d'utilisateurs : le débit monte puis plafonne, la latence P99 explose. "
        "Allure typique.",
    )
    x0, y0, w, h = 8, 10, 90, 44
    ax.add_patch(plt.Rectangle((x0, y0), w, h, facecolor=WHITE, edgecolor=MUTED, lw=1))
    u = np.linspace(0, 1000, 200)
    cap = 900.0
    rps = cap * (1 - np.exp(-u * 4.5 / cap))
    rho = np.clip(rps / cap, 0, 0.985)
    p99 = 15 + 6 / (1 - rho) ** 1.3
    px = x0 + u / 1000 * w
    ax.plot(px, y0 + rps / 1000 * h, color=NAVY, lw=2.6)
    ax.plot(px, y0 + np.clip(p99, 0, 800) / 800 * h, color=RED, lw=2.6, ls="--")
    ax.text(x0 + w - 2, y0 + cap / 1000 * h - 5, "débit (requêtes/s) : plafonne", ha="right", fontsize=11,
            color=NAVY, fontweight="bold")
    ax.text(x0 + w * 0.52, y0 + h * 0.62, "latence P99 :\nexplose", ha="right", fontsize=11, color=RED,
            fontweight="bold")
    for xu, lab in ((100, "run 1\n100"), (500, "run 2\n500"), (1000, "run 3\n1 000")):
        xx = x0 + xu / 1000 * w
        ax.plot([xx, xx], [y0, y0 + h], color=MUTED, lw=0.8, ls=":")
        ax.text(xx, y0 - 6, lab, ha="center", fontsize=9.5, color=MUTED)
    ax.text(x0 + w / 2, 0.5, "utilisateurs virtuels Locust", ha="center", fontsize=10, color=MUTED)
    box(ax, 106, 30, 50, 24, "Débit attendu (loi de Little)",
        "débit ≈ utilisateurs ÷ (pause + latence)\n100 ÷ (0,2 s + 0,02 s) ≈ 450 req/s",
        fill=LIGHT, edge=NAVY, tsize=11.5, ssize=10.5)
    box(ax, 106, 4, 50, 22, "Le point de saturation",
        "le débit ne monte plus, les requêtes\nattendent dans une file :\nc'est le RPS max du service",
        fill=PALE_ORANGE, edge=ORANGE, tsize=11.5, ssize=10.5)
    save(fig, "02-charge.png")


# 3. Le canary, c'est du hasard mesuré ------------------------------------------------------
def canary():
    fig, ax = canvas(16, 8)
    n, p = 200, 0.10
    k = np.arange(0, 45)
    pmf = np.array([math.comb(n, i) * p**i * (1 - p) ** (n - i) for i in k])
    inside = pmf[(k >= 12) & (k <= 28)].sum()
    title(
        ax,
        "Canary 90/10 : combien de réponses de la v2 sur 200 appels ?",
        "Chaque appel est un tirage au sort (10 % de chances pour la v2) : le compte varie d'un essai à "
        "l'autre.",
    )
    x0, y0, w, h = 8, 10, 100, 44
    ax.add_patch(plt.Rectangle((x0, y0), w, h, facecolor=WHITE, edgecolor=MUTED, lw=1))
    for i, v in zip(k, pmf):
        col = TEAL if 12 <= i <= 28 else MUTED
        ax.add_patch(plt.Rectangle((x0 + i / 45 * w, y0), w / 45 * 0.85, v / pmf.max() * (h - 6),
                                   color=col, alpha=0.85))
    for t in (0, 10, 20, 30, 40):
        ax.text(x0 + (t + 0.4) / 45 * w, y0 - 4, str(t), ha="center", fontsize=9.5, color=MUTED)
    ax.text(x0 + w / 2, 0.8, "nombre de réponses « 2.0.0 » sur 200 appels", ha="center", fontsize=10,
            color=MUTED)
    ax.text(x0 + 20.4 / 45 * w, y0 + h - 3, "attendu : 20", ha="center", fontsize=11, color=NAVY,
            fontweight="bold")
    box(ax, 114, 30, 42, 24, "Moyenne et écart-type",
        "moyenne = n × p = 200 × 0,1 = 20\nécart-type = √(n p (1−p)) ≈ 4,2",
        fill=LIGHT, edge=NAVY, tsize=11.5, ssize=10.5)
    box(ax, 114, 4, 42, 22, "Zone normale",
        f"de 12 à 28 (≈ 20 ± 2 écarts-types)\n{inside:.0%} des essais tombent ici".replace("%", " %"),
        fill=PALE_TEAL, edge=TEAL, tsize=11.5, ssize=10.5)
    save(fig, "03-canary.png")
    return inside


if __name__ == "__main__":
    flux_lab5()
    isvc()
    charge()
    print("P(12<=X<=28) =", canary())
    print("ok", sorted(p.name for p in OUT.glob("*.png")))
