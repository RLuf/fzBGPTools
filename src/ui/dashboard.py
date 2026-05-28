import math
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QFrame, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt, QTimer, QPointF
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont, QLinearGradient, QPolygonF

NODES = [
    {"id": "AS263870", "org": "Webstorage", "type": "self",    "x": 0.50, "y": 0.50, "asn": "263870", "sub": "OWN"},
    {"id": "AS262332", "org": "IX.br SP",   "type": "ix",      "x": 0.25, "y": 0.20, "asn": "262332", "sub": "PTT"},
    {"id": "AS12956",  "org": "Telefônica", "type": "transit", "x": 0.75, "y": 0.25, "asn": "12956",  "sub": "TRA"},
    {"id": "AS174",    "org": "Cogent",     "type": "transit", "x": 0.80, "y": 0.70, "asn": "174",    "sub": "TRA"},
    {"id": "AS15169",  "org": "Google",     "type": "dest",    "x": 0.20, "y": 0.75, "asn": "15169",  "sub": "DST"},
    {"id": "AS16509",  "org": "AWS",        "type": "dest",    "x": 0.55, "y": 0.85, "asn": "16509",  "sub": "DST"},
]

EDGES = [
    {"from": "AS263870", "to": "AS262332", "label": "Public Peering", "kind": "public", "bps": "1.2 Gbps"},
    {"from": "AS263870", "to": "AS12956",  "label": "Trânsito IP",    "kind": "transit", "bps": "850 Mbps"},
    {"from": "AS263870", "to": "AS174",    "label": "Trânsito IP",    "kind": "transit", "bps": "620 Mbps"},
    {"from": "AS262332", "to": "AS15169",  "label": "BGP Peering",    "kind": "peering", "bps": "340 Mbps"},
    {"from": "AS262332", "to": "AS16509",  "label": "BGP Peering",    "kind": "peering", "bps": "510 Mbps"},
    {"from": "AS12956",  "to": "AS15169",  "label": "Trânsito",       "kind": "transit", "bps": "210 Mbps"},
    {"from": "AS174",    "to": "AS16509",  "label": "Trânsito",       "kind": "transit", "bps": "280 Mbps"},
]

class BGPGraphWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dash_offset = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(50)  # 20 FPS

    def animate(self):
        self.dash_offset = (self.dash_offset - 1) % 20
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        # Draw grid backdrop
        painter.setPen(QPen(QColor(255, 255, 255, 6), 1))
        grid_size = 48
        for x in range(0, w, grid_size):
            painter.drawLine(x, 0, x, h)
        for y in range(0, h, grid_size):
            painter.drawLine(0, y, w, y)

        # Helper to get node position
        def get_pos(node):
            return QPointF(node["x"] * w, node["y"] * h)

        # Draw Edges (Connection Lines)
        for edge in EDGES:
            node_from = next(n for n in NODES if n["id"] == edge["from"])
            node_to = next(n for n in NODES if n["id"] == edge["to"])
            
            p1 = get_pos(node_from)
            p2 = get_pos(node_to)
            
            # Draw line
            pen = QPen()
            if edge["kind"] == "public":
                color = QColor("#a18cff")
            elif edge["kind"] == "transit":
                color = QColor("#94a3b8")
            else:
                color = QColor("#21d4fd")
                
            pen.setColor(color)
            pen.setWidth(2)
            pen.setStyle(Qt.DashLine)
            pen.setDashOffset(self.dash_offset)
            painter.setPen(pen)
            
            # Adjust line to end outside node radius (radius is 40)
            dx = p2.x() - p1.x()
            dy = p2.y() - p1.y()
            dist = math.hypot(dx, dy)
            if dist > 80:
                sx = p1.x() + (dx / dist) * 40
                sy = p1.y() + (dy / dist) * 40
                ex = p2.x() - (dx / dist) * 45
                ey = p2.y() - (dy / dist) * 45
                painter.drawLine(QPointF(sx, sy), QPointF(ex, ey))
                
                # Draw arrowhead at endpoint (ex, ey)
                arrow_pen = QPen(color, 2)
                painter.setPen(arrow_pen)
                painter.setBrush(QBrush(color))
                angle = math.atan2(dy, dx)
                arrow_size = 8
                ap1 = QPointF(ex - arrow_size * math.cos(angle - math.pi/6), ey - arrow_size * math.sin(angle - math.pi/6))
                ap2 = QPointF(ex - arrow_size * math.cos(angle + math.pi/6), ey - arrow_size * math.sin(angle + math.pi/6))
                poly = QPolygonF([QPointF(ex, ey), ap1, ap2])
                painter.drawPolygon(poly)
                
                # Draw edge label in the middle
                mx = (sx + ex) / 2
                my = (sy + ey) / 2
                painter.setPen(QPen(QColor("#9aa6c2"), 1))
                painter.setFont(QFont("Inter", 8))
                painter.drawText(int(mx - 30), int(my - 6), f"{edge['bps']}")

        # Draw Nodes
        for node in NODES:
            p = get_pos(node)
            
            # Node glow & border gradients
            grad = QLinearGradient(p.x() - 40, p.y() - 40, p.x() + 40, p.y() + 40)
            if node["type"] == "self":
                grad.setColorAt(0, QColor("#1e40af"))
                grad.setColorAt(1, QColor("#3da9fc"))
                glow_color = QColor(61, 169, 252, 60)
            elif node["type"] == "ix":
                grad.setColorAt(0, QColor("#6d28d9"))
                grad.setColorAt(1, QColor("#a18cff"))
                glow_color = QColor(161, 140, 255, 50)
            elif node["type"] == "transit":
                grad.setColorAt(0, QColor("#475569"))
                grad.setColorAt(1, QColor("#94a3b8"))
                glow_color = QColor(148, 163, 184, 30)
            else: # dest
                grad.setColorAt(0, QColor("#15803d"))
                grad.setColorAt(1, QColor("#4ade80"))
                glow_color = QColor(74, 222, 128, 40)
                
            # Draw glow
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(glow_color))
            painter.drawEllipse(p, 46, 46)
            
            # Draw Node circle
            painter.setBrush(QBrush(grad))
            painter.setPen(QPen(QColor(255, 255, 255, 40), 1.5))
            painter.drawEllipse(p, 36, 36)
            
            # Draw labels
            painter.setPen(QPen(QColor("#ffffff"), 1))
            painter.setFont(QFont("Inter", 9, QFont.Bold))
            asn_text = f"AS{node['asn']}"
            painter.drawText(int(p.x() - 30), int(p.y() - 2), 60, 16, Qt.AlignCenter, asn_text)
            
            painter.setPen(QPen(QColor("rgba(255,255,255,0.7)"), 1))
            painter.setFont(QFont("Inter", 8))
            painter.drawText(int(p.x() - 30), int(p.y() + 12), 60, 12, Qt.AlignCenter, node["sub"])
            
            # Draw Org Name below node
            painter.setPen(QPen(QColor("#e7ecf7"), 1))
            painter.setFont(QFont("Inter", 8, QFont.Bold))
            painter.drawText(int(p.x() - 60), int(p.y() + 48), 120, 14, Qt.AlignCenter, node["id"])
            
            painter.setPen(QPen(QColor("#6b7693"), 1))
            painter.setFont(QFont("Inter", 8))
            painter.drawText(int(p.x() - 60), int(p.y() + 60), 120, 14, Qt.AlignCenter, node["org"])

class DashboardScreen(QWidget):
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
        
        title_lbl = QLabel("Mapa de Peering BGP")
        title_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #3da9fc;")
        sub_lbl = QLabel("Visualização ao vivo das sessões eBGP de AS263870 — sessões públicas, trânsitos e destinos prioritários.")
        sub_lbl.setStyleSheet("font-size: 12px; color: #9aa6c2;")
        title_layout.addWidget(title_lbl)
        title_layout.addWidget(sub_lbl)
        
        btn_layout = QHBoxLayout()
        refresh_btn = QPushButton("Atualizar")
        refresh_btn.setObjectName("Btn")
        refresh_btn.clicked.connect(self.refresh_data)
        new_sess_btn = QPushButton("Nova sessão BGP")
        new_sess_btn.setObjectName("BtnPrimary")
        btn_layout.addWidget(refresh_btn)
        btn_layout.addWidget(new_sess_btn)
        
        header_layout.addWidget(title_block)
        header_layout.addStretch()
        header_layout.addLayout(btn_layout)
        layout.addWidget(header_frame)
        
        # Stats row
        stats_frame = QFrame()
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(12)
        
        self.stat_cards = []
        stats_data = [
            ("Sessões eBGP", "7 / 7", "↑ 100% Established", "up"),
            ("Prefixos recebidos", "964.3 K", "+1.2K nas últimas 24h", "up"),
            ("Hosts monitorados", "152 / 156", "152 online · 4 offline", "up"),
            ("Tráfego agregado", "3.81 Gbps", "↑ 8.4% vs ontem", "up"),
            ("Alertas ativos", "3", "2 críticos · 1 warn", "dn")
        ]
        
        for title, val, delta, status in stats_data:
            card = QFrame()
            card.setObjectName("StatCard")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(14, 14, 14, 14)
            card_layout.setSpacing(4)
            
            lbl = QLabel(title)
            lbl.setObjectName("StatLabel")
            v_lbl = QLabel(val)
            v_lbl.setObjectName("StatValue")
            d_lbl = QLabel(delta)
            d_lbl.setObjectName("StatDelta")
            d_lbl.setProperty("status", status)
            
            card_layout.addWidget(lbl)
            card_layout.addWidget(v_lbl)
            card_layout.addWidget(d_lbl)
            stats_layout.addWidget(card)
            
        layout.addWidget(stats_frame)
        
        # Main Grid Layout (Graph left, Alerts/Traceroute right)
        grid_frame = QFrame()
        grid_layout = QHBoxLayout(grid_frame)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(16)
        
        # Left Graph Card
        graph_card = QFrame()
        graph_card.setObjectName("Card")
        graph_card_layout = QVBoxLayout(graph_card)
        graph_card_layout.setContentsMargins(0, 0, 0, 0)
        graph_card_layout.setSpacing(0)
        
        graph_header = QFrame()
        graph_header.setObjectName("CardHeader")
        graph_header_layout = QHBoxLayout(graph_header)
        graph_header_layout.setContentsMargins(14, 12, 14, 12)
        gh_title = QLabel("TOPOLOGIA / PEERING BGP")
        gh_title.setObjectName("CardTitle")
        graph_header_layout.addWidget(gh_title)
        graph_header_layout.addStretch()
        live_badge = QLabel("Live · 1s")
        live_badge.setStyleSheet("color: #4ade80; background-color: rgba(74,222,128,0.1); border: 1px solid rgba(74,222,128,0.3); border-radius: 4px; padding: 2px 8px; font-size: 11px; font-weight: bold;")
        graph_header_layout.addWidget(live_badge)
        graph_card_layout.addWidget(graph_header)
        
        self.graph_widget = BGPGraphWidget()
        graph_card_layout.addWidget(self.graph_widget)
        
        # Right Side (Alerts + Traceroute)
        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(16)
        
        # Alerts Card
        alerts_card = QFrame()
        alerts_card.setObjectName("Card")
        alerts_card.setFixedHeight(230)
        alerts_layout = QVBoxLayout(alerts_card)
        alerts_layout.setContentsMargins(0, 0, 0, 0)
        alerts_layout.setSpacing(0)
        
        alerts_header = QFrame()
        alerts_header.setObjectName("CardHeader")
        alerts_header_layout = QHBoxLayout(alerts_header)
        alerts_header_layout.setContentsMargins(14, 12, 14, 12)
        ah_title = QLabel("ALERTAS BGP")
        ah_title.setObjectName("CardTitle")
        alerts_header_layout.addWidget(ah_title)
        alerts_header_layout.addStretch()
        self.alert_badge = QLabel("3 ativos")
        self.alert_badge.setStyleSheet("color: #ff5c7a; background-color: rgba(255,92,122,0.1); border: 1px solid rgba(255,92,122,0.3); border-radius: 4px; padding: 2px 8px; font-size: 11px; font-weight: bold;")
        alerts_header_layout.addWidget(self.alert_badge)
        alerts_layout.addWidget(alerts_header)
        
        self.alerts_table = QTableWidget(0, 3)
        self.alerts_table.setHorizontalHeaderLabels(["Nível", "Título", "Detalhes"])
        self.alerts_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.alerts_table.verticalHeader().setVisible(False)
        self.alerts_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.alerts_table.setSelectionBehavior(QTableWidget.SelectRows)
        alerts_layout.addWidget(self.alerts_table)
        
        right_layout.addWidget(alerts_card)
        
        # Traceroute Card
        trace_card = QFrame()
        trace_card.setObjectName("Card")
        trace_layout = QVBoxLayout(trace_card)
        trace_layout.setContentsMargins(0, 0, 0, 0)
        trace_layout.setSpacing(0)
        
        trace_header = QFrame()
        trace_header.setObjectName("CardHeader")
        trace_header_layout = QHBoxLayout(trace_header)
        trace_header_layout.setContentsMargins(14, 12, 14, 12)
        th_title = QLabel("ÚLTIMO TRACEROUTE (→ 8.8.8.8)")
        th_title.setObjectName("CardTitle")
        trace_header_layout.addWidget(th_title)
        trace_layout.addWidget(trace_header)
        
        self.trace_table = QTableWidget(0, 5)
        self.trace_table.setHorizontalHeaderLabels(["Hop", "IP", "ASN", "AS Nome", "ms"])
        self.trace_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.trace_table.verticalHeader().setVisible(False)
        self.trace_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.trace_table.setSelectionBehavior(QTableWidget.SelectRows)
        trace_layout.addWidget(self.trace_table)
        
        right_layout.addWidget(trace_card)
        
        grid_layout.addWidget(graph_card, 2)
        grid_layout.addWidget(right_panel, 1)
        
        layout.addWidget(grid_frame)
        
        self.refresh_data()

    def refresh_data(self):
        # Populate alerts
        alerts = self.db.get_alerts()
        self.alerts_table.setRowCount(0)
        self.alert_badge.setText(f"{len(alerts)} ativos")
        for sev, title, desc, meta, timestamp in alerts:
            row = self.alerts_table.rowCount()
            self.alerts_table.insertRow(row)
            
            # Level item
            level_item = QTableWidgetItem(sev.upper())
            if sev == "critical":
                level_item.setForeground(QColor("#ff5c7a"))
            else:
                level_item.setForeground(QColor("#fbbf24"))
            
            self.alerts_table.setItem(row, 0, level_item)
            self.alerts_table.setItem(row, 1, QTableWidgetItem(title))
            self.alerts_table.setItem(row, 2, QTableWidgetItem(desc))

        # Populate mock last traceroute data matching design
        mock_trace = [
            ("1", "10.0.0.1", "AS263870", "Webstorage", "0.4 ms"),
            ("2", "187.16.220.1", "AS12956", "Telefônica", "1.8 ms"),
            ("3", "200.219.130.45", "AS262332", "IX.br SP (IX)", "2.6 ms"),
            ("4", "200.219.130.118", "AS262332", "IX.br SP (IX)", "2.9 ms"),
            ("5", "108.170.243.1", "AS15169", "Google", "3.4 ms"),
            ("6", "142.250.227.142", "AS15169", "Google", "4.1 ms"),
            ("7", "8.8.8.8", "AS15169", "Google", "4.0 ms")
        ]
        self.trace_table.setRowCount(0)
        for hop, ip, asn, name, ms in mock_trace:
            row = self.trace_table.rowCount()
            self.trace_table.insertRow(row)
            self.trace_table.setItem(row, 0, QTableWidgetItem(hop))
            self.trace_table.setItem(row, 1, QTableWidgetItem(ip))
            
            asn_item = QTableWidgetItem(asn)
            if "262332" in asn:
                asn_item.setForeground(QColor("#a18cff"))
            else:
                asn_item.setForeground(QColor("#3da9fc"))
            self.trace_table.setItem(row, 2, asn_item)
            
            self.trace_table.setItem(row, 3, QTableWidgetItem(name))
            self.trace_table.setItem(row, 4, QTableWidgetItem(ms))
