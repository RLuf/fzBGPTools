"""
Janela principal — sidebar, topbar, stacked screens.
Adiciona Discovery e fia ações entre telas (Host Manager → Network Tools etc).
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFrame,
                              QLabel, QPushButton, QStackedWidget, QButtonGroup)
from PyQt5.QtCore import Qt

from src.ui.dashboard import DashboardScreen
from src.ui.asn_manager import AsnManagerScreen
from src.ui.host_manager import HostManagerScreen
from src.ui.discovery import DiscoveryScreen
from src.ui.network_tools import NetworkToolsScreen
from src.ui.logs_console import LogsConsoleScreen
from src.ui.settings import SettingsScreen
from src.version import __version__, __app_name__


class MainWindow(QMainWindow):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self._init_ui()
        self._wire_cross_screen_actions()

    def _init_ui(self):
        self.setWindowTitle(f"{__app_name__} v{__version__} — Network Peering Mapper")
        self.resize(1280, 820)

        central = QWidget(self)
        self.setCentralWidget(central)
        main = QHBoxLayout(central)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        # ─── Sidebar ───
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(240)
        sl = QVBoxLayout(sidebar)
        sl.setContentsMargins(14, 22, 14, 18)
        sl.setSpacing(0)

        # Brand
        brand = QFrame()
        bl = QVBoxLayout(brand)
        bl.setContentsMargins(6, 4, 4, 18)
        bl.setSpacing(2)
        bt = QLabel("fzBGPTools")
        bt.setStyleSheet("font-size: 18px; font-weight: 800; color: #e7ecf7; letter-spacing: 0.04em;")
        bs = QLabel(f"PEERING MAPPER · v{__version__}")
        bs.setStyleSheet("font-size: 9.5px; color: #6b7693; letter-spacing: 0.18em; font-weight: 600;")
        bl.addWidget(bt); bl.addWidget(bs)
        sl.addWidget(brand)

        sl.addWidget(self._nav_label("OPERAÇÃO"))
        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)
        self.dash_btn  = self._nav_item("Dashboard",   "dashboard", checked=True)
        self.asn_btn   = self._nav_item("ASN Manager", "asn")
        self.hosts_btn = self._nav_item("Host Manager","hosts")
        sl.addWidget(self.dash_btn); sl.addWidget(self.asn_btn); sl.addWidget(self.hosts_btn)

        sl.addWidget(self._nav_label("DIAGNÓSTICO"))
        self.discovery_btn = self._nav_item("Auto Descoberta", "discovery")
        self.tools_btn     = self._nav_item("Network Tools",   "tools")
        self.logs_btn      = self._nav_item("Console de Logs", "logs")
        sl.addWidget(self.discovery_btn); sl.addWidget(self.tools_btn); sl.addWidget(self.logs_btn)

        sl.addWidget(self._nav_label("SISTEMA"))
        self.settings_btn = self._nav_item("Configurações", "settings")
        sl.addWidget(self.settings_btn)

        sl.addStretch()

        # Footer
        footer = QFrame()
        fl = QVBoxLayout(footer)
        fl.setContentsMargins(0, 14, 0, 0)
        fl.setSpacing(10)
        footer.setStyleSheet("border-top: 1px solid rgba(110, 140, 220, 0.14);")

        status_pill = QFrame()
        status_pill.setStyleSheet(
            "background-color: rgba(74, 222, 128, 0.06); "
            "border: 1px solid rgba(74, 222, 128, 0.18); border-radius: 8px;")
        sp_l = QHBoxLayout(status_pill)
        sp_l.setContentsMargins(10, 8, 10, 8)
        dot = QLabel(); dot.setFixedSize(8, 8)
        dot.setStyleSheet("background-color: #4ade80; border-radius: 4px;")
        st = QLabel("Monitorando")
        st.setStyleSheet("color: #4ade80; font-size: 11px; font-weight: 700;")
        sp_l.addWidget(dot); sp_l.addWidget(st); sp_l.addStretch()
        fl.addWidget(status_pill)

        version_lbl = QLabel(f"v{__version__} · build local")
        version_lbl.setStyleSheet("color: #6b7693; font-size: 10px; padding: 4px 6px;")
        fl.addWidget(version_lbl)
        sl.addWidget(footer)

        main.addWidget(sidebar)

        # ─── Right pane ───
        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(0)

        topbar = QFrame()
        topbar.setFixedHeight(56)
        topbar.setStyleSheet("background-color: rgba(11,15,25,0.4); "
                             "border-bottom: 1px solid rgba(110, 140, 220, 0.14);")
        tl = QHBoxLayout(topbar)
        tl.setContentsMargins(28, 0, 28, 0)
        self.crumb = QLabel("Operação / <b>Dashboard</b>")
        self.crumb.setObjectName("Crumb")
        tl.addWidget(self.crumb)
        tl.addStretch()
        refresh = QPushButton("↻")
        refresh.setFixedSize(36, 36)
        refresh.setObjectName("Btn")
        refresh.clicked.connect(self.trigger_refresh)
        tl.addWidget(refresh)
        rl.addWidget(topbar)

        # Stack of screens
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background-color: transparent;")

        self.screen_dashboard = DashboardScreen(self.db)
        self.screen_asn       = AsnManagerScreen(self.db)
        self.screen_hosts     = HostManagerScreen(self.db)
        self.screen_discovery = DiscoveryScreen(self.db)
        self.screen_tools     = NetworkToolsScreen(self.db)
        self.screen_logs      = LogsConsoleScreen(self.db)
        self.screen_settings  = SettingsScreen(self.db)

        for s in (self.screen_dashboard, self.screen_asn, self.screen_hosts,
                  self.screen_discovery, self.screen_tools,
                  self.screen_logs, self.screen_settings):
            self.stack.addWidget(s)

        view_container = QWidget()
        vc = QVBoxLayout(view_container)
        vc.setContentsMargins(28, 24, 28, 30)
        vc.addWidget(self.stack)
        rl.addWidget(view_container, 1)

        main.addWidget(right, 1)

    def _wire_cross_screen_actions(self):
        # Host Manager → Network Tools
        self.screen_hosts.ping_requested.connect(self.screen_tools.quick_ping)
        self.screen_hosts.trace_requested.connect(self.screen_tools.quick_trace)
        self.screen_hosts.ssh_requested.connect(self.screen_tools.quick_ssh)
        self.screen_hosts.telnet_requested.connect(self.screen_tools.quick_telnet)
        self.screen_hosts.ping_requested.connect(lambda _: self._switch("tools"))
        self.screen_hosts.trace_requested.connect(lambda _: self._switch("tools"))
        self.screen_hosts.ssh_requested.connect(lambda _: self._switch("tools"))
        self.screen_hosts.telnet_requested.connect(lambda _: self._switch("tools"))

        # Discovery → Network Tools / Host Manager
        self.screen_discovery.ssh_requested.connect(self.screen_tools.quick_ssh)
        self.screen_discovery.ssh_requested.connect(lambda _: self._switch("tools"))
        self.screen_discovery.ping_requested.connect(self.screen_tools.quick_ping)
        self.screen_discovery.ping_requested.connect(lambda _: self._switch("tools"))
        self.screen_discovery.register_host_requested.connect(self._register_discovered_host)

    def _register_discovered_host(self, ip, hostname, vendor):
        """Cria um host na tabela hosts a partir de uma linha do Discovery."""
        vendor = vendor or "Outro"
        type_ = "Router" if vendor in ("MikroTik", "Cisco", "Juniper") else "Server"
        self.db.add_host(ip, hostname or ip, 22, 23, "", "", type_, vendor, "Discovery", "Online")
        self.db.add_log("INFO", "Discovery", f"Host {hostname} ({ip}) registrado a partir da descoberta.")
        self.screen_hosts.load_data()
        self.screen_tools.refresh_lists()
        self._switch("hosts")

    def _nav_label(self, text):
        l = QLabel(text)
        l.setStyleSheet("font-size: 9px; color: #6b7693; letter-spacing: 0.18em; "
                        "font-weight: bold; padding: 14px 10px 6px;")
        return l

    def _nav_item(self, text, name, checked=False):
        btn = QPushButton(text)
        btn.setObjectName("NavItem")
        btn.setCheckable(True)
        self.btn_group.addButton(btn)
        if checked:
            btn.setChecked(True)
        btn.clicked.connect(lambda: self._switch(name))
        return btn

    def _switch(self, name):
        m = {
            "dashboard": (0, "Operação / <b>Dashboard</b>",        self.dash_btn,  lambda: self.screen_dashboard.refresh_data()),
            "asn":       (1, "Operação / <b>ASN Manager</b>",      self.asn_btn,   lambda: self.screen_asn.load_data()),
            "hosts":     (2, "Operação / <b>Host Manager</b>",     self.hosts_btn, lambda: self.screen_hosts.load_data()),
            "discovery": (3, "Diagnóstico / <b>Auto Descoberta</b>",self.discovery_btn, lambda: self.screen_discovery.refresh_groups()),
            "tools":     (4, "Diagnóstico / <b>Network Tools</b>", self.tools_btn, lambda: self.screen_tools.refresh_lists()),
            "logs":      (5, "Diagnóstico / <b>Console de Logs</b>",self.logs_btn, lambda: self.screen_logs.load_logs()),
            "settings":  (6, "Sistema / <b>Configurações</b>",     self.settings_btn, lambda: self.screen_settings.update_db_size()),
        }
        if name not in m:
            return
        idx, crumb, btn, refresh = m[name]
        self.crumb.setText(crumb)
        self.stack.setCurrentIndex(idx)
        btn.setChecked(True)
        try:
            refresh()
        except Exception:
            pass

    def trigger_refresh(self):
        idx = self.stack.currentIndex()
        refreshers = [
            self.screen_dashboard.refresh_data,
            self.screen_asn.load_data,
            self.screen_hosts.load_data,
            self.screen_discovery.refresh_groups,
            self.screen_tools.refresh_lists,
            self.screen_logs.load_logs,
            self.screen_settings.update_db_size,
        ]
        if 0 <= idx < len(refreshers):
            try:
                refreshers[idx]()
            except Exception:
                pass
