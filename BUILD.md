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

## 🤖 Compilação e Release no GitHub (Recomendado)

O repositório possui uma pipeline CI/CD configurada no GitHub Actions em `.github/workflows/release.yml` que compila e empacota a aplicação automaticamente. Existem duas maneiras de usar este fluxo:

### Método 1: Criação de Release Oficial (Via Git Tag)
Este é o método recomendado para gerar uma nova versão pública com os instaladores executáveis finais.
1. Atualize a versão no código rodando:
   ```bash
   python scripts/bump_version.py 0.3.0
   ```
2. Documente as alterações no [CHANGELOG.md](CHANGELOG.md) sob a seção da nova versão.
3. Crie um commit e envie a tag correspondente:
   ```bash
   git add -A
   git commit -m "release: v0.3.0"
   make tag  # Executa: git tag v0.3.0 && git push origin v0.3.0
   ```
4. A pipeline do GitHub Actions será disparada automaticamente:
   - Compila o binário standalone e gera o `.deb` em um runner Ubuntu Linux.
   - Compila o binário e gera o `.exe` do instalador em um runner Windows Server.
   - Cria um **GitHub Release** automático contendo ambos os instaladores e extrai as notas de atualização direto do `CHANGELOG.md`.

### Método 2: Execução Manual (Sem Criar Release)
Se você deseja apenas testar a compilação remota a partir de uma branch qualquer, sem publicar uma release formal:
1. Vá até a página do repositório no GitHub.
2. Acesse a aba **Actions** e selecione o workflow **Release** no menu à esquerda.
3. Clique no botão dropdown **Run workflow** do lado direito.
4. Escolha a branch desejada e digite a versão temporária (ex: `0.2.0`).
5. Clique em **Run workflow**.
6. A execução irá compilar ambos os pacotes (Linux e Windows) em paralelo. Quando concluído, os instaladores estarão disponíveis para download direto como arquivos zipados na seção **Artifacts** na base da página da execução do Action (com os nomes `fzbgptools-deb` e `fzbgptools-exe`).

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
