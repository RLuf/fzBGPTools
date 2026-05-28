def get_stylesheet():
    return """
    /* Global Styles */
    QWidget {
        color: #e7ecf7;
        font-family: 'Inter', 'Segoe UI', sans-serif;
        font-size: 13px;
    }
    
    QMainWindow {
        background-color: #0b0f19;
    }
    
    QDialog {
        background-color: #0e1424;
        border: 1px solid rgba(120, 160, 240, 0.28);
        border-radius: 12px;
    }
    
    /* Left Sidebar */
    QFrame#Sidebar {
        background-color: #0e1424;
        border-right: 1px solid rgba(110, 140, 220, 0.14);
    }
    
    /* Sidebar Navigation Buttons */
    QPushButton#NavItem {
        background-color: transparent;
        color: #9aa6c2;
        border: none;
        border-radius: 8px;
        padding: 10px 14px;
        text-align: left;
        font-weight: 500;
    }
    QPushButton#NavItem:hover {
        background-color: rgba(255, 255, 255, 0.03);
        color: #e7ecf7;
    }
    QPushButton#NavItem:checked {
        background-color: rgba(61, 169, 252, 0.14);
        color: #3da9fc;
        border-left: 3px solid #3da9fc;
        font-weight: 600;
    }
    
    /* Topbar Crumb */
    QLabel#Crumb {
        color: #6b7693;
        font-size: 12px;
    }
    
    /* Stats Widgets */
    QFrame#StatCard {
        background-color: rgba(20, 27, 48, 0.55);
        border: 1px solid rgba(110, 140, 220, 0.14);
        border-radius: 12px;
    }
    QLabel#StatLabel {
        color: #6b7693;
        font-size: 10px;
        font-weight: 600;
        text-transform: uppercase;
    }
    QLabel#StatValue {
        color: #e7ecf7;
        font-size: 24px;
        font-weight: bold;
    }
    QLabel#StatDelta {
        font-size: 11px;
    }
    QLabel#StatDelta[status="up"] {
        color: #4ade80;
    }
    QLabel#StatDelta[status="dn"] {
        color: #ff5c7a;
    }
    
    /* Main Layout Cards */
    QFrame#Card {
        background-color: rgba(20, 27, 48, 0.55);
        border: 1px solid rgba(110, 140, 220, 0.14);
        border-radius: 12px;
    }
    
    QFrame#CardHeader {
        border-bottom: 1px solid rgba(110, 140, 220, 0.14);
    }
    
    QLabel#CardTitle {
        font-size: 13px;
        font-weight: bold;
        color: #e7ecf7;
    }
    
    /* Buttons */
    QPushButton#Btn {
        background-color: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(110, 140, 220, 0.14);
        border-radius: 8px;
        color: #e7ecf7;
        padding: 8px 14px;
        font-weight: 500;
    }
    QPushButton#Btn:hover {
        background-color: rgba(255, 255, 255, 0.06);
    }
    
    QPushButton#BtnPrimary {
        background-color: #3da9fc;
        color: #0b0f19;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 8px 14px;
    }
    QPushButton#BtnPrimary:hover {
        background-color: #21d4fd;
    }
    
    QPushButton#BtnDanger {
        background-color: rgba(255, 92, 122, 0.08);
        border: 1px solid rgba(255, 92, 122, 0.32);
        color: #ff5c7a;
        border-radius: 8px;
        padding: 8px 14px;
        font-weight: 500;
    }
    QPushButton#BtnDanger:hover {
        background-color: rgba(255, 92, 122, 0.16);
    }
    
    /* Line Edits & ComboBoxes */
    QLineEdit {
        background-color: rgba(11, 15, 25, 0.6);
        border: 1px solid rgba(110, 140, 220, 0.14);
        border-radius: 6px;
        padding: 6px 10px;
        color: #e7ecf7;
    }
    QLineEdit:focus {
        border-color: #3da9fc;
    }
    
    QComboBox {
        background-color: rgba(11, 15, 25, 0.6);
        border: 1px solid rgba(110, 140, 220, 0.14);
        border-radius: 6px;
        padding: 6px 10px;
        color: #e7ecf7;
    }
    QComboBox::drop-down {
        border: none;
    }
    QComboBox QAbstractItemView {
        background-color: #0e1424;
        color: #e7ecf7;
        selection-background-color: #3da9fc;
        selection-color: #0b0f19;
    }
    
    /* Table View Styling */
    QTableWidget {
        background-color: transparent;
        border: 1px solid rgba(110, 140, 220, 0.14);
        border-radius: 12px;
        gridline-color: rgba(255, 255, 255, 0.03);
    }
    QTableWidget::item {
        padding: 10px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.03);
    }
    QTableWidget::item:selected {
        background-color: rgba(61, 169, 252, 0.16);
        color: #e7ecf7;
    }
    QHeaderView::section {
        background-color: rgba(11, 15, 25, 0.85);
        color: #6b7693;
        padding: 8px;
        font-size: 10.5px;
        font-weight: bold;
        text-transform: uppercase;
        border: none;
        border-bottom: 1px solid rgba(110, 140, 220, 0.14);
    }
    
    /* Scrollbars */
    QScrollBar:vertical {
        border: none;
        background: #0b0f19;
        width: 10px;
        margin: 0px;
    }
    QScrollBar::handle:vertical {
        background: #1c243c;
        min-height: 20px;
        border-radius: 5px;
    }
    QScrollBar::handle:vertical:hover {
        background: #3da9fc;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    
    /* Console / Terminal QTextEdit */
    QTextEdit#Terminal {
        background-color: #050810;
        border: 1px solid rgba(74, 222, 128, 0.18);
        border-radius: 12px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12.5px;
        color: #b6f3c8;
        line-height: 1.5;
    }
    
    /* Tab Widget */
    QTabWidget::pane {
        border: 1px solid rgba(110, 140, 220, 0.14);
        background-color: rgba(20, 27, 48, 0.55);
        border-radius: 8px;
        top: -1px;
    }
    QTabBar::tab {
        background: rgba(11, 15, 25, 0.5);
        border: 1px solid rgba(110, 140, 220, 0.14);
        border-bottom-color: none;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        padding: 8px 16px;
        color: #9aa6c2;
    }
    QTabBar::tab:selected {
        background-color: #3da9fc;
        color: #0b0f19;
        font-weight: bold;
    }
    """
