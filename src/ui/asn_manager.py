"""
ASN Manager — CRUD com stats, busca, filtros, CIDR multi-input e país.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
                              QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QLineEdit,
                              QComboBox, QFormLayout, QMessageBox, QTextEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
import ipaddress

from src.ui.widgets import badge, stat_card, page_header, small_action_btn


TYPE_COLORS = {
    "self":    ("#3da9fc", "blue"),
    "peer":    ("#21d4fd", "cyan"),
    "transit": ("#94a3b8", "gray"),
    "ix":      ("#a18cff", "purple"),
    "dest":    ("#4ade80", "green"),
}

TYPE_LABELS = {
    "self":    "Próprio",
    "peer":    "Peer",
    "transit": "Trânsito",
    "ix":      "IX",
    "dest":    "Destino",
}


def _validate_cidr(c):
    try:
        ipaddress.ip_network(c.strip(), strict=False)
        return True
    except Exception:
        return False


class CidrTextEdit(QTextEdit):
    """Multi-CIDR input com validação e contador IPv4/IPv6/inválido."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("CidrInput")
        self.setFixedHeight(80)
        self.setFont(QFont("JetBrains Mono", 10))
        self.setStyleSheet("""
            QTextEdit#CidrInput {
                background-color: rgba(11, 15, 25, 0.6);
                border: 1px solid rgba(110, 140, 220, 0.14);
                border-radius: 8px;
                padding: 8px 10px;
                color: #e7ecf7;
            }
            QTextEdit#CidrInput:focus { border-color: #3da9fc; }
        """)
        self.setPlaceholderText("200.149.0.0/16, 2804:7f0::/32, ...")

    def get_cidrs(self):
        text = self.toPlainText()
        parts = [p.strip() for p in text.replace("\n", ",").replace(";", ",").split(",") if p.strip()]
        return parts

    def set_cidrs(self, text):
        self.setPlainText(text or "")

    def summary(self):
        items = self.get_cidrs()
        v4 = sum(1 for c in items if _validate_cidr(c) and "." in c.split("/")[0])
        v6 = sum(1 for c in items if _validate_cidr(c) and ":" in c.split("/")[0])
        bad = sum(1 for c in items if not _validate_cidr(c))
        return v4, v6, bad, len(items)


class AsnDialog(QDialog):
    def __init__(self, parent=None, asn_data=None):
        super().__init__(parent)
        self.asn_data = asn_data
        self.setWindowTitle("Editar ASN" if asn_data else "Adicionar novo ASN")
        self.setFixedWidth(520)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title = QLabel(self.windowTitle())
        title.setStyleSheet("font-size: 16px; font-weight: 700; color: #e7ecf7;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignLeft)

        self.asn_input = QLineEdit()
        self.asn_input.setPlaceholderText("263870")

        self.country_input = QComboBox()
        self.country_input.addItems(["BR", "US", "ES", "AR", "CL", "DE", "FR", "UK", "PT", "JP"])

        # ASN + Country na mesma linha
        row1 = QHBoxLayout()
        row1.setSpacing(10)
        row1.addWidget(self._labeled("Número ASN", self.asn_input), 2)
        row1.addWidget(self._labeled("País", self.country_input), 1)
        layout.addLayout(row1)

        self.org_input = QLineEdit()
        self.org_input.setPlaceholderText("ex: Cloudflare Inc.")
        layout.addWidget(self._labeled("Organização", self.org_input))

        self.cidr_input = CidrTextEdit()
        layout.addWidget(self._labeled("Prefixos / Ranges (separe múltiplos com vírgula ou nova linha)",
                                       self.cidr_input))

        # Resumo dinâmico
        self.cidr_summary = QLabel("0 prefixos")
        self.cidr_summary.setStyleSheet("font-size: 11px; color: #6b7693;")
        layout.addWidget(self.cidr_summary)
        self.cidr_input.textChanged.connect(self._update_cidr_summary)

        # Tipo / Sub / Status
        self.type_input = QComboBox()
        for k, v in TYPE_LABELS.items():
            self.type_input.addItem(v, k)
        self.sub_input = QComboBox()
        self.sub_input.addItems(["OWN", "PTT", "TRA", "DST", "PEER"])
        self.status_input = QComboBox()
        self.status_input.addItems(["Ativo", "Inativo"])

        row3 = QHBoxLayout()
        row3.setSpacing(10)
        row3.addWidget(self._labeled("Tipo", self.type_input))
        row3.addWidget(self._labeled("Categoria", self.sub_input))
        row3.addWidget(self._labeled("Status", self.status_input))
        layout.addLayout(row3)

        # Carregar dados
        if self.asn_data:
            asn, org, type_, sub, prefixes, country, status, *_ = self.asn_data
            self.asn_input.setText(asn)
            self.asn_input.setReadOnly(True)
            self.org_input.setText(org)
            self.cidr_input.set_cidrs(prefixes)
            self.country_input.setCurrentText(country or "BR")
            idx = self.type_input.findData(type_)
            if idx >= 0: self.type_input.setCurrentIndex(idx)
            self.sub_input.setCurrentText(sub)
            self.status_input.setCurrentText(status)

        self._update_cidr_summary()

        # Botões
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel = QPushButton("Cancelar")
        cancel.setObjectName("Btn")
        cancel.clicked.connect(self.reject)
        save = QPushButton("Salvar alterações" if self.asn_data else "Adicionar ASN")
        save.setObjectName("BtnPrimary")
        save.clicked.connect(self.accept)
        btn_row.addWidget(cancel)
        btn_row.addWidget(save)
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

    def _update_cidr_summary(self):
        v4, v6, bad, total = self.cidr_input.summary()
        parts = [f"{total} prefixo{'s' if total != 1 else ''}"]
        if v4: parts.append(f"<span style='color:#7ec3ff'>IPv4: {v4}</span>")
        if v6: parts.append(f"<span style='color:#c4b5ff'>IPv6: {v6}</span>")
        if bad: parts.append(f"<span style='color:#ff5c7a'>{bad} inválido(s)</span>")
        self.cidr_summary.setText("  ·  ".join(parts))

    def get_data(self):
        return {
            "asn": self.asn_input.text().strip().replace("AS", "").replace("as", ""),
            "org": self.org_input.text().strip(),
            "type": self.type_input.currentData(),
            "sub": self.sub_input.currentText(),
            "prefixes": ", ".join(self.cidr_input.get_cidrs()),
            "country": self.country_input.currentText(),
            "status": self.status_input.currentText(),
        }


class AsnManagerScreen(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Header + actions
        actions = []
        add_btn = QPushButton("＋  Adicionar ASN")
        add_btn.setObjectName("BtnPrimary")
        add_btn.clicked.connect(self.add_asn)
        actions.append(add_btn)
        layout.addWidget(page_header(
            "ASN", "Manager",
            "Cadastro e governança de números de sistema autônomo, prefixos e relações de peering.",
            actions=actions))

        # Stats row
        stats_row = QHBoxLayout()
        stats_row.setSpacing(10)
        self.stat_total = stat_card("Total ASNs", "0", "Próprios · Peers · Trânsito · IX", "up")
        self.stat_own   = stat_card("Próprios",   "0", "Originados por nós")
        self.stat_peer  = stat_card("Peers",      "0", "Diretos + via IX", "up")
        self.stat_tra   = stat_card("Trânsito",   "0", "Upstream providers")
        for s in (self.stat_total, self.stat_own, self.stat_peer, self.stat_tra):
            stats_row.addWidget(s)
        layout.addLayout(stats_row)

        # Filtros
        filters = QHBoxLayout()
        filters.setSpacing(10)
        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍  Buscar ASN, organização ou prefixo…")
        self.search.textChanged.connect(self.load_data)

        self.filter_type = QComboBox()
        self.filter_type.addItem("Todos os tipos", None)
        for k, v in TYPE_LABELS.items():
            self.filter_type.addItem(v, k)
        self.filter_type.currentIndexChanged.connect(self.load_data)

        self.filter_status = QComboBox()
        self.filter_status.addItems(["Todos os status", "Ativo", "Inativo"])
        self.filter_status.currentIndexChanged.connect(self.load_data)

        self.result_badge = badge("0 resultados", "gray")

        filters.addWidget(self.search, 3)
        filters.addWidget(self.filter_type, 1)
        filters.addWidget(self.filter_status, 1)
        filters.addStretch()
        filters.addWidget(self.result_badge)
        layout.addLayout(filters)

        # Tabela
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(
            ["ASN", "Organização", "Prefixos / Ranges", "País", "Tipo", "Status", "Cadastro", "Ações"])
        h = self.table.horizontalHeader()
        h.setSectionResizeMode(QHeaderView.Stretch)
        h.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table, 1)

        self.load_data()

    def load_data(self):
        rows = self.db.get_asns()
        # Stats
        self.stat_total.value_label.setText(str(len(rows)))
        self.stat_own.value_label.setText(str(sum(1 for r in rows if r[2] == "self")))
        self.stat_peer.value_label.setText(str(sum(1 for r in rows if r[2] in ("peer", "dest"))))
        self.stat_tra.value_label.setText(str(sum(1 for r in rows if r[2] == "transit")))

        # Filtros
        q = self.search.text().strip().lower()
        ftype = self.filter_type.currentData()
        fstatus = self.filter_status.currentText()

        def match(r):
            asn, org, type_, sub, prefixes, country, status, *_ = r
            if q and q not in (f"{asn} {org} {prefixes}").lower():
                return False
            if ftype and type_ != ftype:
                return False
            if fstatus != "Todos os status" and status != fstatus:
                return False
            return True

        filtered = [r for r in rows if match(r)]
        self.result_badge.setText(f"{len(filtered)} resultado{'s' if len(filtered) != 1 else ''}")

        self.table.setRowCount(0)
        for r in filtered:
            asn, org, type_, sub, prefixes, country, status, date_added = r
            row = self.table.rowCount()
            self.table.insertRow(row)

            # ASN
            it = QTableWidgetItem(f"AS{asn}")
            it.setFont(QFont("JetBrains Mono", 10, QFont.Bold))
            it.setForeground(QColor("#e7ecf7"))
            it.setData(Qt.UserRole, asn)
            self.table.setItem(row, 0, it)

            # Org
            it = QTableWidgetItem(org)
            it.setFont(QFont("Inter", 10, QFont.Bold))
            self.table.setItem(row, 1, it)

            # Prefixes
            it = QTableWidgetItem(prefixes or "—")
            it.setFont(QFont("JetBrains Mono", 9))
            it.setForeground(QColor("#9aa6c2"))
            it.setToolTip(prefixes or "")
            self.table.setItem(row, 2, it)

            # País
            it = QTableWidgetItem(country or "—")
            it.setTextAlignment(Qt.AlignCenter)
            it.setForeground(QColor("#9aa6c2"))
            self.table.setItem(row, 3, it)

            # Tipo
            it = QTableWidgetItem(TYPE_LABELS.get(type_, type_))
            color, _ = TYPE_COLORS.get(type_, ("#9aa6c2", "gray"))
            it.setForeground(QColor(color))
            it.setFont(QFont("Inter", 10, QFont.Bold))
            self.table.setItem(row, 4, it)

            # Status
            it = QTableWidgetItem(("● " if status == "Ativo" else "○ ") + status)
            it.setForeground(QColor("#4ade80" if status == "Ativo" else "#6b7693"))
            self.table.setItem(row, 5, it)

            # Data
            it = QTableWidgetItem((date_added or "")[:10])
            it.setFont(QFont("JetBrains Mono", 9))
            it.setForeground(QColor("#6b7693"))
            self.table.setItem(row, 6, it)

            # Ações
            actions_widget = QFrame()
            al = QHBoxLayout(actions_widget)
            al.setContentsMargins(4, 4, 4, 4)
            al.setSpacing(6)
            edit_btn = small_action_btn("Editar", "✎")
            edit_btn.clicked.connect(lambda _, a=asn: self.edit_asn(a))
            del_btn = small_action_btn("Remover", "🗑", "danger")
            del_btn.clicked.connect(lambda _, a=asn, o=org: self.delete_asn(a, o))
            al.addWidget(edit_btn)
            al.addWidget(del_btn)
            al.addStretch()
            self.table.setCellWidget(row, 7, actions_widget)
            self.table.setRowHeight(row, 44)

    def add_asn(self):
        dialog = AsnDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            d = dialog.get_data()
            if not d["asn"] or not d["org"]:
                QMessageBox.warning(self, "Aviso", "Preencha ASN e Organização.")
                return
            self.db.add_asn(d["asn"], d["org"], d["type"], d["sub"], d["prefixes"], d["status"], d["country"])
            self.db.add_log("INFO", "ASN", f"AS{d['asn']} ({d['org']}) adicionado.")
            self.load_data()

    def edit_asn(self, asn):
        match = next((r for r in self.db.get_asns() if r[0] == asn), None)
        if not match:
            return
        dialog = AsnDialog(self, asn_data=match)
        if dialog.exec_() == QDialog.Accepted:
            d = dialog.get_data()
            self.db.add_asn(asn, d["org"], d["type"], d["sub"], d["prefixes"], d["status"], d["country"])
            self.db.add_log("INFO", "ASN", f"AS{asn} ({d['org']}) atualizado.")
            self.load_data()

    def delete_asn(self, asn, org):
        reply = QMessageBox.question(
            self, "Confirmação",
            f"Remover AS{asn} ({org})?",
            QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.remove_asn(asn)
            self.db.add_log("INFO", "ASN", f"AS{asn} ({org}) removido.")
            self.load_data()
