' 全规则服务器 · 状态上报静默启动器（无黑窗口）
pythonw = "C:\Users\Lenovo\AppData\Local\Programs\Python\Python312\pythonw.exe"
Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
Set ws = CreateObject("WScript.Shell")
ws.Run """" & pythonw & """ """ & scriptDir & "\report.py""", 0, False
