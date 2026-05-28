"""
Discovery — varredura ativa de ranges, fingerprint de serviços, monitoramento.
Tela equivalente à do mockup HTML (screens/discovery.jsx).
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
                              QListWidget, QListWidgetItem, QTableWidget, QTableWidgetItem,
                              QHeaderView, QProgressBar, QDialog, QLineEdit, QComboBox,
                              QSpinBox, QMessageBox, QCheckBox)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QColor, QFont, QPainter, QBrush, QPixmap

from src.engine.scanner import ScanRunner, expand_cidrs
from src.ui.widgets import badge, stat_card, page_header, small_action_btn


SERVICE_KIND = {
    "SSH":      "blue",
    "Telnet":   "yellow",
    "BGP":      "purple",
    "SNMP":     "cyan",
    "NETCONF":  "green",
    "HTTP":     "gray",
    "HTTPS":    "cyan",
    "BMP":      "purple",
    "Postgres": "green",
    "gRPC":     "cyan",
    "LDP":      "blue",
    "DNS":      "gray",
    "HTTP-Alt": "gray",
}


class ColorDot(QWidget):
    def __init__(self, color="#3da9fc", parent=None):
        super().__init__(parent)
        self._color = color
        self.setFixedSize(8, 22)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QBrush(QColor(self._color)))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(0, 4, 4, 14, 2, 2)


class AddRangeDialog(QDialog):
    def __init__(self, parent=None, group=None):
        super().__init__(parent)
        self.group = group
        self.setWindowTitle("Editar grupo de range" if group else "Adicionar grupo de range")
        self.setFixedWidth(480)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title = QLabel(self.windowTitle())
        title.setStyleSheet("font-size: 16px; font-weight: 700; color: #e7ecf7;")
        layout.addWidget(title)

        self.name = QLineEdit()
        self.name.setPlaceholderText("Backbone SP")
        layout.addWidget(self._labeled("Nome do grupo", self.name))

        self.cidrs = QLineEdit()
        self.cidrs.setPlaceholderText("10.0.0.0/24, 10.0.5.0/24")
        layout.addWidget(self._labeled("CIDRs (separe múltiplos com vírgula)", self.cidrs))

        row = QHBoxLayout()
        self.color = QComboBox()
        for c, name in [("#3da9fc", "Azul"), ("#a18cff", "Roxo"), ("#21d4fd", "Ciano"),
                        ("#4ade80", "Verde"), ("#fbbf24", "Amarelo"), ("#ff5c7a", "Vermelho")]:
            pm = QPixmap(12, 12); pm.fill(QColor(c))
            self.color.addItem(name, c)
            self.color.setItemData(self.color.count() - 1, QColor(c), Qt.DecorationRole)

        self.interval = QSpinBox()
        self.interval.setRange(1, 120)
        self.interval.setValue(15)
        self.interval.setSuffix(" min")

        row.addWidget(self._labeled("Cor", self.color), 1)
        row.addWidget(self._labeled("Intervalo de scan", self.interval), 1)
        layout.addLayout(row)

        self.monitor = QCheckBox("Monitorar serviços continuamente")
        self.monitor.setChecked(True)
        layout.addWidget(self.monitor)

        if self.group:
            gid, name, color, cidrs, interval, monitor, _ = self.group
            self.name.setText(name)
            self.cidrs.setText(cidrs)
            idx = self.color.findData(color)
            if idx >= 0: self.color.setCurrentIndex(idx)
            self.interval.setValue(interval or 15)
            self.monitor.setChecked(bool(monitor))

        # Botões
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel = QPushButton("Cancelar")
        cancel.setObjectName("Btn")
        cancel.clicked.connect(self.reject)
        save = QPushButton("Salvar" if self.group else "Adicionar e varrer")
        save.setObjectName("BtnPrimary")
        save.clicked.connect(self.accept)
        btn_row.addWidget(cancel); btn_row.addWidget(save)
        layout.addLayout(btn_row)

    def _labeled(self, label, widget):
        f = QFrame()
        l = QVBoxLayout(f)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(4)
        lbl = QLabel(label.upper())
        lbl.setStyleSheet("font-size: 10px; color: #6b7693; font-weight: 600; letter-spacing: 0.1em;")
        l.addWidget(lbl)
        l.addWidget(widget)
        return f

    def get_data(self):
        return {
            "name": self.name.text().strip(),
            "cidrs": self.cidrs.text().strip(),
            "color": self.color.currentData(),
            "scan_interval_min": self.interval.value(),
            "monitor": 1 if self.monitor.isChecked() else 0,
        }


class DiscoveryScreen(QWidget):
    ssh_requested = pyqtSignal(str)
    ping_requested = pyqtSignal(str)
    register_host_requested = pyqtSignal(str, str, str)  # ip, hostname, vendor

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self._active_group_id = None
        self._scanner = ScanRunner(self)
        self._scanner.host_done.connect(self._on_host_found)
        self._scanner.progress.connect(self._on_progress)
        self._scanner.finished.connect(self._on_scan_done)
        self._init_ui()
        self.refresh_groups()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        add_btn = QPushButton("＋  Adicionar Range")
        add_btn.setObjectName("BtnPrimary")
        add_btn.clicked.connect(self.add_group)
        layout.addWidget(page_header(
            "Auto", "Descoberta",
            "Varredura ativa de ranges CIDR, fingerprint de serviços e monitoramento contínuo.",
            actions=[add_btn]))

        # Stats
        stats_row = QHBoxLayout()
        stats_row.setSpacing(10)
        self.stat_hosts = stat_card("Hosts descobertos", "0", "online · offline", "up")
        self.stat_groups = stat_card("Grupos", "0", "CIDRs monitorados")
        self.stat_services = stat_card("Serviços", "0", "SSH · BGP · SNMP")
        self.stat_scan = stat_card("Última varredura", "—", "")
        for s in (self.stat_hosts, self.stat_groups, self.stat_services, self.stat_scan):
            stats_row.addWidget(s)
        layout.addLayout(stats_row)

        # Body grid: left=group list  right=hosts table
        body = QHBoxLayout()
        body.setSpacing(16)

        # ── LEFT — Group list card ──
        left_card = QFrame()
        left_card.setObjectName("Card")
        left_card.setFixedWidth(340)
        ll = QVBoxLayout(left_card)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.setSpacing(0)

        head = QFrame()
        head.setObjectName("CardHeader")
        head_l = QHBoxLayout(head)
        head_l.setContentsMargins(14, 12, 14, 12)
        head_title = QLabel("GRUPOS DE RANGE")
        head_title.setObjectName("CardTitle")
        head_l.addWidget(head_title)
        head_l.addStretch()
        head_add = QPushButton("＋")
        head_add.setObjectName("BtnSmall")
        head_add.setFixedSize(28, 24)
        head_add.clicked.connect(self.add_group)
        head_l.addWidget(head_add)
        ll.addWidget(head)

        self.group_list = QListWidget()
        self.group_list.setFrameShape(QFrame.NoFrame)
        self.group_list.itemSelectionChanged.connect(self._on_group_selected)
        ll.addWidget(self.group_list, 1)

        # Footer actions
        foot = QFrame()
        foot_l = QHBoxLayout(foot)
        foot_l.setContentsMargins(10, 8, 10, 10)
        edit_btn = QPushButton("Editar"); edit_btn.setObjectName("BtnSmall")
        edit_btn.clicked.connect(self.edit_group)
        del_btn = QPushButton("Remover"); del_btn.setObjectName("BtnDangerSmall")
        del_btn.clicked.connect(self.delete_group)
        foot_l.addWidget(edit_btn)
        foot_l.addWidget(del_btn)
        foot_l.addStretch()
        ll.addWidget(foot)

        body.addWidget(left_card)

        # ── RIGHT — Active group detail ──
        right_card = QFrame()
        right_card.setObjectName("Card")
        rl = QVBoxLayout(right_card)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(0)

        # Header bar with group name + scan button
        rhead = QFrame()
        rhead.setObjectName("CardHeader")
        rhead_l = QHBoxLayout(rhead)
        rhead_l.setContentsMargins(16, 12, 14, 12)
        self.active_dot = ColorDot("#3da9fc")
        self.active_title = QLabel("Selecione um grupo")
        self.active_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #e7ecf7;")
        self.active_cidrs = QLabel("")
        self.active_cidrs.setStyleSheet("color: #6b7693; font-family: 'JetBrains Mono'; font-size: 11.5px;")
        rhead_l.addWidget(self.active_dot)
        rhead_l.addWidget(self.active_title)
        rhead_l.addWidget(self.active_cidrs)
        rhead_l.addStretch()
        self.scan_btn = QPushButton("◉  Scan agora")
        self.scan_btn.setObjectName("BtnSmall")
        self.scan_btn.clicked.connect(self.trigger_scan)
        rhead_l.addWidget(self.scan_btn)
        rl.addWidget(rhead)

        # Progress bar (visible during scan)
        self.scan_status = QFrame()
        self.scan_status.setStyleSheet(
            "background: rgba(33,212,253,0.06); border-bottom: 1px solid rgba(33,212,253,0.18);")
        ss_l = QHBoxLayout(self.scan_status)
        ss_l.setContentsMargins(16, 10, 16, 10)
        self.scan_label = QLabel("")
        self.scan_label.setStyleSheet("color: #21d4fd; font-size: 12px;")
        ss_l.addWidget(self.scan_label)
        ss_l.addStretch()
        self.scan_progress = QProgressBar()
        self.scan_progress.setFixedWidth(200)
        self.scan_progress.setTextVisible(False)
        ss_l.addWidget(self.scan_progress)
        self.scan_status.setVisible(False)
        rl.addWidget(self.scan_status)

        # Hosts table
        self.host_table = QTableWidget(0, 7)
        self.host_table.setHorizontalHeaderLabels(
            ["IP", "Hostname", "Vendor / OS", "Serviços detectados", "RTT", "Status", "Ações"])
        h = self.host_table.horizontalHeader()
        h.setSectionResizeMode(QHeaderView.Stretch)
        h.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.host_table.verticalHeader().setVisible(False)
        self.host_table.setEditTriggers(QTableWidget.NoEditTriggers)
        rl.addWidget(self.host_table, 1)

        body.addWidget(right_card, 1)

        layout.addLayout(body, 1)

    # ───────────────── Groups ─────────────────
    def refresh_groups(self):
        groups = self.db.get_range_groups()
        self.group_list.clear()
        total_cidrs = 0
        for g in groups:
            gid, name, color, cidrs, interval, monitor, last_scan = g
            n_cidrs = len([c for c in cidrs.split(",") if c.strip()])
            total_cidrs += n_cidrs
            item = QListWidgetItem()
            item.setData(Qt.UserRole, gid)
            w = self._group_item_widget(name, color, cidrs, last_scan or "—")
            item.setSizeHint(QSize(0, 78))
            self.group_list.addItem(item)
            self.group_list.setItemWidget(item, w)

        self.stat_groups.value_label.setText(str(len(groups)))
        if self.stat_groups.delta_label:
            self.stat_groups.delta_label.setText(f"{total_cidrs} CIDRs monitorados")

        if self._active_group_id is None and groups:
            self.group_list.setCurrentRow(0)
        else:
            for i in range(self.group_list.count()):
                if self.group_list.item(i).data(Qt.UserRole) == self._active_group_id:
                    self.group_list.setCurrentRow(i)
                    break

    def _group_item_widget(self, name, color, cidrs, last_scan):
        f = QFrame()
        l = QHBoxLayout(f)
        l.setContentsMargins(8, 4, 8, 4)
        l.setSpacing(10)
        l.addWidget(ColorDot(color))

        center = QVBoxLayout()
        center.setSpacing(2)
        n = QLabel(name); n.setStyleSheet("font-size: 13px; font-weight: 600; color: #e7ecf7;")
        c = QLabel(cidrs); c.setStyleSheet("font-size: 11px; color: #6b7693; font-family: 'JetBrains Mono';")
        center.addWidget(n)
        center.addWidget(c)
        l.addLayout(center, 1)

        ts = QLabel(str(last_scan)[:16] if last_scan != "—" else "—")
        ts.setStyleSheet("font-size: 10.5px; color: #6b7693;")
        l.addWidget(ts)
        return f

    def _on_group_selected(self):
        items = self.group_list.selectedItems()
        if not items:
            return
        gid = items[0].data(Qt.UserRole)
        self._active_group_id = gid
        groups = self.db.get_range_groups()
        g = next((x for x in groups if x[0] == gid), None)
        if not g:
            return
        _, name, color, cidrs, _, _, last_scan = g
        self.active_dot._color = color
        self.active_dot.update()
        self.active_title.setText(name)
        self.active_cidrs.setText("  ·  " + cidrs)
        self._load_hosts()

    def add_group(self):
        d = AddRangeDialog(self)
        if d.exec_() == QDialog.Accepted:
            data = d.get_data()
            if not data["name"] or not data["cidrs"]:
                QMessageBox.warning(self, "Aviso", "Preencha nome e CIDRs.")
                return
            try:
                self.db.add_range_group(**data)
            except Exception as e:
                QMessageBox.warning(self, "Erro", f"Falha ao adicionar: {e}")
                return
            self.db.add_log("INFO", "Discovery", f"Grupo '{data['name']}' adicionado.")
            self.refresh_groups()

    def edit_group(self):
        if not self._active_group_id:
            return
        g = next((x for x in self.db.get_range_groups() if x[0] == self._active_group_id), None)
        if not g:
            return
        d = AddRangeDialog(self, group=g)
        if d.exec_() == QDialog.Accepted:
            data = d.get_data()
            self.db.update_range_group(self._active_group_id, **data)
            self.refresh_groups()

    def delete_group(self):
        if not self._active_group_id:
            return
        g = next((x for x in self.db.get_range_groups() if x[0] == self._active_group_id), None)
        if not g:
            return
        reply = QMessageBox.question(self, "Confirmação", f"Remover grupo '{g[1]}'?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.remove_range_group(self._active_group_id)
            self._active_group_id = None
            self.refresh_groups()
            self.host_table.setRowCount(0)

    # ───────────────── Scan ─────────────────
    def trigger_scan(self):
        if not self._active_group_id:
            QMessageBox.information(self, "Aviso", "Selecione um grupo para varrer.")
            return
        g = next((x for x in self.db.get_range_groups() if x[0] == self._active_group_id), None)
        if not g:
            return
        cidrs = g[3]
        # Confirmação se range muito grande
        ips = expand_cidrs(cidrs, max_hosts=1024)
        if not ips:
            QMessageBox.warning(self, "Aviso", "CIDR inválido ou range muito grande (>1024 hosts).")
            return

        self.host_table.setRowCount(0)
        self.scan_status.setVisible(True)
        self.scan_label.setText(f"Varrendo {len(ips)} IPs em {cidrs}  ·  TCP connect + service fingerprint…")
        self.scan_progress.setRange(0, len(ips))
        self.scan_progress.setValue(0)
        self.scan_btn.setText("◼  Parar")
        self.scan_btn.clicked.disconnect()
        self.scan_btn.clicked.connect(self._stop_scan)
        self._scanner.run(cidrs, max_hosts=1024, workers=64)

    def _stop_scan(self):
        self._scanner.stop()
        self.scan_label.setText("Cancelando…")

    def _on_host_found(self, ip, hostname, vendor, os_name, rtt, services):
        # Salvar no DB
        host_id = self.db.upsert_discovered_host(
            self._active_group_id, ip, hostname=hostname,
            vendor=vendor or None, os_name=os_name or None,
            rtt_ms=rtt, status="online")
        for port, proto, service in services:
            self.db.add_discovered_service(host_id, port, proto, service)
        self._append_host_row(ip, hostname, vendor, os_name, rtt, services, "online", host_id)

    def _on_progress(self, done, total):
        self.scan_progress.setRange(0, total)
        self.scan_progress.setValue(done)
        self.scan_label.setText(f"Varrendo… {done}/{total} hosts probed")

    def _on_scan_done(self, hosts_up):
        self.scan_status.setVisible(False)
        self.scan_btn.setText("◉  Scan agora")
        try:
            self.scan_btn.clicked.disconnect()
        except Exception:
            pass
        self.scan_btn.clicked.connect(self.trigger_scan)
        if self._active_group_id:
            self.db.touch_range_scan(self._active_group_id)
        self.db.add_log("INFO", "Discovery", f"Scan concluído: {hosts_up} hosts up.")
        self.refresh_groups()

    # ───────────────── Tabela de hosts ─────────────────
    def _load_hosts(self):
        if not self._active_group_id:
            return
        self.host_table.setRowCount(0)
        hosts_with_services = self.db.get_discovered(self._active_group_id)
        all_services = 0
        for host_row, services in hosts_with_services:
            hid, ip, hostname, vendor, os_name, rtt, status, monitor, last_seen = host_row
            self._append_host_row(ip, hostname or ip, vendor or "", os_name or "",
                                   rtt or 0.0, [(s[0], s[1], s[2]) for s in services], status, hid)
            all_services += len(services)
        # update stats
        total_disc = sum(1 for _ in hosts_with_services)
        online = sum(1 for h, _ in hosts_with_services if h[6] == "online")
        self.stat_hosts.value_label.setText(str(total_disc))
        if self.stat_hosts.delta_label:
            self.stat_hosts.delta_label.setText(f"{online} online · {total_disc - online} offline")
        self.stat_services.value_label.setText(str(all_services))

    def _append_host_row(self, ip, hostname, vendor, os_name, rtt, services, status, host_id):
        row = self.host_table.rowCount()
        self.host_table.insertRow(row)
        self.host_table.setRowHeight(row, 48)

        it = QTableWidgetItem(ip); it.setFont(QFont("JetBrains Mono", 10))
        self.host_table.setItem(row, 0, it)

        it = QTableWidgetItem(hostname); it.setFont(QFont("Inter", 10, QFont.Bold))
        self.host_table.setItem(row, 1, it)

        vendor_text = f"{vendor}\n{os_name}" if (vendor or os_name) else "—"
        it = QTableWidgetItem(vendor_text)
        it.setForeground(QColor("#9aa6c2"))
        self.host_table.setItem(row, 2, it)

        # Services badge container
        svc_frame = QFrame()
        sl = QHBoxLayout(svc_frame)
        sl.setContentsMargins(4, 4, 4, 4)
        sl.setSpacing(4)
        for port, proto, sname in services[:6]:
            label = f"{sname}:{port}" if sname else f"{port}/{proto}"
            kind = SERVICE_KIND.get(sname, "gray")
            sl.addWidget(badge(label, kind))
        if len(services) > 6:
            sl.addWidget(badge(f"+{len(services) - 6}", "gray"))
        sl.addStretch()
        self.host_table.setCellWidget(row, 3, svc_frame)

        rtt_text = f"{rtt:.1f} ms" if rtt > 0 else "—"
        it = QTableWidgetItem(rtt_text)
        it.setFont(QFont("JetBrains Mono", 9))
        it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        if rtt <= 0:
            it.setForeground(QColor("#6b7693"))
        elif rtt < 5:
            it.setForeground(QColor("#4ade80"))
        else:
            it.setForeground(QColor("#fbbf24"))
        self.host_table.setItem(row, 4, it)

        status_text = "● online" if status == "online" else "○ offline"
        it = QTableWidgetItem(status_text)
        it.setForeground(QColor("#4ade80" if status == "online" else "#6b7693"))
        self.host_table.setItem(row, 5, it)

        # Ações
        actions_w = QFrame()
        al = QHBoxLayout(actions_w)
        al.setContentsMargins(4, 4, 4, 4)
        al.setSpacing(4)
        ssh_b = small_action_btn("SSH", "▶")
        ssh_b.clicked.connect(lambda _, ip=ip: self.ssh_requested.emit(ip))
        ping_b = small_action_btn("Ping")
        ping_b.clicked.connect(lambda _, ip=ip: self.ping_requested.emit(ip))
        reg_b = small_action_btn("Cadastrar", "↑")
        reg_b.clicked.connect(lambda _, ip=ip, h=hostname, v=vendor:
                              self.register_host_requested.emit(ip, h, v))
        al.addWidget(ssh_b); al.addWidget(ping_b); al.addWidget(reg_b)
        al.addStretch()
        self.host_table.setCellWidget(row, 6, actions_w)
