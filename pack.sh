pyinstaller -n ge-rfid-wms -F -w -i icon.ico app.py

source_file="dist"
zip_file="ge-rfid-wms.zip"
if [ -f "$zip_file" ]; then
  rm "$zip_file"
fi
powershell.exe -nologo -noprofile -command "& { Add-Type -A 'System.IO.Compression.FileSystem'; [System.IO.Compression.ZipFile]::CreateFromDirectory('$source_file', '$zip_file', 'Optimal', 0); }"

makensis.exe create_shortcut.nsi