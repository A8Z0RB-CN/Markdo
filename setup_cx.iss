; Inno Setup Installer Script
; For creating Markdo installer

#define MyAppName "Markdo"
#define MyAppVersion "1.0.3"
#define MyAppPublisher "A8Z0RB"
#define MyAppURL "https://github.com"
#define MyAppExeName "Markdo.exe"
#define MyAppId "{{A8Z0RB-Markdo-1.0.3}"

[Setup]
; Application basic information
AppId={#MyAppId}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=
InfoBeforeFile=
InfoAfterFile=
OutputDir=installer_cx
OutputBaseFilename=Markdo_Setup_CX_{#MyAppVersion}
SetupIconFile=Markdo.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

; Installer appearance (using default images, comment out if not found)
; WizardImageFile=compiler:WizModernImage-IS.bmp
; WizardSmallImageFile=compiler:WizModernSmallImage-IS.bmp

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode
Name: "fileassociation"; Description: "Associate .md files with Markdo"; GroupDescription: "File Associations"; Flags: checkedonce

[Files]
; Main program
Source: "build\exe.win-amd64-3.13\Markdo.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "build\exe.win-amd64-3.13\python3.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "build\exe.win-amd64-3.13\python313.dll"; DestDir: "{app}"; Flags: ignoreversion

; Resource files
Source: "build\exe.win-amd64-3.13\markdo-icon.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "build\exe.win-amd64-3.13\register_file_association.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "build\exe.win-amd64-3.13\unregister_file_association.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "build\exe.win-amd64-3.13\FILE_ASSOCIATION_README.md"; DestDir: "{app}"; Flags: ignoreversion

; Library files directory
Source: "build\exe.win-amd64-3.13\lib\*"; DestDir: "{app}\lib"; Flags: ignoreversion recursesubdirs createallsubdirs

; PyQt6 plugins
Source: "build\exe.win-amd64-3.13\PyQt6.uic.widget-plugins\*"; DestDir: "{app}\PyQt6.uic.widget-plugins"; Flags: ignoreversion recursesubdirs createallsubdirs

; License file (if exists)
Source: "build\exe.win-amd64-3.13\frozen_application_license.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Registry]
; File association - .md files
Root: HKCR; Subkey: ".md"; ValueType: string; ValueName: ""; ValueData: "MarkdoMarkdownFile"; Flags: uninsdeletevalue; Tasks: fileassociation
Root: HKCR; Subkey: "MarkdoMarkdownFile"; ValueType: string; ValueName: ""; ValueData: "Markdown Document"; Flags: uninsdeletekey; Tasks: fileassociation
Root: HKCR; Subkey: "MarkdoMarkdownFile\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"; Tasks: fileassociation
Root: HKCR; Subkey: "MarkdoMarkdownFile\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Tasks: fileassociation

; File association - .markdown files
Root: HKCR; Subkey: ".markdown"; ValueType: string; ValueName: ""; ValueData: "MarkdoMarkdownFile"; Flags: uninsdeletevalue; Tasks: fileassociation

[Run]
; Run file association script after installation
Filename: "{app}\register_file_association.bat"; Description: "Register file associations"; Flags: runhidden; Tasks: fileassociation
; Optionally run program after installation
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
; Run file association unregister script before uninstallation
Filename: "{app}\unregister_file_association.bat"; Flags: runhidden

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Operations that can be performed after installation
  end;
end;

function InitializeUninstall(): Boolean;
begin
  Result := True;
end;

