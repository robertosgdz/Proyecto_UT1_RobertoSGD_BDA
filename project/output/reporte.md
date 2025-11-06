
# Informe de Analítica Web

- **Periodo Analizado:** 2025-01-03 a 2025-01-03
- **Fecha de Generación:** 2025-11-06 11:06:55 UTC
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
| 2025-01-03 |                 5 |

### Top 10 Páginas Más Visitadas

| path       |   visitas |
|------------|-----------|
| /productos |         6 |
| /checkout  |         4 |
| /          |         3 |
| /contacto  |         2 |

### Embudo de Conversión (Home → Productos → Checkout)

| Paso                  |   Sesiones |   Tasa_Conversion_Paso_Anterior |   Tasa_Conversion_Total |
|-----------------------|------------|---------------------------------|-------------------------|
| 1. Visita a Home (/)  |          2 |                          100.00 |                  100.00 |
| 2. Visita a Productos |          1 |                           50.00 |                   50.00 |
| 3. Visita a Checkout  |          1 |                          100.00 |                   50.00 |

---

## Conclusiones y Acciones (Plantilla)

- **Insight:** *[Observación clave basada en los datos, ej. "La tasa de abandono entre Productos y Checkout es del X%"]*
- **Implicación:** *[Consecuencia de negocio del insight, ej. "Estamos perdiendo una cantidad significativa de ventas potenciales en el último paso"]*
- **Acción:** *[Siguiente paso propuesto, ej. "Analizar el flujo de checkout para identificar puntos de fricción"]*
