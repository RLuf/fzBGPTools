# fzBGPTools — Makefile
# Convenience targets for development, build and packaging.

VERSION := $(shell python3 -c "from src.version import __version__; print(__version__)" 2>/dev/null || echo "0.2.0")
PYTHON  ?= python3
PIP     ?= pip3

.PHONY: help install dev run clean test bin deb exe release tag

help:
	@echo ""
	@echo "  fzBGPTools v$(VERSION) — Build targets"
	@echo ""
	@echo "  make install      Instala dependências de runtime"
	@echo "  make dev          Instala dev + build deps"
	@echo "  make run          Executa em modo dev"
	@echo "  make clean        Remove dist/, build/, *.egg-info/"
	@echo "  make bin          Compila binário standalone com PyInstaller"
	@echo "  make deb          Empacota .deb (Linux)"
	@echo "  make exe          Empacota instalador .exe (Windows / NSIS)"
	@echo "  make release      Roda bin + deb + exe (precisa ambiente correto)"
	@echo "  make tag          Cria git tag v$(VERSION) e dispara CI"
	@echo ""

install:
	$(PIP) install -r requirements.txt

dev:
	$(PIP) install -r requirements.txt
	$(PIP) install pyinstaller

run:
	$(PYTHON) -m src.main

clean:
	rm -rf build/work dist *.egg-info __pycache__
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

bin:
	$(PYTHON) -m PyInstaller --noconfirm --clean fzbgptools.spec

deb: bin
	bash build/linux/build-deb.sh $(VERSION)

exe:
	cmd /c build\\windows\\build-win.bat $(VERSION)

release: clean bin
	@echo "✓ Binary built: dist/fzbgptools"
	@echo "Run 'make deb' on Linux or 'make exe' on Windows to package."

tag:
	git tag -a v$(VERSION) -m "Release v$(VERSION)"
	git push origin v$(VERSION)
	@echo "→ CI will build .deb + .exe and publish to Releases."
