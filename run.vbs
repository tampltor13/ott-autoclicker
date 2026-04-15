Set objShell = CreateObject("WScript.Shell")
objShell.CurrentDirectory = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\") - 1)
objShell.Run "python ott_autoclicker.py", 0, False
