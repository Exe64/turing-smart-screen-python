' ============================================================================
'  Lance le gestionnaire multi-ecrans SANS aucune fenetre (console masquee).
'  Utilise par le demarrage automatique (raccourci dans le dossier Demarrage).
'  Peut aussi etre lance manuellement par double-clic.
' ============================================================================

Set fso   = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

' Dossier racine du projet = dossier parent de "windows\"
projectDir = fso.GetParentFolderName(fso.GetParentFolderName(WScript.ScriptFullName))
shell.CurrentDirectory = projectDir

' pythonw.exe = interpreteur Python sans console.
' Le 0 masque toute fenetre, False = ne pas attendre la fin du programme.
shell.Run "pythonw.exe multiscreen.py", 0, False
