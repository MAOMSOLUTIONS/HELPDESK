# Análisis de Patrones de Help Desk (Últimos 4 Meses)

**Total de Tickets Analizados:** 517
**Total de Horas Hombre Invertidas:** 87,329.3 horas

Este análisis detecta palabras clave en la descripción de los requerimientos para agruparlos en categorías y así identificar qué problemas consumen más tiempo del equipo de IT, revelando oportunidades claras de automatización o capacitación.

## 1. Distribución y Patrones Principales

| Problema (Categoría) | Frecuencia Total | Horas Invertidas | Impacto en KPI IT (%) | ENE | FEB | MAR | ABR |
|---|---|---|---|---|---|---|---|
| **OTROS REQUERIMIENTOS MENORES** | 239 | 31,132.2 hrs | 35.6% | 49 | 53 | 56 | 81 |
| **RED Y COMUNICACIONES** | 76 | 17,681.9 hrs | 20.2% | 22 | 9 | 13 | 32 |
| **CORREO Y OFFICE** | 56 | 9,097.4 hrs | 10.4% | 10 | 13 | 14 | 19 |
| **ERP / SISTEMAS CORE** | 47 | 7,096.5 hrs | 8.1% | 7 | 16 | 13 | 11 |
| **ACCESOS Y CONTRASEÑAS** | 40 | 8,216.9 hrs | 9.4% | 13 | 11 | 7 | 9 |
| **IMPRESORAS Y ESCÁNERES** | 36 | 9,360.0 hrs | 10.7% | 11 | 8 | 9 | 8 |
| **EQUIPO DE CÓMPUTO** | 18 | 3,784.5 hrs | 4.3% | 4 | 2 | 6 | 6 |
| **TELEFONÍA** | 4 | 720.0 hrs | 0.8% | 1 | 2 | 1 | 0 |
| **RESPALDOS / SERVIDORES** | 1 | 240.0 hrs | 0.3% | 0 | 0 | 1 | 0 |

## 2. Detalle de Tiempo Invertido por Técnico en el Patrón Principal

Para la categoría número uno (**OTROS REQUERIMIENTOS MENORES**), así se divide el esfuerzo del equipo:

| Recurso (Responsable) | Tickets Atendidos | Horas Invertidas |
|---|---|---|
| SALAZAR MARTINEZ ERNESTO | 100.0 | 16800.0 hrs |
| GARCIA ROMERO MANUEL | 29.0 | 5200.5 hrs |
| CASAS VALDEZ VICTOR MANUEL | 11.0 | 3760.5 hrs |
| ERICK POZAS | 38.0 | 2032.5 hrs |
| CLEMENTE CLEMENTE ELIZABETH | 32.0 | 1272.0 hrs |
| SABINO NAVARRO | 11.0 | 960.0 hrs |
| JAIME CABALLERO | 8.0 | 576.0 hrs |
| DANIEL OCHOA | 4.0 | 288.0 hrs |
| SIN ASIGNAR | 6.0 | 242.8 hrs |

## 3. Oportunidades de Automatización (Recomendación)

- **RED Y COMUNICACIONES**: Sugerencia: Desplegar un script diagnóstico automático (`RedCheck.bat`) en los equipos de los usuarios para que ejecute una limpieza de DNS o reinicio de adaptador antes de levantar el ticket.
