"""
Update checker — consulta o Gitea em fzrepo.rogerluft.com.br para detectar
versões mais novas do que a instalada.

Roda em uma QThread para não bloquear a UI. Estado é exposto via signals:
  - state_changed("idle" | "checking" | "uptodate" | "available" | "error")
  - update_available(latest_version, release_url, notes)

Uso pelo sidebar / settings:

    from src.engine.updater import UpdateChecker
    checker = UpdateChecker()
    checker.state_changed.connect(on_state)
    checker.update_available.connect(on_update)
    checker.check()
"""

import json
import re
import urllib.request
import urllib.error
from PyQt5.QtCore import QObject, QThread, pyqtSignal

from src.version import __version__, __update_url__


# Endpoint Gitea (compatível com API v1 do Gitea)
# https://docs.gitea.com/api/1.20/#tag/repository/operation/repoGetLatestRelease
GITEA_HOST = __update_url__.rstrip("/")
GITEA_OWNER = "webstorage"
GITEA_REPO = "fzBGPTools"
LATEST_RELEASE_URL = f"{GITEA_HOST}/api/v1/repos/{GITEA_OWNER}/{GITEA_REPO}/releases/latest"


def _parse_semver(v):
    """'v0.2.0' or '0.2.0-rc1' → (0, 2, 0). Returns None if unparseable."""
    if not v:
        return None
    v = v.lstrip("v").split("-", 1)[0]
    m = re.match(r"^(\d+)\.(\d+)\.(\d+)$", v)
    if not m:
        return None
    return tuple(int(x) for x in m.groups())


def is_newer(remote, local):
    r = _parse_semver(remote)
    l = _parse_semver(local)
    if not r or not l:
        return False
    return r > l


class _Worker(QThread):
    result = pyqtSignal(str, str, str)  # state, version, url
    error = pyqtSignal(str)

    def run(self):
        try:
            req = urllib.request.Request(
                LATEST_RELEASE_URL,
                headers={"User-Agent": f"fzBGPTools/{__version__}",
                         "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=4.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            tag = data.get("tag_name", "")
            html_url = data.get("html_url", "")
            notes = data.get("body", "")
            if is_newer(tag, __version__):
                self.result.emit("available", tag, html_url)
            else:
                self.result.emit("uptodate", tag or __version__, html_url)
        except urllib.error.URLError as e:
            self.error.emit(f"Sem conexão com {GITEA_HOST}: {e.reason}")
        except Exception as e:
            self.error.emit(f"Erro ao verificar: {e}")


class UpdateChecker(QObject):
    state_changed = pyqtSignal(str)  # idle | checking | uptodate | available | error
    update_available = pyqtSignal(str, str)  # version, url
    update_uptodate = pyqtSignal(str)  # latest tag known
    update_failed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = None
        self._state = "idle"

    @property
    def state(self):
        return self._state

    def _set_state(self, s):
        self._state = s
        self.state_changed.emit(s)

    def check(self):
        if self._state == "checking":
            return
        self._set_state("checking")
        self._worker = _Worker()
        self._worker.result.connect(self._on_result)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_result(self, state, version, url):
        self._set_state(state)
        if state == "available":
            self.update_available.emit(version, url)
        else:
            self.update_uptodate.emit(version)

    def _on_error(self, msg):
        self._set_state("error")
        self.update_failed.emit(msg)
