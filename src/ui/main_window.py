from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel, QPushButton, QStackedWidget, QButtonGroup
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from src.ui.dashboard import DashboardScreen
from src.ui.asn_manager import AsnManagerScreen
from src.ui.host_manager import HostManagerScreen
from src.ui.network_tools import NetworkToolsScreen
from src.ui.logs_console import LogsConsoleScreen
from src.ui.settings import SettingsScreen

class MainWindow(QMainWindow):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("fzBGPTools — Network Peering Mapper")
        self.resize(1200, 800)
        
        # Central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 1. Left Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(240)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(14, 22, 14, 18)
        sidebar_layout.setSpacing(0)
        
        # Brand Block
        brand_frame = QFrame()
        brand_layout = QVBoxLayout(brand_frame)
        brand_layout.setContentsMargins(4, 4, 4, 18)
        brand_layout.setSpacing(2)
        
        brand_title = QLabel("fzBGPTools")
        brand_title.setStyleSheet("font-size: 18px; font-weight: 800; color: #e7ecf7; letter-spacing: 0.05em;")
        brand_sub = QLabel("PEERING MAPPER")
        brand_sub.setStyleSheet("font-size: 10px; color: #6b7693; letter-spacing: 0.16em;")
        brand_layout.addWidget(brand_title)
        brand_layout.addWidget(brand_sub)
        sidebar_layout.addWidget(brand_frame)
        
        # Navigation label & Buttons
        sidebar_layout.addWidget(self.create_nav_label("OPERAÇÃO"))
        
        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)
        
        self.dash_btn = self.create_nav_item("Dashboard", "dashboard", True)
        self.asn_btn = self.create_nav_item("ASN Manager", "asn")
        self.hosts_btn = self.create_nav_item("Host Manager", "hosts")
        
        sidebar_layout.addWidget(self.dash_btn)
        sidebar_layout.addWidget(self.asn_btn)
        sidebar_layout.addWidget(self.hosts_btn)
        
        sidebar_layout.addWidget(self.create_nav_label("DIAGNÓSTICO"))
        
        self.tools_btn = self.create_nav_item("Network Tools", "tools")
        self.logs_btn = self.create_nav_item("Console de Logs", "logs")
        
        sidebar_layout.addWidget(self.tools_btn)
        sidebar_layout.addWidget(self.logs_btn)
        
        sidebar_layout.addWidget(self.create_nav_label("SISTEMA"))
        self.settings_btn = self.create_nav_item("Configurações", "settings")
        sidebar_layout.addWidget(self.settings_btn)
        
        # Spacer
        sidebar_layout.addStretch()
        
        # Sidebar Footer
        footer = QFrame()
        footer_layout = QVBoxLayout(footer)
        footer_layout.setContentsMargins(0, 14, 0, 0)
        footer_layout.setSpacing(10)
        footer.setStyleSheet("border-top: 1px solid rgba(110, 140, 220, 0.14);")
        
        # Status Pill
        status_pill = QFrame()
        status_pill.setObjectName("StatCard")
        status_pill.setStyleSheet("background-color: rgba(74, 222, 128, 0.06); border: 1px solid rgba(74, 222, 128, 0.18); border-radius: 8px;")
        sp_layout = QHBoxLayout(status_pill)
        sp_layout.setContentsMargins(10, 8, 10, 8)
        
        dot = QLabel()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet("background-color: #4ade80; border-radius: 4px;")
        status_text = QLabel("Monitorando")
        status_text.setStyleSheet("color: #4ade80; font-size: 11px; font-weight: bold;")
        
        sp_layout.addWidget(dot)
        sp_layout.addWidget(status_text)
        sp_layout.addStretch()
        footer_layout.addWidget(status_pill)
        
        # Profile Card
        profile = QFrame()
        profile.setObjectName("StatCard")
        p_layout = QHBoxLayout(profile)
        p_layout.setContentsMargins(8, 8, 8, 8)
        
        avatar = QLabel("RL")
        avatar.setFixedSize(30, 30)
        avatar.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #3da9fc, stop:1 #a18cff); color: #0b0f19; font-weight: bold; font-size: 11px; border-radius: 6px; qproperty-alignment: AlignCenter;")
        
        name_info = QFrame()
        ni_layout = QVBoxLayout(name_info)
        ni_layout.setContentsMargins(0, 0, 0, 0)
        ni_layout.setSpacing(2)
        
        p_name = QLabel("Roger Luft")
        p_name.setStyleSheet("font-size: 11px; font-weight: bold; color: #e7ecf7;")
        p_role = QLabel("Administrador")
        p_role.setStyleSheet("font-size: 9px; color: #6b7693;")
        
        ni_layout.addWidget(p_name)
        ni_layout.addWidget(p_role)
        
        p_layout.addWidget(avatar)
        p_layout.addWidget(name_info)
        p_layout.addStretch()
        
        footer_layout.addWidget(profile)
        sidebar_layout.addWidget(footer)
        
        main_layout.addWidget(sidebar)
        
        # 2. Right Content Pane
        right_pane = QWidget()
        right_layout = QVBoxLayout(right_pane)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        # Topbar
        topbar = QFrame()
        topbar.setFixedHeight(56)
        topbar.setStyleSheet("background-color: rgba(11, 15, 25, 0.4); border-bottom: 1px solid rgba(110, 140, 220, 0.14);")
        topbar_layout = QHBoxLayout(topbar)
        topbar_layout.setContentsMargins(28, 0, 28, 0)
        
        self.crumb_lbl = QLabel("Operação / <b>Dashboard</b>")
        self.crumb_lbl.setObjectName("Crumb")
        topbar_layout.addWidget(self.crumb_lbl)
        
        topbar_layout.addStretch()
        
        # Refresh and notification buttons
        refresh_btn = QPushButton("↻")
        refresh_btn.setFixedSize(36, 36)
        refresh_btn.setObjectName("Btn")
        refresh_btn.clicked.connect(self.trigger_refresh)
        topbar_layout.addWidget(refresh_btn)
        
        right_layout.addWidget(topbar)
        
        # Stacked Screens
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background-color: transparent;")
        
        self.screen_dashboard = DashboardScreen(self.db)
        self.screen_asn = AsnManagerScreen(self.db)
        self.screen_hosts = HostManagerScreen(self.db)
        self.screen_tools = NetworkToolsScreen(self.db)
        self.screen_logs = LogsConsoleScreen(self.db)
        self.screen_settings = SettingsScreen(self.db)
        
        self.stacked_widget.addWidget(self.screen_dashboard)  # Index 0
        self.stacked_widget.addWidget(self.screen_asn)        # Index 1
        self.stacked_widget.addWidget(self.screen_hosts)      # Index 2
        self.stacked_widget.addWidget(self.screen_tools)      # Index 3
        self.stacked_widget.addWidget(self.screen_logs)       # Index 4
        self.stacked_widget.addWidget(self.screen_settings)   # Index 5
        
        # View area with padding
        view_container = QWidget()
        vc_layout = QVBoxLayout(view_container)
        vc_layout.setContentsMargins(28, 24, 28, 30)
        vc_layout.addWidget(self.stacked_widget)
        
        right_layout.addWidget(view_container)
        main_layout.addWidget(right_pane)

    def create_nav_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("font-size: 9px; color: #6b7693; letter-spacing: 0.18em; font-weight: bold; padding: 14px 10px 6px;")
        return lbl

    def create_nav_item(self, text, screen_name, active=False):
        btn = QPushButton(text)
        btn.setObjectName("NavItem")
        btn.setCheckable(True)
        self.btn_group.addButton(btn)
        
        if active:
            btn.setChecked(True)
            
        btn.clicked.connect(lambda: self.switch_screen(screen_name))
        return btn

    def switch_screen(self, screen_name):
        # Update breadcrumbs and active stacked widget index
        if screen_name == "dashboard":
            self.crumb_lbl.setText("Operação / <b>Dashboard</b>")
            self.stacked_widget.setCurrentIndex(0)
            self.screen_dashboard.refresh_data()
        elif screen_name == "asn":
            self.crumb_lbl.setText("Operação / <b>ASN Manager</b>")
            self.stacked_widget.setCurrentIndex(1)
            self.screen_asn.load_data()
        elif screen_name == "hosts":
            self.crumb_lbl.setText("Operação / <b>Host Manager</b>")
            self.stacked_widget.setCurrentIndex(2)
            self.screen_hosts.load_data()
        elif screen_name == "tools":
            self.crumb_lbl.setText("Diagnóstico / <b>Network Tools</b>")
            self.stacked_widget.setCurrentIndex(3)
            self.screen_tools.refresh_lists()
        elif screen_name == "logs":
            self.crumb_lbl.setText("Diagnóstico / <b>Console de Logs</b>")
            self.stacked_widget.setCurrentIndex(4)
            self.screen_logs.load_logs()
        elif screen_name == "settings":
            self.crumb_lbl.setText("Sistema / <b>Configurações</b>")
            self.stacked_widget.setCurrentIndex(5)
            self.screen_settings.update_db_size()

    def trigger_refresh(self):
        current_idx = self.stacked_widget.currentIndex()
        if current_idx == 0:
            self.screen_dashboard.refresh_data()
        elif current_idx == 1:
            self.screen_asn.load_data()
        elif current_idx == 2:
            self.screen_hosts.load_data()
        elif current_idx == 3:
            self.screen_tools.refresh_lists()
        elif current_idx == 4:
            self.screen_logs.load_logs()
        elif current_idx == 5:
            self.screen_settings.update_db_size()
