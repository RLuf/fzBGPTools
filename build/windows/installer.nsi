; build/windows/installer.nsi — NSIS installer for fzBGPTools (Windows)
; Build with:  makensis /DVERSION=0.2.0 build\windows\installer.nsi
; Expects dist\fzbgptools.exe to exist (run `pyinstaller fzbgptools.spec` first).

!ifndef VERSION
  !define VERSION "0.2.0"
!endif

!define APP_NAME    "fzBGPTools"
!define COMPANY     "fzBGPTools"
!define EXE_NAME    "fzbgptools.exe"
!define INSTALL_DIR "$PROGRAMFILES64\${APP_NAME}"
!define UNINST_KEY  "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"

SetCompressor /SOLID lzma
Unicode true

Name        "${APP_NAME}"
OutFile     "..\..\dist\${APP_NAME}-${VERSION}-setup.exe"
InstallDir  "${INSTALL_DIR}"
InstallDirRegKey HKLM "Software\${APP_NAME}" "InstallDir"
RequestExecutionLevel admin
BrandingText "${APP_NAME} v${VERSION}"

; ─── Modern UI ───
!include "MUI2.nsh"

!define MUI_ABORTWARNING
!define MUI_ICON   "..\..\src\resources\icon.ico"
!define MUI_UNICON "..\..\src\resources\icon.ico"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "..\..\LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\${EXE_NAME}"
!define MUI_FINISHPAGE_RUN_TEXT "Iniciar ${APP_NAME} agora"
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "PortugueseBR"
!insertmacro MUI_LANGUAGE "English"

; ─── Version info ───
VIProductVersion "${VERSION}.0"
VIAddVersionKey "ProductName"    "${APP_NAME}"
VIAddVersionKey "CompanyName"    "${COMPANY}"
VIAddVersionKey "FileDescription" "Network Peering Mapper"
VIAddVersionKey "FileVersion"    "${VERSION}"
VIAddVersionKey "ProductVersion" "${VERSION}"
VIAddVersionKey "LegalCopyright" "© Roger Luft"

; ─── Sections ───
Section "fzBGPTools (obrigatório)" SecMain
  SectionIn RO
  SetOutPath "$INSTDIR"

  ; Binary (PyInstaller --onefile output)
  File "..\..\dist\${EXE_NAME}"
  File "..\..\README.md"
  File "..\..\CHANGELOG.md"
  File "..\..\LICENSE"

  ; Registry
  WriteRegStr HKLM "Software\${APP_NAME}" "InstallDir" "$INSTDIR"
  WriteRegStr HKLM "Software\${APP_NAME}" "Version" "${VERSION}"

  ; Add/Remove Programs entry
  WriteRegStr HKLM "${UNINST_KEY}" "DisplayName"     "${APP_NAME}"
  WriteRegStr HKLM "${UNINST_KEY}" "DisplayVersion"  "${VERSION}"
  WriteRegStr HKLM "${UNINST_KEY}" "Publisher"       "${COMPANY}"
  WriteRegStr HKLM "${UNINST_KEY}" "UninstallString" "$\"$INSTDIR\Uninstall.exe$\""
  WriteRegStr HKLM "${UNINST_KEY}" "DisplayIcon"     "$INSTDIR\${EXE_NAME}"
  WriteRegStr HKLM "${UNINST_KEY}" "URLInfoAbout"    "https://github.com/rluft/fzBGPTools"
  WriteRegDWORD HKLM "${UNINST_KEY}" "NoModify" 1
  WriteRegDWORD HKLM "${UNINST_KEY}" "NoRepair" 1

  ; Uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd

Section "Atalho no Menu Iniciar" SecStartMenu
  CreateDirectory "$SMPROGRAMS\${APP_NAME}"
  CreateShortcut  "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk"   "$INSTDIR\${EXE_NAME}"
  CreateShortcut  "$SMPROGRAMS\${APP_NAME}\Desinstalar.lnk"   "$INSTDIR\Uninstall.exe"
SectionEnd

Section "Atalho na Área de Trabalho" SecDesktop
  CreateShortcut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${EXE_NAME}"
SectionEnd

; ─── Uninstaller ───
Section "Uninstall"
  Delete "$INSTDIR\${EXE_NAME}"
  Delete "$INSTDIR\README.md"
  Delete "$INSTDIR\CHANGELOG.md"
  Delete "$INSTDIR\LICENSE"
  Delete "$INSTDIR\Uninstall.exe"
  RMDir  "$INSTDIR"

  Delete "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk"
  Delete "$SMPROGRAMS\${APP_NAME}\Desinstalar.lnk"
  RMDir  "$SMPROGRAMS\${APP_NAME}"
  Delete "$DESKTOP\${APP_NAME}.lnk"

  DeleteRegKey HKLM "${UNINST_KEY}"
  DeleteRegKey HKLM "Software\${APP_NAME}"
SectionEnd
