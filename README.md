# SAE IA Décisionnelle — Bomber IA

Projet réalisé par **Benamghar** et **Boulakhras** dans le cadre de la SAE IA Décisionnelle (BUT Informatique).

## Description

`IA_BENAMGHAR_BOULAKHRAS.py` implémente une intelligence artificielle pour le jeu **Bomber** (style Bomberman).  
L'IA est conçue pour collecter des minerais de manière autonome tout en évitant les bombes, les fantômes et les autres joueurs.

## Stratégie

L'IA fonctionne selon trois modes :

| Mode | Déclenchement | Comportement |
|---|---|---|
| `CHERCHER_MINERAI` | Mode par défaut | Recherche et se dirige vers le minerai le plus accessible |
| `FUIR` | Danger > 2 | Fuit vers la case adjacente la plus sûre |
| `ATTENDRE` | Aucune action possible | Reste sur place (`N`) |

## Algorithmes

- **Pathfinding (BFS)** — `calculer_chemin()` : trouve le chemin le plus court en évitant les murs et les zones dangereuses.
- **Évaluation du danger** — `calculer_niveau_danger()` : score de 0 (sûr) à 999 (mortel) en tenant compte des bombes, fantômes et joueurs adverses.
- **Sélection du minerai** — `localiser_meilleur_minerai()` : choisit le minerai avec le meilleur ratio distance/danger.
- **Pose de bombe** — pose une bombe lorsqu'adjacent à un minerai, uniquement si une sortie sûre existe et que le cooldown (5 tours) est respecté.

## Actions possibles

| Action | Signification |
|---|---|
| `H` | Haut |
| `B` | Bas |
| `G` | Gauche |
| `D` | Droite |
| `X` | Poser une bombe |
| `N` | Ne rien faire |

## Utilisation

L'IA s'intègre dans le moteur de jeu via `BB_IA_start.py` :

```python
from IA_BENAMGHAR_BOULAKHRAS import IA_Bomber

ia = IA_Bomber(num_joueur, game_dic, timerglobal, timerfantôme)
action = ia.action(game_dict)
```

## Structure du fichier

```
IA/
└── IA_BENAMGHAR_BOULAKHRAS.py   # Classe IA_Bomber
```
