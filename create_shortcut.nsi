; The name of the installer
Name "ge-rfid-wms"

; The file to write
OutFile "ge-rfid-wms-Setup.exe"

; The default installation directory
InstallDir "$PROGRAMFILES\ge"

; Request application privileges for Windows Vista
RequestExecutionLevel admin

; Pages
Page directory
Page instfiles

; Sections

Section "MainSection" SEC01

  ; Set output path to the installation directory.
  SetOutPath $INSTDIR

  ; Put file there
  File ".\dist\ge-rfid-wms.exe"

SectionEnd

Section "Shortcuts"

  ; Set output path to the desktop
  SetOutPath $DESKTOP

  ; Create a desktop shortcut
  CreateShortCut "$DESKTOP\ge-rfid-wms.lnk" "$INSTDIR\ge-rfid-wms.exe"

SectionEnd

; Functions

Function .onInit

  ; Set the shell variable context to all users
  SetShellVarContext all

  ; Get the desktop path and store it in a variable
  ;StrCpy $DESKTOP $DESKTOP

FunctionEnd
