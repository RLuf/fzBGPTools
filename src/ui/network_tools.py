"""
Network Tools — Ping, Traceroute, SSH e Telnet.
Saídas com formatação tipo terminal (colored lines, IX/PTT badges, stats cards).
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
                              QTabWidget, QLineEdit, QTextEdit, QTableWidget, QTableWidgetItem,
                              QHeaderView, QComboBox, QMessageBox, QSpinBox)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QColor, QTextCursor, QFont, QTextCharFormat

from src.engine.ping import PingRunner
from src.engine.traceroute import TracerouteRunner
from src.engine.ssh_client import SSHShellWorker
from src.engine.telnet_client import TelnetShellWorker
from src.ui.widgets import badge, page_header, terminal_card, stat_card


# Cores para classes de linha no terminal
LINE_COLORS = {
    "ok":    "#4ade80",
    "info":  "#7ec3ff",
    "warn":  "#fbbf24",
    "err":   "#ff5c7a",
    "dim":   "#6b7693",
    "stats": "#21d4fd",
}


class TerminalEdit(QTextEdit):
    """QTextEdit com suporte a injeção de linhas coloridas."""
    key_pressed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Terminal")
        self.setReadOnly(True)
        self.setFont(QFont("JetBrains Mono", 10))
        self._cursor_visible = False

    def append_line(self, text, kind="dim"):
        """Adiciona uma linha colorida conforme o kind."""
        color = LINE_COLORS.get(kind, "#b6f3c8")
        weight = 700 if kind in ("ok", "stats", "err") else 400
        # Escapar HTML básico
        safe = (text or "")
        safe = (safe.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    .replace("  ", "&nbsp;&nbsp;"))
        self.append(f"<span style='color:{color};font-weight:{weight}'>{safe}</span>")
        self.moveCursor(QTextCursor.End)

    def append_raw(self, text):
        """Append raw text (para streams SSH/Telnet que já têm controle de cores)."""
        self.insertPlainText(text)
        self.moveCursor(QTextCursor.End)

    def keyPressEvent(self, event):
        text = event.text()
        key = event.key()
        if key == Qt.Key_Return or key == Qt.Key_Enter:
            self.key_pressed.emit("\r")
        elif key == Qt.Key_Backspace:
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
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        layout.addWidget(page_header(
            "Network", "Tools",
            "Diagnóstico de conectividade, latência e acesso CLI remoto."))

        self.tabs = QTabWidget()
        self._init_ping_tab()
        self._init_trace_tab()
        self._init_ssh_tab()
        self._init_telnet_tab()
        layout.addWidget(self.tabs)

    # ═════════════════════ PING ═════════════════════
    def _init_ping_tab(self):
        tab = QWidget()
        lay = QVBoxLayout(tab)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(14)

        # Linha de controles
        ctrl = QHBoxLayout()
        ctrl.setSpacing(10)
        self.ping_input = QLineEdit()
        self.ping_input.setPlaceholderText("IP ou hostname (ex: 8.8.8.8)")
        self.ping_input.returnPressed.connect(self.toggle_ping)

        self.ping_count = QComboBox()
        for n, lab in [(4, "4 pacotes"), (7, "7 pacotes"), (10, "10 pacotes"),
                       (30, "30 pacotes"), (0, "Contínuo")]:
            self.ping_count.addItem(lab, n)
        self.ping_count.setCurrentIndex(1)

        self.ping_btn = QPushButton("▶  Executar Ping")
        self.ping_btn.setObjectName("BtnPrimary")
        self.ping_btn.clicked.connect(self.toggle_ping)

        ctrl.addWidget(self.ping_input, 4)
        ctrl.addWidget(self.ping_count, 1)
        ctrl.addWidget(self.ping_btn, 1)
        lay.addLayout(ctrl)

        # Stats cards row (loss, min, avg, max)
        stats_row = QHBoxLayout()
        stats_row.setSpacing(10)
        self.stat_loss = stat_card("Perda", "—")
        self.stat_min  = stat_card("RTT mín", "—")
        self.stat_avg  = stat_card("RTT avg", "—")
        self.stat_max  = stat_card("RTT máx", "—")
        for c in (self.stat_loss, self.stat_min, self.stat_avg, self.stat_max):
            stats_row.addWidget(c)
        lay.addLayout(stats_row)

        # Terminal card
        card, self.ping_title, self.ping_status, body, body_lay = terminal_card("~/ping")
        self.ping_terminal = TerminalEdit()
        self.ping_terminal.setStyleSheet("border: none; border-radius: 0; "
                                          "border-top-left-radius: 0; border-top-right-radius: 0;"
                                          "border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;")
        body_lay.addWidget(self.ping_terminal)
        lay.addWidget(card, 1)

        self.tabs.addTab(tab, "Ping")

        # Runner
        self.ping_runner = PingRunner(self)
        self.ping_runner.line_event.connect(self._on_ping_line)
        self.ping_runner.stats.connect(self._on_ping_stats)
        self.ping_runner.finished.connect(self._on_ping_finished)
        self.ping_active = False

    def toggle_ping(self):
        if self.ping_active:
            self.ping_runner.stop()
            return
        host = self.ping_input.text().strip()
        if not host:
            QMessageBox.warning(self, "Aviso", "Insira um host válido.")
            return
        count = self.ping_count.currentData()
        self.ping_terminal.clear()
        for c in (self.stat_loss, self.stat_min, self.stat_avg, self.stat_max):
            c.value_label.setText("—")
        self.ping_title.setText(f"~/ping {host}")
        self.ping_status.setText("executando")
        self.ping_status.setProperty("kind", "green")
        self.ping_status.style().unpolish(self.ping_status); self.ping_status.style().polish(self.ping_status)
        self.ping_btn.setText("◼  Parar")
        self.ping_active = True
        if count == 0:
            self.ping_runner.start_continuous(host)
        else:
            self.ping_runner.start_ping(host, count=count)

    def _on_ping_line(self, kind, text):
        self.ping_terminal.append_line(text, kind)

    def _on_ping_stats(self, tx, rx, loss, mn, av, mx):
        if tx:
            self.stat_loss.value_label.setText(f"{loss:.1f}%")
            self.stat_loss.value_label.setStyleSheet(
                "color:" + ("#4ade80" if loss < 1 else "#fbbf24" if loss < 25 else "#ff5c7a") +
                "; font-size:26px; font-weight:800;")
        else:
            self.stat_loss.value_label.setText(f"{loss:.1f}%")
        self.stat_min.value_label.setText(f"{mn:.1f} ms")
        self.stat_avg.value_label.setText(f"{av:.1f} ms")
        self.stat_max.value_label.setText(f"{mx:.1f} ms")

    def _on_ping_finished(self, exit_code):
        self.ping_active = False
        self.ping_btn.setText("▶  Executar Ping")
        kind = "green" if exit_code == 0 else "red"
        self.ping_status.setText("concluído" if exit_code == 0 else "falhou")
        self.ping_status.setProperty("kind", kind)
        self.ping_status.style().unpolish(self.ping_status); self.ping_status.style().polish(self.ping_status)
        self.ping_terminal.append_line(f"--- Fim do ping (exit code: {exit_code}) ---", "dim")

    # ═════════════════════ TRACEROUTE ═════════════════════
    def _init_trace_tab(self):
        tab = QWidget()
        lay = QVBoxLayout(tab)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(14)

        ctrl = QHBoxLayout()
        ctrl.setSpacing(10)
        self.trace_input = QLineEdit()
        self.trace_input.setPlaceholderText("IP ou hostname destino")
        self.trace_input.returnPressed.connect(self.toggle_trace)

        self.trace_proto = QComboBox()
        self.trace_proto.addItems(["ICMP", "UDP", "TCP/443"])

        self.trace_btn = QPushButton("▶  Executar Traceroute")
        self.trace_btn.setObjectName("BtnPrimary")
        self.trace_btn.clicked.connect(self.toggle_trace)

        ctrl.addWidget(self.trace_input, 4)
        ctrl.addWidget(self.trace_proto, 1)
        ctrl.addWidget(self.trace_btn, 1)
        lay.addLayout(ctrl)

        # Status row
        status_row = QHBoxLayout()
        self.trace_status_text = QLabel("Aguardando execução.")
        self.trace_status_text.setStyleSheet("color: #6b7693; font-size: 12px;")
        self.trace_hop_count = badge("0 hops", "gray")
        self.trace_ix_count  = badge("0 IX/PTT", "purple")
        status_row.addWidget(self.trace_status_text)
        status_row.addStretch()
        status_row.addWidget(self.trace_hop_count)
        status_row.addWidget(self.trace_ix_count)
        lay.addLayout(status_row)

        # Tabela
        self.trace_table = QTableWidget(0, 7)
        self.trace_table.setHorizontalHeaderLabels(
            ["#", "IP Address", "Hostname", "ASN", "AS Nome", "RTT (ms)", "Tipo"])
        h = self.trace_table.horizontalHeader()
        h.setSectionResizeMode(QHeaderView.Stretch)
        h.setSectionResizeMode(0, QHeaderView.Fixed); self.trace_table.setColumnWidth(0, 46)
        h.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.trace_table.verticalHeader().setVisible(False)
        self.trace_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.trace_table.setAlternatingRowColors(False)
        lay.addWidget(self.trace_table, 1)

        self.tabs.addTab(tab, "Traceroute")

        # Runner
        self.trace_runner = TracerouteRunner(self)
        self.trace_runner.hop_received.connect(self._on_trace_hop)
        self.trace_runner.finished.connect(self._on_trace_finished)
        self.trace_active = False

    def toggle_trace(self):
        if self.trace_active:
            self.trace_runner.stop()
            return
        host = self.trace_input.text().strip()
        if not host:
            QMessageBox.warning(self, "Aviso", "Insira um host válido.")
            return
        self.trace_table.setRowCount(0)
        self.trace_status_text.setText(f"Sondando hops até {host}...")
        self.trace_hop_count.setText("0 hops")
        self.trace_ix_count.setText("0 IX/PTT")
        self.trace_btn.setText("◼  Parar")
        self.trace_active = True
        self._ix_count = 0
        self.trace_runner.start_traceroute(host)

    def _on_trace_hop(self, hop_num, ip, host, asn, as_name, ms, is_ix):
        row = self.trace_table.rowCount()
        self.trace_table.insertRow(row)

        # # hop
        n_item = QTableWidgetItem(str(hop_num))
        n_item.setForeground(QColor("#6b7693"))
        n_item.setTextAlignment(Qt.AlignCenter)
        self.trace_table.setItem(row, 0, n_item)

        # IP
        ip_item = QTableWidgetItem(ip)
        ip_item.setFont(QFont("JetBrains Mono", 10))
        if ip.startswith("*"):
            ip_item.setForeground(QColor("#6b7693"))
        self.trace_table.setItem(row, 1, ip_item)

        # Hostname
        host_item = QTableWidgetItem(host)
        host_item.setForeground(QColor("#9aa6c2"))
        self.trace_table.setItem(row, 2, host_item)

        # ASN
        asn_item = QTableWidgetItem(asn)
        asn_item.setFont(QFont("JetBrains Mono", 10))
        if is_ix:
            asn_item.setForeground(QColor("#a18cff"))
        elif "UNKNOWN" in asn or "LOCAL" in asn:
            asn_item.setForeground(QColor("#6b7693"))
        else:
            asn_item.setForeground(QColor("#3da9fc"))
        self.trace_table.setItem(row, 3, asn_item)

        # AS Name
        name_item = QTableWidgetItem(as_name)
        if is_ix:
            name_item.setForeground(QColor("#a18cff"))
        self.trace_table.setItem(row, 4, name_item)

        # RTT
        rtt_text = f"{ms:.2f}" if ms > 0 else "* * *"
        rtt_item = QTableWidgetItem(rtt_text)
        rtt_item.setFont(QFont("JetBrains Mono", 10))
        rtt_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        if ms <= 0:
            rtt_item.setForeground(QColor("#6b7693"))
        elif ms < 5:
            rtt_item.setForeground(QColor("#4ade80"))
        elif ms < 50:
            rtt_item.setForeground(QColor("#fbbf24"))
        else:
            rtt_item.setForeground(QColor("#ff5c7a"))
        self.trace_table.setItem(row, 5, rtt_item)

        # Tipo
        type_text = "IX/PTT" if is_ix else "Trânsito" if "UNKNOWN" not in asn else "—"
        type_item = QTableWidgetItem(type_text)
        type_item.setTextAlignment(Qt.AlignCenter)
        if is_ix:
            type_item.setForeground(QColor("#a18cff"))
            type_item.setFont(QFont("Inter", 9, QFont.Bold))
            self._ix_count += 1
        elif type_text == "Trânsito":
            type_item.setForeground(QColor("#9aa6c2"))
        else:
            type_item.setForeground(QColor("#6b7693"))
        self.trace_table.setItem(row, 6, type_item)

        self.trace_hop_count.setText(f"{self.trace_table.rowCount()} hops")
        self.trace_ix_count.setText(f"{self._ix_count} IX/PTT")

    def _on_trace_finished(self, exit_code):
        self.trace_active = False
        self.trace_btn.setText("▶  Executar Traceroute")
        self.trace_status_text.setText(
            f"Traceroute concluído ({self.trace_table.rowCount()} hops, "
            f"{self._ix_count} via IX/PTT).")

    # ═════════════════════ SSH / Telnet ═════════════════════
    def _init_ssh_tab(self):
        tab, *rest = self._build_shell_tab(is_ssh=True)
        self.tabs.addTab(tab, "Terminal SSH")
        (self.ssh_hosts_cb, self.ssh_btn, self.ssh_terminal,
         self.ssh_status, self.ssh_title) = rest
        self.ssh_worker = None
        self.ssh_active = False
        self.refresh_ssh_hosts()
        self.ssh_terminal.key_pressed.connect(self._on_ssh_key)

    def _init_telnet_tab(self):
        tab, *rest = self._build_shell_tab(is_ssh=False)
        self.tabs.addTab(tab, "Terminal Telnet")
        (self.telnet_hosts_cb, self.telnet_btn, self.telnet_terminal,
         self.telnet_status, self.telnet_title) = rest
        self.telnet_worker = None
        self.telnet_active = False
        self.refresh_telnet_hosts()
        self.telnet_terminal.key_pressed.connect(self._on_telnet_key)

    def _build_shell_tab(self, is_ssh):
        tab = QWidget()
        lay = QVBoxLayout(tab)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(14)

        ctrl = QHBoxLayout()
        ctrl.setSpacing(10)
        hosts_cb = QComboBox()

        proto = "SSH" if is_ssh else "Telnet"
        warn = "" if is_ssh else "  ⚠ texto puro"
        info = QLabel(f"Conexão {proto}{warn}")
        info.setStyleSheet(f"color: {'#9aa6c2' if is_ssh else '#fbbf24'}; font-size: 12px;")
        info.setMinimumWidth(160)

        btn = QPushButton(f"▶  Conectar {proto}")
        btn.setObjectName("BtnPrimary")
        if is_ssh:
            btn.clicked.connect(self.toggle_ssh)
        else:
            btn.clicked.connect(self.toggle_telnet)

        ctrl.addWidget(hosts_cb, 4)
        ctrl.addWidget(info, 1)
        ctrl.addWidget(btn, 1)
        lay.addLayout(ctrl)

        card, title_lbl, status_b, body, body_lay = terminal_card(f"~ {proto.lower()}")
        terminal = TerminalEdit()
        terminal.setStyleSheet("border: none; border-radius: 0;"
                               "border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;")
        body_lay.addWidget(terminal)
        lay.addWidget(card, 1)

        return tab, hosts_cb, btn, terminal, status_b, title_lbl

    def refresh_ssh_hosts(self):
        self.ssh_hosts_cb.clear()
        for h in self.db.get_hosts():
            ip, hostname, p_ssh = h[0], h[1], h[2]
            self.ssh_hosts_cb.addItem(f"{hostname} — {ip}:{p_ssh}", ip)

    def refresh_telnet_hosts(self):
        self.telnet_hosts_cb.clear()
        for h in self.db.get_hosts():
            ip, hostname, p_tel = h[0], h[1], h[3]
            self.telnet_hosts_cb.addItem(f"{hostname} — {ip}:{p_tel}", ip)

    def toggle_ssh(self):
        if self.ssh_active:
            if self.ssh_worker:
                self.ssh_worker.stop()
            return
        ip = self.ssh_hosts_cb.currentData()
        if not ip:
            QMessageBox.warning(self, "Aviso", "Cadastre um host primeiro em Host Manager.")
            return
        host = next((h for h in self.db.get_hosts() if h[0] == ip), None)
        if not host:
            return
        _, hostname, p_ssh, _, user, pw, *_ = host
        self.ssh_terminal.clear()
        self.ssh_title.setText(f"{user}@{hostname}")
        self.ssh_status.setText("conectando…"); self.ssh_status.setProperty("kind", "yellow")
        self.ssh_status.style().unpolish(self.ssh_status); self.ssh_status.style().polish(self.ssh_status)
        self.ssh_terminal.append_line(f"$ ssh {user}@{ip} -p {p_ssh}", "dim")
        self.ssh_worker = SSHShellWorker(ip, p_ssh, user, pw)
        self.ssh_worker.stdout_received.connect(lambda t: self.ssh_terminal.append_raw(t))
        self.ssh_worker.connected.connect(lambda: self._set_status(self.ssh_status, "conectado", "green"))
        self.ssh_worker.connection_failed.connect(lambda e: self._on_shell_failed(self.ssh_terminal, self.ssh_status, e))
        self.ssh_worker.finished.connect(self._on_ssh_done)
        self.ssh_worker.start()
        self.ssh_btn.setText("◼  Desconectar")
        self.ssh_active = True

    def toggle_telnet(self):
        if self.telnet_active:
            if self.telnet_worker:
                self.telnet_worker.stop()
            return
        ip = self.telnet_hosts_cb.currentData()
        if not ip:
            QMessageBox.warning(self, "Aviso", "Cadastre um host primeiro em Host Manager.")
            return
        host = next((h for h in self.db.get_hosts() if h[0] == ip), None)
        if not host:
            return
        _, hostname, _, p_tel, user, pw, *_ = host
        self.telnet_terminal.clear()
        self.telnet_title.setText(f"{user}@{hostname}")
        self._set_status(self.telnet_status, "conectando…", "yellow")
        self.telnet_terminal.append_line(f"$ telnet {ip} {p_tel}", "dim")
        self.telnet_worker = TelnetShellWorker(ip, p_tel, user, pw)
        self.telnet_worker.stdout_received.connect(lambda t: self.telnet_terminal.append_raw(t))
        self.telnet_worker.connected.connect(lambda: self._set_status(self.telnet_status, "conectado", "green"))
        self.telnet_worker.connection_failed.connect(lambda e: self._on_shell_failed(self.telnet_terminal, self.telnet_status, e))
        self.telnet_worker.finished.connect(self._on_telnet_done)
        self.telnet_worker.start()
        self.telnet_btn.setText("◼  Desconectar")
        self.telnet_active = True

    def _set_status(self, status_widget, text, kind):
        status_widget.setText(text)
        status_widget.setProperty("kind", kind)
        status_widget.style().unpolish(status_widget); status_widget.style().polish(status_widget)

    def _on_shell_failed(self, term, status, err):
        term.append_line(f"✗ Falha: {err}", "err")
        self._set_status(status, "falhou", "red")

    def _on_ssh_done(self):
        self.ssh_active = False
        self.ssh_btn.setText("▶  Conectar SSH")
        self._set_status(self.ssh_status, "desconectado", "gray")
        self.ssh_terminal.append_line("Conexão SSH encerrada.", "dim")

    def _on_telnet_done(self):
        self.telnet_active = False
        self.telnet_btn.setText("▶  Conectar Telnet")
        self._set_status(self.telnet_status, "desconectado", "gray")
        self.telnet_terminal.append_line("Conexão Telnet encerrada.", "dim")

    def _on_ssh_key(self, ch):
        if self.ssh_active and self.ssh_worker:
            self.ssh_worker.send_input(ch)

    def _on_telnet_key(self, ch):
        if self.telnet_active and self.telnet_worker:
            self.telnet_worker.send_input(ch)

    def refresh_lists(self):
        self.refresh_ssh_hosts()
        self.refresh_telnet_hosts()

    # Atalhos chamados externamente (ex: pelo Host Manager)
    def quick_ping(self, host):
        self.tabs.setCurrentIndex(0)
        self.ping_input.setText(host)
        if not self.ping_active:
            self.toggle_ping()

    def quick_trace(self, host):
        self.tabs.setCurrentIndex(1)
        self.trace_input.setText(host)
        if not self.trace_active:
            self.toggle_trace()

    def quick_ssh(self, ip):
        self.tabs.setCurrentIndex(2)
        idx = self.ssh_hosts_cb.findData(ip)
        if idx >= 0:
            self.ssh_hosts_cb.setCurrentIndex(idx)
        if not self.ssh_active:
            self.toggle_ssh()

    def quick_telnet(self, ip):
        self.tabs.setCurrentIndex(3)
        idx = self.telnet_hosts_cb.findData(ip)
        if idx >= 0:
            self.telnet_hosts_cb.setCurrentIndex(idx)
        if not self.telnet_active:
            self.toggle_telnet()
