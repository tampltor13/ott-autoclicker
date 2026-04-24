Set objShell = CreateObject("WScript.Shell")
objShell.CurrentDirectory = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\") - 1)

Dim python
python = ""

' Check registry for Python install path (system-wide and per-user, 3.10-3.13)
Dim versions(7), hives(1), i, j, pyPath
versions(0) = "3.13" : versions(1) = "3.12" : versions(2) = "3.11" : versions(3) = "3.10"
versions(4) = "3.9"  : versions(5) = "3.8"  : versions(6) = "3.7"  : versions(7) = "3.6"
hives(0) = "HKLM\SOFTWARE\Python\PythonCore\"
hives(1) = "HKCU\SOFTWARE\Python\PythonCore\"

On Error Resume Next
For j = 0 To 1
    For i = 0 To 7
        If python = "" Then
            pyPath = objShell.RegRead(hives(j) & versions(i) & "\InstallPath\")
            If pyPath <> "" Then
                python = pyPath & "python.exe"
            End If
        End If
    Next
Next
On Error GoTo 0

If python = "" Then python = "python"

objShell.Run """" & python & """ ott_autoclicker.py", 0, False
