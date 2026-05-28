import time
import socket
import telnetlib
from PyQt5.QtCore import QThread, pyqtSignal

class TelnetShellWorker(QThread):
    stdout_received = pyqtSignal(str)
    connected = pyqtSignal()
    connection_failed = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, host, port, username=None, password=None):
        super().__init__()
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.tn = None
        self._running = True
        self.input_queue = []

    def send_input(self, text):
        self.input_queue.append(text)

    def stop(self):
        self._running = False
        if self.tn:
            self.tn.close()

    def run(self):
        try:
            self.tn = telnetlib.Telnet(self.host, self.port, timeout=5.0)
            self.connected.emit()
            
            # Read lazily and send queued inputs
            while self._running:
                # Send queued input
                if self.input_queue:
                    inp = self.input_queue.pop(0)
                    self.tn.write(inp.encode('utf-8', errors='ignore'))
                
                # Check for output (using non-blocking select read)
                try:
                    data = self.tn.read_very_eager().decode('utf-8', errors='ignore')
                    if data:
                        self.stdout_received.emit(data)
                except EOFError:
                    break
                except Exception:
                    break
                
                time.sleep(0.02)
                
        except Exception as e:
            self.connection_failed.emit(str(e))
        finally:
            if self.tn:
                self.tn.close()
            self.finished.emit()
