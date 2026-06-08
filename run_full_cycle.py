import subprocess
import os
import argparse
import sys
from datetime import datetime

# Paths
CWD = r"c:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP\HelpDesk"

LOG_FILE = os.path.join(CWD, "automation_history.log")

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_msg = f"[{timestamp}] {msg}"
    print(formatted_msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(formatted_msg + "\n")

def run_step(command_list, name):
    log(f"Iniciando: {name}...")
    try:
        result = subprocess.run(["python"] + command_list, cwd=CWD, capture_output=True, text=True)
        if result.returncode == 0:
            log(f"Éxito: {name}")
            if result.stdout:
                print(result.stdout.strip())
            return True
        else:
            log(f"ERROR en {name}:")
            print(result.stderr)
            return False
    except Exception as e:
        log(f"FALLO CRÍTICO en {name}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Automatización End-to-End de Reportes HelpDesk.")
    parser.add_argument("--flavor", type=str, required=True, choices=["IT", "NEGOCIO"], help="Flavor del reporte a enviar (IT o NEGOCIO)")
    args = parser.parse_args()

    log(f"=== INICIANDO CICLO DE AUTOMATIZACIÓN - FLAVOR: {args.flavor} ===")

    # 1. Descargar Datos
    if not run_step(["download_today.py"], "Descarga de Datos"):
        log("Abortando ciclo por error en descarga.")
        sys.exit(1)

    # 2. Generar Reportes (Silenciosamente)
    if not run_step(["generate_premium_report.py", "--silent"], "Generación de Reportes"):
        log("Abortando ciclo por error en generación.")
        sys.exit(1)

    # 3. Enviar Reporte Especificado
    if not run_step(["send_helpdesk_report.py", "--flavor", args.flavor], f"Envío de Reporte {args.flavor}"):
        log("Ciclo finalizado con errores en el envío.")
        sys.exit(1)

    log("=== CICLO COMPLETADO EXITOSAMENTE ===")

if __name__ == "__main__":
    main()
