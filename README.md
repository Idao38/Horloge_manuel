# Horloge - Un jour de plus

Horloge digitale manuelle pour suivi du temps en JDR, sous forme d'exécutable Windows autonome.

## Fonctionnalités

- Affichage **HH:MM** au format 24h ou **compte à rebours** en `MM:SS`.
- Heure initiale toujours **00:00** à chaque lancement.
- Contrôles du temps (fenêtre de contrôle) :
  - Boutons : `-1 h`, `-10 min`, `+10 min`, `+1 h`, `-1 j`, `+1 j`.
- Compteur de jours :
  - Affichage discret `Jour N` dans un coin de la fenêtre d'affichage.
  - Boutons `-1 j` et `+1 j` dans la fenêtre de contrôle.
- Compte à rebours :
  - Saisie du nombre de minutes dans la fenêtre de contrôle.
  - Boutons `Démarrer`, `Arrêter`, `Réinitialiser`.
  - Bascule du mode d'affichage entre **heure manuelle** et **compte à rebours**.
- Affichage de type horloge numérique :
  - **Chiffres rouges** sur **fond noir**.
  - Effet de clignotement léger type néon fatigué.
  - Fenêtre d'affichage redimensionnable, l'affichage s'adapte à la taille.
- Aucune sauvegarde à la fermeture, aucun fichier de configuration.

## Structure du projet

- `src/horloge_jdr/time_model.py` : logique de calcul du temps (modèle de base).
- `src/horloge_jdr/domain.py` : couche de domaine (`ClockState`, `CountdownModel`, `AppState`).
- `src/horloge_jdr/controller.py` : contrôleur (`HorlogeController`) qui orchestre les mises à jour et notifie les vues.
- `src/horloge_jdr/app.py` : point d'entrée Tkinter, création des deux fenêtres (`DisplayWindow` et `ControlWindow`).
- `tests/test_domain.py` : tests unitaires sur la logique de domaine.

## Prérequis

- Windows 10 ou 11 (64 bits).
- Python 3.10+ installé (pour développer / générer l'exécutable).

## Installation des dépendances (développement)

Dans un terminal positionné à la racine du projet :

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Lancer l'application en mode développement

Depuis la racine du projet :

```bash
python -m src.horloge_jdr.app
```

En mode **deux écrans** (extension d'écran détectée), la fenêtre d'affichage essaiera de se placer en plein écran sur le deuxième moniteur, tandis que la fenêtre de contrôle restera sur l'écran principal.  
Si aucun deuxième écran n'est détecté, les deux fenêtres seront créées sur l'écran principal (l'affichage reste plein écran, la fenêtre de contrôle est positionnée dans un coin).

## Exécuter les tests

```bash
pytest
```

## Générer l'exécutable Windows autonome

Depuis la racine du projet, dans l'environnement virtuel :

```bash
pyinstaller --onefile --noconsole -n "Horloge - Un jour de plus" src/horloge_jdr/app.py
```

L'exécutable sera généré dans le dossier `dist` sous le nom `Horloge - Un jour de plus.exe`.  
Tu pourras ensuite copier ce fichier où tu veux et le lancer directement, sans installateur.

