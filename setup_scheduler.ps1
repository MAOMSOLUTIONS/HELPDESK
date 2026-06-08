# Script de Configuracion: Programador de Tareas de Windows para Reportes HelpDesk (VERSION DE ALTA FIABILIDAD)

$CWD = "c:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP\HelpDesk"
$PythonPath = "C:\Users\DIRECCION-TI\AppData\Local\Microsoft\WindowsApps\python.exe"

# Funcion para registrar una tarea
function Register-HelpDeskTask {
    param(
        [string]$TaskName,
        [string]$Flavor,
        [string]$Time,
        [string[]]$Days
    )

    $Action = New-ScheduledTaskAction -Execute $PythonPath -Argument "$CWD\run_full_cycle.py --flavor $Flavor" -WorkingDirectory $CWD
    
    # Crear disparador semanal
    $Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $Days -At $Time
    
    $Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive
    
    # AJUSTES DE ALTA FIABILIDAD:
    # - WakeToRun: Despierta la PC si esta suspendida.
    # - StartWhenAvailable: Ejecuta la tarea lo antes posible si se perdio el inicio (ej. PC apagada).
    # - Priority 1: Prioridad maxima de ejecucion.
    $Settings = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -StartWhenAvailable `
        -WakeToRun `
        -Priority 1 `
        -ExecutionTimeLimit (New-TimeSpan -Minutes 30)

    # Registrar la tarea (Sobrescribe si existe)
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -Force
    Write-Host "Tarea registrada: $TaskName ($Flavor a las $Time L-V)" -ForegroundColor Green
}

# 1. Reporte IT Mañana (08:30 AM)
Register-HelpDeskTask -TaskName "HelpDesk_IT_Morning" -Flavor "IT" -Time "08:30" -Days "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"

# 2. Reporte Negocio (09:00 AM)
Register-HelpDeskTask -TaskName "HelpDesk_Business_Morning" -Flavor "NEGOCIO" -Time "09:00" -Days "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"

# 3. Reporte IT Tarde (03:00 PM / 15:00)
Register-HelpDeskTask -TaskName "HelpDesk_IT_Afternoon" -Flavor "IT" -Time "15:00" -Days "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"

Write-Host "=== CONFIGURACION DE ALTA FIABILIDAD COMPLETADA EXITOSAMENTE ===" -ForegroundColor Cyan
Write-Host "Se activo 'WakeToRun' y 'StartWhenAvailable'."
