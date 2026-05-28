from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QLineEdit, QComboBox, QFormLayout, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

class AddHostDialog(QDialog):
    def __init__(self, parent=None, host_data=None):
        super().__init__(parent)
        self.host_data = host_data
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Cadastrar Host" if not self.host_data else "Editar Host")
        self.setFixedWidth(400)
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("ex: 192.168.0.106")
        if self.host_data:
            self.ip_input.setText(self.host_data[0])
            self.ip_input.setReadOnly(True) # IP is primary key
            
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("ex: RouterBoard")
        if self.host_data:
            self.host_input.setText(self.host_data[1])
            
        self.ssh_port_input = QLineEdit("22")
        if self.host_data:
            self.ssh_port_input.setText(str(self.host_data[2]))
            
        self.telnet_port_input = QLineEdit("23")
        if self.host_data:
            self.telnet_port_input.setText(str(self.host_data[3]))
            
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("ex: admin")
        if self.host_data:
            self.user_input.setText(self.host_data[4])
            
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setPlaceholderText("Senha (mascarada)")
        if self.host_data:
            self.pass_input.setText(self.host_data[5])
            
        self.type_input = QComboBox()
        self.type_input.addItems(["Router", "Switch", "Server", "Firewall"])
        if self.host_data:
            self.type_input.setCurrentText(self.host_data[6])
            
        self.mfg_input = QComboBox()
        self.mfg_input.addItems(["MikroTik", "Cisco", "Juniper", "Linux", "Outro"])
        if self.host_data:
            self.mfg_input.setCurrentText(self.host_data[7])
            
        form_layout.addRow("IP Address:", self.ip_input)
        form_layout.addRow("Hostname:", self.host_input)
        form_layout.addRow("Porta SSH:", self.ssh_port_input)
        form_layout.addRow("Porta Telnet:", self.telnet_port_input)
        form_layout.addRow("Username:", self.user_input)
        form_layout.addRow("Password:", self.pass_input)
        form_layout.addRow("Tipo:", self.type_input)
        form_layout.addRow("Fabricante:", self.mfg_input)
        
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
            self.ip_input.text().strip(),
            self.host_input.text().strip(),
            int(self.ssh_port_input.text().strip() or 22),
            int(self.telnet_port_input.text().strip() or 23),
            self.user_input.text().strip(),
            self.pass_input.text().strip(),
            self.type_input.currentText(),
            self.mfg_input.currentText()
        )

class HostManagerScreen(QWidget):
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
        
        title_lbl = QLabel("Gerenciamento de Hosts")
        title_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #3da9fc;")
        sub_lbl = QLabel("Cadastre roteadores, switches, servidores e outros ativos de rede.")
        sub_lbl.setStyleSheet("font-size: 12px; color: #9aa6c2;")
        title_layout.addWidget(title_lbl)
        title_layout.addWidget(sub_lbl)
        
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Adicionar Host")
        add_btn.setObjectName("BtnPrimary")
        add_btn.clicked.connect(self.add_host)
        edit_btn = QPushButton("Editar")
        edit_btn.setObjectName("Btn")
        edit_btn.clicked.connect(self.edit_host)
        del_btn = QPushButton("Remover")
        del_btn.setObjectName("BtnDanger")
        del_btn.clicked.connect(self.delete_host)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(del_btn)
        
        header_layout.addWidget(title_block)
        header_layout.addStretch()
        header_layout.addLayout(btn_layout)
        layout.addWidget(header_frame)
        
        # Table
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["Hostname", "IP Address", "Porta SSH", "Porta Telnet", "Tipo", "Fabricante", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)
        
        self.load_data()

    def load_data(self):
        self.table.setRowCount(0)
        hosts = self.db.get_hosts()
        for ip, hostname, p_ssh, p_tel, username, password, type_, mfg, status in hosts:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(hostname))
            self.table.setItem(row, 1, QTableWidgetItem(ip))
            self.table.setItem(row, 2, QTableWidgetItem(str(p_ssh)))
            self.table.setItem(row, 3, QTableWidgetItem(str(p_tel)))
            self.table.setItem(row, 4, QTableWidgetItem(type_))
            self.table.setItem(row, 5, QTableWidgetItem(mfg))
            
            status_item = QTableWidgetItem(status)
            if status == "Online":
                status_item.setForeground(QColor("#4ade80"))
            else:
                status_item.setForeground(QColor("#ff5c7a"))
            self.table.setItem(row, 6, status_item)

    def add_host(self):
        dialog = AddHostDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            ip, hostname, p_ssh, p_tel, username, password, type_, mfg = dialog.get_data()
            if not ip or not hostname:
                QMessageBox.warning(self, "Aviso", "Preencha o IP e Hostname!")
                return
            self.db.add_host(ip, hostname, p_ssh, p_tel, username, password, type_, mfg)
            self.db.add_log("INFO", "Host", f"Host {hostname} ({ip}) cadastrado.")
            self.load_data()

    def edit_host(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.information(self, "Aviso", "Selecione uma linha para editar.")
            return
        
        row = selected[0].row()
        hostname = self.table.item(row, 0).text()
        ip = self.table.item(row, 1).text()
        p_ssh = int(self.table.item(row, 2).text())
        p_tel = int(self.table.item(row, 3).text())
        type_ = self.table.item(row, 4).text()
        mfg = self.table.item(row, 5).text()
        
        # Get matching host password/username from DB
        hosts = self.db.get_hosts()
        match = next((h for h in hosts if h[0] == ip), None)
        username = match[4] if match else ""
        password = match[5] if match else ""
        
        dialog = AddHostDialog(self, (ip, hostname, p_ssh, p_tel, username, password, type_, mfg))
        if dialog.exec_() == QDialog.Accepted:
            _, new_host, new_ssh, new_tel, new_user, new_pass, new_type, new_mfg = dialog.get_data()
            self.db.add_host(ip, new_host, new_ssh, new_tel, new_user, new_pass, new_type, new_mfg)
            self.db.add_log("INFO", "Host", f"Host {new_host} ({ip}) atualizado.")
            self.load_data()

    def delete_host(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.information(self, "Aviso", "Selecione uma linha para remover.")
            return
        
        row = selected[0].row()
        hostname = self.table.item(row, 0).text()
        ip = self.table.item(row, 1).text()
        
        reply = QMessageBox.question(self, "Confirmação", f"Tem certeza que deseja remover o host {hostname} ({ip})?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.remove_host(ip)
            self.db.add_log("INFO", "Host", f"Host {hostname} ({ip}) removido.")
            self.load_data()
