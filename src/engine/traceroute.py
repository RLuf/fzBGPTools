"""Traceroute runner with ASN/IX resolution."""
import sys
import re
import socket
from PyQt5.QtCore import QProcess, QObject, pyqtSignal
from src.engine.asn_resolver import resolve_asn_and_org


class TracerouteRunner(QObject):
    # hop_received: hop_num, ip, host, asn, as_name, ms, is_ix
    hop_received = pyqtSignal(int, str, str, str, str, float, bool)
    finished = pyqtSignal(int)
    output_raw = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self._on_stdout)
        self.process.readyReadStandardError.connect(self._on_stderr)
        self.process.finished.connect(self._on_finished)

    def start_traceroute(self, host):
        if sys.platform == "win32":
            self.process.start("tracert", [host])
        else:
            # -q 1 = 1 query per hop, -n = no resolution (we do it)
            self.process.start("traceroute", ["-q", "1", "-n", host])

    def stop(self):
        if self.process.state() == QProcess.Running:
            self.process.terminate()
            if not self.process.waitForFinished(800):
                self.process.kill()

    def _on_stdout(self):
        data = self.process.readAllStandardOutput().data().decode("utf-8", errors="ignore")
        self.output_raw.emit(data)
        self._parse(data)

    def _on_stderr(self):
        data = self.process.readAllStandardError().data().decode("utf-8", errors="ignore")
        self.output_raw.emit(data)

    def _parse(self, text):
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            m = re.match(r"^(\d+)\s+", line)
            if not m:
                continue
            hop = int(m.group(1))
            ip_m = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", line)
            if not ip_m:
                self.hop_received.emit(hop, "* * *", "Sem resposta", "AS-UNKNOWN", "—", 0.0, False)
                continue
            ip = ip_m.group(1)
            try:
                host = socket.gethostbyaddr(ip)[0]
            except Exception:
                host = ip
            ms_matches = re.findall(r"(\d+(?:\.\d+)?)\s*ms", line)
            ms = sum(float(x) for x in ms_matches) / len(ms_matches) if ms_matches else 0.0
            asn, org = resolve_asn_and_org(ip)
            is_ix = ("ptt.br" in host.lower() or "ix.br" in host.lower() or
                     "ix" in org.lower() or "ptt" in org.lower())
            self.hop_received.emit(hop, ip, host, asn, org, ms, is_ix)

    def _on_finished(self, exit_code, _status):
        self.finished.emit(exit_code)
