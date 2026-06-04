"""
Janela principal — sidebar, topbar, stacked screens.
Adiciona Discovery e fia ações entre telas (Host Manager → Network Tools etc).
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFrame,
                              QLabel, QPushButton, QStackedWidget, QButtonGroup, QLineEdit,
                              QScrollArea, QDialog)
from PyQt5.QtCore import Qt, QTimer, QUrl, QPoint
from PyQt5.QtGui import QFont, QColor, QDesktopServices

from src.ui.dashboard import DashboardScreen
from src.ui.asn_manager import AsnManagerScreen
from src.ui.host_manager import HostManagerScreen
from src.ui.discovery import DiscoveryScreen
from src.ui.network_tools import NetworkToolsScreen
from src.ui.logs_console import LogsConsoleScreen
from src.ui.settings import SettingsScreen
from src.version import __version__, __app_name__
from src.engine.updater import UpdateChecker


class AlertsDropdown(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent, Qt.Popup | Qt.FramelessWindowHint)
        self.db = db
        self.parent_window = parent
        self.setFixedWidth(380)
        self.setFixedHeight(360)
        self.setObjectName("AlertsDropdownDialog")
        
        self.setStyleSheet("""
            QDialog#AlertsDropdownDialog {
                background-color: #0e1424;
                border: 1px solid rgba(120, 160, 240, 0.28);
                border-radius: 12px;
            }
        """)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        head = QFrame()
        head.setStyleSheet("background-color: transparent; border-bottom: 1px solid rgba(110, 140, 220, 0.14);")
        hl = QHBoxLayout(head)
        hl.setContentsMargins(14, 12, 14, 12)
        
        title = QLabel("ALERTAS BGP")
        title.setStyleSheet("font-size: 11px; font-weight: bold; color: #e7ecf7; letter-spacing: 0.04em;")
        hl.addWidget(title)
        
        alerts = self.db.get_alerts()
        crit_count = sum(1 for a in alerts if a[0] == "critical")
        
        hl.addStretch()
        
        crit_badge = QLabel(f"{crit_count} CRÍTICO{'S' if crit_count != 1 else ''}")
        crit_badge.setStyleSheet(
            "background-color: rgba(255, 92, 122, 0.14); color: #ff5c7a; "
            "border: 1px solid rgba(255, 92, 122, 0.32); border-radius: 6px; "
            "padding: 2px 6px; font-size: 10px; font-weight: bold;"
        )
        hl.addWidget(crit_badge)
        layout.addWidget(head)

        # Scroll area for alerts list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background-color: transparent;")
        
        content = QWidget()
        content.setStyleSheet("background-color: transparent;")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(10, 8, 10, 8)
        cl.setSpacing(8)

        if not alerts:
            empty = QLabel("Sem alertas ativos.")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet("color: #6b7693; font-size: 12px; padding: 20px;")
            cl.addWidget(empty)
        else:
            for sev, atitle, desc, meta, timestamp in alerts:
                item = QFrame()
                if sev == "critical":
                    border_color = "rgba(255, 92, 122, 0.15)"
                    bg_color = "rgba(255, 92, 122, 0.04)"
                    icon_color = "#ff5c7a"
                else:
                    border_color = "rgba(251, 191, 36, 0.15)"
                    bg_color = "rgba(251, 191, 36, 0.04)"
                    icon_color = "#fbbf24"
                    
                item.setStyleSheet(f"""
                    QFrame {{
                        background-color: {bg_color};
                        border: 1px solid {border_color};
                        border-radius: 8px;
                    }}
                """)
                il = QHBoxLayout(item)
                il.setContentsMargins(10, 10, 10, 10)
                il.setSpacing(10)

                ico = QLabel("⚠️" if sev == "critical" else "⚡")
                ico.setFixedSize(22, 22)
                ico.setAlignment(Qt.AlignCenter)
                ico.setStyleSheet(f"background-color: rgba(255,255,255,0.03); border-radius: 4px; font-size: 12px; color: {icon_color};")
                il.addWidget(ico)

                body = QFrame()
                body.setStyleSheet("border: none; background: transparent;")
                bl = QVBoxLayout(body)
                bl.setContentsMargins(0, 0, 0, 0)
                bl.setSpacing(2)

                t_lbl = QLabel(atitle)
                t_lbl.setStyleSheet("font-size: 12px; font-weight: bold; color: #e7ecf7;")
                
                d_lbl = QLabel(desc)
                d_lbl.setWordWrap(True)
                d_lbl.setStyleSheet("font-size: 11px; color: #9aa6c2;")
                
                time_lbl = QLabel(str(timestamp)[:16])
                time_lbl.setStyleSheet("font-size: 10px; color: #6b7693; font-family: monospace;")
                
                bl.addWidget(t_lbl)
                bl.addWidget(d_lbl)
                bl.addWidget(time_lbl)
                il.addWidget(body, 1)
                
                cl.addWidget(item)
        
        cl.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        # Footer
        foot = QFrame()
        foot.setStyleSheet("background-color: rgba(11, 15, 25, 0.4); border-top: 1px solid rgba(110, 140, 220, 0.14);")
        ftl = QHBoxLayout(foot)
        ftl.setContentsMargins(12, 10, 12, 10)
        ftl.setSpacing(8)

        clear_btn = QPushButton("Limpar Alertas")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #ff5c7a;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """)
        clear_btn.clicked.connect(self.clear_alerts)
        
        view_btn = QPushButton("Ver no Dashboard")
        view_btn.setFixedHeight(28)
        view_btn.setStyleSheet("""
            QPushButton {
                background-color: #3da9fc;
                color: #0b0f19;
                font-weight: bold;
                font-size: 11px;
                border: none;
                border-radius: 6px;
                padding: 4px 10px;
            }
            QPushButton:hover {
                background-color: #21d4fd;
            }
        """)
        view_btn.clicked.connect(self.go_to_dashboard)

        ftl.addWidget(clear_btn)
        ftl.addStretch()
        ftl.addWidget(view_btn)
        layout.addWidget(foot)

    def clear_alerts(self):
        with self.db.get_conn() as conn:
            conn.cursor().execute("DELETE FROM alerts")
            conn.commit()
        self.db.add_log("INFO", "Alerts", "Todos os alertas marcados como lidos e removidos pelo usuário.")
        if hasattr(self.parent_window, "screen_dashboard"):
            self.parent_window.screen_dashboard.refresh_data()
        self.accept()

    def go_to_dashboard(self):
        if hasattr(self.parent_window, "_switch"):
            self.parent_window._switch("dashboard")
        self.accept()


class MainWindow(QMainWindow):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.updater = UpdateChecker(self)
        self.updater.state_changed.connect(self._on_update_state)
        
        self._init_ui()
        self._wire_cross_screen_actions()
        self.update_alerts_badge()

        # Update alerts count badge periodically
        self.badge_timer = QTimer(self)
        self.badge_timer.timeout.connect(self.update_alerts_badge)
        self.badge_timer.start(5000)

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
        bs = QLabel("PEERING MAPPER")
        bs.setStyleSheet("font-size: 9.5px; color: #6b7693; letter-spacing: 0.18em; font-weight: 600; text-transform: uppercase;")
        bc = QLabel("© Webstorage Tecnologia")
        bc.setStyleSheet("font-size: 9.5px; color: #6b7693; margin-top: 4px; opacity: 0.7;")
        bl.addWidget(bt)
        bl.addWidget(bs)
        bl.addWidget(bc)
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
        sp_l.addWidget(dot)
        sp_l.addWidget(st)
        sp_l.addStretch()
        
        small_as = QLabel("AS263870")
        small_as.setStyleSheet("color: #6b7693; font-size: 10.5px; font-weight: 500;")
        sp_l.addWidget(small_as)
        fl.addWidget(status_pill)

        # Upgrade button
        self.upgrade_btn = QPushButton("Verificar atualização")
        self.upgrade_btn.setObjectName("UpgradeBtn")
        self.upgrade_btn.clicked.connect(self.check_update)
        fl.addWidget(self.upgrade_btn)

        # User Card
        user_card = QFrame()
        user_card.setObjectName("UserCard")
        u_layout = QHBoxLayout(user_card)
        u_layout.setContentsMargins(8, 8, 8, 8)
        u_layout.setSpacing(10)
        
        avatar = QLabel("NA")
        avatar.setObjectName("UserAvatar")
        avatar.setFixedSize(32, 32)
        avatar.setAlignment(Qt.AlignCenter)
        
        info = QFrame()
        info.setStyleSheet("border: none; background: transparent;")
        info_layout = QVBoxLayout(info)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)
        name_lbl = QLabel("netadmin")
        name_lbl.setStyleSheet("font-size: 12px; font-weight: 600; color: #e7ecf7;")
        role_lbl = QLabel("Webstorage NOC")
        role_lbl.setStyleSheet("font-size: 11px; color: #6b7693;")
        info_layout.addWidget(name_lbl)
        info_layout.addWidget(role_lbl)
        
        u_layout.addWidget(avatar)
        u_layout.addWidget(info)
        u_layout.addStretch()
        fl.addWidget(user_card)

        # Author and License
        author_lbl = QLabel('Eng. <a href="https://about.rogerluft.com.br" style="color: #9aa6c2; text-decoration: none;">Roger Luft</a>')
        author_lbl.setOpenExternalLinks(True)
        author_lbl.setToolTip("roger@webstorage.com.br")
        author_lbl.setAlignment(Qt.AlignCenter)
        author_lbl.setStyleSheet("font-size: 10px; color: #6b7693; margin-top: 2px;")
        fl.addWidget(author_lbl)

        license_lbl = QLabel('<a href="https://creativecommons.org/licenses/by/4.0/" style="color: #6b7693; text-decoration: none; font-weight: bold;">CC BY 4.0</a>')
        license_lbl.setOpenExternalLinks(True)
        license_lbl.setAlignment(Qt.AlignCenter)
        license_lbl.setStyleSheet("font-size: 10px; color: #6b7693;")
        fl.addWidget(license_lbl)

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
        tl.setSpacing(12)

        self.crumb = QLabel("Operação / <b>Dashboard</b>")
        self.crumb.setObjectName("Crumb")
        tl.addWidget(self.crumb)
        tl.addStretch()

        # Global Add Dropdown Menu
        self.add_asset_btn = QPushButton("＋ Adicionar")
        self.add_asset_btn.setObjectName("BtnPrimary")
        self.add_asset_btn.setFixedHeight(36)
        self.add_asset_btn.setMinimumWidth(110)
        
        from PyQt5.QtWidgets import QMenu
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #0e1424;
                color: #e7ecf7;
                border: 1px solid rgba(120, 160, 240, 0.28);
                border-radius: 8px;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #3da9fc;
                color: #0b0f19;
                font-weight: bold;
            }
        """)
        action_asn = menu.addAction("Novo ASN")
        action_host = menu.addAction("Novo Host")
        action_asn.triggered.connect(self._add_asn_global)
        action_host.triggered.connect(self._add_host_global)
        self.add_asset_btn.setMenu(menu)
        tl.addWidget(self.add_asset_btn)

        # Global Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar ASN, IP, hostname...")
        self.search_input.setFixedWidth(280)
        self.search_input.setObjectName("SearchInput")
        self.search_input.textChanged.connect(self.on_global_search)
        tl.addWidget(self.search_input)

        # Keyboard shortcut label ⌘K
        self.kbd_lbl = QLabel("⌘K")
        self.kbd_lbl.setStyleSheet("font-size: 10px; padding: 2px 6px; border-radius: 4px; background-color: rgba(255,255,255,0.06); color: #6b7693; border: 1px solid rgba(110, 140, 220, 0.14);")
        tl.addWidget(self.kbd_lbl)

        # Alerts Button with Badge Overlay
        self.alerts_btn = QPushButton("🔔")
        self.alerts_btn.setObjectName("AlertsBtn")
        self.alerts_btn.setFixedSize(36, 36)
        self.alerts_btn.clicked.connect(self.show_alerts_dropdown)
        tl.addWidget(self.alerts_btn)

        # Alerts Badge
        self.alerts_badge = QLabel("0", self.alerts_btn)
        self.alerts_badge.setStyleSheet(
            "background-color: #ff5c7a; color: #0b0f19; border-radius: 7px; "
            "font-size: 9px; font-weight: bold; border: 1.5px solid #0e1424;"
        )
        self.alerts_badge.setFixedSize(15, 15)
        self.alerts_badge.setAlignment(Qt.AlignCenter)
        self.alerts_badge.move(20, -1)
        self.alerts_badge.hide()

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
        
        # Reset search box text when switching screens
        self.search_input.clear()
        
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
        self.update_alerts_badge()

    # ─── Mockup Updates fiação ───
    def check_update(self):
        self.updater.check()

    def _on_update_state(self, state):
        # idle | checking | uptodate | available | error
        if state == "checking":
            self.upgrade_btn.setText("Verificando...")
            self.upgrade_btn.setEnabled(False)
            self.upgrade_btn.setStyleSheet("background-color: rgba(251, 191, 36, 0.08); border: 1px solid rgba(251, 191, 36, 0.28); color: #fbbf24; font-weight: 600; padding: 8px 12px; border-radius: 8px;")
        elif state == "available":
            self.upgrade_btn.setText("Atualização disponível")
            self.upgrade_btn.setEnabled(True)
            self.upgrade_btn.setStyleSheet("background-color: rgba(161, 140, 255, 0.10); border: 1px solid rgba(161, 140, 255, 0.32); color: #a18cff; font-weight: 600; padding: 8px 12px; border-radius: 8px;")
            self.upgrade_btn.clicked.disconnect()
            self.upgrade_btn.clicked.connect(self._open_release_url)
        elif state == "uptodate":
            self.upgrade_btn.setText("✓ Atualizado")
            self.upgrade_btn.setEnabled(False)
            self.upgrade_btn.setStyleSheet("background-color: rgba(74, 222, 128, 0.08); border: 1px solid rgba(74, 222, 128, 0.28); color: #4ade80; font-weight: 600; padding: 8px 12px; border-radius: 8px;")
            QTimer.singleShot(3000, self._reset_upgrade_btn)
        elif state == "error" or state == "idle":
            self.upgrade_btn.setText("Verificar atualização")
            self.upgrade_btn.setEnabled(True)
            self.upgrade_btn.setStyleSheet("")
            try:
                self.upgrade_btn.clicked.disconnect()
            except Exception:
                pass
            self.upgrade_btn.clicked.connect(self.check_update)

    def _open_release_url(self):
        QDesktopServices.openUrl(QUrl("https://fzrepo.rogerluft.com.br/webstorage/fzBGPTools/releases/latest"))
        self._reset_upgrade_btn()

    def _reset_upgrade_btn(self):
        self.upgrade_btn.setText("Verificar atualização")
        self.upgrade_btn.setEnabled(True)
        self.upgrade_btn.setStyleSheet("")
        try:
            self.upgrade_btn.clicked.disconnect()
        except Exception:
            pass
        self.upgrade_btn.clicked.connect(self.check_update)

    def show_alerts_dropdown(self):
        dropdown = AlertsDropdown(self.db, self)
        # Position right below the alerts button
        btn_pos = self.alerts_btn.mapToGlobal(self.alerts_btn.rect().bottomLeft())
        x = btn_pos.x() + self.alerts_btn.width() - dropdown.width()
        y = btn_pos.y() + 4
        dropdown.move(x, y)
        dropdown.exec_()
        self.update_alerts_badge()

    def update_alerts_badge(self):
        try:
            alerts = self.db.get_alerts()
            count = len(alerts)
            if count > 0:
                self.alerts_badge.setText(str(count))
                self.alerts_badge.show()
            else:
                self.alerts_badge.hide()
        except Exception:
            pass

    def on_global_search(self, text):
        idx = self.stack.currentIndex()
        screens = [
            None,                  # Dashboard - no search
            self.screen_asn,       # ASN Manager
            self.screen_hosts,     # Host Manager
            None,                  # Auto Descoberta - no search
            None,                  # Network Tools - no search
            None,                  # Console de Logs - no search
            None                   # Settings - no search
        ]
        if idx < len(screens) and screens[idx] is not None:
            screen = screens[idx]
            if hasattr(screen, "search") and isinstance(screen.search, QLineEdit):
                screen.search.setText(text)

    def _add_asn_global(self):
        self._switch("asn")
        self.screen_asn.add_asn()

    def _add_host_global(self):
        self._switch("hosts")
        self.screen_hosts.add_host()

    def keyPressEvent(self, event):
        # Ctrl+K focus search
        if event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_K:
            self.search_input.setFocus()
            self.search_input.selectAll()
            event.accept()
        else:
            super().keyPressEvent(event)
