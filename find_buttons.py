import re
import os

file_path = 'page_source.html'
if os.path.exists(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
        links = re.findall(r'id="([^"]*LinkButton[^"]*)"', text)
        print("LinkButtons found:")
        for l in links:
            print(l)
        
        # Also look for any button that might be export
        exports = re.findall(r'id="([^"]*Export[^"]*)"', text)
        print("\nExport buttons found:")
        for e in exports:
            print(e)
            
        # Look for any doPostBack calls
        postbacks = re.findall(r'__doPostBack\(\'([^\']*)\'', text)
        print("\nPostBack targets found:")
        for p in set(postbacks):
            print(p)
