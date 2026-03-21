from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List

# Import adapté au contexte (package vs exécutable PyInstaller)
if __package__ in (None, ""):
    # Contexte script/gelé : modules plats dans le même dossier
    from domain import AppState, DisplayMode  # type: ignore[import-not-found]
else:
    # Contexte package : src.horloge_jdr.domain
    from .domain import AppState, DisplayMode


StateListener = Callable[[AppState], None]


@dataclass
class HorlogeController:
    """Orchestre les mises à jour de l'état de l'application et notifie les vues."""

    state: AppState = field(default_factory=AppState)
    _listeners: List[StateListener] = field(default_factory=list)

    # Gestion des vues / observation
    def add_listener(self, listener: StateListener) -> None:
        if listener not in self._listeners:
            self._listeners.append(listener)

    def remove_listener(self, listener: StateListener) -> None:
        if listener in self._listeners:
            self._listeners.remove(listener)

    def _notify_listeners(self) -> None:
        for listener in list(self._listeners):
            listener(self.state)

    # Commandes liées à l'heure/jour
    def on_plus_hour(self) -> None:
        self.state.update_hours(1)
        self._notify_listeners()

    def on_minus_hour(self) -> None:
        self.state.update_hours(-1)
        self._notify_listeners()

    def on_plus_10min(self) -> None:
        self.state.update_time_minutes(10)
        self._notify_listeners()

    def on_minus_10min(self) -> None:
        self.state.update_time_minutes(-10)
        self._notify_listeners()

    def on_plus_day(self) -> None:
        self.state.update_days(1)
        self._notify_listeners()

    def on_minus_day(self) -> None:
        self.state.update_days(-1)
        self._notify_listeners()

    # Commandes liées au compte à rebours
    def on_start_countdown(self, minutes: int) -> None:
        self.state.start_countdown(minutes)
        self._notify_listeners()

    def on_stop_countdown(self) -> None:
        self.state.stop_countdown()
        self._notify_listeners()

    def on_reset_countdown(self) -> None:
        self.state.reset_countdown()
        self._notify_listeners()

    def tick_countdown(self) -> None:
        """À appeler chaque seconde par la boucle Tkinter."""
        self.state.tick_countdown_second()
        # On notifie seulement si le compte à rebours existe encore
        self._notify_listeners()

    # Mode d'affichage
    def on_set_display_manual_time(self) -> None:
        self.state.set_display_mode(DisplayMode.MANUAL_TIME)
        self._notify_listeners()

    def on_set_display_countdown(self) -> None:
        self.state.set_display_mode(DisplayMode.COUNTDOWN)
        self._notify_listeners()

    def on_toggle_display_mode(self) -> None:
        self.state.toggle_display_mode()
        self._notify_listeners()

    def on_set_display_message(self, text: str) -> None:
        """Met à jour le texte affiché sous l'horloge (fenêtre d'affichage)."""
        self.state.set_display_message(text)
        self._notify_listeners()

    def on_set_display_message_right(self, text: str) -> None:
        """Met à jour le texte de la colonne droite (~20 % de la largeur)."""
        self.state.set_display_message_right(text)
        self._notify_listeners()

