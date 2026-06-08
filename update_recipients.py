import json
import os

raw_list = '"Elizabeth Ortiz" <elizabeth.ortiz@cinlatlogistics.com>; "Ricardo Romero" <ricardo.romero@cinlatlogistics.com>; "Jorge Vazquez" <jorge.vazquez@cinlatlogistics.com>; "Eloisa Perez" <eloisa.perez@cinlatlogistics.com>; "Jessica Aguilar" <Jessica.aguilar@cinlatlogistics.com>; "Paz Paez" <paz.paez@cinlatlogistics.com>; "Briseida Marin" <briseida.marin@cinlatlogistics.com>; "Lourdes Nieto" <lourdes.nieto@cinlatlogistics.com>; "Joaquin Flores" <joaquin.flores@cinlatlogistics.com>; "Irais Moreno" <irais.moreno@cinlatlogistics.com>; "Cristina Hernandez" <cristina.hernandez@cinlatlogistics.com>; "Alfredo Cruz" <alfredo.cruz@cinlatlogistics.com>; "Victor Casas" <victor.casas@cinlatlogistics.com>; "Ernesto Salazar" <ernesto.salazar@cinlatlogistics.com>; "Alonso López" <alonso.lopez@cinlatlogistics.com>; "Carmen Martinez" <carmen.martinez@cinlatlogistics.com>; "Alfredo Cruz" <alfredo.cruz@cinlatlogistics.com>; "Edgar Reyes" <edgar.reyes@cinlatlogistics.com>; "Ernesto Salazar" <ernesto.salazar@cinlatlogistics.com>; "Manuel Garcia" <manuel.garcia@cinlatlogistics.com>; "Elizabeth Clemente" <elizabeth.clemente@cinlatlogistics.com>; "Erick Pozas" <erick.pozas@cinlatlogistics.com>; "Jaime Caballero" <jaime.caballero@cinlatlogistics.com>; "Sabino Navarro" <sabino.navarro@cinlatlogistics.com>; "Daniel Ochoa" <daniel.ochoa@cinlatlogistics.com>; "Santander Mendoza" <santander.mendoza@cinlatlogistics.com>; "Miguel Ochoa" <Miguel.ochoa@cinlatlogistics.com>'

# Split by semicolon and strip whitespace
recipients = [r.strip() for r in raw_list.split(';')]
# Remove duplicates while preserving order
seen = set()
unique_recipients = []
for r in recipients:
    if r.lower() not in seen:
        unique_recipients.append(r)
        seen.add(r.lower())

config = {
    "it": unique_recipients,
    "negocio": unique_recipients
}

config_path = r"C:\Users\DIRECCION-TI\OneDrive - CINLAT LOGISTICS S.A. de C.V\Miguel Ochoa\2025-A\MVP\HelpDesk\recipients_config.json"

with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=4, ensure_ascii=False)

print(f"Updated {config_path} with {len(unique_recipients)} unique recipients.")
