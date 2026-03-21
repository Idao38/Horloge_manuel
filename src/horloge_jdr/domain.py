from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

# Import adapté au contexte (package vs exécutable PyInstaller)
if __package__ in (None, ""):
    # Contexte script/gelé : modules plats dans le même dossier
    from time_model import DayCounter, TimeModel  # type: ignore[import-not-found]
else:
    # Contexte package : src.horloge_jdr.time_model
    from .time_model import DayCounter, TimeModel


class DisplayMode(str, Enum):
    MANUAL_TIME = "manual_time"
    COUNTDOWN = "countdown"


@dataclass
class ClockState:
    time_model: TimeModel = field(default_factory=TimeModel)
    day_counter: DayCounter = field(default_factory=DayCounter)

    def add_minutes(self, delta_minutes: int) -> None:
        """Ajoute des minutes et ajuste le compteur de jours si on passe par minuit."""
        if delta_minutes == 0:
            return

        old_minutes = self.time_model.total_minutes
        self.time_model.add_minutes(delta_minutes)
        new_minutes = self.time_model.total_minutes

        if delta_minutes > 0 and new_minutes < old_minutes:
            self.day_counter.add_days(1)
        elif delta_minutes < 0 and new_minutes > old_minutes:
            self.day_counter.add_days(-1)

    def add_hours(self, delta_hours: int) -> None:
        self.add_minutes(delta_hours * 60)

    def add_days(self, delta_days: int) -> None:
        self.day_counter.add_days(delta_days)

    def formatted_time(self) -> str:
        return self.time_model.formatted()

    def formatted_day(self) -> str:
        return self.day_counter.formatted()


@dataclass
class CountdownModel:
    remaining_seconds: int = 0
    running: bool = False

    def start(self, duration_minutes: int) -> None:
        """Démarre un nouveau compte à rebours à partir d'un nombre de minutes."""
        total_seconds = max(0, int(duration_minutes)) * 60
        self.remaining_seconds = total_seconds
        self.running = self.remaining_seconds > 0

    def stop(self) -> None:
        self.running = False

    def reset(self) -> None:
        self.remaining_seconds = 0
        self.running = False

    def tick_one_second(self) -> None:
        """Fait avancer le compte à rebours d'une seconde."""
        if not self.running or self.remaining_seconds <= 0:
            self.running = False
            return

        self.remaining_seconds -= 1
        if self.remaining_seconds <= 0:
            self.remaining_seconds = 0
            self.running = False

    def formatted_mm_ss(self) -> str:
        minutes, seconds = divmod(max(0, self.remaining_seconds), 60)
        return f"{minutes:02d}:{seconds:02d}"


@dataclass
class AppState:
    clock: ClockState = field(default_factory=ClockState)
    countdown: CountdownModel = field(default_factory=CountdownModel)
    display_mode: DisplayMode = DisplayMode.MANUAL_TIME
    display_message: str = ""  # texte libre sous l'horloge, colonne gauche (~80 %)
    display_message_right: str = ""  # colonne droite (~20 % de la largeur)

    def set_display_mode(self, mode: DisplayMode) -> None:
        self.display_mode = mode

    def set_display_message(self, text: str) -> None:
        """Définit le texte sous l'horloge ; normalise les fins de ligne Windows."""
        self.display_message = str(text).replace("\r\n", "\n")

    def set_display_message_right(self, text: str) -> None:
        """Texte de la colonne droite sous l'horloge."""
        self.display_message_right = str(text).replace("\r\n", "\n")

    def toggle_display_mode(self) -> None:
        if self.display_mode is DisplayMode.MANUAL_TIME:
            self.display_mode = DisplayMode.COUNTDOWN
        else:
            self.display_mode = DisplayMode.MANUAL_TIME

    # Opérations de haut niveau sur le temps et les jours
    def update_time_minutes(self, delta_minutes: int) -> None:
        self.clock.add_minutes(delta_minutes)

    def update_hours(self, delta_hours: int) -> None:
        self.clock.add_hours(delta_hours)

    def update_days(self, delta_days: int) -> None:
        self.clock.add_days(delta_days)

    # Opérations de haut niveau sur le compte à rebours
    def start_countdown(self, minutes: int) -> None:
        self.countdown.start(minutes)

    def stop_countdown(self) -> None:
        self.countdown.stop()

    def reset_countdown(self) -> None:
        self.countdown.reset()

    def tick_countdown_second(self) -> None:
        self.countdown.tick_one_second()

    # Valeurs dérivées pour l'affichage
    def current_display_text(self) -> str:
        if self.display_mode is DisplayMode.MANUAL_TIME:
            return self.clock.formatted_time()
        return self.countdown.formatted_mm_ss()

    def current_day_text(self) -> str:
        return self.clock.formatted_day()

