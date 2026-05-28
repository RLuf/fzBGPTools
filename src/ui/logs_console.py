from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QTextEdit, QComboBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QTextCursor

class LogsConsoleScreen(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # Header Area
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title_block = QFrame()
        title_layout = QVBoxLayout(title_block)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(4)
        
        title_lbl = QLabel("Console de Logs")
        title_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #3da9fc;")
        sub_lbl = QLabel("Visualização em tempo real das mensagens e eventos do sistema.")
        sub_lbl.setStyleSheet("font-size: 12px; color: #9aa6c2;")
        title_layout.addWidget(title_lbl)
        title_layout.addWidget(sub_lbl)
        
        # Filters and Clear
        controls_layout = QHBoxLayout()
        self.filter_cb = QComboBox()
        self.filter_cb.addItems(["Todos", "INFO", "WARN", "ERROR"])
        self.filter_cb.currentIndexChanged.connect(self.load_logs)
        
        clear_btn = QPushButton("Limpar Logs")
        clear_btn.setObjectName("BtnDanger")
        clear_btn.clicked.connect(self.clear_logs)
        
        refresh_btn = QPushButton("Atualizar")
        refresh_btn.setObjectName("Btn")
        refresh_btn.clicked.connect(self.load_logs)
        
        controls_layout.addWidget(QLabel("Filtrar por:"))
        controls_layout.addWidget(self.filter_cb)
        controls_layout.addWidget(refresh_btn)
        controls_layout.addWidget(clear_btn)
        
        header_layout.addWidget(title_block)
        header_layout.addStretch()
        header_layout.addLayout(controls_layout)
        layout.addWidget(header_frame)
        
        # Terminal log console
        self.console = QTextEdit()
        self.console.setObjectName("Terminal")
        self.console.setReadOnly(True)
        layout.addWidget(self.console)
        
        self.load_logs()

    def load_logs(self):
        self.console.clear()
        logs = self.db.get_logs()
        filter_text = self.filter_cb.currentText()
        
        for sev, module, msg, timestamp in reversed(logs):
            if filter_text != "Todos" and sev.upper() != filter_text:
                continue
                
            color = "#4ade80"  # Info green
            if sev.upper() == "WARN":
                color = "#fbbf24"  # Warning yellow
            elif sev.upper() in ["ERROR", "CRITICAL"]:
                color = "#ff5c7a"  # Error red
                
            log_line = f"<span style='color: #6b7693;'>[{timestamp}]</span> <span style='color: {color}; font-weight: bold;'>[{sev}]</span> <span style='color: #3da9fc;'>[{module}]</span> {msg}<br>"
            self.console.insertHtml(log_line)
            
        self.console.moveCursor(QTextCursor.End)

    def clear_logs(self):
        with self.db.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM logs")
            conn.commit()
        self.db.add_log("INFO", "System", "Console de logs limpo pelo usuário.")
        self.load_logs()
