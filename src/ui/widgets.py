"""
Componentes compartilhados — badges, terminal-card, stat-cards, action-button.
"""

from PyQt5.QtWidgets import QLabel, QFrame, QHBoxLayout, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor


def badge(text, kind="gray"):
    """Cria um QLabel estilizado como badge. Use kind in [gray,blue,cyan,green,yellow,red,purple]."""
    lbl = QLabel(text)
    lbl.setObjectName("Badge")
    lbl.setProperty("kind", kind)
    lbl.setAlignment(Qt.AlignCenter)
    lbl.style().unpolish(lbl)
    lbl.style().polish(lbl)
    return lbl


def stat_card(label, value, delta="", status=""):
    """Cria um stat-card (StatCard QFrame com label + value + delta)."""
    card = QFrame()
    card.setObjectName("StatCard")
    lay = QVBoxLayout(card)
    lay.setContentsMargins(16, 14, 16, 14)
    lay.setSpacing(4)
    l = QLabel(label.upper())
    l.setObjectName("StatLabel")
    v = QLabel(value)
    v.setObjectName("StatValue")
    lay.addWidget(l)
    lay.addWidget(v)
    if delta:
        d = QLabel(delta)
        d.setObjectName("StatDelta")
        if status:
            d.setProperty("status", status)
        lay.addWidget(d)
    card.value_label = v
    card.delta_label = d if delta else None
    return card


def page_header(title, accent, subtitle, actions=None):
    """
    Header padronizado: 'Título <accent>' em destaque + subtitle abaixo.
    actions = lista de QWidgets para o canto direito.
    """
    frame = QFrame()
    lay = QHBoxLayout(frame)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(12)

    left = QFrame()
    ll = QVBoxLayout(left)
    ll.setContentsMargins(0, 0, 0, 0)
    ll.setSpacing(4)
    title_lbl = QLabel(f"<span style='color:#e7ecf7;font-weight:300'>{title}</span> "
                       f"<span style='color:#3da9fc;font-weight:800'>{accent}</span>")
    title_lbl.setStyleSheet("font-size: 22px; letter-spacing: -0.01em;")
    sub_lbl = QLabel(subtitle)
    sub_lbl.setStyleSheet("font-size: 12.5px; color: #9aa6c2;")
    sub_lbl.setWordWrap(True)
    ll.addWidget(title_lbl)
    ll.addWidget(sub_lbl)

    lay.addWidget(left, 1)

    if actions:
        for a in actions:
            lay.addWidget(a)
    return frame


def terminal_card(title_text, parent=None):
    """
    Card estilo terminal com barra superior (red/yellow/green dots + title + status badge).
    Retorna (card_frame, title_label, status_badge, body_widget).
    O body_widget pode receber um QTextEdit#Terminal ou layout customizado.
    """
    card = QFrame(parent)
    card.setObjectName("TermFrame")
    lay = QVBoxLayout(card)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(0)

    # Bar
    bar = QFrame()
    bar.setObjectName("TermBar")
    bar.setFixedHeight(36)
    bar_lay = QHBoxLayout(bar)
    bar_lay.setContentsMargins(12, 0, 12, 0)
    bar_lay.setSpacing(8)

    for color in ("#ff5c7a", "#fbbf24", "#4ade80"):
        d = QLabel()
        d.setFixedSize(10, 10)
        d.setStyleSheet(f"background:{color}; border-radius:5px;")
        bar_lay.addWidget(d)

    bar_lay.addSpacing(6)
    title_lbl = QLabel(title_text)
    title_lbl.setObjectName("TermTitle")
    bar_lay.addWidget(title_lbl)
    bar_lay.addStretch()
    status_b = badge("pronto", "gray")
    bar_lay.addWidget(status_b)

    lay.addWidget(bar)

    body = QWidget()
    body_lay = QVBoxLayout(body)
    body_lay.setContentsMargins(0, 0, 0, 0)
    body_lay.setSpacing(0)
    lay.addWidget(body, 1)

    return card, title_lbl, status_b, body, body_lay


def small_action_btn(text, icon_text="", kind="default"):
    """Botão pequeno para ações de tabela."""
    btn = QPushButton(f"{icon_text} {text}".strip() if icon_text else text)
    btn.setCursor(QCursor(Qt.PointingHandCursor))
    if kind == "danger":
        btn.setObjectName("BtnDangerSmall")
    else:
        btn.setObjectName("BtnSmall")
    return btn
