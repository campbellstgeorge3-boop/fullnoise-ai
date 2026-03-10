' Double-click to start Boss Assistant — no console window, no PowerShell.
' The app window will open; use "Stop server" or close it when done.
Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
pythonw = scriptDir & "\.venv\Scripts\pythonw.exe"
script = scriptDir & "\run_app.py"
If Not fso.FileExists(pythonw) Then
  pythonw = "pythonw.exe"
End If
' Run from scriptDir so uvicorn and imports work
CreateObject("WScript.Shell").Run "cmd /c cd /d """ & scriptDir & """ && """ & pythonw & """ """ & script & """", 0, False
