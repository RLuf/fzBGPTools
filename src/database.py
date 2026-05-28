import sqlite3
import os

class Database:
    def __init__(self, db_path=None):
        if db_path is None:
            if os.name == 'nt':
                config_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser("~")), "fzbgptools")
            else:
                config_dir = os.path.expanduser("~/.config/fzbgptools")
            os.makedirs(config_dir, exist_ok=True)
            db_path = os.path.join(config_dir, "fzbgptools.db")
        self.db_path = db_path
        self.init_db()

    def get_conn(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            # ASNs Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS asns (
                    asn TEXT PRIMARY KEY,
                    org TEXT NOT NULL,
                    type TEXT NOT NULL,
                    sub TEXT NOT NULL,
                    prefixes TEXT,
                    status TEXT NOT NULL
                )
            """)
            # Hosts Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hosts (
                    ip TEXT PRIMARY KEY,
                    hostname TEXT NOT NULL,
                    port_ssh INTEGER DEFAULT 22,
                    port_telnet INTEGER DEFAULT 23,
                    username TEXT,
                    password TEXT,
                    type TEXT NOT NULL,
                    fabricante TEXT NOT NULL,
                    status TEXT DEFAULT 'Offline'
                )
            """)
            # Alerts Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sev TEXT NOT NULL,
                    title TEXT NOT NULL,
                    desc TEXT NOT NULL,
                    meta TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Logs Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sev TEXT NOT NULL,
                    module TEXT NOT NULL,
                    msg TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Seed default ASNs if empty
            cursor.execute("SELECT COUNT(*) FROM asns")
            if cursor.fetchone()[0] == 0:
                default_asns = [
                    ("263870", "Webstorage", "self", "OWN", "138.186.228.0/22", "Ativo"),
                    ("262332", "IX.br SP", "ix", "PTT", "200.219.130.0/24", "Ativo"),
                    ("12956", "Telefônica", "transit", "TRA", "187.16.220.0/24", "Ativo"),
                    ("174", "Cogent", "transit", "TRA", "185.0.0.0/8", "Ativo"),
                    ("15169", "Google", "dest", "DST", "8.8.8.0/24,8.8.4.4/24", "Ativo"),
                    ("16509", "AWS", "dest", "DST", "52.0.0.0/8", "Ativo")
                ]
                cursor.executemany("INSERT INTO asns VALUES (?, ?, ?, ?, ?, ?)", default_asns)

            # Seed default Hosts if empty
            cursor.execute("SELECT COUNT(*) FROM hosts")
            if cursor.fetchone()[0] == 0:
                default_hosts = [
                    ("192.168.0.106", "RouterBoard", 22, 23, "admin", "7878", "Router", "MikroTik", "Online"),
                    ("192.168.0.22", "walker", 22, 23, "rluft", "7878", "Server", "Linux", "Online"),
                    ("192.168.0.101", "papaimach", 22, 23, "rluft", "7878", "Server", "Linux", "Offline"),
                    ("192.168.0.104", "TP-Link AP", 22, 23, "admin", "admin", "Switch", "TP-Link", "Online")
                ]
                cursor.executemany("INSERT INTO hosts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", default_hosts)

            # Seed default Alerts if empty
            cursor.execute("SELECT COUNT(*) FROM alerts")
            if cursor.fetchone()[0] == 0:
                default_alerts = [
                    ("critical", "Prepend detection", "AS174 está fazendo AS-Path prepend (3x) no prefixo 200.149.0.0/16. Possível shift de tráfego.", "AS_PATH 174 174 174 263870 · há 3 min"),
                    ("critical", "Route flapping", "Prefixo 187.45.128.0/19 oscilou 8 vezes nos últimos 15 min via AS12956.", "RFD threshold 2000 · suprimido por 30 min"),
                    ("warn", "MED change", "Telefônica alterou MED de 100 → 250 em 17 prefixos do upstream.", "Sessão eBGP 187.16.220.1 · há 12 min")
                ]
                cursor.executemany("INSERT INTO alerts (sev, title, desc, meta) VALUES (?, ?, ?, ?)", default_alerts)

            # Seed default Logs if empty
            cursor.execute("SELECT COUNT(*) FROM logs")
            if cursor.fetchone()[0] == 0:
                default_logs = [
                    ("INFO", "System", "fzBGPTools inicializado com sucesso."),
                    ("INFO", "BGP", "Sessão BGP com AS262332 (IX.br SP) está estabelecida."),
                    ("WARN", "BGP", "Alteração de rota detectada para o prefixo 187.45.128.0/19."),
                    ("ERROR", "Host", "Host papaimach (192.168.0.101) não responde ao ping.")
                ]
                cursor.executemany("INSERT INTO logs (sev, module, msg) VALUES (?, ?, ?)", default_logs)
            
            conn.commit()

    def get_asns(self):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT asn, org, type, sub, prefixes, status FROM asns")
            return cursor.fetchall()

    def add_asn(self, asn, org, type_, sub, prefixes, status):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO asns VALUES (?, ?, ?, ?, ?, ?)", (asn, org, type_, sub, prefixes, status))
            conn.commit()

    def remove_asn(self, asn):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM asns WHERE asn = ?", (asn,))
            conn.commit()

    def get_hosts(self):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT ip, hostname, port_ssh, port_telnet, username, password, type, fabricante, status FROM hosts")
            return cursor.fetchall()

    def add_host(self, ip, hostname, port_ssh, port_telnet, username, password, type_, fabricante, status="Offline"):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO hosts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                           (ip, hostname, port_ssh, port_telnet, username, password, type_, fabricante, status))
            conn.commit()

    def remove_host(self, ip):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM hosts WHERE ip = ?", (ip,))
            conn.commit()

    def get_alerts(self):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT sev, title, desc, meta, timestamp FROM alerts ORDER BY timestamp DESC")
            return cursor.fetchall()

    def get_logs(self):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT sev, module, msg, timestamp FROM logs ORDER BY timestamp DESC")
            return cursor.fetchall()

    def add_log(self, sev, module, msg):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO logs (sev, module, msg) VALUES (?, ?, ?)", (sev, module, msg))
            conn.commit()

    def add_alert(self, sev, title, desc, meta):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO alerts (sev, title, desc, meta) VALUES (?, ?, ?, ?)", (sev, title, desc, meta))
            conn.commit()
