---
title: "Reporte Final UT1: Resultados de Analítica Web"
---
    
# Informe de Analítica Web

- **Periodo Analizado:** 2025-01-03 a 2025-01-03
- **Fecha de Generación:** 2025-11-09 10:54:58 UTC
- **Fuente de Datos:** Ficheros NDJSON en `project/data/drops/`

---

## Definiciones de KPIs

- **Sesión:** Una secuencia de eventos de un mismo usuario donde el tiempo entre eventos consecutivos no supera los 30 minutos.
- **Tasa de Conversión:** Porcentaje de sesiones que avanzan de un paso del embudo al siguiente.

---

## Resumen de Actividad

### Sesiones Únicas por Día

| fecha      |   sesiones_unicas |
|------------|-------------------|
| 2025-01-03 |              6620 |

### Top 10 Páginas Más Visitadas

| path       |   visitas |
|------------|-----------|
| /          |      3865 |
| /productos |      2472 |
| /checkout  |      1010 |
| /contacto  |      1001 |
| /login     |       531 |
| /blog      |       505 |
| /ayuda     |       496 |

### Embudo de Conversión (Home → Productos → Checkout)

| Paso                  |   Sesiones |   Tasa_Conversion_Paso_Anterior |   Tasa_Conversion_Total |
|-----------------------|------------|---------------------------------|-------------------------|
| 1. Visita a Home (/)  |       3266 |                          100.00 |                  100.00 |
| 2. Visita a Productos |        637 |                           19.50 |                   19.50 |
| 3. Visita a Checkout  |         72 |                           11.30 |                    2.20 |

---

## Conclusiones y Acciones (Plantilla)

- **Insight:** *[Observación clave basada en los datos, ej. "La tasa de abandono entre Productos y Checkout es del X%"]*
- **Implicación:** *[Consecuencia de negocio del insight, ej. "Estamos perdiendo una cantidad significativa de ventas potenciales en el último paso"]*
- **Acción:** *[Siguiente paso propuesto, ej. "Analizar el flujo de checkout para identificar puntos de fricción"]*
