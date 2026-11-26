# Journal de bord (monôme)

<!--
Mode d'emploi (à garder en tête du fichier) :
- Une entrée par séance (et par session de travail importante hors séance), la plus récente en bas.
- 3 à 5 lignes : qui a piloté, ce qui a été fait, ce qui a bloqué ou ce qui a été appris,
  la prochaine étape. Pas de roman : c'est un outil de pilotage, pas un rapport.
- Titre d'entrée au format exact « ## S<n> — AAAA-MM-JJ — <sujet> » (date réelle) :
  le pré-contrôle de rendu (make check-m10) compte les entrées datées.
- Liez les PR, issues et ADR (#12, docs/adr/0003-...). Les problèmes non résolus restent
  visibles : c'est précisément ce qui aide l'enseignant à vous débloquer.
- L'entrée d'exemple ci-dessous (date AAAA-MM-JJ) n'est pas comptée ; supprimez-la
  quand vous aurez écrit la vôtre.
-->

**Monôme :** @Raslenemaiza (Raslene Maiza) — travail individuel, organisation de type option B
**Repo :** https://github.com/Raslenemaiza/mlops-cours-2026
**Dataset :** german-credit (fil rouge du cours)
**Extension :** à confirmer avec l'enseignante (piste : @Raslenemaiza → ext/gate-equite)

<!-- Vos entrées commencent ici. Modèle :

## S1 — AAAA-MM-JJ — Lab 0 : setup

- **Pilote / copilote :**
- **Fait :**
- **Bloqué / appris :**
- **Prochaine étape :**

-->

## S1 — 2026-11-26 — Lab 0 : setup (rattrapage)

- **Pilote / copilote :** @Raslenemaiza (seul)
- **Fait :** VM du cours recréée (6 Go, 4 vCPU), cluster kind 3 nœuds, SeaweedFS + MLflow, `uv sync`, smoke tests MLflow et DVC ; `make check-m0` 19/19 ; PR #1 fusionnée.
- **Bloqué / appris :** ancienne VM VirtualBox « inaccessible » qui bloquait `vagrant up` (désenregistrée) ; PC à 7,8 Go de RAM avec Hyper-V actif (VM lente, suffisant pour les Labs 0-1 seulement) ; première PR ouverte par erreur vers le repo du cours (fermée) : vérifier la *base repository*.
- **Prochaine étape :** Lab 1 (DVC + MLflow sur German Credit) ; demander à l'enseignante une solution de repli matérielle pour le Lab 2+ et valider l'extension.
