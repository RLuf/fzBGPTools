from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QLineEdit, QComboBox, QFormLayout, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

class AddAsnDialog(QDialog):
    def __init__(self, parent=None, asn_data=None):
        super().__init__(parent)
        self.asn_data = asn_data
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Cadastrar ASN" if not self.asn_data else "Editar ASN")
        self.setFixedWidth(400)
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        self.asn_input = QLineEdit()
        self.asn_input.setPlaceholderText("ex: 263870")
        if self.asn_data:
            self.asn_input.setText(self.asn_data[0])
            self.asn_input.setReadOnly(True) # ASN is primary key
            
        self.org_input = QLineEdit()
        self.org_input.setPlaceholderText("ex: Webstorage")
        if self.asn_data:
            self.org_input.setText(self.asn_data[1])
            
        self.type_input = QComboBox()
        self.type_input.addItems(["self", "ix", "transit", "dest"])
        if self.asn_data:
            self.type_input.setCurrentText(self.asn_data[2])
            
        self.sub_input = QComboBox()
        self.sub_input.addItems(["OWN", "PTT", "TRA", "DST"])
        if self.asn_data:
            self.sub_input.setCurrentText(self.asn_data[3])
            
        self.prefixes_input = QLineEdit()
        self.prefixes_input.setPlaceholderText("ex: 138.186.228.0/22")
        if self.asn_data:
            self.prefixes_input.setText(self.asn_data[4])
            
        self.status_input = QComboBox()
        self.status_input.addItems(["Ativo", "Inativo"])
        if self.asn_data:
            self.status_input.setCurrentText(self.asn_data[5])
            
        form_layout.addRow("ASN Number:", self.asn_input)
        form_layout.addRow("Organização:", self.org_input)
        form_layout.addRow("Tipo:", self.type_input)
        form_layout.addRow("Categoria/Sub:", self.sub_input)
        form_layout.addRow("Prefixos (CIDR):", self.prefixes_input)
        form_layout.addRow("Status:", self.status_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setObjectName("Btn")
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("Salvar")
        save_btn.setObjectName("BtnPrimary")
        save_btn.clicked.connect(self.accept)
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def get_data(self):
        return (
            self.asn_input.text().strip(),
            self.org_input.text().strip(),
            self.type_input.currentText(),
            self.sub_input.currentText(),
            self.prefixes_input.text().strip(),
            self.status_input.currentText()
        )

class AsnManagerScreen(QWidget):
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
        
        title_lbl = QLabel("Gerenciamento de ASNs")
        title_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #3da9fc;")
        sub_lbl = QLabel("Adicione, remova ou edite blocos ASN e seus respectivos ranges CIDR.")
        sub_lbl.setStyleSheet("font-size: 12px; color: #9aa6c2;")
        title_layout.addWidget(title_lbl)
        title_layout.addWidget(sub_lbl)
        
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Adicionar ASN")
        add_btn.setObjectName("BtnPrimary")
        add_btn.clicked.connect(self.add_asn)
        edit_btn = QPushButton("Editar")
        edit_btn.setObjectName("Btn")
        edit_btn.clicked.connect(self.edit_asn)
        del_btn = QPushButton("Remover")
        del_btn.setObjectName("BtnDanger")
        del_btn.clicked.connect(self.delete_asn)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(del_btn)
        
        header_layout.addWidget(title_block)
        header_layout.addStretch()
        header_layout.addLayout(btn_layout)
        layout.addWidget(header_frame)
        
        # Table
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["ASN Number", "Organização", "Tipo", "Sub", "Prefixos CIDR", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)
        
        self.load_data()

    def load_data(self):
        self.table.setRowCount(0)
        asns = self.db.get_asns()
        for asn, org, type_, sub, prefixes, status in asns:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(f"AS{asn}"))
            self.table.setItem(row, 1, QTableWidgetItem(org))
            
            # Type badge
            type_item = QTableWidgetItem(type_.upper())
            if type_ == "self":
                type_item.setForeground(QColor("#3da9fc"))
            elif type_ == "ix":
                type_item.setForeground(QColor("#a18cff"))
            elif type_ == "transit":
                type_item.setForeground(QColor("#94a3b8"))
            else:
                type_item.setForeground(QColor("#4ade80"))
            self.table.setItem(row, 2, type_item)
            
            self.table.setItem(row, 3, QTableWidgetItem(sub))
            self.table.setItem(row, 4, QTableWidgetItem(prefixes if prefixes else "N/A"))
            
            status_item = QTableWidgetItem(status)
            if status == "Ativo":
                status_item.setForeground(QColor("#4ade80"))
            else:
                status_item.setForeground(QColor("#ff5c7a"))
            self.table.setItem(row, 5, status_item)

    def add_asn(self):
        dialog = AddAsnDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            asn, org, type_, sub, prefixes, status = dialog.get_data()
            if not asn or not org:
                QMessageBox.warning(self, "Aviso", "Preencha o ASN e Organização!")
                return
            # Remove AS prefix if user typed it
            asn = asn.replace("AS", "").replace("as", "").strip()
            self.db.add_asn(asn, org, type_, sub, prefixes, status)
            self.db.add_log("INFO", "ASN", f"ASN AS{asn} ({org}) adicionado.")
            self.load_data()

    def edit_asn(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.information(self, "Aviso", "Selecione uma linha para editar.")
            return
        
        row = selected[0].row()
        asn = self.table.item(row, 0).text().replace("AS", "")
        org = self.table.item(row, 1).text()
        type_ = self.table.item(row, 2).text().lower()
        sub = self.table.item(row, 3).text()
        prefixes = self.table.item(row, 4).text()
        status = self.table.item(row, 5).text()
        
        dialog = AddAsnDialog(self, (asn, org, type_, sub, prefixes, status))
        if dialog.exec_() == QDialog.Accepted:
            _, new_org, new_type, new_sub, new_prefixes, new_status = dialog.get_data()
            self.db.add_asn(asn, new_org, new_type, new_sub, new_prefixes, new_status)
            self.db.add_log("INFO", "ASN", f"ASN AS{asn} ({new_org}) atualizado.")
            self.load_data()

    def delete_asn(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.information(self, "Aviso", "Selecione uma linha para remover.")
            return
        
        row = selected[0].row()
        asn = self.table.item(row, 0).text().replace("AS", "")
        org = self.table.item(row, 1).text()
        
        reply = QMessageBox.question(self, "Confirmação", f"Tem certeza que deseja remover o AS{asn} ({org})?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.remove_asn(asn)
            self.db.add_log("INFO", "ASN", f"ASN AS{asn} ({org}) removido.")
            self.load_data()
