import sys
from PyQt5.QtCore import QProcess, QObject, pyqtSignal

class PingRunner(QObject):
    output_received = pyqtSignal(str)
    finished = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.on_stdout)
        self.process.readyReadStandardError.connect(self.on_stderr)
        self.process.finished.connect(self.on_finished)

    def start_ping(self, host, count=4):
        # Determine platform-specific ping command
        if sys.platform == "win32":
            args = ["-n", str(count), host]
        else:
            args = ["-c", str(count), host]
        
        self.process.start("ping", args)

    def stop(self):
        if self.process.state() == QProcess.Running:
            self.process.terminate()

    def on_stdout(self):
        data = self.process.readAllStandardOutput().data().decode("utf-8", errors="ignore")
        self.output_received.emit(data)

    def on_stderr(self):
        data = self.process.readAllStandardError().data().decode("utf-8", errors="ignore")
        self.output_received.emit(data)

    def on_finished(self, exit_code, exit_status):
        self.finished.emit(exit_code)
