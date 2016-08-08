' http://superuser.com/questions/392061/how-to-make-a-shortcut-from-cmd
' http://answers.microsoft.com/en-us/windows/forum/windows_vista-files/how-to-create-a-shortcut-with-relative-path/3e1b0ede-1e18-4ecd-937b-66756d3409d3?auth=1

' http://stackoverflow.com/questions/16138831/getting-current-directory-in-vbscript#16143382
dim fso: set fso = CreateObject("Scripting.FileSystemObject")
dim currentDirectory
currentDirectory = fso.GetAbsolutePathName(".")

Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "Blarg.LNK"
Set oLink = oWS.CreateShortcut(sLinkFile)
    oLink.TargetPath = "%windir%\system32\cmd.exe"
    oLink.Arguments = "/c start blarg.exe"
    oLink.Description = "Blarg. Fait par R" & ChrW(233) & "ch" & ChrW(232) & "r. http://recher.wordpress.com"
    ' http://www.tek-tips.com/viewthread.cfm?qid=1235645
    oLink.IconLocation = fso.BuildPath(currentDirectory, "gam_icon.ico") & ", 0"
    ' https://support.microsoft.com/en-us/kb/244677
    oLink.WindowStyle = "7"
oLink.Save