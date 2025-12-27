; Inno Setup Installer Script
; For creating Markdo installer from Nuitka build
; Fixed: Removed [UninstallRun] section to prevent uninstaller freezing

#define MyAppName "Markdo"
#define MyAppVersion "1.0.3"
#define MyAppPublisher "A8Z0RB"
#define MyAppURL "https://github.com"
#define MyAppExeName "Markdo.exe"

[Setup]
; Application basic information
AppId={{A8Z0RB-Markdo-1.0.3}}
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
OutputDir=installer_nuitka
OutputBaseFilename=Markdo_Setup_Nuitka_{#MyAppVersion}
SetupIconFile=Markdo.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

; Installer appearance
; WizardImageFile=compiler:WizModernImage-IS.bmp
; WizardSmallImageFile=compiler:WizModernSmallImage-IS.bmp

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode
Name: "fileassociation"; Description: "Associate .md and .markdown files with Markdo"; GroupDescription: "File Associations"; Flags: checkedonce

[Files]
; Main executable
Source: "build\main.dist\Markdo.exe"; DestDir: "{app}"; Flags: ignoreversion

; All files and directories from Nuitka build
Source: "build\main.dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Additional resource files (if not already included in build directory)
Source: "markdo-icon.png"; DestDir: "{app}"; Flags: ignoreversion; Check: not FileExists(ExpandConstant('{app}\markdo-icon.png'))
Source: "register_file_association.bat"; DestDir: "{app}"; Flags: ignoreversion; Check: not FileExists(ExpandConstant('{app}\register_file_association.bat'))
Source: "unregister_file_association.bat"; DestDir: "{app}"; Flags: ignoreversion; Check: not FileExists(ExpandConstant('{app}\unregister_file_association.bat'))
Source: "FILE_ASSOCIATION_README.md"; DestDir: "{app}"; Flags: ignoreversion; Check: not FileExists(ExpandConstant('{app}\FILE_ASSOCIATION_README.md'))

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Registry]
; File association - .md files
; Note: uninsdeletevalue and uninsdeletekey flags ensure automatic cleanup during uninstall
Root: HKCR; Subkey: ".md"; ValueType: string; ValueName: ""; ValueData: "MarkdoMarkdownFile"; Flags: uninsdeletevalue; Tasks: fileassociation
Root: HKCR; Subkey: "MarkdoMarkdownFile"; ValueType: string; ValueName: ""; ValueData: "Markdown Document"; Flags: uninsdeletekey; Tasks: fileassociation
Root: HKCR; Subkey: "MarkdoMarkdownFile\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"; Flags: uninsdeletekey; Tasks: fileassociation
Root: HKCR; Subkey: "MarkdoMarkdownFile\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Flags: uninsdeletekey; Tasks: fileassociation

; File association - .markdown files
Root: HKCR; Subkey: ".markdown"; ValueType: string; ValueName: ""; ValueData: "MarkdoMarkdownFile"; Flags: uninsdeletevalue; Tasks: fileassociation

; Context menu - Edit with Markdo
Root: HKCR; Subkey: "MarkdoMarkdownFile\shell\edit"; ValueType: string; ValueName: ""; ValueData: "Edit with Markdo"; Flags: uninsdeletekey; Tasks: fileassociation
Root: HKCR; Subkey: "MarkdoMarkdownFile\shell\edit\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Flags: uninsdeletekey; Tasks: fileassociation

[Run]
; File associations are already registered via [Registry] section, no need to run script
; Optionally run program after installation (non-blocking)
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

; IMPORTANT: [UninstallRun] section is completely removed to prevent uninstaller freezing
; File associations are automatically cleaned up by Inno Setup using the uninsdeletevalue
; and uninsdeletekey flags in the [Registry] section above

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
  // Always allow uninstall to proceed
  Result := True;
end;
