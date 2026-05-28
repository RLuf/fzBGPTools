# HANDOFF — fzBGPTools v0.2.0 → Antigravity (build .deb + .exe)

> **Para o dev Antigravity/Gemini:** este documento é o briefing pra você
> compilar e empacotar o fzBGPTools. Leia inteiro antes de rodar qualquer build.

---

## 🎯 Objetivo
Empacotar o app desktop **fzBGPTools** em dois instaladores funcionais:
- **Linux:** `fzbgptools_0.2.0_amd64.deb` (Deepin/Ubuntu/Debian)
- **Windows:** `fzBGPTools-0.2.0-setup.exe` (NSIS, com atalhos Menu Iniciar + Desktop)

Toda a infra já está montada — você só precisa rodar os comandos certos
no ambiente certo.

---

## ⚡ TL;DR — comandos de build

### Linux (.deb)
```bash
make install      # pip install -r requirements.txt
make bin          # PyInstaller → dist/fzbgptools
make deb          # dpkg-deb → dist/fzbgptools_0.2.0_amd64.deb
```

### Windows (.exe)
```cmd
build\windows\build-win.bat 0.2.0
REM Faz tudo: pip install, gera .ico via Pillow, PyInstaller, NSIS
REM → dist\fzBGPTools-0.2.0-setup.exe
```

### CI automatizado (preferido)
```bash
git tag v0.2.0 && git push origin v0.2.0
# .github/workflows/release.yml builda os dois em paralelo e publica em Releases
```

---

## ⚠️ Pontos de atenção — leia ANTES de buildar

### 1. Compatibilidade PyQt5 vs PySide6
O código **usa PyQt5 explicitamente** (`from PyQt5.QtWidgets import ...`).
Se você quiser migrar para PySide6, substitua via:
```bash
find src -name "*.py" -exec sed -i 's/PyQt5/PySide6/g' {} \;
sed -i 's/pyqtSignal/Signal/g; s/pyqtSlot/Slot/g' src/**/*.py
```
Mas **não precisa** — PyQt5 funciona e é o padrão atual.

### 2. Dependências de sistema (Linux runtime)
Quem instalar o `.deb` precisa ter:
- `libqt5core5a libqt5gui5 libqt5widgets5` (já listadas em `Depends:` do control)
- `iputils-ping traceroute` (listadas em `Depends:`)
- `openssh-client telnet` (em `Recommends:` — usuário pode pular)

Se rodar `apt install ./fzbgptools_*.deb`, o apt resolve sozinho.

### 3. Dependências de build (Linux)
```bash
sudo apt install -y \
    python3 python3-pip python3-dev \
    libxcb-xinerama0 libxkbcommon-x11-0 libegl1 libdbus-1-3 \
    dpkg-dev fakeroot
pip install -r requirements.txt pyinstaller
```

### 4. Dependências de build (Windows)
- **Python 3.11** instalado em `C:\Python311` (ou via Microsoft Store)
- **NSIS 3.x** instalado e no `PATH` — https://nsis.sourceforge.io
- **Pillow** é instalado automaticamente pelo `build-win.bat` para gerar `icon.ico`
- **Não precisa** de Visual C++ Build Tools (PyQt5 vem com wheels prontos)

### 5. Conversão de ícone — Windows
O NSIS precisa de `.ico`, mas só temos `icon.png`. O `build-win.bat` resolve isso
automaticamente via Pillow:
```python
from PIL import Image
img = Image.open('src/resources/icon.png')
img.save('src/resources/icon.ico', sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])
```
Se rodar manual, **gere o .ico antes do `makensis`** — senão o build quebra.

### 6. Arquitetura
- Linux: o `.deb` é compilado para a arch do host (`amd64` em runner padrão).
  Se precisar `arm64`, rode num runner ARM — não há cross-compile.
- Windows: 64-bit por padrão (`$PROGRAMFILES64` no NSIS). Para 32-bit altere
  `installer.nsi` linha `InstallDir`.

### 7. Banco SQLite no usuário final
Path: `~/.config/fzbgptools/fzbgptools.db` (Linux) ou
`%APPDATA%\fzbgptools\fzbgptools.db` (Windows — Qt resolve via `QStandardPaths`,
mas atualmente o código usa `os.path.expanduser("~/.config/...")` que NÃO
funciona em Windows).

**🔴 BUG conhecido:** corrija `src/database.py` se quiser path Windows correto:
```python
def __init__(self, db_path=None):
    if db_path is None:
        if sys.platform == "win32":
            config_dir = os.path.join(os.environ.get("APPDATA", "."), "fzbgptools")
        else:
            config_dir = os.path.expanduser("~/.config/fzbgptools")
        os.makedirs(config_dir, exist_ok=True)
        db_path = os.path.join(config_dir, "fzbgptools.db")
```
Sem isso o `.exe` cria o DB em `C:\Users\X\.config\fzbgptools\` — funciona mas
fica fora da convenção Windows.

### 8. Assinatura digital (opcional mas recomendado)
- **Windows:** o `.exe` não-assinado dispara o SmartScreen. Para assinar:
  ```cmd
  signtool sign /f cert.pfx /p SENHA /tr http://timestamp.digicert.com /td sha256 dist\fzBGPTools-0.2.0-setup.exe
  ```
  Sem certificado válido, instrua usuário a clicar "Mais informações → Executar mesmo assim".
- **Linux:** `.deb` não precisa assinatura, mas se for distribuir num repo apt,
  use `dpkg-sig --sign builder dist/*.deb` com chave GPG.

### 9. Update checker — endpoint Gitea
`src/engine/updater.py` consulta:
```
GET https://fzrepo.rogerluft.com.br/api/v1/repos/webstorage/fzBGPTools/releases/latest
```

Se o Gitea **ainda não está com esse repo criado**, o botão "Verificar
atualização" vai mostrar erro de rede. Confirme com o Roger se o repo
`webstorage/fzBGPTools` já existe no Gitea antes de prometer o feature funcionar.

Para testar offline, force estado mockado:
```python
# em src/engine/updater.py, função check():
self._set_state("uptodate")  # ou "available"
```

### 10. Versão tem 3 fontes de verdade — sincronize
Quando bumpar versão, rode `python scripts/bump_version.py X.Y.Z` que atualiza:
- `src/version.py` → `__version__`
- `pyproject.toml` → `version`
- `CHANGELOG.md` → nova seção placeholder

**Não esqueça também:**
- `build/windows/installer.nsi` → `!define VERSION` (passado via CLI no `.bat`, mas hardcoded como fallback)
- `Makefile` → `VERSION := ...` (lê do `src/version.py` automaticamente)
- `README.md` → badge `version-0.2.0` (manual)

---

## 🧪 Smoke test pós-build

### Linux (.deb)
```bash
# 1. Instalar
sudo apt install ./dist/fzbgptools_0.2.0_amd64.deb

# 2. Rodar do menu OU
fzbgptools

# 3. Verificações
# ✓ Janela abre em 1280×820
# ✓ Sidebar lista 7 telas (Dashboard, ASN, Hosts, Discovery, Tools, Logs, Settings)
# ✓ Botão "Verificar atualização" muda de estado quando clica
# ✓ Settings → "Sobre" mostra v0.2.0, autor Roger Luft
# ✓ Network Tools → Ping para 8.8.8.8 funciona (precisa de iputils-ping)
# ✓ Tema escuro aplicado em tudo

# 4. Desinstalar limpo
sudo apt remove fzbgptools
# ✓ /usr/lib/fzbgptools/ removido
# ✓ ~/.config/fzbgptools/ PRESERVADO (dados do usuário)
```

### Windows (.exe)
```cmd
REM 1. Rodar instalador (admin)
dist\fzBGPTools-0.2.0-setup.exe

REM 2. Verificações
REM ✓ Welcome → License (CC BY 4.0) → Install Dir → Install
REM ✓ Atalho criado em Menu Iniciar e Desktop
REM ✓ Adiciona em Add/Remove Programs
REM ✓ Versão e ícone corretos no Explorer (botão direito → Propriedades)

REM 3. Desinstalar pelo Painel de Controle
REM ✓ Remove tudo de Program Files\fzBGPTools
REM ✓ Limpa registro
```

---

## 🚨 Erros comuns que você vai ver

| Erro | Causa | Solução |
|------|-------|---------|
| `ModuleNotFoundError: PyQt5` | `pip install` não rodou | `pip install -r requirements.txt` |
| `dpkg-deb: command not found` | Falta dpkg-dev | `sudo apt install dpkg-dev` |
| `makensis: command not found` | NSIS fora do PATH | Adicione `C:\Program Files (x86)\NSIS` ao PATH |
| `libxcb-xinerama.so.0: cannot open shared object file` | Libs Qt faltando | `sudo apt install libxcb-xinerama0 libxkbcommon-x11-0` |
| `failed to load icon.ico` | Pillow não gerou | Rode manualmente: `python -c "from PIL import Image; Image.open('src/resources/icon.png').save('src/resources/icon.ico')"` |
| App roda em dev mas binário travado | hiddenimports faltando | Veja `fzbgptools.spec` → `hiddenimports=['paramiko', 'cryptography', 'PyQt5.sip']` |
| `.deb` instala mas app não aparece no menu | Cache de ícones | `sudo update-desktop-database; sudo gtk-update-icon-cache /usr/share/icons/hicolor` |

---

## 📦 Tamanho esperado dos artefatos

| Plataforma | Binário | Pacote final |
|-----------|---------|--------------|
| Linux `.deb`  | ~80–120 MB (PyInstaller embute Python + Qt) | ~40–60 MB compactado |
| Windows `.exe`| ~80–120 MB                                  | ~40–60 MB compactado |

Se sair muito maior, revise `excludes=` no `fzbgptools.spec` — provavelmente
`tkinter`, `matplotlib` ou `numpy` voltaram.

---

## ✅ Checklist final antes de publicar release

- [ ] `make clean && make bin` roda sem warnings
- [ ] `dist/fzbgptools` (Linux) ou `dist\fzbgptools.exe` (Windows) abre e mostra a janela
- [ ] `make deb` ou `build-win.bat` gera o instalador
- [ ] Smoke test pós-instalação passa nos 3 itens críticos (abre, navega, faz ping)
- [ ] `CHANGELOG.md` tem seção para esta versão
- [ ] `git tag v0.2.0 && git push origin v0.2.0`
- [ ] GitHub Actions termina verde
- [ ] Release no GitHub tem os 2 assets anexados
- [ ] Upload manual no Gitea `fzrepo.rogerluft.com.br` (se servir como mirror)

---

## 📞 Contato com o autor
- **Eng. Roger Luft** — roger@webstorage.com.br
- **Site:** https://about.rogerluft.com.br
- **Empresa:** Webstorage Tecnologia

Em caso de bug crítico no build, abra issue em
https://github.com/rluft/fzBGPTools/issues e mencione `@rluft`.

---

**Boa sorte com o build! 🚀**

— Claude (sessão de design/spec, 2026-05-27)
