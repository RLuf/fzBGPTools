"""Settings — DB backup/restore/reset + About panel with version info."""
import os
import shutil
import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
                              QFileDialog, QMessageBox, QGridLayout)
from PyQt5.QtCore import Qt

from src.ui.widgets import page_header, badge
from src.version import __version__, __app_name__, __description__, __author__, __url__


class SettingsScreen(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        layout.addWidget(page_header(
            "System", "Settings",
            "Gerenciamento do banco de dados, backups e informações da aplicação."))

        # ── Card 1: Database ──
        db_card = QFrame()
        db_card.setObjectName("Card")
        dl = QVBoxLayout(db_card)
        dl.setContentsMargins(20, 18, 20, 18)
        dl.setSpacing(12)

        title = QLabel("BANCO DE DADOS LOCAL (SQLITE)")
        title.setStyleSheet("font-size: 11px; color: #6b7693; font-weight: 700; letter-spacing: 0.14em;")
        dl.addWidget(title)

        info = QGridLayout()
        info.setSpacing(8)
        info.addWidget(self._kv_label("Arquivo:"), 0, 0)
        self.path_val = QLabel(self.db.db_path)
        self.path_val.setStyleSheet("font-family: 'JetBrains Mono'; font-size: 11px; color: #9aa6c2;")
        self.path_val.setTextInteractionFlags(Qt.TextSelectableByMouse)
        info.addWidget(self.path_val, 0, 1)

        info.addWidget(self._kv_label("Tamanho:"), 1, 0)
        self.size_val = QLabel("0 KB")
        self.size_val.setStyleSheet("font-family: 'JetBrains Mono'; font-size: 11px; color: #4ade80;")
        info.addWidget(self.size_val, 1, 1)

        info.addWidget(self._kv_label("Versão do esquema:"), 2, 0)
        info.addWidget(QLabel(f"v{self.db.SCHEMA_VERSION}"), 2, 1)

        dl.addLayout(info)

        # Action buttons
        actions = QHBoxLayout()
        backup = QPushButton("⤓  Fazer Backup")
        backup.setObjectName("BtnPrimary")
        backup.clicked.connect(self.backup_db)

        restore = QPushButton("⤒  Restaurar Backup")
        restore.setObjectName("Btn")
        restore.clicked.connect(self.restore_db)

        reset = QPushButton("⟲  Resetar DB")
        reset.setObjectName("BtnDanger")
        reset.clicked.connect(self.reset_db)

        actions.addWidget(backup)
        actions.addWidget(restore)
        actions.addWidget(reset)
        actions.addStretch()
        dl.addLayout(actions)

        layout.addWidget(db_card)

        # ── Card 2: About ──
        about = QFrame()
        about.setObjectName("Card")
        al = QVBoxLayout(about)
        al.setContentsMargins(20, 18, 20, 18)
        al.setSpacing(10)

        title = QLabel("SOBRE")
        title.setStyleSheet("font-size: 11px; color: #6b7693; font-weight: 700; letter-spacing: 0.14em;")
        al.addWidget(title)

        head = QHBoxLayout()
        app_name = QLabel(f"<span style='color:#e7ecf7'>fzBGPTools</span>")
        app_name.setStyleSheet("font-size: 22px; font-weight: 800;")
        head.addWidget(app_name)
        head.addWidget(badge(f"v{__version__}", "blue"))
        head.addStretch()
        al.addLayout(head)

        desc = QLabel(__description__)
        desc.setStyleSheet("color: #9aa6c2; font-size: 12.5px;")
        desc.setWordWrap(True)
        al.addWidget(desc)

        meta = QGridLayout()
        meta.setSpacing(6)
        meta.addWidget(self._kv_label("Autor:"), 0, 0)
        meta.addWidget(QLabel(__author__), 0, 1)
        meta.addWidget(self._kv_label("Repositório:"), 1, 0)
        url = QLabel(f"<a href='{__url__}' style='color:#3da9fc'>{__url__}</a>")
        url.setOpenExternalLinks(True)
        meta.addWidget(url, 1, 1)
        meta.addWidget(self._kv_label("Python:"), 2, 0)
        meta.addWidget(QLabel(sys.version.split()[0]), 2, 1)
        meta.addWidget(self._kv_label("Plataforma:"), 3, 0)
        meta.addWidget(QLabel(sys.platform), 3, 1)
        al.addLayout(meta)

        layout.addWidget(about)
        layout.addStretch()

        self.update_db_size()

    def _kv_label(self, text):
        l = QLabel(text)
        l.setStyleSheet("color: #6b7693; font-weight: 600; font-size: 11px;")
        return l

    def update_db_size(self):
        try:
            if os.path.exists(self.db.db_path):
                size = os.path.getsize(self.db.db_path)
                if size < 1024 * 1024:
                    self.size_val.setText(f"{size / 1024:.2f} KB")
                else:
                    self.size_val.setText(f"{size / (1024*1024):.2f} MB")
        except Exception:
            self.size_val.setText("Erro ao ler")

    def backup_db(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Exportar Banco de Dados",
            f"fzbgptools-backup-v{__version__}.db", "SQLite Database (*.db)")
        if not path:
            return
        if not path.endswith(".db"):
            path += ".db"
        try:
            shutil.copy2(self.db.db_path, path)
            self.db.add_log("INFO", "Backup", f"Backup exportado: {path}")
            QMessageBox.information(self, "Sucesso", f"Backup salvo em\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao exportar: {e}")

    def restore_db(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Restaurar Backup", "", "SQLite Database (*.db)")
        if not path:
            return
        reply = QMessageBox.question(
            self, "Confirmar",
            "Restaurar o banco de dados substituirá TODOS os dados atuais. Continuar?",
            QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                shutil.copy2(path, self.db.db_path)
                self.db.init_db()
                self.db.add_log("INFO", "Backup", f"DB restaurado de {path}")
                QMessageBox.information(self, "Sucesso",
                    "DB restaurado. Reinicie a aplicação para garantir consistência.")
                self.update_db_size()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao restaurar: {e}")

    def reset_db(self):
        reply = QMessageBox.question(
            self, "Confirmar Reset",
            "Resetar o banco de dados para valores de fábrica? Todos os cadastros serão perdidos.",
            QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                if os.path.exists(self.db.db_path):
                    os.remove(self.db.db_path)
                self.db.init_db()
                self.db.add_log("INFO", "System", "DB resetado para padrão de fábrica.")
                QMessageBox.information(self, "Sucesso", "Banco de dados resetado.")
                self.update_db_size()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao resetar: {e}")
