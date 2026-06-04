"""Settings — DB backup/restore/reset + SMTP email configuration + Help + About panel."""
import os
import shutil
import sys
import smtplib
from email.mime.text import MIMEText

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
                               QFileDialog, QMessageBox, QGridLayout, QTabWidget, QLineEdit,
                               QSpinBox, QCheckBox, QFormLayout, QScrollArea)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from src.ui.widgets import page_header, badge
from src.version import __version__, __app_name__, __description__, __author__, __url__


class SmtpTestWorker(QThread):
    finished = pyqtSignal(bool, str)

    def __init__(self, host, port, user, pwd, ssl, to_email):
        super().__init__()
        self.host = host
        self.port = port
        self.user = user
        self.pwd = pwd
        self.ssl = ssl
        self.to_email = to_email

    def run(self):
        try:
            msg = MIMEText("Conectividade de alerta SMTP do fzBGPTools configurada com sucesso!")
            msg['Subject'] = "Teste de Alerta SMTP — fzBGPTools"
            msg['From'] = self.user or "alerta@fzgptools.local"
            msg['To'] = self.to_email

            if self.ssl:
                server = smtplib.SMTP_SSL(self.host, self.port, timeout=10)
            else:
                server = smtplib.SMTP(self.host, self.port, timeout=10)
                server.starttls()

            if self.user and self.pwd:
                server.login(self.user, self.pwd)

            server.sendmail(self.user or "alerta@fzgptools.local", [self.to_email], msg.as_string())
            server.quit()
            self.finished.emit(True, "E-mail de teste enviado com sucesso!")
        except Exception as e:
            self.finished.emit(False, str(e))


class SettingsScreen(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.smtp_worker = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        layout.addWidget(page_header(
            "System", "Settings",
            "Configurações gerais do sistema, SMTP de alertas, banco de dados local e ajuda."))

        self.tabs = QTabWidget()
        
        # 1. Tab Database
        self.tabs.addTab(self._build_db_tab(), "Banco de Dados")
        
        # 2. Tab SMTP Config
        self.tabs.addTab(self._build_smtp_tab(), "Configurações SMTP")
        
        # 3. Tab Help
        self.tabs.addTab(self._build_help_tab(), "Ajuda")
        
        # 4. Tab About
        self.tabs.addTab(self._build_about_tab(), "Sobre")

        layout.addWidget(self.tabs)
        self.update_db_size()

    # ─── DATABASE TAB ───
    def _build_db_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(16)

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

        lay.addWidget(db_card)
        lay.addStretch()
        return w

    # ─── SMTP TAB ───
    def _build_smtp_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(16)

        card = QFrame()
        card.setObjectName("Card")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(20, 18, 20, 18)
        cl.setSpacing(14)

        title = QLabel("CONFIGURAÇÃO DE EMAIL DE ALERTA (SMTP)")
        title.setStyleSheet("font-size: 11px; color: #6b7693; font-weight: 700; letter-spacing: 0.14em;")
        cl.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignLeft)

        self.smtp_host = QLineEdit()
        self.smtp_host.setPlaceholderText("ex: smtp.webstorage.com.br")
        
        self.smtp_port = QSpinBox()
        self.smtp_port.setRange(1, 65535)
        self.smtp_port.setValue(587)
        self.smtp_port.setStyleSheet("min-width: 100px;")

        self.smtp_user = QLineEdit()
        self.smtp_user.setPlaceholderText("ex: alerta@webstorage.com.br")

        self.smtp_pass = QLineEdit()
        self.smtp_pass.setEchoMode(QLineEdit.Password)
        self.smtp_pass.setPlaceholderText("senha do e-mail smtp")

        self.smtp_ssl = QCheckBox("Utilizar conexão criptografada SSL/TLS (Porta 465)")
        self.smtp_ssl.toggled.connect(self._on_ssl_toggled)

        self.smtp_to = QLineEdit()
        self.smtp_to.setPlaceholderText("ex: noc@webstorage.com.br")

        form.addRow(self._kv_label("Servidor SMTP:"), self.smtp_host)
        form.addRow(self._kv_label("Porta SMTP:"), self.smtp_port)
        form.addRow(self._kv_label("Usuário/Email:"), self.smtp_user)
        form.addRow(self._kv_label("Senha SMTP:"), self.smtp_pass)
        form.addRow("", self.smtp_ssl)
        form.addRow(self._kv_label("E-mail Destino:"), self.smtp_to)
        
        cl.addLayout(form)

        # Actions
        btn_lay = QHBoxLayout()
        save_btn = QPushButton("💾  Salvar SMTP")
        save_btn.setObjectName("BtnPrimary")
        save_btn.clicked.connect(self.save_smtp)
        
        test_btn = QPushButton("⚡  Testar Conexão")
        test_btn.setObjectName("Btn")
        test_btn.clicked.connect(self.test_smtp)

        self.smtp_status_lbl = QLabel("")
        self.smtp_status_lbl.setStyleSheet("font-size: 12px; color: #9aa6c2;")

        btn_lay.addWidget(save_btn)
        btn_lay.addWidget(test_btn)
        btn_lay.addWidget(self.smtp_status_lbl)
        btn_lay.addStretch()
        cl.addLayout(btn_lay)

        # Load values
        smtp_data = self.db.get_smtp_config()
        if smtp_data:
            shost, sport, suser, spass, sssl, sto = smtp_data
            self.smtp_host.setText(shost)
            self.smtp_port.setValue(sport or 587)
            self.smtp_user.setText(suser)
            self.smtp_pass.setText(spass)
            self.smtp_ssl.setChecked(bool(sssl))
            self.smtp_to.setText(sto)

        lay.addWidget(card)
        lay.addStretch()
        return w

    def _on_ssl_toggled(self, checked):
        if checked:
            self.smtp_port.setValue(465)
        else:
            self.smtp_port.setValue(587)

    def save_smtp(self):
        host = self.smtp_host.text().strip()
        port = self.smtp_port.value()
        user = self.smtp_user.text().strip()
        password = self.smtp_pass.text()
        ssl = self.smtp_ssl.isChecked()
        to_email = self.smtp_to.text().strip()

        if not host or not to_email:
            QMessageBox.warning(self, "Aviso", "Servidor SMTP e E-mail Destino são obrigatórios.")
            return

        self.db.save_smtp_config(host, port, user, password, ssl, to_email)
        self.db.add_log("INFO", "SMTP", "Configurações de alerta SMTP atualizadas.")
        QMessageBox.information(self, "Sucesso", "Configurações de alerta SMTP salvas com sucesso.")

    def test_smtp(self):
        host = self.smtp_host.text().strip()
        port = self.smtp_port.value()
        user = self.smtp_user.text().strip()
        password = self.smtp_pass.text()
        ssl = self.smtp_ssl.isChecked()
        to_email = self.smtp_to.text().strip()

        if not host or not to_email:
            QMessageBox.warning(self, "Aviso", "Preencha o servidor e o e-mail de destino para testar.")
            return

        self.smtp_status_lbl.setText("Enviando e-mail de teste...")
        self.smtp_status_lbl.setStyleSheet("color: #fbbf24;")
        
        self.smtp_worker = SmtpTestWorker(host, port, user, password, ssl, to_email)
        self.smtp_worker.finished.connect(self._on_smtp_test_finished)
        self.smtp_worker.start()

    def _on_smtp_test_finished(self, success, msg):
        if success:
            self.smtp_status_lbl.setText("✓ Teste enviado com sucesso!")
            self.smtp_status_lbl.setStyleSheet("color: #4ade80;")
            QMessageBox.information(self, "Sucesso", msg)
        else:
            self.smtp_status_lbl.setText("✗ Falha no envio de teste.")
            self.smtp_status_lbl.setStyleSheet("color: #ff5c7a;")
            QMessageBox.critical(self, "Falha de Conectividade", f"Erro ao enviar e-mail:\n{msg}")

    # ─── HELP TAB ───
    def _build_help_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(10)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background-color: transparent;")

        content = QFrame()
        content.setObjectName("Card")
        content.setStyleSheet("background-color: rgba(20, 27, 48, 0.55); border: 1px solid rgba(110, 140, 220, 0.14); border-radius: 12px;")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(20, 20, 20, 20)
        cl.setSpacing(12)

        title = QLabel("INSTRUÇÕES BÁSICAS DE USO")
        title.setStyleSheet("font-size: 12px; color: #3da9fc; font-weight: bold; letter-spacing: 0.1em; margin-bottom: 8px;")
        cl.addWidget(title)

        help_text = QLabel(
            "<h3 style='color:#e7ecf7;'>1. Mapa de Peering BGP</h3>"
            "<p style='color:#9aa6c2; line-height: 1.4; font-size:12.5px;'>"
            "O <b>Dashboard</b> apresenta uma representação gráfica da topologia de rotas BGP. "
            "As sessões cadastradas no <b>ASN Manager</b> são renderizadas em tempo real em formato circular ao redor do seu AS próprio (marcado como tipo 'Próprio' / 'self'). "
            "A cor e as informações das linhas tracejadas refletem o tipo de peer (Trânsito BGP, Peer direto ou conexões de IX/PTT)."
            "</p>"
            "<h3 style='color:#e7ecf7;'>2. Gerenciador de ASNs e Hosts</h3>"
            "<p style='color:#9aa6c2; line-height: 1.4; font-size:12.5px;'>"
            "Utilize a barra superior para adicionar ativos globalmente ou acesse os painéis específicos:<br>"
            "&nbsp;&nbsp;• <b>ASN Manager</b>: Cadastro e controle de ASNs parceiros, trânsitos e destinos, permitindo múltiplos prefixos em bloco (formato CIDR).<br>"
            "&nbsp;&nbsp;• <b>Host Manager</b>: Inventário de roteadores, switches, firewalls e servidores locais e de borda, incluindo portas e credenciais para conexões automáticas."
            "</p>"
            "<h3 style='color:#e7ecf7;'>3. Diagnóstico e Acesso CLI</h3>"
            "<p style='color:#9aa6c2; line-height: 1.4; font-size:12.5px;'>"
            "No painel de <b>Network Tools</b> é possível disparar ferramentas rápidas como <i>Ping</i> e <i>Traceroute</i> "
            "com visualização analítica inteligente de saltos e trânsitos em IX.br.<br>"
            "Os terminais <i>SSH</i> e <i>Telnet</i> permitem acesso direto via CLI em tempo real aos hosts cadastrados, bastando selecionar o host e clicar em Conectar."
            "</p>"
            "<h3 style='color:#e7ecf7;'>4. Alertas e Logs do Sistema</h3>"
            "<p style='color:#9aa6c2; line-height: 1.4; font-size:12.5px;'>"
            "Alertas ativos geram notificações visuais na barra superior e no dashboard (com detalhes dos incidentes críticos como prepend e flapping). "
            "Eventos de sistema são registrados no <b>Console de Logs</b>, de onde podem ser monitorados e filtrados por nível de severidade (INFO, WARN, ERROR)."
            "</p>"
        )
        help_text.setWordWrap(True)
        help_text.setTextFormat(Qt.RichText)
        cl.addWidget(help_text)
        cl.addStretch()

        scroll.setWidget(content)
        lay.addWidget(scroll)
        return w

    # ─── ABOUT TAB ───
    def _build_about_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(16)

        about = QFrame()
        about.setObjectName("Card")
        al = QVBoxLayout(about)
        al.setContentsMargins(20, 18, 20, 18)
        al.setSpacing(10)

        title = QLabel("INFORMAÇÕES DO SISTEMA")
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

        lay.addWidget(about)
        lay.addStretch()
        return w

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
