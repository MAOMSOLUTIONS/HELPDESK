@echo off
title Automatización HelpDesk - OMEGAFUSION
set CWD="c:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP\HelpDesk"
cd /d %CWD%

echo [%date% %time%] Iniciando Automatización Diaria...

echo Ejecutando Reporte IT...
python run_full_cycle.py --flavor IT >> automation_history.log 2>&1

echo Ejecutando Reporte NEGOCIO...
python run_full_cycle.py --flavor NEGOCIO >> automation_history.log 2>&1

echo [%date% %time%] Automatización Finalizada.
exit
