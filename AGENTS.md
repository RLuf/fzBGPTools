# AGENTS.md

> **REGRA ZERO — smoke test OBRIGATORIO depois de cada mudanca.**
> A compilacao sem erros nao prova nada. Toda mudanca em codigo ou configuracao de empacotamento deve terminar com `make clean && make bin && make deb` (ou correspondente local) + execucao real do binario/atalho ou chamada no terminal `fzbgptools` se instalado. Se a janela PyQt5 nao abrir ou houver erros no console, a mudanca falhou. Nao marcar tarefas como concluidas sem este smoke test.

## Sobre o projeto

**fzBGPTools** eh uma aplicacao desktop desenvolvida em Python 3 e PyQt5 para visualizacao de peering BGP, auto descoberta de hosts, ferramentas de rede e console CLI integrado.
O banco de dados eh local (SQLite) armazenado em `~/.config/fzbgptools/fzbgptools.db`.

## Onde achar o que

| Pergunta                                  | Onde                                                                       |
| ----------------------------------------- | -------------------------------------------------------------------------- |
| Ponto de entrada (Entrypoint)             | [src/main.py](file:///home/rluft/fzBGPTools/src/main.py)                    |
| Versao oficial canonica                   | [src/version.py](file:///home/rluft/fzBGPTools/src/version.py)              |
| Interface Gráfica (Widgets e Janelas)     | [src/ui/](file:///home/rluft/fzBGPTools/src/ui/)                            |
| Engine de Ping, Traceroute e Scanner      | [src/engine/](file:///home/rluft/fzBGPTools/src/engine/)                    |
| Script de empacotamento Debian            | [build/linux/build-deb.sh](file:///home/rluft/fzBGPTools/build/linux/build-deb.sh) |
| Script de empacotamento Windows           | [build/windows/build-win.bat](file:///home/rluft/fzBGPTools/build/windows/build-win.bat) |
| Pipeline de CI (GitHub Actions)           | [.github/workflows/release.yml](file:///home/rluft/fzBGPTools/.github/workflows/release.yml) |

## Comandos essenciais

A aplicacao possui um `Makefile` na raiz com os seguintes comandos principais:

```bash
make install      # Instala as dependencias de execução (requirements.txt)
make dev          # Instala dependencias de desenvolvimento e compilacao
make run          # Executa a aplicacao localmente em modo desenvolvedor (python -m src.main)
make clean        # Limpa pastas temporarias de build, caches e dist/
make bin          # Compila o binario unico (standalone) usando o fzbgptools.spec
make deb          # Cria o pacote Debian .deb na pasta dist/ para Linux
make tag          # Cria e envia tag git automatizada que dispara a pipeline de CI
```

## Convencoes do Repositorio

### Codigo
- Python 3.7+ (adere ao PyQt5).
- Versao declarada exclusivamente em `src/version.py`. Nunca hardcodar a versao em scripts de build de forma desassociada deste arquivo.
- Banco de dados e migrações estruturados de forma idempotente em `src/database.py`.

### Commits
- Usar formato de commits semanticos (`feat:`, `fix:`, `chore:`, `docs:`).
- Sempre registrar as alteracoes no arquivo `CHANGELOG.md` na secao correspondente a versao sob a diretriz "Keep a Changelog".

### ASCII-only por padrao
- Em codigo, comentarios, mensagens de erro, logs internos e documentacao técnica, **escrever sem acentos**.
- Preservar strings e interfaces voltadas ao usuario final no idioma local (PT-BR) com a devida acentuacao grafica. A regra de ASCII-only aplica-se a documentacao interna, logs tecnicos e comentarios de codigo.

### Mascaramento de credenciais
- Nunca commitar ou printar em logs chaves privadas, senhas de SSH ou credenciais.
- Se for exibir configs, mascarar chaves seguindo o formato: 4 primeiros caracteres + `...` + 4 ultimos caracteres.

## Checklist da REGRA ZERO (Apos qualquer alteracao)

1. **Incrementar Versao**: Incrementar a versao de forma semantica em [src/version.py](file:///home/rluft/fzBGPTools/src/version.py).
2. **Atualizar CHANGELOG**: Registrar as alteracoes detalhadas em [CHANGELOG.md](file:///home/rluft/fzBGPTools/CHANGELOG.md) sob a nova versao.
3. **Limpeza e Compilacao**: Executar `make clean` seguido de `make bin` para compilar o executavel.
4. **Geracao do Pacote**: Executar `make deb` para gerar o pacote Debian `.deb` atualizado na pasta `dist/`.
5. **Remover Versao Antiga**: Desinstalar a versao anterior instalada no sistema executando `sudo apt remove -y fzbgptools` ou `sudo dpkg -r fzbgptools`.
6. **Instalar Versao Nova**: Instalar o novo pacote Debian gerado executando `sudo apt install -y --reinstall ./dist/fzbgptools_<VERSAO>_amd64.deb` ou `sudo dpkg -i ./dist/fzbgptools_<VERSAO>_amd64.deb`.
7. **Teste Manual**: Executar o comando `fzbgptools` no terminal do sistema ou pelo atalho e realizar o smoke test.
8. **Verificar Telas**: Validar se todas as telas (Dashboard, ASN, Host Manager, Discovery, Network Tools, Logs, Settings) carregam perfeitamente e se os logs e alertas estao sendo povoados.
9. **Git Hygiene**: Garantir que o `.gitignore` nao contem nenhum arquivo sensivel novo exposto e fazer o commit.

