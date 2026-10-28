; Inno Setup script: wraps dist\EtkinlikRadari (PyInstaller output) in a Turkish/English setup wizard.
; Built by packaging/build_windows.py, which passes /DAppVersion=<version> from etkinlik_radari/__init__.py.

#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif
#define AppName "Etkinlik Radarı"
#define AppExe "EtkinlikRadari.exe"

[Setup]
AppId={{6C1E9A43-58B2-4C55-9D0E-2B7F4A61E7C1}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher=Mehmet Emin Aruk
AppPublisherURL=https://x.com/eminarukk
AppContact=eminaruk@cingozsystems.com
VersionInfoVersion={#AppVersion}
DefaultDirName={autopf}\EtkinlikRadari
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
; per-user install by default (no admin prompt); the wizard offers "all users" too
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
LicenseFile=..\LICENSE
SetupIconFile=..\etkinlik_radari\assets\icon.ico
UninstallDisplayIcon={app}\{#AppExe}
OutputDir=..\dist
OutputBaseFilename=EtkinlikRadari-{#AppVersion}-Setup
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ShowLanguageDialog=auto

[Languages]
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[CustomMessages]
turkish.WebView2Missing=Etkinlik Radarı, Microsoft Edge WebView2 Runtime gerektirir. Windows 10/11'de genellikle yüklüdür; değilse indirme sayfası açılacak.
english.WebView2Missing=Etkinlik Radarı needs the Microsoft Edge WebView2 Runtime. It ships with Windows 10/11; if it is missing, the download page will open.

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "..\dist\EtkinlikRadari\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExe}"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent

[Code]
// The app renders through Edge WebView2; warn once at the end of setup if the runtime is not registered.
function WebView2Installed(): Boolean;
var v: String;
begin
  Result :=
    RegQueryStringValue(HKLM, 'SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}', 'pv', v) or
    RegQueryStringValue(HKLM, 'SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}', 'pv', v) or
    RegQueryStringValue(HKCU, 'Software\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}', 'pv', v);
  Result := Result and (v <> '') and (v <> '0.0.0.0');
end;

procedure CurStepChanged(CurStep: TSetupStep);
var code: Integer;
begin
  if (CurStep = ssPostInstall) and not WizardSilent() and not WebView2Installed() then
  begin
    MsgBox(CustomMessage('WebView2Missing'), mbInformation, MB_OK);
    ShellExec('open', 'https://developer.microsoft.com/microsoft-edge/webview2/', '', '', SW_SHOWNORMAL, ewNoWait, code);
  end;
end;
