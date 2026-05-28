import time
import socket
import paramiko
from PyQt5.QtCore import QThread, pyqtSignal

class SSHShellWorker(QThread):
    stdout_received = pyqtSignal(str)
    connected = pyqtSignal()
    connection_failed = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, host, port, username, password):
        super().__init__()
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.ssh = None
        self.channel = None
        self._running = True
        self.input_queue = []

    def send_input(self, text):
        if self.channel and not self.channel.closed:
            self.input_queue.append(text)

    def stop(self):
        self._running = False
        if self.channel:
            self.channel.close()
        if self.ssh:
            self.ssh.close()

    def run(self):
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(
                self.host, 
                port=self.port, 
                username=self.username, 
                password=self.password,
                timeout=5.0
            )
            self.connected.emit()
            
            # Start interactive shell
            self.channel = self.ssh.invoke_shell(term='vt100', width=80, height=24)
            self.channel.setblocking(0)
            
            while self._running:
                # Send queued input
                if self.input_queue:
                    inp = self.input_queue.pop(0)
                    self.channel.send(inp)
                
                # Check for output
                try:
                    if self.channel.recv_ready():
                        data = self.channel.recv(4096).decode('utf-8', errors='ignore')
                        if data:
                            self.stdout_received.emit(data)
                except socket.timeout:
                    pass
                except Exception:
                    break
                
                if self.channel.exit_status_ready():
                    break
                
                time.sleep(0.02)
                
        except Exception as e:
            self.connection_failed.emit(str(e))
        finally:
            if self.channel:
                self.channel.close()
            if self.ssh:
                self.ssh.close()
            self.finished.emit()
