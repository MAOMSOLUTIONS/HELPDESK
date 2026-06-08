import requests
import os

# Configuration
URL = "http://192.168.14.6:82/HelpdeskAdmon.aspx"
SESSION_ID = "tnaj0ovvislj31w52cq52jml" # From subagent
VIEWSTATE_DIR = r"C:\Users\DIRECCION-TI\.gemini\antigravity\brain\7663a553-3364-4b83-8028-aeb15be0f533\browser"
OUTPUT_PATH = r"C:\Users\DIRECCION-TI\Downloads\ReporteHelpdesk_20260408_Manual.xlsx"

# Load form data from files (to be filled by subagent)
def load_file(name):
    with open(os.path.join(VIEWSTATE_DIR, name), 'r', encoding='utf-8') as f:
        return f.read().strip()

try:
    viewstate = load_file("viewstate.txt")
    generator = load_file("generator.txt")
    validation = load_file("validation.txt")

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"ASP.NET_SessionId={SESSION_ID}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    data = {
        "__EVENTTARGET": "ctl00$Contentplaceholder1$LinkButton1",
        "__EVENTARGUMENT": "",
        "__VIEWSTATE": viewstate,
        "__VIEWSTATEGENERATOR": generator,
        "__EVENTVALIDATION": validation,
        "ctl00$Contentplaceholder1$RadDatePickerDel$dateInput": "2026-01-01-00-00-00",
        "ctl00$Contentplaceholder1$RadDatePickerAl$dateInput": "2026-04-08-00-00-00",
        "ctl00_Contentplaceholder1_RadDatePickerDel_dateInput_ClientState": '{"enabled":true,"emptyMessage":"","validationText":"2026-01-01-00-00-00","valueAsString":"2026-01-01-00-00-00","lastSetTextBoxValue":"01/01/2026"}',
        "ctl00_Contentplaceholder1_RadDatePickerAl_dateInput_ClientState": '{"enabled":true,"emptyMessage":"","validationText":"2026-04-08-00-00-00","valueAsString":"2026-04-08-00-00-00","lastSetTextBoxValue":"08/04/2026"}'
    }

    print("Sending POST request to download report...")
    response = requests.post(URL, headers=headers, data=data)

    if response.status_code == 200:
        with open(OUTPUT_PATH, 'wb') as f:
            f.write(response.content)
        print(f"Report downloaded successfully to: {OUTPUT_PATH}")
        print(f"File size: {len(response.content)} bytes")
    else:
        print(f"Failed to download report. Status code: {response.status_code}")
        print(response.text[:500])

except Exception as e:
    print(f"Error: {e}")
