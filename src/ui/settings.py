import os
import shutil
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QFileDialog, QMessageBox, QGridLayout
from PyQt5.QtCore import Qt

class SettingsScreen(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Header Area
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title_block = QFrame()
        title_layout = QVBoxLayout(title_block)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(4)
        
        title_lbl = QLabel("Configurações do Sistema")
        title_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #3da9fc;")
        sub_lbl = QLabel("Gerenciamento de banco de dados, backups e configurações gerais.")
        sub_lbl.setStyleSheet("font-size: 12px; color: #9aa6c2;")
        title_layout.addWidget(title_lbl)
        title_layout.addWidget(sub_lbl)
        
        header_layout.addWidget(title_block)
        layout.addWidget(header_frame)
        
        # Settings Layout Card
        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 18, 18, 18)
        card_layout.setSpacing(16)
        
        # DB Info Section
        db_title = QLabel("Banco de Dados Local (SQLite)")
        db_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #3da9fc;")
        card_layout.addWidget(db_title)
        
        info_grid = QGridLayout()
        info_grid.setSpacing(10)
        
        self.path_lbl = QLabel("Caminho do Arquivo:")
        self.path_lbl.setStyleSheet("color: #6b7693; font-weight: bold;")
        self.path_val = QLabel(self.db.db_path)
        self.path_val.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        self.size_lbl = QLabel("Tamanho do Arquivo:")
        self.size_lbl.setStyleSheet("color: #6b7693; font-weight: bold;")
        self.size_val = QLabel("0 KB")
        
        info_grid.addWidget(self.path_lbl, 0, 0)
        info_grid.addWidget(self.path_val, 0, 1)
        info_grid.addWidget(self.size_lbl, 1, 0)
        info_grid.addWidget(self.size_val, 1, 1)
        card_layout.addLayout(info_grid)
        
        # Action Buttons
        btn_layout = QHBoxLayout()
        backup_btn = QPushButton("Fazer Backup (Exportar .db)")
        backup_btn.setObjectName("BtnPrimary")
        backup_btn.clicked.connect(self.backup_db)
        
        restore_btn = QPushButton("Restaurar Backup (Importar .db)")
        restore_btn.setObjectName("Btn")
        restore_btn.clicked.connect(self.restore_db)
        
        reset_btn = QPushButton("Resetar Banco de Dados")
        reset_btn.setObjectName("BtnDanger")
        reset_btn.clicked.connect(self.reset_db)
        
        btn_layout.addWidget(backup_btn)
        btn_layout.addWidget(restore_btn)
        btn_layout.addWidget(reset_btn)
        card_layout.addLayout(btn_layout)
        
        layout.addWidget(card)
        layout.addStretch()
        
        self.update_db_size()

    def update_db_size(self):
        try:
            if os.path.exists(self.db.db_path):
                size_bytes = os.path.getsize(self.db.db_path)
                self.size_val.setText(f"{size_bytes / 1024:.2f} KB")
        except Exception:
            self.size_val.setText("Erro ao ler tamanho")

    def backup_db(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Exportar Banco de Dados", "", "SQLite Database (*.db)", options=options)
        if file_path:
            try:
                # Add extension if not typed
                if not file_path.endswith(".db"):
                    file_path += ".db"
                shutil.copy2(self.db.db_path, file_path)
                self.db.add_log("INFO", "Backup", f"Backup exportado para {file_path}")
                QMessageBox.information(self, "Sucesso", "Backup exportado com sucesso!")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao exportar backup: {e}")

    def restore_db(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecionar Arquivo de Backup", "", "SQLite Database (*.db)", options=options)
        if file_path:
            reply = QMessageBox.question(self, "Confirmar Restauração", 
                                         "Restaurar o banco de dados substituirá todas as configurações e registros atuais. Continuar?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                try:
                    shutil.copy2(file_path, self.db.db_path)
                    self.db.init_db() # re-init if schema is old
                    self.db.add_log("INFO", "Backup", f"Banco de dados restaurado de {file_path}")
                    QMessageBox.information(self, "Sucesso", "Banco de dados restaurado com sucesso! Reinicie o aplicativo para aplicar todas as mudanças.")
                    self.update_db_size()
                except Exception as e:
                    QMessageBox.critical(self, "Erro", f"Falha ao restaurar backup: {e}")

    def reset_db(self):
        reply = QMessageBox.question(self, "Confirmar Reset", 
                                     "Deseja resetar o banco de dados para os valores padrão de fábrica?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                if os.path.exists(self.db.db_path):
                    os.remove(self.db.db_path)
                self.db.init_db()
                self.db.add_log("INFO", "System", "Banco de dados resetado para as configurações de fábrica.")
                QMessageBox.information(self, "Sucesso", "Banco de dados resetado com sucesso!")
                self.update_db_size()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao resetar banco de dados: {e}")
