from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QTabWidget, QLineEdit, QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QTextCursor, QFont
from src.engine.ping import PingRunner
from src.engine.traceroute import TracerouteRunner
from src.engine.ssh_client import SSHShellWorker
from src.engine.telnet_client import TelnetShellWorker

class TerminalEdit(QTextEdit):
    key_pressed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Terminal")
        self.setReadOnly(True)
        # Set monospace font
        self.setFont(QFont("JetBrains Mono", 10))

    def keyPressEvent(self, event):
        text = event.text()
        key = event.key()
        
        if key == Qt.Key_Return or key == Qt.Key_Enter:
            self.key_pressed.emit("\r")
        elif key == Qt.Key_Backspace:
            # Send character delete (DEL)
            self.key_pressed.emit("\x08")
        elif key == Qt.Key_Escape:
            self.key_pressed.emit("\x1b")
        elif key == Qt.Key_Tab:
            self.key_pressed.emit("\t")
        elif text:
            self.key_pressed.emit(text)

class NetworkToolsScreen(QWidget):
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
        
        title_lbl = QLabel("Diagnósticos de Rede")
        title_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #3da9fc;")
        sub_lbl = QLabel("Execute pings, traceroutes e acesse dispositivos via terminal SSH/Telnet.")
        sub_lbl.setStyleSheet("font-size: 12px; color: #9aa6c2;")
        title_layout.addWidget(title_lbl)
        title_layout.addWidget(sub_lbl)
        
        header_layout.addWidget(title_block)
        layout.addWidget(header_frame)
        
        # Tabs
        self.tabs = QTabWidget()
        
        # Tab 1: Ping
        self.init_ping_tab()
        # Tab 2: Traceroute
        self.init_trace_tab()
        # Tab 3: SSH Terminal
        self.init_ssh_tab()
        # Tab 4: Telnet Terminal
        self.init_telnet_tab()
        
        layout.addWidget(self.tabs)

    def init_ping_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        
        controls = QHBoxLayout()
        self.ping_input = QLineEdit()
        self.ping_input.setPlaceholderText("Endereço IP ou Hostname para Ping (ex: 8.8.8.8)")
        self.ping_btn = QPushButton("Executar Ping")
        self.ping_btn.setObjectName("BtnPrimary")
        self.ping_btn.clicked.connect(self.toggle_ping)
        
        controls.addWidget(self.ping_input, 4)
        controls.addWidget(self.ping_btn, 1)
        layout.addLayout(controls)
        
        self.ping_terminal = QTextEdit()
        self.ping_terminal.setObjectName("Terminal")
        self.ping_terminal.setReadOnly(True)
        layout.addWidget(self.ping_terminal)
        
        self.tabs.addTab(tab, "Ping")
        
        # Ping runner setup
        self.ping_runner = PingRunner(self)
        self.ping_runner.output_received.connect(self.on_ping_output)
        self.ping_runner.finished.connect(self.on_ping_finished)
        self.ping_active = False

    def toggle_ping(self):
        if self.ping_active:
            self.ping_runner.stop()
            self.ping_btn.setText("Executar Ping")
            self.ping_active = False
        else:
            host = self.ping_input.text().strip()
            if not host:
                QMessageBox.warning(self, "Aviso", "Insira um host válido!")
                return
            self.ping_terminal.clear()
            self.ping_runner.start_ping(host)
            self.ping_btn.setText("Parar")
            self.ping_active = True

    def on_ping_output(self, text):
        self.ping_terminal.insertPlainText(text)
        self.ping_terminal.moveCursor(QTextCursor.End)

    def on_ping_finished(self, exit_code):
        self.ping_btn.setText("Executar Ping")
        self.ping_active = False
        self.ping_terminal.insertPlainText(f"\n--- Fim do Ping (Exit code: {exit_code}) ---\n")

    def init_trace_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        
        controls = QHBoxLayout()
        self.trace_input = QLineEdit()
        self.trace_input.setPlaceholderText("Endereço IP ou Hostname para Traceroute (ex: 8.8.8.8)")
        self.trace_btn = QPushButton("Executar Traceroute")
        self.trace_btn.setObjectName("BtnPrimary")
        self.trace_btn.clicked.connect(self.toggle_trace)
        
        controls.addWidget(self.trace_input, 4)
        controls.addWidget(self.trace_btn, 1)
        layout.addLayout(controls)
        
        self.trace_table = QTableWidget(0, 7)
        self.trace_table.setHorizontalHeaderLabels(["Hop", "IP Address", "Hostname", "ASN", "AS Nome", "Latência (ms)", "Tipo"])
        self.trace_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.trace_table.verticalHeader().setVisible(False)
        layout.addWidget(self.trace_table)
        
        self.tabs.addTab(tab, "Traceroute")
        
        # Traceroute setup
        self.trace_runner = TracerouteRunner(self)
        self.trace_runner.hop_received.connect(self.on_trace_hop)
        self.trace_runner.finished.connect(self.on_trace_finished)
        self.trace_active = False

    def toggle_trace(self):
        if self.trace_active:
            self.trace_runner.stop()
            self.trace_btn.setText("Executar Traceroute")
            self.trace_active = False
        else:
            host = self.trace_input.text().strip()
            if not host:
                QMessageBox.warning(self, "Aviso", "Insira um host válido!")
                return
            self.trace_table.setRowCount(0)
            self.trace_runner.start_traceroute(host)
            self.trace_btn.setText("Parar")
            self.trace_active = True

    def on_trace_hop(self, hop_num, ip, host, asn, as_name, ms, is_ix):
        row = self.trace_table.rowCount()
        self.trace_table.insertRow(row)
        self.trace_table.setItem(row, 0, QTableWidgetItem(str(hop_num)))
        self.trace_table.setItem(row, 1, QTableWidgetItem(ip))
        self.trace_table.setItem(row, 2, QTableWidgetItem(host))
        
        asn_item = QTableWidgetItem(asn)
        if is_ix:
            asn_item.setForeground(QColor("#a18cff"))
        else:
            asn_item.setForeground(QColor("#3da9fc"))
        self.trace_table.setItem(row, 3, asn_item)
        
        self.trace_table.setItem(row, 4, QTableWidgetItem(as_name))
        self.trace_table.setItem(row, 5, QTableWidgetItem(f"{ms:.2f}" if ms > 0 else "*"))
        
        type_item = QTableWidgetItem("IX/PTT" if is_ix else "Trânsito")
        if is_ix:
            type_item.setForeground(QColor("#a18cff"))
        self.trace_table.setItem(row, 6, type_item)

    def on_trace_finished(self, exit_code):
        self.trace_btn.setText("Executar Traceroute")
        self.trace_active = False

    def init_ssh_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        
        controls = QHBoxLayout()
        self.ssh_hosts_cb = QComboBox()
        self.refresh_ssh_hosts()
        
        self.ssh_btn = QPushButton("Conectar SSH")
        self.ssh_btn.setObjectName("BtnPrimary")
        self.ssh_btn.clicked.connect(self.toggle_ssh)
        
        controls.addWidget(self.ssh_hosts_cb, 4)
        controls.addWidget(self.ssh_btn, 1)
        layout.addLayout(controls)
        
        self.ssh_terminal = TerminalEdit()
        self.ssh_terminal.key_pressed.connect(self.on_ssh_key)
        layout.addWidget(self.ssh_terminal)
        
        self.tabs.addTab(tab, "Terminal SSH")
        
        self.ssh_worker = None
        self.ssh_active = False

    def refresh_ssh_hosts(self):
        self.ssh_hosts_cb.clear()
        hosts = self.db.get_hosts()
        for ip, hostname, p_ssh, p_tel, username, password, type_, mfg, status in hosts:
            self.ssh_hosts_cb.addItem(f"{hostname} ({ip}) - SSH:{p_ssh}", ip)

    def toggle_ssh(self):
        if self.ssh_active:
            if self.ssh_worker:
                self.ssh_worker.stop()
            self.ssh_btn.setText("Conectar SSH")
            self.ssh_active = False
        else:
            ip = self.ssh_hosts_cb.currentData()
            if not ip:
                QMessageBox.warning(self, "Aviso", "Nenhum host cadastrado!")
                return
            
            # Fetch host details from DB
            hosts = self.db.get_hosts()
            host_data = next((h for h in hosts if h[0] == ip), None)
            if not host_data:
                return
            
            _, hostname, p_ssh, _, username, password, _, _, _ = host_data
            
            self.ssh_terminal.clear()
            self.ssh_terminal.insertPlainText(f"Conectando a {hostname} ({ip})...\n")
            
            self.ssh_worker = SSHShellWorker(ip, p_ssh, username, password)
            self.ssh_worker.stdout_received.connect(self.on_ssh_stdout)
            self.ssh_worker.connected.connect(self.on_ssh_connected)
            self.ssh_worker.connection_failed.connect(self.on_ssh_failed)
            self.ssh_worker.finished.connect(self.on_ssh_finished)
            self.ssh_worker.start()
            self.ssh_btn.setText("Desconectar")
            self.ssh_active = True

    def on_ssh_stdout(self, text):
        self.ssh_terminal.insertPlainText(text)
        self.ssh_terminal.moveCursor(QTextCursor.End)

    def on_ssh_connected(self):
        self.ssh_terminal.insertPlainText("Conectado com sucesso!\n\n")

    def on_ssh_failed(self, error):
        self.ssh_terminal.insertPlainText(f"\nFalha na conexão: {error}\n")
        self.ssh_btn.setText("Conectar SSH")
        self.ssh_active = False

    def on_ssh_finished(self):
        self.ssh_terminal.insertPlainText("\nConexão SSH encerrada.\n")
        self.ssh_btn.setText("Conectar SSH")
        self.ssh_active = False

    def on_ssh_key(self, char):
        if self.ssh_active and self.ssh_worker:
            self.ssh_worker.send_input(char)

    def init_telnet_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        
        controls = QHBoxLayout()
        self.telnet_hosts_cb = QComboBox()
        self.refresh_telnet_hosts()
        
        self.telnet_btn = QPushButton("Conectar Telnet")
        self.telnet_btn.setObjectName("BtnPrimary")
        self.telnet_btn.clicked.connect(self.toggle_telnet)
        
        controls.addWidget(self.telnet_hosts_cb, 4)
        controls.addWidget(self.telnet_btn, 1)
        layout.addLayout(controls)
        
        self.telnet_terminal = TerminalEdit()
        self.telnet_terminal.key_pressed.connect(self.on_telnet_key)
        layout.addWidget(self.telnet_terminal)
        
        self.tabs.addTab(tab, "Terminal Telnet")
        
        self.telnet_worker = None
        self.telnet_active = False

    def refresh_telnet_hosts(self):
        self.telnet_hosts_cb.clear()
        hosts = self.db.get_hosts()
        for ip, hostname, p_ssh, p_tel, username, password, type_, mfg, status in hosts:
            self.telnet_hosts_cb.addItem(f"{hostname} ({ip}) - Telnet:{p_tel}", ip)

    def toggle_telnet(self):
        if self.telnet_active:
            if self.telnet_worker:
                self.telnet_worker.stop()
            self.telnet_btn.setText("Conectar Telnet")
            self.telnet_active = False
        else:
            ip = self.telnet_hosts_cb.currentData()
            if not ip:
                QMessageBox.warning(self, "Aviso", "Nenhum host cadastrado!")
                return
            
            # Fetch host details from DB
            hosts = self.db.get_hosts()
            host_data = next((h for h in hosts if h[0] == ip), None)
            if not host_data:
                return
            
            _, hostname, _, p_tel, username, password, _, _, _ = host_data
            
            self.telnet_terminal.clear()
            self.telnet_terminal.insertPlainText(f"Conectando via Telnet a {hostname} ({ip})...\n")
            
            self.telnet_worker = TelnetShellWorker(ip, p_tel, username, password)
            self.telnet_worker.stdout_received.connect(self.on_telnet_stdout)
            self.telnet_worker.connected.connect(self.on_telnet_connected)
            self.telnet_worker.connection_failed.connect(self.on_telnet_failed)
            self.telnet_worker.finished.connect(self.on_telnet_finished)
            self.telnet_worker.start()
            self.telnet_btn.setText("Desconectar")
            self.telnet_active = True

    def on_telnet_stdout(self, text):
        self.telnet_terminal.insertPlainText(text)
        self.telnet_terminal.moveCursor(QTextCursor.End)

    def on_telnet_connected(self):
        self.telnet_terminal.insertPlainText("Conectado com sucesso!\n\n")

    def on_telnet_failed(self, error):
        self.telnet_terminal.insertPlainText(f"\nFalha na conexão Telnet: {error}\n")
        self.telnet_btn.setText("Conectar Telnet")
        self.telnet_active = False

    def on_telnet_finished(self):
        self.telnet_terminal.insertPlainText("\nConexão Telnet encerrada.\n")
        self.telnet_btn.setText("Conectar Telnet")
        self.telnet_active = False

    def on_telnet_key(self, char):
        if self.telnet_active and self.telnet_worker:
            self.telnet_worker.send_input(char)

    def refresh_lists(self):
        self.refresh_ssh_hosts()
        self.refresh_telnet_hosts()
