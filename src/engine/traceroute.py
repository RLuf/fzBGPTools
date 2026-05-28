import sys
import re
import socket
from PyQt5.QtCore import QProcess, QObject, pyqtSignal
from src.engine.asn_resolver import resolve_asn_and_org

class TracerouteRunner(QObject):
    # Signals to emit to UI
    # hop_received: hop_num, ip, host, asn, as_name, ms, is_ix
    hop_received = pyqtSignal(int, str, str, str, str, float, bool)
    finished = pyqtSignal(int)
    output_raw = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.on_stdout)
        self.process.readyReadStandardError.connect(self.on_stderr)
        self.process.finished.connect(self.on_finished)
        self.current_hop = 0

    def start_traceroute(self, host):
        self.current_hop = 0
        if sys.platform == "win32":
            # Windows tracert command
            args = [host]
            self.process.start("tracert", args)
        else:
            # Linux traceroute command
            # Using -I (ICMP) is often more reliable on home networks
            args = ["-q", "1", host] # 1 query per hop for speed
            self.process.start("traceroute", args)

    def stop(self):
        if self.process.state() == QProcess.Running:
            self.process.terminate()

    def on_stdout(self):
        data = self.process.readAllStandardOutput().data().decode("utf-8", errors="ignore")
        self.output_raw.emit(data)
        self.parse_output(data)

    def on_stderr(self):
        data = self.process.readAllStandardError().data().decode("utf-8", errors="ignore")
        self.output_raw.emit(data)

    def parse_output(self, text):
        lines = text.splitlines()
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Match hop number at the beginning
            hop_match = re.match(r"^(\d+)\s+", line)
            if not hop_match:
                continue
            
            hop_num = int(hop_match.group(1))
            
            # Find IP address
            ip_match = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", line)
            if not ip_match:
                # Hop timed out or no IP found (e.g. * * *)
                self.hop_received.emit(hop_num, "* * *", "Sem resposta", "AS-UNKNOWN", "N/A", 0.0, False)
                continue
            
            ip = ip_match.group(1)
            
            # Try to resolve hostname
            try:
                host = socket.gethostbyaddr(ip)[0]
            except Exception:
                host = ip
            
            # Extract latency (find numbers followed by ms)
            ms_matches = re.findall(r"(\d+(?:\.\d+)?)\s*ms", line)
            if ms_matches:
                # Calculate average RTT if multiple exist
                ms = sum(float(x) for x in ms_matches) / len(ms_matches)
            else:
                ms = 0.0
                
            # Query ASN and Org Name
            asn, org = resolve_asn_and_org(ip)
            
            # Check if it goes through an IX/PTT
            # Typically has "sp.ptt.br", "ix.br", "sp.ix.br" or Org name contains IX or PTT
            is_ix = "ptt.br" in host.lower() or "ix.br" in host.lower() or "ix" in org.lower() or "ptt" in org.lower()
            
            self.hop_received.emit(hop_num, ip, host, asn, org, ms, is_ix)

    def on_finished(self, exit_code, exit_status):
        self.finished.emit(exit_code)
