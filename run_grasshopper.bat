SET rhinoFilePath=""%cd%\Form-Finding.3dm""
SET ghFilePath=""%cd%\Form-Finding.gh""

"C:\Program Files\Rhino 7\System\Rhino.exe" /nosplash /runscript="-open %rhinoFilePath% -grasshopper document open %ghFilePath% _save _enter _save exit"
exit