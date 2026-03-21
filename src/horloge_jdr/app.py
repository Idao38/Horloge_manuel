from __future__ import annotations

import os
import random
import sys
import tkinter as tk
from tkinter import ttk

# Import du contrôleur adapté au contexte (package vs exécutable PyInstaller)
if getattr(sys, "frozen", False) and (__package__ is None or __package__ == ""):
    # Contexte exécutable : modules plats dans le même dossier qu'app.py
    from controller import HorlogeController
else:
    # Contexte package : exécution via python -m src.horloge_jdr.app
    from .controller import HorlogeController


def _get_icon_path() -> str | None:
    """Localise clock_icon.ico aussi bien en mode développement que dans le .exe PyInstaller."""
    try:
        if hasattr(sys, "_MEIPASS"):
            base_dir = sys._MEIPASS  # type: ignore[attr-defined]
        else:
            # Racine du projet : deux niveaux au-dessus de ce fichier (src/horloge_jdr/.. /..)
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
        candidate = os.path.join(base_dir, "assets", "clock_icon.ico")
        if os.path.exists(candidate):
            return candidate
    except Exception:
        pass
    return None


# Texte libre sous l'horloge : style terminal / Matrix
_MATRIX_GREEN = "#00FF41"
_MATRIX_EDITOR_BG = "#030803"
_MATRIX_EDITOR_BORDER = "#2d6a3d"
_MATRIX_SELECT_BG = "#003311"

def _matrix_font(size: int) -> tuple[str, int, str]:
    """Police monospace type terminal ; Consolas est généralement disponible sous Windows."""
    return ("Consolas", max(size, 5), "normal")


# Colonnes sous l'horloge : ~80 % gauche / 20 % droite (avec marges)
_LEFT_TEXT_MARGIN_REL = 0.01
_GAP_TEXT_COLUMNS_REL = 0.01
_RIGHT_TEXT_RELWIDTH = 0.20
_LEFT_TEXT_RELWIDTH_BOTH = 1.0 - _LEFT_TEXT_MARGIN_REL - _GAP_TEXT_COLUMNS_REL - _RIGHT_TEXT_RELWIDTH

# Police Matrix : taille mini pour le rétrécissement adaptatif (tout le texte doit tenir dans la zone).
_MATRIX_MIN_FONT = 5


def _fit_matrix_label_to_height(
    root: tk.Misc,
    label: tk.Label,
    *,
    wraplength_px: int,
    max_height_px: float,
    max_font: int,
    min_font: int = _MATRIX_MIN_FONT,
) -> int:
    """
    Plus grande taille de police pour que le Label (wraplength fixé) tienne en hauteur.
    Recherche dichotomique : peu d'appels à update_idletasks (évite boucles / plantages).
    """
    min_font = max(min_font, _MATRIX_MIN_FONT)
    max_font = max(max_font, min_font)
    wl = max(1, int(wraplength_px))
    lo, hi = min_font, max_font
    best = min_font
    limit = float(max_height_px) + 4.0
    while lo <= hi:
        mid = (lo + hi) // 2
        label.config(font=_matrix_font(mid), wraplength=wl, fg=_MATRIX_GREEN)
        root.update_idletasks()
        try:
            h = float(label.winfo_reqheight())
        except tk.TclError:
            h = limit + 1.0
        if h <= limit:
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1
    label.config(font=_matrix_font(best), wraplength=wl, fg=_MATRIX_GREEN)
    return best


class NeonFlickerEffect:
    """Effet de clignotement type néon pour un label Tkinter."""

    def __init__(self, root: tk.Misc, widget: tk.Label, prob: float) -> None:
        self._root = root
        self._widget = widget
        self._prob = prob
        self._running = True
        self._schedule_tick()

    def stop(self) -> None:
        self._running = False

    def _schedule_tick(self) -> None:
        if not self._running:
            return
        self._root.after(1000, self._tick)

    def _tick(self) -> None:
        if not self._running:
            return
        if random.random() < self._prob:
            self._start_flicker()
        self._schedule_tick()

    def _start_flicker(self) -> None:
        sequence = ["#330000", "#880000", "#330000", "#FF0000"]
        self._flicker_step(sequence, 0)

    def _flicker_step(self, colors: list[str], index: int) -> None:
        if index >= len(colors):
            return
        try:
            self._widget.config(fg=colors[index])
        except tk.TclError:
            return
        self._root.after(70, lambda: self._flicker_step(colors, index + 1))


class DisplayWindow(tk.Toplevel):
    """Fenêtre d'affichage (heure / compte à rebours + jour)."""

    def __init__(self, master: tk.Tk, controller: HorlogeController, control_window: ControlWindow | None = None) -> None:
        super().__init__(master)
        self.controller = controller
        self._control_window = control_window

        self.title("Affichage - Horloge JDR")
        self.configure(bg="black")
        self.minsize(300, 150)

        icon_path = _get_icon_path()
        if icon_path is not None:
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

        self.main_frame = tk.Frame(self, bg="black", bd=0, highlightthickness=0)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.display_frame = tk.Frame(self.main_frame, bg="black", bd=0, highlightthickness=0)
        self.display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 0))

        # Import local pour éviter les cycles au chargement, avec fallback exécutable
        try:
            from .domain import AppState  # type: ignore[import-not-found]
        except ImportError:  # pragma: no cover - exécutable PyInstaller
            from domain import AppState  # type: ignore[import-not-found]

        initial_state = controller.state if isinstance(controller.state, AppState) else None
        initial_time = initial_state.current_display_text() if initial_state else "00:00"
        initial_day = initial_state.current_day_text() if initial_state else "Jour 0"
        initial_message = (initial_state.display_message if initial_state else "") or ""
        initial_message_right = (initial_state.display_message_right if initial_state else "") or ""

        # Placement absolu : l'heure reste centrée dans la fenêtre (rely=0.5) même si du texte est affiché en dessous.
        self.time_label = tk.Label(
            self.display_frame,
            text=initial_time,
            fg="red",
            bg="black",
            anchor="center",
        )

        self.day_label = tk.Label(
            self.display_frame,
            text=initial_day,
            fg="red",
            bg="black",
            anchor="ne",
        )

        self.message_label = tk.Label(
            self.display_frame,
            text=initial_message,
            fg=_MATRIX_GREEN,
            bg="black",
            anchor="nw",
            justify="left",
        )

        self.message_right_label = tk.Label(
            self.display_frame,
            text=initial_message_right,
            fg=_MATRIX_GREEN,
            bg="black",
            anchor="nw",
            justify="left",
        )

        self._message_left_visible = bool(initial_message.strip())
        self._message_right_visible = bool(initial_message_right.strip())

        self._layout_busy = False
        self._last_message_fit_key: tuple[object, ...] | None = None
        self._display_config_wh = (0, 0)

        # Bandeau d'aide en bas à gauche (rappel du raccourci pour rouvrir la fenêtre de contrôle)
        help_frame = tk.Frame(self.main_frame, bg="black", bd=0, highlightthickness=0)
        help_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.help_label = tk.Label(
            help_frame,
            text="Ctrl + C : rouvrir la fenêtre de contrôle",
            fg="red",
            bg="black",
            anchor="w",
            font=("Courier New", 10, "bold"),
        )
        self.help_label.pack(side=tk.LEFT, anchor="w")

        self._time_flicker = NeonFlickerEffect(self, self.time_label, prob=0.04)
        self._day_flicker = NeonFlickerEffect(self, self.day_label, prob=0.10)

        # Configure sur la zone d'affichage uniquement (évite boucles avec les labels sous l'horloge).
        self.display_frame.bind("<Configure>", self._on_display_configure)

        # Raccourci clavier pour rouvrir/afficher la fenêtre de contrôle
        self.bind_all("<Control-c>", self._on_show_control_window)

        self.controller.add_listener(self._on_state_changed)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._update_fonts()
        self._update_help_visibility()
        self._schedule_help_visibility_check()

    def _on_state_changed(self, state) -> None:
        # Si la fenêtre est déjà détruite, on se désabonne du contrôleur.
        if not self.winfo_exists():
            try:
                self.controller.remove_listener(self._on_state_changed)
            except Exception:
                pass
            return
        try:
            self.time_label.config(text=state.current_display_text())
            self.day_label.config(text=state.current_day_text())
            self._sync_display_messages(state.display_message, state.display_message_right)
        except tk.TclError:
            # En cas de destruction asynchrone des widgets, on se désabonne pour éviter les erreurs.
            try:
                self.controller.remove_listener(self._on_state_changed)
            except Exception:
                pass
            return
        self.after_idle(self._update_fonts)

    def _sync_display_messages(self, text_left: str, text_right: str) -> None:
        self._message_left_visible = bool(text_left.strip())
        self._message_right_visible = bool(text_right.strip())
        self.message_label.config(text=text_left)
        self.message_right_label.config(text=text_right)

    def _on_display_configure(self, event: tk.Event) -> None:  # type: ignore[type-arg]
        if event.widget != self.display_frame:
            return
        w, h = int(event.width), int(event.height)
        if w < 2 or h < 2:
            return
        if (w, h) == self._display_config_wh:
            return
        self._display_config_wh = (w, h)
        self._last_message_fit_key = None
        self.after_idle(self._update_fonts)

    def _update_fonts(self) -> None:
        if self._layout_busy:
            return
        self._layout_busy = True
        try:
            self.update_idletasks()
            width = max(self.display_frame.winfo_width(), 1)
            df_h = max(self.display_frame.winfo_height(), 1)

            # Police d'horloge : toujours calculée comme si seule l'horloge remplissait la zone (comme sans texte).
            base = min(width // 5, df_h // 2)
            font_size = max(base, 20)
            self.time_label.config(font=("Courier New", font_size, "bold"))
            day_font_size = max(font_size // 4, 8)
            self.day_label.config(font=("Courier New", day_font_size, "bold"))

            self.time_label.place(relx=0.5, rely=0.5, anchor="center")
            self.day_label.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)

            if not (self._message_left_visible or self._message_right_visible):
                self.message_label.place_forget()
                self.message_right_label.place_forget()
                self._last_message_fit_key = None
                return

            txt_l = self.message_label.cget("text") or ""
            txt_r = self.message_right_label.cget("text") or ""
            fit_key = (
                int(width),
                int(df_h),
                txt_l,
                txt_r,
                self._message_left_visible,
                self._message_right_visible,
            )
            if fit_key == self._last_message_fit_key:
                return

            self.update_idletasks()
            time_h = float(self.time_label.winfo_reqheight())
            gap_px = 12.0
            msg_rely = (0.5 * float(df_h) + time_h / 2.0 + gap_px) / float(df_h)
            msg_rely = min(max(msg_rely, 0.02), 0.96)

            msg_top_px = msg_rely * float(df_h)
            msg_h = max(float(df_h) - msg_top_px - 16.0, 24.0)
            base_msg = max(font_size // 6, 6)

            both = self._message_left_visible and self._message_right_visible

            if self._message_left_visible:
                wl = max(int(width * (_LEFT_TEXT_RELWIDTH_BOTH if both else 0.98) - 24), 40)
                if both:
                    self.message_label.place(
                        relx=_LEFT_TEXT_MARGIN_REL,
                        rely=msg_rely,
                        anchor="nw",
                        relwidth=_LEFT_TEXT_RELWIDTH_BOTH,
                    )
                else:
                    self.message_label.place(relx=_LEFT_TEXT_MARGIN_REL, rely=msg_rely, anchor="nw", relwidth=0.98)
                _fit_matrix_label_to_height(
                    self,
                    self.message_label,
                    wraplength_px=wl,
                    max_height_px=msg_h,
                    max_font=base_msg,
                )

            if self._message_right_visible:
                wr = max(int(width * _RIGHT_TEXT_RELWIDTH - 16), 24)
                relx_r = (
                    _LEFT_TEXT_MARGIN_REL + _LEFT_TEXT_RELWIDTH_BOTH + _GAP_TEXT_COLUMNS_REL
                    if both
                    else 1.0 - _RIGHT_TEXT_RELWIDTH - _LEFT_TEXT_MARGIN_REL
                )
                self.message_right_label.place(relx=relx_r, rely=msg_rely, anchor="nw", relwidth=_RIGHT_TEXT_RELWIDTH)
                _fit_matrix_label_to_height(
                    self,
                    self.message_right_label,
                    wraplength_px=wr,
                    max_height_px=msg_h,
                    max_font=base_msg,
                )

            if self._message_left_visible:
                self.time_label.lift(self.message_label)
                self.day_label.lift(self.message_label)
            if self._message_right_visible:
                self.time_label.lift(self.message_right_label)
                self.day_label.lift(self.message_right_label)
            if not self._message_left_visible:
                self.message_label.place_forget()
            if not self._message_right_visible:
                self.message_right_label.place_forget()

            self._last_message_fit_key = fit_key
        finally:
            self._layout_busy = False

    def _on_show_control_window(self, event: tk.Event | None = None) -> None:  # type: ignore[type-arg]
        if self._control_window is not None:
            try:
                self._control_window.deiconify()
                self._control_window.lift()
                self._control_window.focus_force()
                self._update_help_visibility()
            except tk.TclError:
                pass

    def _update_help_visibility(self) -> None:
        """Affiche le raccourci Ctrl+C seulement si la fenêtre de contrôle est masquée."""
        visible = False
        if self._control_window is not None:
            try:
                # winfo_viewable() == 1 si la fenêtre est affichée à l'écran
                visible = bool(self._control_window.winfo_viewable())
            except tk.TclError:
                visible = False
        if visible:
            self.help_label.config(text="")
        else:
            self.help_label.config(text="Ctrl + C : rouvrir la fenêtre de contrôle")

    def _schedule_help_visibility_check(self) -> None:
        """Met à jour périodiquement la visibilité de l'aide, au cas où l'état change."""
        self._update_help_visibility()
        # Intervalle léger, suffisant pour suivre l'état sans surcharger la boucle Tkinter
        self.after(500, self._schedule_help_visibility_check)

    def _on_close(self) -> None:
        # Arrêter les effets et se désabonner proprement du contrôleur.
        self._time_flicker.stop()
        self._day_flicker.stop()
        try:
            self.controller.remove_listener(self._on_state_changed)
        except Exception:
            pass
        self.destroy()


class ControlWindow(tk.Toplevel):
    """Fenêtre de contrôle (heure, jour, compte à rebours, mode d'affichage)."""

    def __init__(self, master: tk.Tk, controller: HorlogeController) -> None:
        super().__init__(master)
        self._root = master
        self.controller = controller

        self.title("Contrôle - Horloge JDR")
        self.configure(bg="black")
        # Taille minimale : aperçu + texte + boutons + compte à rebours + mode + fermer
        self.minsize(600, 600)

        self.main_frame = tk.Frame(self, bg="black", bd=0, highlightthickness=0)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        try:
            from .domain import AppState  # type: ignore[import-not-found]
        except ImportError:  # pragma: no cover - exécutable PyInstaller
            from domain import AppState  # type: ignore[import-not-found]

        initial_state = controller.state if isinstance(controller.state, AppState) else None
        initial_time = initial_state.current_display_text() if initial_state else "00:00"
        initial_day = initial_state.current_day_text() if initial_state else "Jour 0"
        initial_message = (initial_state.display_message if initial_state else "") or ""
        initial_message_right = (initial_state.display_message_right if initial_state else "") or ""

        preview_frame = tk.LabelFrame(
            self.main_frame,
            text="Aperçu (écran affichage)",
            fg="white",
            bg="black",
            bd=1,
            highlightthickness=0,
        )
        preview_frame.pack(fill=tk.X, pady=(0, 10))

        self._preview_canvas = tk.Frame(
            preview_frame,
            bg="black",
            bd=0,
            highlightthickness=1,
            highlightbackground="#660000",
            height=160,
        )
        self._preview_canvas.pack(fill=tk.X, padx=6, pady=6)
        self._preview_canvas.pack_propagate(False)

        self._preview_time_label = tk.Label(
            self._preview_canvas,
            text=initial_time,
            fg="red",
            bg="black",
            anchor="center",
        )

        self._preview_day_label = tk.Label(
            self._preview_canvas,
            text=initial_day,
            fg="red",
            bg="black",
            anchor="ne",
        )

        self._preview_message_label = tk.Label(
            self._preview_canvas,
            text=initial_message,
            fg=_MATRIX_GREEN,
            bg="black",
            anchor="nw",
            justify="left",
        )

        self._preview_message_right_label = tk.Label(
            self._preview_canvas,
            text=initial_message_right,
            fg=_MATRIX_GREEN,
            bg="black",
            anchor="nw",
            justify="left",
        )

        self._preview_message_left_visible = bool(initial_message.strip())
        self._preview_message_right_visible = bool(initial_message_right.strip())

        self._preview_layout_busy = False
        self._last_preview_fit_key: tuple[object, ...] | None = None
        self._preview_config_wh = (0, 0)

        self._preview_canvas.bind("<Configure>", self._on_preview_canvas_configure)
        self.after_idle(self._update_preview_fonts)

        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure(
            "Dark.TButton",
            foreground="white",
            background="#222222",
            padding=6,
        )

        buttons_frame = tk.Frame(self.main_frame, bg="black", bd=0, highlightthickness=0)
        buttons_frame.pack(fill=tk.X, pady=(0, 10))

        self._add_button(buttons_frame, "+1 h", self.controller.on_plus_hour)
        self._add_button(buttons_frame, "-1 h", self.controller.on_minus_hour)
        self._add_button(buttons_frame, "+10 min", self.controller.on_plus_10min)
        self._add_button(buttons_frame, "-10 min", self.controller.on_minus_10min)
        self._add_button(buttons_frame, "+1 j", self.controller.on_plus_day)
        self._add_button(buttons_frame, "-1 j", self.controller.on_minus_day)

        message_frame = tk.LabelFrame(
            self.main_frame,
            text="Textes sous l'horloge (gauche ~80 % / droite ~20 %)",
            fg="white",
            bg="black",
            bd=1,
            highlightthickness=0,
        )
        message_frame.pack(fill=tk.X, pady=(0, 10))
        message_frame.grid_columnconfigure(0, weight=8)
        message_frame.grid_columnconfigure(1, weight=2)
        message_frame.grid_rowconfigure(0, weight=1)

        self._message_editor_left_wrap = tk.Frame(
            message_frame,
            bg=_MATRIX_EDITOR_BG,
            highlightthickness=1,
            highlightbackground=_MATRIX_EDITOR_BORDER,
            bd=0,
        )
        self._message_editor_left_wrap.grid(row=0, column=0, sticky="nsew", padx=(6, 3), pady=(6, 4))

        self._message_editor_left = tk.Text(
            self._message_editor_left_wrap,
            height=4,
            wrap="word",
            fg=_MATRIX_GREEN,
            bg=_MATRIX_EDITOR_BG,
            insertbackground=_MATRIX_GREEN,
            font=("Consolas", 10),
            relief=tk.FLAT,
            padx=6,
            pady=4,
            selectbackground=_MATRIX_SELECT_BG,
            selectforeground=_MATRIX_GREEN,
        )
        self._message_editor_left.pack(fill=tk.BOTH, expand=True)

        self._message_editor_right_wrap = tk.Frame(
            message_frame,
            bg=_MATRIX_EDITOR_BG,
            highlightthickness=1,
            highlightbackground=_MATRIX_EDITOR_BORDER,
            bd=0,
        )
        self._message_editor_right_wrap.grid(row=0, column=1, sticky="nsew", padx=(3, 6), pady=(6, 4))

        self._message_editor_right = tk.Text(
            self._message_editor_right_wrap,
            height=4,
            width=22,
            wrap="word",
            fg=_MATRIX_GREEN,
            bg=_MATRIX_EDITOR_BG,
            insertbackground=_MATRIX_GREEN,
            font=("Consolas", 10),
            relief=tk.FLAT,
            padx=6,
            pady=4,
            selectbackground=_MATRIX_SELECT_BG,
            selectforeground=_MATRIX_GREEN,
        )
        self._message_editor_right.pack(fill=tk.BOTH, expand=True)

        if initial_message:
            self._message_editor_left.insert("1.0", initial_message)
        if initial_message_right:
            self._message_editor_right.insert("1.0", initial_message_right)

        apply_msg_btn = ttk.Button(
            message_frame,
            text="Appliquer les textes sur l'écran",
            style="Dark.TButton",
            command=self._on_apply_display_message,
        )
        apply_msg_btn.grid(row=1, column=0, columnspan=2, sticky="ew", padx=6, pady=(4, 6))

        countdown_frame = tk.LabelFrame(
            self.main_frame,
            text="Compte à rebours",
            fg="white",
            bg="black",
            bd=1,
            highlightthickness=0,
        )
        countdown_frame.pack(fill=tk.X, pady=(0, 10))

        self.countdown_minutes_var = tk.StringVar(value="5")

        minutes_label = tk.Label(countdown_frame, text="Minutes :", fg="white", bg="black")
        minutes_label.pack(side=tk.LEFT, padx=(5, 2), pady=5)

        self.minutes_entry = tk.Spinbox(
            countdown_frame,
            from_=1,
            to=999,
            textvariable=self.countdown_minutes_var,
            width=5,
        )
        self.minutes_entry.pack(side=tk.LEFT, padx=2, pady=5)

        start_btn = ttk.Button(
            countdown_frame,
            text="Démarrer",
            style="Dark.TButton",
            command=self._on_start_countdown,
        )
        start_btn.pack(side=tk.LEFT, padx=4, pady=5)

        stop_btn = ttk.Button(
            countdown_frame,
            text="Arrêter",
            style="Dark.TButton",
            command=self.controller.on_stop_countdown,
        )
        stop_btn.pack(side=tk.LEFT, padx=4, pady=5)

        reset_btn = ttk.Button(
            countdown_frame,
            text="Réinitialiser",
            style="Dark.TButton",
            command=self.controller.on_reset_countdown,
        )
        reset_btn.pack(side=tk.LEFT, padx=4, pady=5)

        mode_frame = tk.LabelFrame(
            self.main_frame,
            text="Mode d'affichage",
            fg="white",
            bg="black",
            bd=1,
            highlightthickness=0,
        )
        mode_frame.pack(fill=tk.X, pady=(0, 10))

        self.display_mode_var = tk.StringVar(value="time")

        time_radio = tk.Radiobutton(
            mode_frame,
            text="Heure manuelle",
            variable=self.display_mode_var,
            value="time",
            command=self._on_display_mode_changed,
            fg="white",
            bg="black",
            selectcolor="#222222",
        )
        time_radio.pack(side=tk.LEFT, padx=5, pady=5)

        countdown_radio = tk.Radiobutton(
            mode_frame,
            text="Compte à rebours",
            variable=self.display_mode_var,
            value="countdown",
            command=self._on_display_mode_changed,
            fg="white",
            bg="black",
            selectcolor="#222222",
        )
        countdown_radio.pack(side=tk.LEFT, padx=5, pady=5)

        # Bouton global pour fermer proprement l'application
        quit_btn = ttk.Button(
            self.main_frame,
            text="Fermer l'application",
            style="Dark.TButton",
            command=self._on_quit_app,
        )
        quit_btn.pack(fill=tk.X, pady=(0, 5))

        self.controller.add_listener(self._on_state_changed)

        # Si l'utilisateur ferme la fenêtre de contrôle avec le X,
        # on la masque simplement (withdraw) au lieu de la détruire,
        # pour pouvoir la rouvrir depuis la fenêtre d'affichage.
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _add_button(self, parent: tk.Misc, text: str, command) -> None:
        btn = ttk.Button(parent, text=text, style="Dark.TButton", command=command)
        btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

    def _on_start_countdown(self) -> None:
        try:
            minutes = int(self.countdown_minutes_var.get())
        except ValueError:
            minutes = 0
        self.controller.on_start_countdown(minutes)

    def _on_display_mode_changed(self) -> None:
        value = self.display_mode_var.get()
        if value == "countdown":
            self.controller.on_set_display_countdown()
        else:
            self.controller.on_set_display_manual_time()

    def _on_apply_display_message(self) -> None:
        left = self._message_editor_left.get("1.0", "end-1c")
        right = self._message_editor_right.get("1.0", "end-1c")
        self.controller.on_set_display_message(left)
        self.controller.on_set_display_message_right(right)

    def _on_preview_canvas_configure(self, event: tk.Event) -> None:  # type: ignore[type-arg]
        if event.widget != self._preview_canvas:
            return
        w, h = int(event.width), int(event.height)
        if w < 2 or h < 2:
            return
        if (w, h) == self._preview_config_wh:
            return
        self._preview_config_wh = (w, h)
        self._last_preview_fit_key = None
        self.after_idle(self._update_preview_fonts)

    def _update_preview_fonts(self) -> None:
        if self._preview_layout_busy:
            return
        self._preview_layout_busy = True
        try:
            self.update_idletasks()
            w = max(self._preview_canvas.winfo_width(), 1)
            canvas_h = max(self._preview_canvas.winfo_height(), 1)
            base = min(w // 5, canvas_h // 2)
            font_size = max(base, 14)
            self._preview_time_label.config(font=("Courier New", font_size, "bold"))
            self._preview_day_label.config(font=("Courier New", max(font_size // 4, 8), "bold"))
            self._preview_time_label.place(relx=0.5, rely=0.5, anchor="center")
            self._preview_day_label.place(relx=1.0, rely=0.0, anchor="ne", x=-8, y=6)

            if not (self._preview_message_left_visible or self._preview_message_right_visible):
                self._preview_message_label.place_forget()
                self._preview_message_right_label.place_forget()
                self._last_preview_fit_key = None
                return

            txt_l = self._preview_message_label.cget("text") or ""
            txt_r = self._preview_message_right_label.cget("text") or ""
            pkey = (
                int(w),
                int(canvas_h),
                txt_l,
                txt_r,
                self._preview_message_left_visible,
                self._preview_message_right_visible,
            )
            if pkey == self._last_preview_fit_key:
                return

            self.update_idletasks()
            time_h = float(self._preview_time_label.winfo_reqheight())
            gap_px = 6.0
            msg_rely = (0.5 * float(canvas_h) + time_h / 2.0 + gap_px) / float(canvas_h)
            msg_rely = min(max(msg_rely, 0.02), 0.96)

            msg_top_px = msg_rely * float(canvas_h)
            msg_h = max(float(canvas_h) - msg_top_px - 8.0, 12.0)
            base_msg = max(font_size // 6, 6)

            both = self._preview_message_left_visible and self._preview_message_right_visible

            if self._preview_message_left_visible:
                wl = max(int(w * (_LEFT_TEXT_RELWIDTH_BOTH if both else 0.98) - 16), 24)
                if both:
                    self._preview_message_label.place(
                        relx=_LEFT_TEXT_MARGIN_REL,
                        rely=msg_rely,
                        anchor="nw",
                        relwidth=_LEFT_TEXT_RELWIDTH_BOTH,
                    )
                else:
                    self._preview_message_label.place(
                        relx=_LEFT_TEXT_MARGIN_REL,
                        rely=msg_rely,
                        anchor="nw",
                        relwidth=0.98,
                    )
                _fit_matrix_label_to_height(
                    self,
                    self._preview_message_label,
                    wraplength_px=wl,
                    max_height_px=msg_h,
                    max_font=base_msg,
                )

            if self._preview_message_right_visible:
                wr = max(int(w * _RIGHT_TEXT_RELWIDTH - 12), 16)
                relx_r = (
                    _LEFT_TEXT_MARGIN_REL + _LEFT_TEXT_RELWIDTH_BOTH + _GAP_TEXT_COLUMNS_REL
                    if both
                    else 1.0 - _RIGHT_TEXT_RELWIDTH - _LEFT_TEXT_MARGIN_REL
                )
                self._preview_message_right_label.place(
                    relx=relx_r,
                    rely=msg_rely,
                    anchor="nw",
                    relwidth=_RIGHT_TEXT_RELWIDTH,
                )
                _fit_matrix_label_to_height(
                    self,
                    self._preview_message_right_label,
                    wraplength_px=wr,
                    max_height_px=msg_h,
                    max_font=base_msg,
                )

            if self._preview_message_left_visible:
                self._preview_time_label.lift(self._preview_message_label)
                self._preview_day_label.lift(self._preview_message_label)
            if self._preview_message_right_visible:
                self._preview_time_label.lift(self._preview_message_right_label)
                self._preview_day_label.lift(self._preview_message_right_label)
            if not self._preview_message_left_visible:
                self._preview_message_label.place_forget()
            if not self._preview_message_right_visible:
                self._preview_message_right_label.place_forget()

            self._last_preview_fit_key = pkey
        except tk.TclError:
            pass
        finally:
            self._preview_layout_busy = False

    def _on_state_changed(self, state) -> None:
        # Synchroniser le radio bouton avec l'état global si besoin
        if state.display_mode.name.lower().startswith("countdown"):
            self.display_mode_var.set("countdown")
        else:
            self.display_mode_var.set("time")
        try:
            self._preview_time_label.config(text=state.current_display_text())
            self._preview_day_label.config(text=state.current_day_text())
            self._preview_message_label.config(text=state.display_message)
            self._preview_message_right_label.config(text=state.display_message_right)
            self._preview_message_left_visible = bool(state.display_message.strip())
            self._preview_message_right_visible = bool(state.display_message_right.strip())
            self.after_idle(self._update_preview_fonts)
        except tk.TclError:
            pass

    def _on_close(self) -> None:
        # Masquer la fenêtre de contrôle mais ne pas la détruire,
        # pour que des raccourcis depuis la fenêtre d'affichage puissent la rouvrir.
        self.withdraw()

    def _on_quit_app(self) -> None:
        """Ferme proprement toute l'application."""
        try:
            self.controller.remove_listener(self._on_state_changed)
        except Exception:
            pass
        try:
            self._root.destroy()
        except Exception:
            pass


def _position_display_window_on_secondary_monitor(root: tk.Tk, window: tk.Toplevel) -> None:
    """Essaie de placer la fenêtre d'affichage sur un 2ème écran si disponible."""
    try:
        from screeninfo import get_monitors  # type: ignore[import-not-found]

        monitors = get_monitors()
        if len(monitors) >= 2:
            second = monitors[1]
            geometry = f"{second.width}x{second.height}+{second.x}+{second.y}"
            window.geometry(geometry)
            window.attributes("-fullscreen", True)
            return
    except Exception:
        pass

    # Fallback : fenêtre maximisée mais redimensionnable sur l'écran principal
    try:
        window.attributes("-fullscreen", False)
    except Exception:
        pass
    window.state("zoomed")


def main() -> None:
    root = tk.Tk()
    root.withdraw()  # on masque la fenêtre racine, seules les Toplevel sont visibles

    controller = HorlogeController()

    control = ControlWindow(root, controller)
    display = DisplayWindow(root, controller, control_window=control)

    _position_display_window_on_secondary_monitor(root, display)

    # Placer la fenêtre de contrôle de manière raisonnable sur l'écran principal
    # Hauteur augmentée pour que tous les contrôles soient visibles sans redimensionner.
    control.geometry("600x620+100+100")

    def _tick() -> None:
        controller.tick_countdown()
        root.after(1000, _tick)

    root.after(1000, _tick)
    root.mainloop()


if __name__ == "__main__":
    main()

