$Action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"%USERPROFILE%\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP\HelpDesk\run_full_automation.bat`""

# Morning Trigger (8:30 AM)
$TriggerAM = New-ScheduledTaskTrigger -Daily -At 8:30am

$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RunOnlyIfNetworkAvailable
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive

# Register/Overwrite the task with only the morning trigger
Register-ScheduledTask -TaskName "OmegaFusion_Full_Automation" -Action $Action -Trigger $TriggerAM -Settings $Settings -Principal $Principal -Force

# Delete the old single-trigger task to avoid confusion
Unregister-ScheduledTask -TaskName "OmegaFusion_HelpDesk_Reports" -Confirm:$false -ErrorAction SilentlyContinue
