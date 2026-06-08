$Action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"%USERPROFILE%\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP\HelpDesk\run_daily_helpdesk.bat`""
$Trigger = New-ScheduledTaskTrigger -Daily -At 8:30am
# StartWhenAvailable ensures it runs after a missed schedule (e.g. computer was off)
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RunOnlyIfNetworkAvailable
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive

Register-ScheduledTask -TaskName "OmegaFusion_HelpDesk_Reports" -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Force
