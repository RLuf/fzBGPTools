"""
TCP connect scanner — async fingerprinting de hosts em ranges CIDR.
Usado pela tela Discovery. Não requer privilégios (TCP connect, não SYN).
"""

import socket
import ipaddress
import threading
from queue import Queue
from PyQt5.QtCore import QObject, pyqtSignal, QThread

# Portas mais relevantes para infra de rede / BGP
DEFAULT_PORTS = [
    (22,    "tcp", "SSH"),
    (23,    "tcp", "Telnet"),
    (53,    "tcp", "DNS"),
    (80,    "tcp", "HTTP"),
    (161,   "tcp", "SNMP"),
    (179,   "tcp", "BGP"),
    (443,   "tcp", "HTTPS"),
    (646,   "tcp", "LDP"),
    (830,   "tcp", "NETCONF"),
    (5432,  "tcp", "Postgres"),
    (8080,  "tcp", "HTTP-Alt"),
    (11019, "tcp", "BMP"),
    (57400, "tcp", "gRPC"),
]


def expand_cidrs(cidr_str, max_hosts=1024):
    """
    Recebe '10.0.0.0/24, 192.168.0.0/24' → lista de IPs (str).
    Aborta se exceder max_hosts para evitar /16 acidental.
    """
    ips = []
    parts = [p.strip() for p in cidr_str.replace(";", ",").split(",") if p.strip()]
    for p in parts:
        try:
            net = ipaddress.ip_network(p, strict=False)
        except ValueError:
            continue
        # Pular IPv6 muito grandes
        if net.num_addresses > max_hosts:
            continue
        # /32 ou /128 → host único
        if net.prefixlen in (32, 128):
            ips.append(str(net.network_address))
            continue
        for ip in net.hosts():
            ips.append(str(ip))
            if len(ips) >= max_hosts:
                return ips
    return ips


def tcp_probe(ip, port, timeout=0.6):
    """True se a porta TCP responde a conexão."""
    try:
        s = socket.socket(socket.AF_INET if ":" not in ip else socket.AF_INET6,
                          socket.SOCK_STREAM)
        s.settimeout(timeout)
        result = s.connect_ex((ip, port))
        s.close()
        return result == 0
    except Exception:
        return False


def grab_banner(ip, port, timeout=0.8):
    """Pega banner curto (primeiros bytes) para fingerprint."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((ip, port))
        try:
            data = s.recv(128)
            s.close()
            return data.decode("utf-8", errors="ignore").strip()[:80]
        except socket.timeout:
            s.close()
            return ""
    except Exception:
        return ""


def reverse_dns(ip, timeout=0.5):
    """rDNS rápido com timeout."""
    socket.setdefaulttimeout(timeout)
    try:
        return socket.gethostbyaddr(ip)[0]
    except Exception:
        return None
    finally:
        socket.setdefaulttimeout(None)


def guess_vendor(banner, services):
    """Heurística simples de fabricante a partir do banner e portas."""
    b = (banner or "").lower()
    if "mikrotik" in b or "routeros" in b:
        return ("MikroTik", "RouterOS")
    if "cisco" in b:
        return ("Cisco", "IOS")
    if "junos" in b or "juniper" in b:
        return ("Juniper", "Junos")
    if "ubuntu" in b:
        return ("Linux", "Ubuntu")
    if "debian" in b:
        return ("Linux", "Debian")
    if "openssh" in b:
        return ("Linux", b.split()[0] if b else "OpenSSH")
    # Heurística por mix de portas
    s = {p for (p, _, _) in services}
    if 179 in s and 22 in s:
        return ("Router", "BGP-capable")
    if 80 in s or 443 in s:
        return ("Web", "")
    return ("", "")


class ScanRunner(QObject):
    """
    Roda em uma QThread. Emite progresso e cada host/serviço descoberto.
    """
    host_started   = pyqtSignal(str)                              # ip
    host_done      = pyqtSignal(str, str, str, str, float, list)  # ip, hostname, vendor, os, rtt_ms, [(port, proto, service)]
    progress       = pyqtSignal(int, int)                         # done, total
    finished       = pyqtSignal(int)                              # hosts_up

    def __init__(self, parent=None):
        super().__init__(parent)
        self._stop = False
        self._thread = None
        self.ports = list(DEFAULT_PORTS)

    def stop(self):
        self._stop = True

    def run(self, cidr_str, max_hosts=1024, workers=64):
        """Disparar o scan. Retorna imediatamente — sinais entregam resultado."""
        self._stop = False
        self._thread = threading.Thread(
            target=self._do_scan, args=(cidr_str, max_hosts, workers), daemon=True)
        self._thread.start()

    def _do_scan(self, cidr_str, max_hosts, workers):
        ips = expand_cidrs(cidr_str, max_hosts=max_hosts)
        total = len(ips)
        done = [0]
        up = [0]
        lock = threading.Lock()
        queue = Queue()
        for ip in ips:
            queue.put(ip)

        def worker():
            while not self._stop:
                try:
                    ip = queue.get_nowait()
                except Exception:
                    return
                self._probe_host(ip, up, lock)
                with lock:
                    done[0] += 1
                self.progress.emit(done[0], total)
                queue.task_done()

        ts = []
        for _ in range(min(workers, max(1, total))):
            t = threading.Thread(target=worker, daemon=True)
            t.start()
            ts.append(t)
        for t in ts:
            t.join()
        self.finished.emit(up[0])

    def _probe_host(self, ip, up, lock):
        self.host_started.emit(ip)
        # Quick TCP-22 ping for latency estimate
        import time
        services = []
        rtt = 0.0
        any_open = False
        for port, proto, name in self.ports:
            if self._stop:
                return
            t0 = time.perf_counter()
            if tcp_probe(ip, port, timeout=0.5):
                ms = (time.perf_counter() - t0) * 1000.0
                if not any_open:
                    rtt = ms
                any_open = True
                services.append((port, proto, name))
        if not any_open:
            return
        with lock:
            up[0] += 1
        hostname = reverse_dns(ip) or ip
        # Try a banner grab on SSH or HTTP
        banner = ""
        for p in (22, 80, 443, 23):
            if any(s[0] == p for s in services):
                banner = grab_banner(ip, p)
                if banner:
                    break
        vendor, os_name = guess_vendor(banner, services)
        self.host_done.emit(ip, hostname, vendor, os_name, rtt, services)
