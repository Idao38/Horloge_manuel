# Horloge — Un jour de plus

![Version](https://img.shields.io/badge/version-1.0.1-blue)

Application de bureau (Python / Tkinter) pour afficher une **horloge manuelle** et un **compteur de jours** lors des parties de JDR. L’affichage est pensé pour être projeté ou montré aux joueurs, avec une fenêtre de contrôle séparée pour le meneur.

## Fonctionnalités

### Affichage principal

- **Heure manuelle** au format **HH:MM** (24 h) ou **compte à rebours** en **MM:SS**.
- Au lancement, l’heure repart toujours de **00:00** ; le jour de **Jour 0** (modifiable).
- Compteur de jours **Jour N** en haut à droite de l’écran d’affichage.
- Style **chiffres rouges sur fond noir**, avec un **léger clignotement** type néon sur l’heure et le jour.
- **Texte libre sous l’horloge** (style terminal / Matrix, vert sur noir) :
  - **Colonne gauche** (~80 % de la largeur) et **colonne droite** (~20 %), pour notes, listes, etc.
  - Texte **redimensionné automatiquement** pour tenir dans la zone disponible.
- Fenêtre d’affichage **redimensionnable** ; polices et mise en page **adaptatives**.
- Icône de fenêtre : `assets/clock_icon.ico` (si présent), y compris dans l’exécutable PyInstaller.

### Fenêtre de contrôle

- **Aperçu** de l’écran d’affichage (mise en page simplifiée).
- Boutons de temps : **+1 h**, **-1 h**, **+10 min**, **-10 min**, **+1 j**, **-1 j**.
- Éditeurs de texte pour les **deux colonnes** sous l’horloge, avec bouton **Appliquer les textes sur l’écran**.
- **Compte à rebours** : saisie des minutes (1–999), **Démarrer**, **Arrêter**, **Réinitialiser**.
- Choix du **mode d’affichage** : heure manuelle ou compte à rebours.
- Fermer la fenêtre de contrôle avec la croix la **masque** (elle reste ouvrable depuis l’affichage).
- **Ctrl+C** depuis la fenêtre d’affichage : **rouvre** la fenêtre de contrôle si elle est masquée. Un bandeau rappelle ce raccourci tant que la fenêtre de contrôle n’est pas visible.
- Bouton **Fermer l’application** pour quitter proprement.

### Multi-écrans

- Si un **second moniteur** est détecté (via la bibliothèque `screeninfo`), la fenêtre d’afficheur tente de passer en **plein écran sur le second écran** ; la fenêtre de contrôle reste sur l’écran principal.
- Sans `screeninfo`, sans second écran, ou en cas d’erreur : l’afficheur est **maximisé** sur l’écran principal.

## Données

- **Aucune persistance** : à la fermeture, rien n’est sauvegardé sur le disque.

## Architecture du code

| Fichier | Rôle |
|--------|------|
| `src/horloge_jdr/time_model.py` | Modèle de temps (minutes dans la journée) et compteur de jours. |
| `src/horloge_jdr/domain.py` | Domaine : `ClockState`, `CountdownModel`, `AppState`, `DisplayMode`. |
| `src/horloge_jdr/controller.py` | `HorlogeController` : actions utilisateur et notifications aux vues. |
| `src/horloge_jdr/app.py` | Point d'entrée `main()` et assemblage des fenêtres. |
| `src/horloge_jdr/ui/display_window.py` | Fenêtre d'affichage (heure, jour, texte Matrix). |
| `src/horloge_jdr/ui/control_window.py` | Fenêtre de contrôle (aperçu, boutons, compte à rebours, mode). |
| `src/horloge_jdr/ui/layout.py` | Mise en page commune (layout horloge + colonnes Matrix). |
| `src/horloge_jdr/ui/neon.py` | Effet de clignotement néon pour les labels. |
| `src/horloge_jdr/ui/screen_position.py` | Placement de la fenêtre sur multi-écrans. |
| `tests/test_time_model.py` | Tests sur le modèle de temps et les jours. |
| `tests/test_domain.py` | Tests sur la logique de domaine (horloge, compte à rebours, messages). |
| `tests/test_controller.py` | Tests sur le contrôleur (actions, notifications). |
| `tests/test_version.py` | Tests sur la version (semver, cohérence avec pyproject.toml). |
## Prérequis

- **Windows** 10 ou 11 (64 bits) — environnement cible principal.
- **Python 3.10+** pour le développement et la génération de l’exécutable.

## Licence

Ce projet est sous **Creative Commons Attribution — Pas d’utilisation commerciale — Partage dans les mêmes conditions 4.0 International** ([**CC BY-NC-SA 4.0**](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.fr)).


Le texte légal complet figure dans le fichier [`LICENSE`](LICENSE). Adapte la ligne de copyright dans `LICENSE` si tu ajoutes d’autres détenteurs de droits.
