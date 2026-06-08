import subprocess
import time
import os
from datetime import datetime

# Configuration
PROJECT_DIR = r"c:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP\HelpDesk"
ANALYSIS_SCRIPT = "advanced_performance_analysis.py"
LOG_FILE = "automation_log.txt"

def run_hourly_report():
    while True:
        now = datetime.now()
        print(f"[{now}] Initializing hourly Helpdesk analysis...")
        
        try:
            # 1. Execute Analysis
            # Note: The output is generated inside advanced_performance_analysis.py
            result = subprocess.run(["python", ANALYSIS_SCRIPT], cwd=PROJECT_DIR, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"[{now}] Analysis completed successfully.")
                
                # 2. Email Integration Placeholder
                # This is where we would call a function to send the email with the .md content
                # send_email("Helpdesk Dashboard", "Actionable_Resolution_Report.md")
                
            else:
                print(f"[{now}] Error in analysis:")
                print(result.stderr)
                
        except Exception as e:
            print(f"[{now}] Execution failed: {e}")
            
        # Log entry
        with open(os.path.join(PROJECT_DIR, LOG_FILE), "a") as log:
            log.write(f"{now} - Status: {'Success' if result.returncode == 0 else 'Error'}\n")
            
        print("Waiting 1 hour for next execution...")
        time.sleep(3600)

if __name__ == "__main__":
    # In a production environment, this would be registered as a Windows Service 
    # or triggered by Task Scheduler every hour.
    run_hourly_report()
