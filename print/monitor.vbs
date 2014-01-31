'Automatic printing on windows
'Based on the DropboxPrint script by by Amit Agarwal http://www.labnol.org/
'Updated on 08/14/2012 @labnol
 
Option Explicit
On Error Resume Next
 
Const WAIT_TIME  = 10000 '5 seconds
Const PRINT_TIME = 10000 '5 seconds
 
Dim WshShell, fso, configFile, objReadFile, str64, strPath, objFile, ApplicationData
Dim dbWatchDir, attFolder, objShell, colItems, objItem, dbLogDir, logFolder, doneFolder
 
Set WshShell = CreateObject("Wscript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

strPath = Wscript.ScriptFullName
Set objFile = objFSO.GetFile(strPath)
dbWatchDir = objFSO.GetParentFolderName(objFile)

If Not fso.FolderExists (dbWatchDir) Then
 Set attFolder = fso.CreateFolder (dbWatchDir)
 WScript.Echo "Created a watch folder to hold your incoming print jobs at " & dbWatchDir
End If
 
doneFolder = dbWatchDir & "\printed"
 
If Not fso.FolderExists (dbLogDir) Then
 Set logFolder = fso.CreateFolder (dbLogDir)
 'WScript.Echo "Created a folder to archive processed jobs - " & dbLogDir
End If
 
Do While True
 
Set objShell = CreateObject("Shell.Application")
Set objFolder = objShell.Namespace(dbWatchDir)
Set colItems = objFolder.Items
 
For Each objItem in colItems
 If Not objItem.IsFolder Then  
  If Mid(objItem.NAME,len(file.NAME)-4,5) = ".html" then
    objItem.InvokeVerbEx("Print")
    WScript.Sleep(PRINT_TIME)
    fso.MoveFile dbWatchDir & "\" & objItem.Name & "*", doneFolder
  End If
 end if
Next
WScript.Sleep(WAIT_TIME)
Set objShell = nothing
Set objFolder = nothing
Set colItems = nothing
Loop
 
