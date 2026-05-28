"""Entry point for fzBGPTools."""
import sys
import os

# Ensure project root in path (works compiled by PyInstaller too)
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

from src.database import Database
from src.ui.main_window import MainWindow
from src.ui.theme import get_stylesheet
from src.version import __app_name__, __version__


def resource_path(rel):
    """Resolve resource path both in dev and PyInstaller bundle."""
    base = getattr(sys, "_MEIPASS", ROOT)
    return os.path.join(base, rel)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(__app_name__)
    app.setApplicationVersion(__version__)
    app.setOrganizationName("fzBGPTools")
    app.setStyleSheet(get_stylesheet())

    # App icon
    icon_path = resource_path(os.path.join("src", "resources", "icon.png"))
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    db = Database()
    db.add_log("INFO", "System", f"{__app_name__} v{__version__} iniciado.")

    win = MainWindow(db)
    if os.path.exists(icon_path):
        win.setWindowIcon(QIcon(icon_path))
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
