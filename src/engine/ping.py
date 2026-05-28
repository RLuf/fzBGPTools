"""
Ping runner com parser de estatísticas (rtt min/avg/max/loss).
Emite eventos estruturados para a UI renderizar com cores estilo terminal.
"""

import sys
import re
from PyQt5.QtCore import QProcess, QObject, pyqtSignal


# Padrões cross-platform
_RE_LINUX_REPLY = re.compile(r"(\d+)\s+bytes from\s+([\d\.:a-fA-F]+).*?icmp_seq=(\d+).*?ttl=(\d+).*?time=([\d.]+)\s*ms", re.IGNORECASE)
_RE_LINUX_STATS = re.compile(r"(\d+)\s+packets transmitted,\s+(\d+)\s+received,\s+([\d.]+)%\s+packet loss", re.IGNORECASE)
_RE_LINUX_RTT   = re.compile(r"rtt min/avg/max/[a-z]+ = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)", re.IGNORECASE)

_RE_WIN_REPLY   = re.compile(r"Resposta de\s+([\d\.:a-fA-F]+).*?bytes=(\d+).*?tempo[=<]([\d]+)ms.*?TTL=(\d+)", re.IGNORECASE)
_RE_WIN_REPLY_EN= re.compile(r"Reply from\s+([\d\.:a-fA-F]+).*?bytes=(\d+).*?time[=<]([\d]+)ms.*?TTL=(\d+)", re.IGNORECASE)
_RE_WIN_LOSS    = re.compile(r"\((\d+)%\s+(?:de\s+)?(?:perda|loss)\)", re.IGNORECASE)
_RE_WIN_RTT     = re.compile(r"M[ií]nimo\s*=\s*(\d+)ms.*?M[áa]ximo\s*=\s*(\d+)ms.*?M[ée]dia\s*=\s*(\d+)ms", re.IGNORECASE | re.DOTALL)


class PingRunner(QObject):
    # Linha bruta para o terminal (sem classificação)
    output_received = pyqtSignal(str)

    # Eventos estruturados — classificam cada linha para a UI colorir
    # line_event(kind, text)  — kind in {"info","ok","warn","err","dim","stats"}
    line_event = pyqtSignal(str, str)

    # Stats agregados ao final
    # stats(transmitted, received, loss_pct, min_ms, avg_ms, max_ms)
    stats = pyqtSignal(int, int, float, float, float, float)

    # exit_code
    finished = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self._on_stdout)
        self.process.readyReadStandardError.connect(self._on_stderr)
        self.process.finished.connect(self._on_finished)
        self._buffer = ""

    def start_ping(self, host, count=7, timeout_sec=None):
        self._buffer = ""
        if sys.platform == "win32":
            args = ["-n", str(count), host]
            if timeout_sec is not None:
                args = ["-w", str(int(timeout_sec * 1000))] + args
            self.process.start("ping", args)
        else:
            args = ["-c", str(count), host]
            if timeout_sec is not None:
                args = ["-W", str(int(timeout_sec))] + args
            self.process.start("ping", args)
        self.line_event.emit("dim", f"$ ping {' '.join(args)}")

    def start_continuous(self, host):
        self._buffer = ""
        if sys.platform == "win32":
            args = ["-t", host]
        else:
            args = [host]  # Linux ping é contínuo por padrão sem -c
        self.process.start("ping", args)
        self.line_event.emit("dim", f"$ ping {' '.join(args)} (contínuo)")

    def stop(self):
        if self.process.state() == QProcess.Running:
            self.process.terminate()
            if not self.process.waitForFinished(800):
                self.process.kill()

    # ───────────── internal ─────────────
    def _emit_lines(self, data):
        self.output_received.emit(data)
        self._buffer += data
        # Quebrar em linhas para classificação
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            self._classify_line(line.rstrip("\r"))

    def _classify_line(self, line):
        if not line.strip():
            return
        # Linhas de resposta
        for rx in (_RE_LINUX_REPLY, _RE_WIN_REPLY, _RE_WIN_REPLY_EN):
            if rx.search(line):
                self.line_event.emit("ok", line)
                return
        # Stats agregados
        m = _RE_LINUX_STATS.search(line)
        if m:
            tx, rx, loss = int(m.group(1)), int(m.group(2)), float(m.group(3))
            kind = "ok" if loss < 1 else ("warn" if loss < 25 else "err")
            self.line_event.emit(kind, line)
            self._partial_stats = (tx, rx, loss)
            return
        m = _RE_LINUX_RTT.search(line)
        if m:
            mn, av, mx, _md = (float(m.group(i)) for i in range(1, 5))
            self.line_event.emit("stats", line)
            tx, rxc, loss = getattr(self, "_partial_stats", (0, 0, 0.0))
            self.stats.emit(tx, rxc, loss, mn, av, mx)
            return
        # Windows
        m = _RE_WIN_LOSS.search(line)
        if m:
            loss = float(m.group(1))
            kind = "ok" if loss < 1 else ("warn" if loss < 25 else "err")
            self.line_event.emit(kind, line)
            self._win_loss = loss
            return
        m = _RE_WIN_RTT.search(line)
        if m:
            mn, mx, av = float(m.group(1)), float(m.group(2)), float(m.group(3))
            self.line_event.emit("stats", line)
            loss = getattr(self, "_win_loss", 0.0)
            self.stats.emit(0, 0, loss, mn, av, mx)
            return
        # Erros conhecidos
        low = line.lower()
        if "timeout" in low or "unreachable" in low or "esgotou" in low or "inacess" in low:
            self.line_event.emit("err", line)
            return
        # Cabeçalho informativo
        if low.startswith(("ping ", "pinging ", "disparando ")) or "bytes of data" in low:
            self.line_event.emit("info", line)
            return
        # default
        self.line_event.emit("dim", line)

    def _on_stdout(self):
        data = self.process.readAllStandardOutput().data().decode("utf-8", errors="ignore")
        self._emit_lines(data)

    def _on_stderr(self):
        data = self.process.readAllStandardError().data().decode("utf-8", errors="ignore")
        self._emit_lines(data)

    def _on_finished(self, exit_code, _status):
        if self._buffer.strip():
            self._classify_line(self._buffer)
            self._buffer = ""
        self.finished.emit(exit_code)
