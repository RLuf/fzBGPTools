"""
Tema / Stylesheet global Qt.
Inclui badges, chrome de terminal, cards, filtros, tabelas
para emparelhar com o mockup HTML.
"""

# ─── Tokens (alinhados com styles.css do mockup) ──────────────────────────
COLOR = {
    "bg":          "#0b0f19",
    "bg2":         "#0e1424",
    "panel":       "rgba(20, 27, 48, 0.55)",
    "border":      "rgba(110, 140, 220, 0.14)",
    "border_strong": "rgba(120, 160, 240, 0.28)",
    "text":        "#e7ecf7",
    "text_dim":    "#9aa6c2",
    "text_mute":   "#6b7693",
    "accent":      "#3da9fc",
    "accent2":     "#21d4fd",
    "purple":      "#a18cff",
    "green":       "#4ade80",
    "yellow":      "#fbbf24",
    "red":         "#ff5c7a",
    "term_bg":     "#050810",
    "term_text":   "#b6f3c8",
}


def get_stylesheet():
    c = COLOR
    return f"""
    /* ════════════════ GLOBAL ════════════════ */
    QWidget {{
        color: {c['text']};
        font-family: 'Inter', 'Segoe UI', sans-serif;
        font-size: 13px;
    }}
    QMainWindow {{ background-color: {c['bg']}; }}
    QDialog {{
        background-color: {c['bg2']};
        border: 1px solid {c['border_strong']};
        border-radius: 12px;
    }}

    /* ════════════════ SIDEBAR ════════════════ */
    QFrame#Sidebar {{
        background-color: {c['bg2']};
        border-right: 1px solid {c['border']};
    }}
    QPushButton#NavItem {{
        background-color: transparent;
        color: {c['text_dim']};
        border: none;
        border-radius: 8px;
        padding: 10px 14px;
        text-align: left;
        font-weight: 500;
    }}
    QPushButton#NavItem:hover {{
        background-color: rgba(255, 255, 255, 0.03);
        color: {c['text']};
    }}
    QPushButton#NavItem:checked {{
        background-color: rgba(61, 169, 252, 0.14);
        color: {c['accent']};
        border-left: 3px solid {c['accent']};
        font-weight: 600;
    }}

    /* ════════════════ TOPBAR ════════════════ */
    QLabel#Crumb {{ color: {c['text_mute']}; font-size: 12px; }}

    /* ════════════════ STAT CARDS ════════════════ */
    QFrame#StatCard {{
        background-color: {c['panel']};
        border: 1px solid {c['border']};
        border-radius: 12px;
    }}
    QLabel#StatLabel {{
        color: {c['text_mute']};
        font-size: 10px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.14em;
    }}
    QLabel#StatValue {{
        color: {c['text']};
        font-size: 26px;
        font-weight: 800;
        letter-spacing: -0.01em;
    }}
    QLabel#StatDelta {{ font-size: 11px; }}
    QLabel#StatDelta[status="up"] {{ color: {c['green']}; }}
    QLabel#StatDelta[status="dn"] {{ color: {c['red']}; }}

    /* ════════════════ CARDS ════════════════ */
    QFrame#Card {{
        background-color: {c['panel']};
        border: 1px solid {c['border']};
        border-radius: 12px;
    }}
    QFrame#CardHeader {{
        border-bottom: 1px solid {c['border']};
    }}
    QLabel#CardTitle {{
        font-size: 13px;
        font-weight: bold;
        color: {c['text']};
    }}

    /* ════════════════ BUTTONS ════════════════ */
    QPushButton#Btn {{
        background-color: rgba(255, 255, 255, 0.03);
        border: 1px solid {c['border']};
        border-radius: 8px;
        color: {c['text']};
        padding: 8px 14px;
        font-weight: 500;
    }}
    QPushButton#Btn:hover {{ background-color: rgba(255, 255, 255, 0.06); }}
    QPushButton#Btn:disabled {{ color: {c['text_mute']}; }}

    QPushButton#BtnSmall {{
        background-color: rgba(255, 255, 255, 0.03);
        border: 1px solid {c['border']};
        border-radius: 6px;
        color: {c['text']};
        padding: 4px 10px;
        font-size: 11px;
        font-weight: 500;
    }}
    QPushButton#BtnSmall:hover {{ background-color: rgba(255, 255, 255, 0.06); }}

    QPushButton#BtnPrimary {{
        background-color: {c['accent']};
        color: {c['bg']};
        font-weight: 700;
        border: none;
        border-radius: 8px;
        padding: 8px 14px;
    }}
    QPushButton#BtnPrimary:hover {{ background-color: {c['accent2']}; }}

    QPushButton#BtnDanger {{
        background-color: rgba(255, 92, 122, 0.08);
        border: 1px solid rgba(255, 92, 122, 0.32);
        color: {c['red']};
        border-radius: 8px;
        padding: 8px 14px;
        font-weight: 500;
    }}
    QPushButton#BtnDanger:hover {{ background-color: rgba(255, 92, 122, 0.16); }}

    QPushButton#BtnDangerSmall {{
        background-color: rgba(255, 92, 122, 0.06);
        border: 1px solid rgba(255, 92, 122, 0.28);
        color: {c['red']};
        border-radius: 6px;
        padding: 4px 10px;
        font-size: 11px;
    }}
    QPushButton#BtnDangerSmall:hover {{ background-color: rgba(255, 92, 122, 0.14); }}

    /* ════════════════ INPUTS ════════════════ */
    QLineEdit {{
        background-color: rgba(11, 15, 25, 0.6);
        border: 1px solid {c['border']};
        border-radius: 8px;
        padding: 7px 11px;
        color: {c['text']};
    }}
    QLineEdit:focus {{ border-color: {c['accent']}; }}
    QLineEdit:read-only {{ color: {c['text_mute']}; }}

    QComboBox {{
        background-color: rgba(11, 15, 25, 0.6);
        border: 1px solid {c['border']};
        border-radius: 8px;
        padding: 7px 11px;
        color: {c['text']};
        min-width: 90px;
    }}
    QComboBox::drop-down {{ border: none; width: 22px; }}
    QComboBox::down-arrow {{ image: none; }}
    QComboBox QAbstractItemView {{
        background-color: {c['bg2']};
        color: {c['text']};
        selection-background-color: {c['accent']};
        selection-color: {c['bg']};
        border: 1px solid {c['border']};
        outline: none;
    }}

    QSpinBox {{
        background-color: rgba(11, 15, 25, 0.6);
        border: 1px solid {c['border']};
        border-radius: 8px;
        padding: 6px 10px;
        color: {c['text']};
    }}
    QCheckBox {{ color: {c['text']}; spacing: 8px; }}
    QCheckBox::indicator {{
        width: 16px; height: 16px;
        border: 1px solid {c['border']};
        border-radius: 4px;
        background: rgba(11, 15, 25, 0.6);
    }}
    QCheckBox::indicator:checked {{
        background-color: {c['accent']};
        border-color: {c['accent']};
    }}

    /* ════════════════ TABLES ════════════════ */
    QTableWidget {{
        background-color: transparent;
        border: 1px solid {c['border']};
        border-radius: 12px;
        gridline-color: rgba(255, 255, 255, 0.03);
        selection-background-color: rgba(61, 169, 252, 0.10);
    }}
    QTableWidget::item {{
        padding: 10px 8px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.03);
    }}
    QTableWidget::item:selected {{
        background-color: rgba(61, 169, 252, 0.16);
        color: {c['text']};
    }}
    QHeaderView::section {{
        background-color: rgba(11, 15, 25, 0.85);
        color: {c['text_mute']};
        padding: 9px 8px;
        font-size: 10.5px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        border: none;
        border-bottom: 1px solid {c['border']};
    }}

    /* ════════════════ SCROLLBARS ════════════════ */
    QScrollBar:vertical {{
        border: none; background: {c['bg']}; width: 10px; margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background: #1c243c; min-height: 24px; border-radius: 5px;
    }}
    QScrollBar::handle:vertical:hover {{ background: {c['accent']}; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    QScrollBar:horizontal {{
        border: none; background: {c['bg']}; height: 10px; margin: 0;
    }}
    QScrollBar::handle:horizontal {{
        background: #1c243c; min-width: 24px; border-radius: 5px;
    }}

    /* ════════════════ TERMINAL ════════════════ */
    QTextEdit#Terminal {{
        background-color: {c['term_bg']};
        border: 1px solid rgba(74, 222, 128, 0.18);
        border-radius: 10px;
        font-family: 'JetBrains Mono', 'Consolas', 'Menlo', monospace;
        font-size: 12.5px;
        color: {c['term_text']};
        padding: 14px;
        selection-background-color: rgba(74, 222, 128, 0.22);
    }}
    QFrame#TermFrame {{
        background-color: {c['term_bg']};
        border: 1px solid {c['border']};
        border-radius: 10px;
    }}
    QFrame#TermBar {{
        background-color: rgba(255, 255, 255, 0.02);
        border-bottom: 1px solid {c['border']};
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
    }}
    QLabel#TermTitle {{
        color: {c['text_dim']};
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        letter-spacing: 0.04em;
    }}

    /* ════════════════ BADGES (QLabel#Badge) ════════════════ */
    QLabel#Badge {{
        padding: 3px 9px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.04em;
    }}
    QLabel#Badge[kind="green"]  {{ color:{c['green']};  background: rgba(74,222,128,0.10); border: 1px solid rgba(74,222,128,0.30); }}
    QLabel#Badge[kind="red"]    {{ color:{c['red']};    background: rgba(255,92,122,0.10); border: 1px solid rgba(255,92,122,0.30); }}
    QLabel#Badge[kind="yellow"] {{ color:{c['yellow']}; background: rgba(251,191,36,0.10); border: 1px solid rgba(251,191,36,0.30); }}
    QLabel#Badge[kind="blue"]   {{ color:{c['accent']}; background: rgba(61,169,252,0.10); border: 1px solid rgba(61,169,252,0.30); }}
    QLabel#Badge[kind="cyan"]   {{ color:{c['accent2']};background: rgba(33,212,253,0.10); border: 1px solid rgba(33,212,253,0.30); }}
    QLabel#Badge[kind="purple"] {{ color:{c['purple']}; background: rgba(161,140,255,0.10); border: 1px solid rgba(161,140,255,0.30); }}
    QLabel#Badge[kind="gray"]   {{ color:{c['text_dim']};background:rgba(255,255,255,0.03);border:1px solid {c['border']}; }}

    /* ════════════════ TABS ════════════════ */
    QTabWidget::pane {{
        border: 1px solid {c['border']};
        background-color: {c['panel']};
        border-radius: 10px;
        top: -1px;
    }}
    QTabBar::tab {{
        background: rgba(11, 15, 25, 0.5);
        border: 1px solid {c['border']};
        border-bottom: none;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        padding: 9px 18px;
        margin-right: 4px;
        color: {c['text_dim']};
    }}
    QTabBar::tab:selected {{
        background-color: {c['accent']};
        color: {c['bg']};
        font-weight: 700;
    }}
    QTabBar::tab:hover:!selected {{ color: {c['text']}; }}

    /* ════════════════ LIST WIDGET (Discovery sidebar) ════════════════ */
    QListWidget {{
        background: transparent;
        border: none;
        outline: none;
    }}
    QListWidget::item {{
        padding: 12px 14px;
        margin: 3px 0;
        border-radius: 10px;
        border: 1px solid {c['border']};
        background: rgba(255, 255, 255, 0.015);
    }}
    QListWidget::item:selected {{
        border: 1px solid {c['border_strong']};
        background: rgba(61, 169, 252, 0.08);
        color: {c['text']};
    }}
    QListWidget::item:hover {{ background: rgba(255, 255, 255, 0.04); }}

    /* ════════════════ PROGRESS / SLIDER ════════════════ */
    QProgressBar {{
        background-color: rgba(255, 255, 255, 0.05);
        border: none;
        border-radius: 3px;
        height: 6px;
        text-align: center;
        color: transparent;
    }}
    QProgressBar::chunk {{
        background-color: {c['accent']};
        border-radius: 3px;
    }}
    """
