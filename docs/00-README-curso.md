# Documentación de Diseño · UT1 — Pipeline de Analítica Web

Este directorio contiene la documentación técnica y de diseño que acompaña al pipeline de ingesta, procesamiento y reporte de datos de analítica web.

Cada documento detalla las decisiones tomadas en las diferentes fases del proyecto, cumpliendo con los requisitos de la entrega.

## Índice de Documentos

1.  **[10-diseno-ingesta.md](./10-diseno-ingesta.md)**
    *   Detalla las decisiones sobre el **proceso de ingestión**, incluyendo la elección del enfoque *batch*, la estrategia de idempotencia mediante `batch_id`, y el uso de metadatos para la trazabilidad.

2.  **[20-limpieza-calidad.md](./20-limpieza-calidad.md)**
    *   Describe las **reglas de calidad de datos** aplicadas durante el paso de la capa Bronce a la Plata. Incluye el tratamiento de tipos, nulos, la normalización de dominios y la política de deduplicación.

3.  **[30-modelado-oro.md](./30-modelado-oro.md)**
    *   Define las **métricas y KPIs de negocio** que se generan en la capa Oro. Explica las fórmulas y supuestos detrás de la construcción de sesiones y el embudo de conversión.

4.  **[99-lecciones-aprendidas.md](./99-lecciones-aprendidas.md)**
    *   Contiene una **retrospectiva** del proyecto: qué funcionó bien, qué desafíos se encontraron y qué mejoras podrían implementarse en el futuro.

---
> Para instrucciones sobre cómo ejecutar el pipeline, consulta el **[README.md](../../README.md)** principal en la raíz del repositorio.