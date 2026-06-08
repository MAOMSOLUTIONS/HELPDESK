@echo off
title Automatización Integral OMEGAFUSION
set CWD="c:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP\HelpDesk"
cd /d %CWD%

echo [%date% %time%] === INICIANDO AUTOMATIZACION INTEGRAL ===

echo --- 1. REPORTES HELPDESK (Tickets) ---
echo Ejecutando Reporte IT...
python run_full_cycle.py --flavor IT >> automation_history.log 2>&1
echo Ejecutando Reporte NEGOCIO...
python run_full_cycle.py --flavor NEGOCIO >> automation_history.log 2>&1

echo --- 2. REPORTE DE PRIORIDADES (Requirements) ---
echo Regenerando Dashboard...
python generate_priority_report.py >> automation_history.log 2>&1
echo Enviando Estatus IT Final...
python send_estatus_it_final.py >> automation_history.log 2>&1

echo [%date% %time%] === AUTOMATIZACION COMPLETADA ===
exit
