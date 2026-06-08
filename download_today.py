import requests
import os
from datetime import datetime

# Configuration
URL = "http://192.168.14.6:82/HelpdeskAdmon.aspx"
TODAY = datetime.now()
DATE_STR = TODAY.strftime("%d/%m/%Y")
FILE_DATE = TODAY.strftime("%d_%m_%Y")
OUTPUT_PATH = f"ReporteHelpdesk{FILE_DATE}.xlsx"

def download_report():
    print(f"Target URL: {URL}")
    print(f"Target Date: {DATE_STR}")
    
    try:
        # 1. Try to get initial cookies and ViewState
        print("Obtaining session and ViewState...")
        session = requests.Session()
        initial_res = session.get(URL, timeout=20)
        
        if initial_res.status_code != 200:
            print(f"Failed to reach server. Status code: {initial_res.status_code}")
            return False
            
        # Basic parsing (could use BeautifulSoup if available, but let's try simple string search)
        text = initial_res.text
        def get_val(name):
            try:
                start = text.find(f'id="{name}" value="') + len(f'id="{name}" value="')
                end = text.find('"', start)
                return text[start:end]
            except:
                return ""

        viewstate = get_val("__VIEWSTATE")
        generator = get_val("__VIEWSTATEGENERATOR")
        validation = get_val("__EVENTVALIDATION")

        print("ViewState obtained. Sending download request...")

        # 2. Send POST request to trigger excel export
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        data = {
            "__EVENTTARGET": "ctl00$Contentplaceholder1$LinkButton1",
            "__EVENTARGUMENT": "",
            "__VIEWSTATE": viewstate,
            "__VIEWSTATEGENERATOR": generator,
            "__EVENTVALIDATION": validation,
            "ctl00$Contentplaceholder1$RadDatePickerDel$dateInput": "2026-01-01-00-00-00",
            "ctl00$Contentplaceholder1$RadDatePickerAl$dateInput": f"{TODAY.strftime('%Y-%m-%d')}-00-00-00",
            "ctl00_Contentplaceholder1_RadDatePickerDel_dateInput_ClientState": '{"enabled":true,"emptyMessage":"","validationText":"2026-01-01-00-00-00","valueAsString":"2026-01-01-00-00-00","lastSetTextBoxValue":"01/01/2026"}',
            "ctl00_Contentplaceholder1_RadDatePickerAl_dateInput_ClientState": f'{{"enabled":true,"emptyMessage":"","validationText":"{TODAY.strftime("%Y-%m-%d")}-00-00-00","valueAsString":"{TODAY.strftime("%Y-%m-%d")}-00-00-00","lastSetTextBoxValue":"{DATE_STR}"}}'
        }

        response = session.post(URL, headers=headers, data=data, timeout=60)

        if response.status_code == 200:
            with open(OUTPUT_PATH, 'wb') as f:
                f.write(response.content)
            print(f"Report downloaded successfully to: {OUTPUT_PATH}")
            print(f"File size: {len(response.content)} bytes")
            return True
        else:
            print(f"Failed to download report. Status code: {response.status_code}")
            return False

    except Exception as e:
        print(f"Error during download: {e}")
        return False

import sys

if __name__ == "__main__":
    if not download_report():
        sys.exit(1)
    sys.exit(0)
