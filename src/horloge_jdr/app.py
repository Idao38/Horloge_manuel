"""Point d'entrée principal de l'application Horloge JDR."""

from __future__ import annotations

import sys
import tkinter as tk

# Import du contrôleur adapté au contexte (package vs exécutable PyInstaller)
if getattr(sys, "frozen", False):
    from horloge_jdr.controller import HorlogeController
    from horloge_jdr.ui.control_window import ControlWindow
    from horloge_jdr.ui.display_window import DisplayWindow
    from horloge_jdr.ui.screen_position import position_display_window_on_secondary_monitor
else:
    from .controller import HorlogeController
    from .ui.control_window import ControlWindow
    from .ui.display_window import DisplayWindow
    from .ui.screen_position import position_display_window_on_secondary_monitor


def main() -> None:
    root = tk.Tk()
    root.withdraw()  # on masque la fenêtre racine, seules les Toplevel sont visibles

    controller = HorlogeController()

    control = ControlWindow(root, controller)
    display = DisplayWindow(root, controller, control_window=control)

    position_display_window_on_secondary_monitor(root, display)

    control.geometry("600x700+100+100")

    def _tick() -> None:
        controller.tick_countdown()
        root.after(1000, _tick)

    root.after(1000, _tick)
    root.mainloop()


if __name__ == "__main__":
    main()
