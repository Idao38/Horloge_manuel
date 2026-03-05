from __future__ import annotations

import os
import random
import sys
import tkinter as tk
from tkinter import ttk

try:
    # Exécution en tant que module de paquet (python -m src.horloge_jdr.app)
    from .time_model import DayCounter, TimeModel
except ImportError:  # pragma: no cover - utilisé surtout dans le .exe PyInstaller
    # Exécution en script "plat" (dans l'exécutable PyInstaller)
    from time_model import DayCounter, TimeModel


class HorlogeJDRApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Horloge - Un jour de plus")
        icon_path = self._get_icon_path()
        if icon_path is not None:
            try:
                self.root.iconbitmap(icon_path)
            except Exception:
                # Si l'icône n'est pas supportée ou introuvable, on ignore simplement.
                pass

        # Modèle de temps
        self.time_model = TimeModel()
        self.day_counter = DayCounter()
        # Paramètres de clignotement type néon fatigué
        self._flicker_running = True
        self._flicker_prob_time = 0.04  # probabilité par tick pour l'heure
        self._flicker_prob_day = 0.10  # probabilité par tick pour le jour

        # Configuration de la fenêtre
        self.root.configure(bg="black")
        self.root.minsize(300, 150)

        # Conteneur principal
        self.main_frame = tk.Frame(self.root, bg="black", bd=0, highlightthickness=0)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Style ttk (toujours utile pour certains widgets éventuels)
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")

        style.configure(
            "Dark.TButton",
            foreground="white",
            background="#222222",
            padding=6,
        )

        # Zone d'affichage principale (fond noir)
        self.display_frame = tk.Frame(self.main_frame, bg="black", bd=0, highlightthickness=0)
        self.display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Label de l'heure (au centre)
        self.time_label = tk.Label(
            self.display_frame,
            text=self.time_model.formatted(),
            fg="red",
            bg="black",
            anchor="center",
        )
        self.time_label.pack(fill=tk.BOTH, expand=True)

        # Label du compteur de jours (dans un angle de la zone noire)
        self.day_label = tk.Label(
            self.display_frame,
            text=self.day_counter.formatted(),
            fg="red",
            bg="black",
            anchor="ne",
        )
        self.day_label.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)

        # Zone basse : tous les boutons (temps + jours) alignés sur une seule ligne
        bottom_frame = tk.Frame(self.main_frame, bg="black", bd=0, highlightthickness=0)
        bottom_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.buttons_frame = tk.Frame(
            bottom_frame, bg="black", bd=0, highlightthickness=0
        )
        self.buttons_frame.pack(fill=tk.X, expand=True)

        # Ordre : +1 h ; -1 h ; +10 min ; -10 min ; +1 j ; -1 j
        btn_plus_hour = self._create_styled_button(
            self.buttons_frame,
            text="+1 h",
            command=lambda: self._change_hours(1),
        )
        btn_plus_hour.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        btn_minus_hour = self._create_styled_button(
            self.buttons_frame,
            text="-1 h",
            command=lambda: self._change_hours(-1),
        )
        btn_minus_hour.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        btn_plus_10min = self._create_styled_button(
            self.buttons_frame,
            text="+10 min",
            command=lambda: self._change_minutes(10),
        )
        btn_plus_10min.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        btn_minus_10min = self._create_styled_button(
            self.buttons_frame,
            text="-10 min",
            command=lambda: self._change_minutes(-10),
        )
        btn_minus_10min.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        btn_plus_day = self._create_styled_button(
            self.buttons_frame,
            text="+1 j",
            command=lambda: self._change_days(1),
        )
        btn_plus_day.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        btn_minus_day = self._create_styled_button(
            self.buttons_frame,
            text="-1 j",
            command=lambda: self._change_days(-1),
        )
        btn_minus_day.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        # Redimensionnement : ajuster la taille de police de l'affichage
        self.main_frame.bind("<Configure>", self._on_resize)

        # Raccourcis clavier
        self.root.bind("<Up>", lambda event: self._change_hours(1))
        self.root.bind("<Down>", lambda event: self._change_hours(-1))

        # Redimensionnement global : ajuster uniquement la taille de police à chaque changement de fenêtre
        self.root.bind("<Configure>", self._on_resize)

        # Initialiser la police et l'affichage
        self._update_time_label_font()
        self._refresh_display()

        # Lancer la boucle de clignotement aléatoire
        self._schedule_flicker()

    def _get_icon_path(self) -> str | None:
        # Localise clock_icon.ico aussi bien en mode développement que dans le .exe PyInstaller.
        try:
            if hasattr(sys, "_MEIPASS"):
                base_dir = sys._MEIPASS
            else:
                # Racine du projet : deux niveaux au-dessus de ce fichier (src/horloge_jdr/.. /..)
                base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
            candidate = os.path.join(base_dir, "assets", "clock_icon.ico")
            if os.path.exists(candidate):
                return candidate
        except Exception:
            pass
        return None

    def _change_hours(self, delta: int) -> None:
        self._apply_time_delta(delta * 60)

    def _change_minutes(self, delta: int) -> None:
        self._apply_time_delta(delta)

    def _apply_time_delta(self, delta_minutes: int) -> None:
        """Modifie l'heure de delta_minutes, et met à jour le jour si on passe par minuit."""
        old_minutes = self.time_model.total_minutes
        self.time_model.add_minutes(delta_minutes)
        new_minutes = self.time_model.total_minutes
        # Passage minuit vers l'avant (ex. 23:50 + 10 min → 00:00) → +1 jour
        if delta_minutes > 0 and new_minutes < old_minutes:
            self.day_counter.add_days(1)
        # Passage minuit vers l'arrière (ex. 00:10 - 10 min → 23:50) → -1 jour
        if delta_minutes < 0 and new_minutes > old_minutes:
            self.day_counter.add_days(-1)
        self._refresh_display()

    def _refresh_display(self) -> None:
        self.time_label.config(text=self.time_model.formatted())
        self.day_label.config(text=self.day_counter.formatted())

    def _change_days(self, delta: int) -> None:
        self.day_counter.add_days(delta)
        self.day_label.config(text=self.day_counter.formatted())

    def _on_resize(self, event: tk.Event) -> None:  # type: ignore[type-arg]
        # Utiliser after_idle pour que le recalcul se fasse une fois la géométrie stabilisée,
        # notamment lors d'un clic sur le bouton de maximisation.
        self.root.after_idle(self._on_resize_idle)

    def _on_resize_idle(self) -> None:
        self._update_time_label_font()

    def _update_time_label_font(self) -> None:
        # Calculer une taille de police en fonction de la taille de la zone d'affichage
        target_widget = getattr(self, "display_frame", self.main_frame)
        width = max(target_widget.winfo_width(), 1)
        height = max(target_widget.winfo_height(), 1)
        # Coefficient empirique pour avoir une bonne lisibilité
        base = min(width // 5, height // 2)
        font_size = max(base, 20)
        self.time_label.config(font=("Courier New", font_size, "bold"))
        # Le compteur de jours est plus petit pour rester discret
        day_font_size = max(font_size // 4, 8)
        self.day_label.config(font=("Courier New", day_font_size, "bold"))

    # ----- Effet de clignotement type néon fatigué -----

    def _schedule_flicker(self) -> None:
        if not self._flicker_running:
            return
        # Tick toutes les secondes environ
        self.root.after(1000, self._flicker_tick)

    def _flicker_tick(self) -> None:
        if not self._flicker_running:
            return

        # Décider aléatoirement si on fait clignoter l'heure et/ou le jour
        if random.random() < self._flicker_prob_time:
            self._start_flicker(self.time_label)

        if random.random() < self._flicker_prob_day:
            self._start_flicker(self.day_label)

        # Planifier le tick suivant
        self._schedule_flicker()

    def _start_flicker(self, widget: tk.Label) -> None:
        # Séquence de couleurs du plus sombre au plus lumineux
        sequence = ["#330000", "#880000", "#330000", "#FF0000"]
        self._flicker_step(widget, sequence, 0)

    def _flicker_step(self, widget: tk.Label, colors: list[str], index: int) -> None:
        if index >= len(colors):
            return
        try:
            widget.config(fg=colors[index])
        except tk.TclError:
            # Le widget a pu être détruit si la fenêtre est fermée
            return
        # Enchaîner rapidement les étapes pour un effet bref
        self.root.after(70, lambda: self._flicker_step(widget, colors, index + 1))

    # ----- Boutons texte stylés -----

    def _create_styled_button(self, parent: tk.Misc, text: str, command) -> tk.Button:
        # Bouton texte simple mais lisible, qui se redimensionne proprement avec la fenêtre.
        btn = tk.Button(
            parent,
            text=text,
            fg="white",
            bg="#222222",
            activebackground="#444444",
            activeforeground="white",
            bd=1,
            highlightthickness=0,
            command=command,
            font=("Courier New", 10, "bold"),
        )
        return btn


def main() -> None:
    root = tk.Tk()
    app = HorlogeJDRApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

