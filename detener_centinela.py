import os
import subprocess
import ctypes
import sys

def detener():
    try:
        # Intentar detener el proceso usando taskkill de forma silenciosa
        resultado = subprocess.run(
            ["taskkill", "/F", "/IM", "CentinelaSFTP.exe"],
            capture_output=True,
            text=True,
            creationflags=0x08000000  # CREATE_NO_WINDOW para evitar parpadeos de consola
        )
        
        # Verificar si se encontró y cerró el proceso de manera exitosa
        if "correcto" in resultado.stdout.lower() or "success" in resultado.stdout.lower() or resultado.returncode == 0:
            ctypes.windll.user32.MessageBoxW(
                0, 
                "El Centinela SFTP ha sido detenido con éxito.\nMonitoreo finalizado y bitácoras guardadas de manera segura.", 
                "Centinela SFTP - Control", 
                0x40  # Icono de información azul
            )
        else:
            ctypes.windll.user32.MessageBoxW(
                0, 
                "El Centinela SFTP no se encuentra en ejecución en este momento.", 
                "Centinela SFTP - Control", 
                0x30  # Icono de advertencia amarillo
            )
    except Exception as e:
        ctypes.windll.user32.MessageBoxW(
            0, 
            f"Ocurrió un error al intentar detener el Centinela:\n{str(e)}", 
            "Centinela SFTP - Error", 
            0x10  # Icono de error rojo
        )

if __name__ == "__main__":
    detener()
