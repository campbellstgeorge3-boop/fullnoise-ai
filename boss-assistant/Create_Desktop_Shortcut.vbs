' Double-click this once to put a "Boss Assistant" shortcut on your Desktop with an icon.
' Then you can pin that shortcut to the taskbar (right-click it -> Pin to taskbar).
Set fso = CreateObject("Scripting.FileSystemObject")
Set wsh = CreateObject("WScript.Shell")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
targetVbs = scriptDir & "\Start_Boss_Assistant.vbs"

' Shortcut on Desktop
desktop = wsh.SpecialFolders("Desktop")
linkPath = desktop & "\Boss Assistant.lnk"

Set shortcut = wsh.CreateShortcut(linkPath)
shortcut.TargetPath = "wscript.exe"
shortcut.Arguments = """" & targetVbs & """"
shortcut.WorkingDirectory = scriptDir
shortcut.Description = "Boss Assistant — monthly reports that answer back"
shortcut.WindowStyle = 7
' Use custom icon if we have one, else a nice built-in (chart = 21)
customIco = scriptDir & "\boss_assistant.ico"
If fso.FileExists(customIco) Then
  shortcut.IconLocation = customIco
Else
  shortcut.IconLocation = "C:\Windows\System32\shell32.dll,21"
End If
shortcut.Save

MsgBox "Shortcut created on your Desktop:" & vbCrLf & vbCrLf & "Boss Assistant", 64, "Done"
