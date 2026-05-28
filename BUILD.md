# BUILD — Guia rápido

Documentação completa em [README.md](README.md). Este arquivo é só o cheatsheet
para empacotar uma release.

## 🐧 Linux → `.deb`

```bash
# Em uma máquina Ubuntu/Debian:
sudo apt install python3 python3-pip dpkg-dev
pip install -r requirements.txt pyinstaller

make bin         # → dist/fzbgptools (binário standalone)
make deb         # → dist/fzbgptools_0.2.0_amd64.deb

# Instalar:
sudo apt install ./dist/fzbgptools_0.2.0_amd64.deb
```

## 🪟 Windows → `.exe` installer

```cmd
REM Em uma máquina Windows 10+:
REM   - Python 3.11 (https://python.org)
REM   - NSIS    (https://nsis.sourceforge.io)

build\windows\build-win.bat 0.2.0
REM → dist\fzBGPTools-0.2.0-setup.exe
```

O script já converte `icon.png` em `icon.ico` automaticamente via Pillow.

## 🤖 Release automatizada (recomendado)

```bash
# 1. Bump
python scripts/bump_version.py 0.3.0

# 2. Edite CHANGELOG.md adicionando as mudanças desta release

# 3. Commit + tag (Makefile faz `git tag` + `push origin v$VERSION`)
git add -A && git commit -m "release: v0.3.0"
make tag
```

A pipeline em `.github/workflows/release.yml`:
1. Roda em paralelo nos runners `ubuntu-22.04` e `windows-2022`
2. Builda o binário PyInstaller em cada plataforma
3. Empacota `.deb` (Linux) e `.exe` (Windows)
4. Cria um GitHub Release com os assets + notas extraídas do CHANGELOG

Tempo total típico: **~6 minutos**.

## 🍎 macOS → `.app` (opcional)

```bash
pyinstaller --noconfirm --clean fzbgptools.spec
# → dist/fzBGPTools.app
```

Para distribuir, assine e notarize:
```bash
codesign --deep --force --options runtime --sign "Developer ID Application: NOME" dist/fzBGPTools.app
xcrun notarytool submit dist/fzBGPTools.app.zip --apple-id ... --wait
```

## ❌ Problemas comuns

| Sintoma | Solução |
|---------|---------|
| `pyinstaller: command not found` | `pip install pyinstaller` |
| `dpkg-deb: command not found` | `sudo apt install dpkg-dev` |
| `makensis: command not found` (Windows) | Instale [NSIS](https://nsis.sourceforge.io) e adicione `C:\Program Files (x86)\NSIS` ao PATH |
| Binário Linux não abre (`libxcb-xinerama.so.0: cannot open`) | `sudo apt install libxcb-xinerama0 libxkbcommon-x11-0 libegl1` |
| `.deb` instala mas app não aparece no menu | Faça logout/login ou rode `sudo update-desktop-database` |
| Windows: ícone genérico | Verifique se `src/resources/icon.ico` foi gerado (passo automático no `build-win.bat`) |
