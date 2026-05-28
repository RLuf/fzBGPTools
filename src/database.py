"""
SQLite database — schema includes legacy tables (asns, hosts, alerts, logs)
plus new Discovery tables (range_groups, discovered_hosts, discovered_services).
"""

import sqlite3
import os


class Database:
    SCHEMA_VERSION = 2

    def __init__(self, db_path=None):
        if db_path is None:
            import sys
            if sys.platform == "win32":
                config_dir = os.path.join(os.environ.get("APPDATA", "."), "fzbgptools")
            else:
                config_dir = os.path.expanduser("~/.config/fzbgptools")
            os.makedirs(config_dir, exist_ok=True)
            db_path = os.path.join(config_dir, "fzbgptools.db")
        self.db_path = db_path
        self.init_db()

    def get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    # ───────────────────────── SCHEMA ─────────────────────────
    def init_db(self):
        with self.get_conn() as conn:
            cur = conn.cursor()

            # Meta table for schema versioning
            cur.execute("""CREATE TABLE IF NOT EXISTS meta (
                k TEXT PRIMARY KEY, v TEXT NOT NULL)""")

            # ASNs — with country & date_added columns
            cur.execute("""CREATE TABLE IF NOT EXISTS asns (
                asn TEXT PRIMARY KEY,
                org TEXT NOT NULL,
                type TEXT NOT NULL,
                sub TEXT NOT NULL,
                prefixes TEXT,
                country TEXT DEFAULT 'BR',
                status TEXT NOT NULL,
                date_added DATETIME DEFAULT CURRENT_TIMESTAMP
            )""")

            # Hosts — with group_name column
            cur.execute("""CREATE TABLE IF NOT EXISTS hosts (
                ip TEXT PRIMARY KEY,
                hostname TEXT NOT NULL,
                port_ssh INTEGER DEFAULT 22,
                port_telnet INTEGER DEFAULT 23,
                username TEXT,
                password TEXT,
                type TEXT NOT NULL,
                fabricante TEXT NOT NULL,
                group_name TEXT DEFAULT '',
                status TEXT DEFAULT 'Offline'
            )""")

            cur.execute("""CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sev TEXT NOT NULL,
                title TEXT NOT NULL,
                desc TEXT NOT NULL,
                meta TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)""")

            cur.execute("""CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sev TEXT NOT NULL,
                module TEXT NOT NULL,
                msg TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)""")

            # ─── Discovery ─────────────────────────────────
            cur.execute("""CREATE TABLE IF NOT EXISTS range_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                color TEXT DEFAULT '#3da9fc',
                cidrs TEXT NOT NULL,
                scan_interval_min INTEGER DEFAULT 15,
                monitor BOOLEAN DEFAULT 1,
                last_scan DATETIME)""")

            cur.execute("""CREATE TABLE IF NOT EXISTS discovered_hosts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER NOT NULL,
                ip TEXT NOT NULL,
                hostname TEXT,
                vendor TEXT,
                os TEXT,
                rtt_ms REAL,
                status TEXT DEFAULT 'unknown',
                monitor BOOLEAN DEFAULT 0,
                last_seen DATETIME,
                FOREIGN KEY (group_id) REFERENCES range_groups(id) ON DELETE CASCADE,
                UNIQUE (group_id, ip))""")

            cur.execute("""CREATE TABLE IF NOT EXISTS discovered_services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                host_id INTEGER NOT NULL,
                port INTEGER NOT NULL,
                proto TEXT NOT NULL,
                service TEXT,
                banner TEXT,
                FOREIGN KEY (host_id) REFERENCES discovered_hosts(id) ON DELETE CASCADE,
                UNIQUE (host_id, port, proto))""")

            self._migrate(cur)
            self._seed(cur)
            conn.commit()

    def _migrate(self, cur):
        """Idempotent migrations for users upgrading from v1 schema."""
        # Add columns to legacy tables if missing
        def cols(table):
            cur.execute(f"PRAGMA table_info({table})")
            return [r[1] for r in cur.fetchall()]

        if "country" not in cols("asns"):
            cur.execute("ALTER TABLE asns ADD COLUMN country TEXT DEFAULT 'BR'")
        if "date_added" not in cols("asns"):
            cur.execute("ALTER TABLE asns ADD COLUMN date_added DATETIME DEFAULT CURRENT_TIMESTAMP")
        if "group_name" not in cols("hosts"):
            cur.execute("ALTER TABLE hosts ADD COLUMN group_name TEXT DEFAULT ''")

        cur.execute("INSERT OR REPLACE INTO meta (k, v) VALUES ('schema_version', ?)",
                    (str(self.SCHEMA_VERSION),))

    def _seed(self, cur):
        # Seed ASNs if empty
        cur.execute("SELECT COUNT(*) FROM asns")
        if cur.fetchone()[0] == 0:
            cur.executemany(
                "INSERT INTO asns (asn, org, type, sub, prefixes, country, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                [
                    ("263870", "Webstorage",  "self",    "OWN", "200.149.0.0/16, 2804:7f0::/32", "BR", "Ativo"),
                    ("262332", "IX.br SP",    "ix",      "PTT", "200.219.130.0/24",              "BR", "Ativo"),
                    ("12956",  "Telefônica",  "transit", "TRA", "213.140.0.0/16, 2a02:8800::/32","ES", "Ativo"),
                    ("174",    "Cogent",      "transit", "TRA", "38.0.0.0/8, 2001:550::/32",     "US", "Ativo"),
                    ("15169",  "Google",      "peer",    "DST", "8.8.8.0/24, 142.250.0.0/15",    "US", "Ativo"),
                    ("16509",  "Amazon AWS",  "peer",    "DST", "52.0.0.0/11",                   "US", "Ativo"),
                ])

        cur.execute("SELECT COUNT(*) FROM hosts")
        if cur.fetchone()[0] == 0:
            cur.executemany(
                "INSERT INTO hosts (ip, hostname, port_ssh, port_telnet, username, password, type, fabricante, group_name, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    ("192.168.0.106", "RouterBoard", 22, 23, "admin", "7878", "Router", "MikroTik", "SP-Core", "Online"),
                    ("192.168.0.22",  "walker",      22, 23, "rluft", "7878", "Server", "Linux",    "Tools",   "Online"),
                    ("192.168.0.101", "papaimach",   22, 23, "rluft", "7878", "Server", "Linux",    "Tools",   "Offline"),
                    ("192.168.0.104", "TP-Link AP",  22, 23, "admin", "admin","Switch", "TP-Link",  "DC1",     "Online"),
                ])

        cur.execute("SELECT COUNT(*) FROM alerts")
        if cur.fetchone()[0] == 0:
            cur.executemany(
                "INSERT INTO alerts (sev, title, desc, meta) VALUES (?, ?, ?, ?)",
                [
                    ("critical", "Prepend detection", "AS174 está fazendo AS-Path prepend (3x) no prefixo 200.149.0.0/16.", "AS_PATH 174 174 174 263870"),
                    ("critical", "Route flapping",    "Prefixo 187.45.128.0/19 oscilou 8 vezes nos últimos 15 min via AS12956.", "RFD threshold 2000"),
                    ("warn",     "MED change",        "Telefônica alterou MED de 100 → 250 em 17 prefixos.", "Sessão eBGP 187.16.220.1"),
                ])

        cur.execute("SELECT COUNT(*) FROM logs")
        if cur.fetchone()[0] == 0:
            cur.executemany(
                "INSERT INTO logs (sev, module, msg) VALUES (?, ?, ?)",
                [
                    ("INFO",  "System", "fzBGPTools inicializado com sucesso."),
                    ("INFO",  "BGP",    "Sessão BGP com AS262332 (IX.br SP) estabelecida."),
                    ("WARN",  "BGP",    "Alteração de rota detectada no prefixo 187.45.128.0/19."),
                    ("ERROR", "Host",   "Host papaimach (192.168.0.101) não responde ao ping."),
                ])

        cur.execute("SELECT COUNT(*) FROM range_groups")
        if cur.fetchone()[0] == 0:
            cur.executemany(
                "INSERT INTO range_groups (name, color, cidrs, scan_interval_min, monitor) VALUES (?, ?, ?, ?, ?)",
                [
                    ("LAN Local",        "#3da9fc", "192.168.0.0/24", 15, 1),
                    ("Backbone SP",      "#a18cff", "10.0.0.0/24, 10.0.5.0/24", 15, 1),
                    ("IX Public Peering","#21d4fd", "200.219.130.0/24", 5,  1),
                ])

    # ───────────────────────── ASNs ─────────────────────────
    def get_asns(self):
        with self.get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT asn, org, type, sub, prefixes, country, status, date_added FROM asns")
            return cur.fetchall()

    def add_asn(self, asn, org, type_, sub, prefixes, status, country="BR"):
        with self.get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""INSERT INTO asns (asn, org, type, sub, prefixes, country, status)
                           VALUES (?, ?, ?, ?, ?, ?, ?)
                           ON CONFLICT(asn) DO UPDATE SET
                             org=excluded.org, type=excluded.type, sub=excluded.sub,
                             prefixes=excluded.prefixes, country=excluded.country,
                             status=excluded.status""",
                        (asn, org, type_, sub, prefixes, country, status))
            conn.commit()

    def remove_asn(self, asn):
        with self.get_conn() as conn:
            conn.execute("DELETE FROM asns WHERE asn = ?", (asn,))
            conn.commit()

    # ───────────────────────── Hosts ─────────────────────────
    def get_hosts(self):
        with self.get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""SELECT ip, hostname, port_ssh, port_telnet, username, password,
                                  type, fabricante, status, COALESCE(group_name, '')
                           FROM hosts""")
            return cur.fetchall()

    def add_host(self, ip, hostname, port_ssh, port_telnet, username, password,
                 type_, fabricante, group_name="", status="Offline"):
        with self.get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""INSERT INTO hosts
                (ip, hostname, port_ssh, port_telnet, username, password, type, fabricante, group_name, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(ip) DO UPDATE SET
                    hostname=excluded.hostname, port_ssh=excluded.port_ssh,
                    port_telnet=excluded.port_telnet, username=excluded.username,
                    password=excluded.password, type=excluded.type,
                    fabricante=excluded.fabricante, group_name=excluded.group_name,
                    status=excluded.status""",
                (ip, hostname, port_ssh, port_telnet, username, password,
                 type_, fabricante, group_name, status))
            conn.commit()

    def remove_host(self, ip):
        with self.get_conn() as conn:
            conn.execute("DELETE FROM hosts WHERE ip = ?", (ip,))
            conn.commit()

    def set_host_status(self, ip, status):
        with self.get_conn() as conn:
            conn.execute("UPDATE hosts SET status = ? WHERE ip = ?", (status, ip))
            conn.commit()

    # ───────────────────────── Alerts / Logs ─────────────────────────
    def get_alerts(self):
        with self.get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT sev, title, desc, meta, timestamp FROM alerts ORDER BY timestamp DESC")
            return cur.fetchall()

    def get_logs(self, limit=500):
        with self.get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT sev, module, msg, timestamp FROM logs ORDER BY id DESC LIMIT ?", (limit,))
            return cur.fetchall()

    def add_log(self, sev, module, msg):
        with self.get_conn() as conn:
            conn.execute("INSERT INTO logs (sev, module, msg) VALUES (?, ?, ?)", (sev, module, msg))
            conn.commit()

    def add_alert(self, sev, title, desc, meta):
        with self.get_conn() as conn:
            conn.execute("INSERT INTO alerts (sev, title, desc, meta) VALUES (?, ?, ?, ?)",
                         (sev, title, desc, meta))
            conn.commit()

    # ───────────────────────── Range Groups ─────────────────────────
    def get_range_groups(self):
        with self.get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""SELECT id, name, color, cidrs, scan_interval_min, monitor, last_scan
                           FROM range_groups ORDER BY id""")
            return cur.fetchall()

    def add_range_group(self, name, color, cidrs, scan_interval_min=15, monitor=1):
        with self.get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""INSERT INTO range_groups (name, color, cidrs, scan_interval_min, monitor)
                           VALUES (?, ?, ?, ?, ?)""",
                        (name, color, cidrs, scan_interval_min, 1 if monitor else 0))
            conn.commit()
            return cur.lastrowid

    def update_range_group(self, gid, **fields):
        if not fields:
            return
        cols = ", ".join(f"{k} = ?" for k in fields)
        vals = list(fields.values()) + [gid]
        with self.get_conn() as conn:
            conn.execute(f"UPDATE range_groups SET {cols} WHERE id = ?", vals)
            conn.commit()

    def remove_range_group(self, gid):
        with self.get_conn() as conn:
            conn.execute("DELETE FROM range_groups WHERE id = ?", (gid,))
            conn.commit()

    def touch_range_scan(self, gid):
        with self.get_conn() as conn:
            conn.execute("UPDATE range_groups SET last_scan = CURRENT_TIMESTAMP WHERE id = ?", (gid,))
            conn.commit()

    # ───────────────────────── Discovered hosts ─────────────────────────
    def get_discovered(self, group_id):
        with self.get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""SELECT id, ip, hostname, vendor, os, rtt_ms, status, monitor, last_seen
                           FROM discovered_hosts WHERE group_id = ? ORDER BY ip""", (group_id,))
            hosts = cur.fetchall()
            result = []
            for h in hosts:
                hid = h[0]
                cur.execute("""SELECT port, proto, service FROM discovered_services
                               WHERE host_id = ? ORDER BY port""", (hid,))
                services = cur.fetchall()
                result.append((h, services))
            return result

    def upsert_discovered_host(self, group_id, ip, hostname=None, vendor=None,
                               os_name=None, rtt_ms=None, status="online"):
        with self.get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""INSERT INTO discovered_hosts
                (group_id, ip, hostname, vendor, os, rtt_ms, status, last_seen)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(group_id, ip) DO UPDATE SET
                    hostname=COALESCE(excluded.hostname, hostname),
                    vendor=COALESCE(excluded.vendor, vendor),
                    os=COALESCE(excluded.os, os),
                    rtt_ms=COALESCE(excluded.rtt_ms, rtt_ms),
                    status=excluded.status,
                    last_seen=CURRENT_TIMESTAMP""",
                (group_id, ip, hostname, vendor, os_name, rtt_ms, status))
            cur.execute("SELECT id FROM discovered_hosts WHERE group_id = ? AND ip = ?",
                        (group_id, ip))
            row = cur.fetchone()
            conn.commit()
            return row[0] if row else None

    def add_discovered_service(self, host_id, port, proto, service=None, banner=None):
        with self.get_conn() as conn:
            conn.execute("""INSERT OR REPLACE INTO discovered_services
                (host_id, port, proto, service, banner) VALUES (?, ?, ?, ?, ?)""",
                (host_id, port, proto, service, banner))
            conn.commit()

    def set_monitor(self, host_id, on):
        with self.get_conn() as conn:
            conn.execute("UPDATE discovered_hosts SET monitor = ? WHERE id = ?",
                         (1 if on else 0, host_id))
            conn.commit()
