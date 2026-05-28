"""
Host Manager — CRUD com stats, filtros, busca e ações rápidas
(SSH / Telnet / Ping / Traceroute) por linha.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
                              QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QLineEdit,
                              QComboBox, QMessageBox, QSpinBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont

from src.ui.widgets import badge, stat_card, page_header, small_action_btn


VENDOR_COLORS = {
    "MikroTik": "#3da9fc",
    "Cisco":    "#21d4fd",
    "Juniper":  "#4ade80",
    "Linux":    "#a18cff",
    "TP-Link":  "#9aa6c2",
    "Outro":    "#9aa6c2",
}


class HostDialog(QDialog):
    def __init__(self, parent=None, host_data=None):
        super().__init__(parent)
        self.host_data = host_data
        self.setWindowTitle("Editar Host" if host_data else "Adicionar novo Host")
        self.setFixedWidth(560)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title = QLabel(self.windowTitle())
        title.setStyleSheet("font-size: 16px; font-weight: 700; color: #e7ecf7;")
        layout.addWidget(title)

        self.hostname = QLineEdit(); self.hostname.setPlaceholderText("br-edge-01")
        self.ip = QLineEdit(); self.ip.setPlaceholderText("10.0.0.1")
        self.ssh = QSpinBox(); self.ssh.setRange(1, 65535); self.ssh.setValue(22)
        self.telnet = QSpinBox(); self.telnet.setRange(1, 65535); self.telnet.setValue(23)
        self.group = QLineEdit(); self.group.setPlaceholderText("SP-Core")
        self.user = QLineEdit(); self.user.setPlaceholderText("netadmin")
        self.pwd = QLineEdit(); self.pwd.setEchoMode(QLineEdit.Password); self.pwd.setPlaceholderText("••••••••")

        self.type_cb = QComboBox()
        self.type_cb.addItems(["Router", "Switch", "Server", "Firewall", "AP"])

        self.vendor_cb = QComboBox()
        self.vendor_cb.addItems(list(VENDOR_COLORS.keys()))

        # Linha 1: hostname + ip
        layout.addLayout(self._row(("Hostname", self.hostname), ("Endereço IP", self.ip)))
        # Linha 2: ssh / telnet / grupo
        layout.addLayout(self._row(("Porta SSH", self.ssh), ("Porta Telnet", self.telnet),
                                     ("Grupo", self.group)))
        # Linha 3: usuário + senha
        layout.addLayout(self._row(("Usuário", self.user), ("Senha", self.pwd)))
        # Linha 4: tipo + fabricante
        layout.addLayout(self._row(("Tipo", self.type_cb), ("Fabricante", self.vendor_cb)))

        if self.host_data:
            ip, hostname, p_ssh, p_tel, user, pwd, type_, mfg, status, group_name = self.host_data
            self.ip.setText(ip)
            self.ip.setReadOnly(True)
            self.hostname.setText(hostname)
            self.ssh.setValue(p_ssh or 22)
            self.telnet.setValue(p_tel or 23)
            self.user.setText(user or "")
            self.pwd.setText(pwd or "")
            self.type_cb.setCurrentText(type_ or "Router")
            self.vendor_cb.setCurrentText(mfg or "MikroTik")
            self.group.setText(group_name or "")

        # Botões
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel = QPushButton("Cancelar")
        cancel.setObjectName("Btn")
        cancel.clicked.connect(self.reject)
        save = QPushButton("Salvar alterações" if self.host_data else "Adicionar Host")
        save.setObjectName("BtnPrimary")
        save.clicked.connect(self.accept)
        btn_row.addWidget(cancel); btn_row.addWidget(save)
        layout.addLayout(btn_row)

    def _row(self, *pairs):
        row = QHBoxLayout()
        row.setSpacing(10)
        for label, widget in pairs:
            f = QFrame()
            l = QVBoxLayout(f)
            l.setContentsMargins(0, 0, 0, 0)
            l.setSpacing(4)
            lab = QLabel(label.upper())
            lab.setStyleSheet("font-size: 10px; color: #6b7693; font-weight: 600; letter-spacing: 0.1em;")
            l.addWidget(lab)
            l.addWidget(widget)
            row.addWidget(f, 1)
        return row

    def get_data(self):
        return {
            "ip": self.ip.text().strip(),
            "hostname": self.hostname.text().strip(),
            "port_ssh": self.ssh.value(),
            "port_telnet": self.telnet.value(),
            "username": self.user.text().strip(),
            "password": self.pwd.text(),
            "type": self.type_cb.currentText(),
            "fabricante": self.vendor_cb.currentText(),
            "group_name": self.group.text().strip(),
        }


class HostManagerScreen(QWidget):
    """Sinais para outras telas pedirem ação."""
    ping_requested  = pyqtSignal(str)   # ip ou hostname
    trace_requested = pyqtSignal(str)
    ssh_requested   = pyqtSignal(str)   # ip
    telnet_requested = pyqtSignal(str)  # ip

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        add_btn = QPushButton("＋  Adicionar Host")
        add_btn.setObjectName("BtnPrimary")
        add_btn.clicked.connect(self.add_host)

        layout.addWidget(page_header(
            "Host", "Manager",
            "Inventário de roteadores, switches, firewalls e servidores. Acesse via SSH/Telnet com 1 clique.",
            actions=[add_btn]))

        # Stats
        stats_row = QHBoxLayout()
        stats_row.setSpacing(10)
        self.stat_total = stat_card("Total Hosts", "0", "")
        self.stat_online = stat_card("Online", "0", "Respondendo", "up")
        self.stat_offline = stat_card("Offline", "0", "Sem resposta", "dn")
        self.stat_groups = stat_card("Grupos", "0", "Distintos")
        for s in (self.stat_total, self.stat_online, self.stat_offline, self.stat_groups):
            stats_row.addWidget(s)
        layout.addLayout(stats_row)

        # Filtros
        filters = QHBoxLayout()
        filters.setSpacing(10)
        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍  Buscar host, IP, grupo ou usuário…")
        self.search.textChanged.connect(self.load_data)

        self.filter_type = QComboBox()
        self.filter_type.addItem("Todos os tipos", None)
        for t in ["Router", "Switch", "Server", "Firewall", "AP"]:
            self.filter_type.addItem(t, t)
        self.filter_type.currentIndexChanged.connect(self.load_data)

        self.filter_vendor = QComboBox()
        self.filter_vendor.addItem("Todos os fabricantes", None)
        for v in VENDOR_COLORS.keys():
            self.filter_vendor.addItem(v, v)
        self.filter_vendor.currentIndexChanged.connect(self.load_data)

        self.result_badge = badge("0 resultados", "gray")
        filters.addWidget(self.search, 3)
        filters.addWidget(self.filter_type, 1)
        filters.addWidget(self.filter_vendor, 1)
        filters.addStretch()
        filters.addWidget(self.result_badge)
        layout.addLayout(filters)

        # Tabela
        self.table = QTableWidget(0, 9)
        self.table.setHorizontalHeaderLabels(
            ["Hostname", "IP", "SSH", "Telnet", "Usuário", "Tipo", "Fabricante", "Grupo", "Ações"])
        h = self.table.horizontalHeader()
        h.setSectionResizeMode(QHeaderView.Stretch)
        for col in (1, 2, 3, 5, 6, 7, 8):
            h.setSectionResizeMode(col, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table, 1)

        self.load_data()

    def load_data(self):
        rows = self.db.get_hosts()
        # Stats
        on = sum(1 for r in rows if r[8] == "Online")
        off = len(rows) - on
        groups = {r[9] for r in rows if r[9]}
        self.stat_total.value_label.setText(str(len(rows)))
        self.stat_online.value_label.setText(str(on))
        self.stat_offline.value_label.setText(str(off))
        self.stat_groups.value_label.setText(str(len(groups)))

        q = self.search.text().strip().lower()
        ftype = self.filter_type.currentData()
        fvendor = self.filter_vendor.currentData()

        def match(r):
            ip, hostname, p_ssh, p_tel, user, pwd, type_, mfg, status, grp = r
            if q and q not in f"{hostname} {ip} {grp} {user}".lower():
                return False
            if ftype and type_ != ftype:
                return False
            if fvendor and mfg != fvendor:
                return False
            return True

        filtered = [r for r in rows if match(r)]
        self.result_badge.setText(f"{len(filtered)} resultado{'s' if len(filtered) != 1 else ''}")

        self.table.setRowCount(0)
        for r in filtered:
            ip, hostname, p_ssh, p_tel, user, pwd, type_, mfg, status, grp = r
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Hostname + status dot inline (item flag)
            host_text = hostname
            it = QTableWidgetItem(("● " if status == "Online" else "○ ") + host_text)
            it.setFont(QFont("Inter", 10, QFont.Bold))
            it.setForeground(QColor("#4ade80" if status == "Online" else "#6b7693"))
            self.table.setItem(row, 0, it)

            it = QTableWidgetItem(ip)
            it.setFont(QFont("JetBrains Mono", 9))
            self.table.setItem(row, 1, it)

            it = QTableWidgetItem(str(p_ssh))
            it.setFont(QFont("JetBrains Mono", 9))
            it.setForeground(QColor("#6b7693"))
            it.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 2, it)

            it = QTableWidgetItem(str(p_tel))
            it.setFont(QFont("JetBrains Mono", 9))
            it.setForeground(QColor("#6b7693"))
            it.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 3, it)

            it = QTableWidgetItem(user or "—")
            it.setFont(QFont("JetBrains Mono", 9))
            self.table.setItem(row, 4, it)

            it = QTableWidgetItem(type_)
            it.setForeground(QColor("#9aa6c2"))
            self.table.setItem(row, 5, it)

            it = QTableWidgetItem(mfg)
            it.setForeground(QColor(VENDOR_COLORS.get(mfg, "#9aa6c2")))
            it.setFont(QFont("Inter", 10, QFont.Bold))
            self.table.setItem(row, 6, it)

            it = QTableWidgetItem(grp or "—")
            it.setFont(QFont("JetBrains Mono", 9))
            it.setForeground(QColor("#9aa6c2"))
            self.table.setItem(row, 7, it)

            # Ações
            actions_w = QFrame()
            al = QHBoxLayout(actions_w)
            al.setContentsMargins(4, 4, 4, 4)
            al.setSpacing(4)
            ssh_b = small_action_btn("SSH", "▶")
            ssh_b.clicked.connect(lambda _, ip=ip: self.ssh_requested.emit(ip))
            tel_b = small_action_btn("Tel", "▶")
            tel_b.clicked.connect(lambda _, ip=ip: self.telnet_requested.emit(ip))
            ping_b = small_action_btn("Ping")
            ping_b.clicked.connect(lambda _, ip=ip: self.ping_requested.emit(ip))
            tr_b = small_action_btn("Trace")
            tr_b.clicked.connect(lambda _, ip=ip: self.trace_requested.emit(ip))
            edit_b = small_action_btn("Editar", "✎")
            edit_b.clicked.connect(lambda _, ip=ip: self.edit_host(ip))
            del_b = small_action_btn("Remover", "🗑", "danger")
            del_b.clicked.connect(lambda _, ip=ip, n=hostname: self.delete_host(ip, n))
            for b in (ssh_b, tel_b, ping_b, tr_b, edit_b, del_b):
                al.addWidget(b)
            al.addStretch()
            self.table.setCellWidget(row, 8, actions_w)
            self.table.setRowHeight(row, 44)

    def add_host(self):
        dialog = HostDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            d = dialog.get_data()
            if not d["ip"] or not d["hostname"]:
                QMessageBox.warning(self, "Aviso", "Preencha IP e Hostname.")
                return
            self.db.add_host(d["ip"], d["hostname"], d["port_ssh"], d["port_telnet"],
                             d["username"], d["password"], d["type"], d["fabricante"],
                             d["group_name"])
            self.db.add_log("INFO", "Host", f"Host {d['hostname']} ({d['ip']}) cadastrado.")
            self.load_data()

    def edit_host(self, ip):
        match = next((r for r in self.db.get_hosts() if r[0] == ip), None)
        if not match:
            return
        dialog = HostDialog(self, host_data=match)
        if dialog.exec_() == QDialog.Accepted:
            d = dialog.get_data()
            self.db.add_host(ip, d["hostname"], d["port_ssh"], d["port_telnet"],
                             d["username"], d["password"], d["type"], d["fabricante"],
                             d["group_name"])
            self.db.add_log("INFO", "Host", f"Host {d['hostname']} ({ip}) atualizado.")
            self.load_data()

    def delete_host(self, ip, hostname):
        reply = QMessageBox.question(
            self, "Confirmação",
            f"Remover {hostname} ({ip})?",
            QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.remove_host(ip)
            self.db.add_log("INFO", "Host", f"Host {hostname} ({ip}) removido.")
            self.load_data()
