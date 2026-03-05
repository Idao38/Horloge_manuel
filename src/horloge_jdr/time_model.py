from __future__ import annotations

from dataclasses import dataclass


MINUTES_PER_DAY = 24 * 60


@dataclass
class TimeModel:
    """
    Modèle d'heure simple pour une horloge JDR.

    L'heure est stockée en minutes depuis 00:00 et reste toujours dans [0, MINUTES_PER_DAY - 1].
    """

    total_minutes: int = 0

    def __post_init__(self) -> None:
        self.total_minutes = self.total_minutes % MINUTES_PER_DAY

    @property
    def hours(self) -> int:
        return self.total_minutes // 60

    @property
    def minutes(self) -> int:
        return self.total_minutes % 60

    def add_hours(self, delta_hours: int) -> None:
        self._add_minutes_internal(delta_hours * 60)

    def add_minutes(self, delta_minutes: int) -> None:
        self._add_minutes_internal(delta_minutes)

    def _add_minutes_internal(self, delta_minutes: int) -> None:
        self.total_minutes = (self.total_minutes + delta_minutes) % MINUTES_PER_DAY

    def formatted(self) -> str:
        return f"{self.hours:02d}:{self.minutes:02d}"


@dataclass
class DayCounter:
    """
    Compteur de jours simple pour le suivi de la durée de la campagne.

    Le nombre de jours peut être incrémenté ou décrémenté librement.
    """

    days: int = 0

    def add_days(self, delta_days: int) -> None:
        self.days += delta_days

    def formatted(self) -> str:
        return f"Jour {self.days}"


