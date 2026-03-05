# Horloge - Un jour de plus

Horloge digitale manuelle pour suivi du temps en JDR, sous forme d'exécutable Windows autonome.

## Fonctionnalités

- Affichage **HH:MM** au format 24h.
- Heure initiale toujours **00:00** à chaque lancement.
- Contrôles du temps :
  - Boutons : `-1 h`, `-10 min`, `+10 min`, `+1 h`.
  - Clavier : flèche **haut** = `+1 h`, flèche **bas** = `-1 h`.
- Compteur de jours :
  - Affichage discret `Jour N` dans un angle.
  - Deux petits boutons `-` et `+` pour ajuster le nombre de jours.
- Affichage de type horloge numérique :
  - **Chiffres rouges** sur **fond noir**.
  - Fenêtre redimensionnable, l'affichage s'adapte à la taille.
- Aucune sauvegarde à la fermeture, aucun fichier de configuration.

## Structure du projet

- `src/horloge_jdr/time_model.py` : logique de calcul du temps (modèle).
- `src/horloge_jdr/app.py` : interface graphique Tkinter.
- `tests/test_time_model.py` : tests unitaires sur la logique de temps.

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

