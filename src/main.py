import sys
import os

# Add parent directory to path so imports work correctly when compiled
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication
from src.database import Database
from src.ui.main_window import MainWindow
from src.ui.theme import get_stylesheet

def main():
    # Setup database
    db = Database()
    
    # Initialize Qt Application
    app = QApplication(sys.argv)
    
    # Apply stylesheet
    app.setStyleSheet(get_stylesheet())
    
    # Show main window
    window = MainWindow(db)
    window.show()
    
    # Execute application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
