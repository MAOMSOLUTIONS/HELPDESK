$CWD = "c:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP\HelpDesk"
$PythonPath = "C:\Users\DIRECCION-TI\AppData\Local\Microsoft\WindowsApps\python.exe"

$Action = New-ScheduledTaskAction -Execute $PythonPath -Argument "$CWD\send_individual_reminders.py" -WorkingDirectory $CWD
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At "08:45"
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive

$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -WakeToRun -Priority 1

Register-ScheduledTask -TaskName "HelpDesk_Individual_Reminders" -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -Force
Write-Host "Tarea registrada: HelpDesk_Individual_Reminders (L-V a las 08:45 AM)" -ForegroundColor Green
