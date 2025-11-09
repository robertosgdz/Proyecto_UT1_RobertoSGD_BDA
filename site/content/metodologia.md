---
title: "Metodología del Pipeline (Bronce → Plata → Oro)"
---

# Metodología del Pipeline de Datos

Este documento resume la arquitectura y los principios de procesamiento de datos utilizados en este proyecto. El flujo de trabajo sigue el modelo de medalla **Bronce → Plata → Oro** para transformar progresivamente los datos crudos en insights de negocio.

## Capa Bronce (Raw Data)

-   **Propósito:** Almacenar los datos de origen **tal cual llegan**, sin modificaciones. Esta capa es la "fuente de la verdad" y permite reprocesar los datos en el futuro.
-   **Enriquecimiento:** En el momento de la ingestión, los datos crudos se enriquecen con metadatos de **trazabilidad**:
    -   `_source_file`: El fichero de origen del registro.
    -   `_ingest_ts`: El timestamp del momento de la ingestión.
    -   `_batch_id`: Un identificador único para el lote procesado.

## Capa Plata (Clean Data)

-   **Propósito:** Contener datos limpios, estandarizados y consistentes, listos para el análisis.
-   **Transformaciones aplicadas:**
    -   **Coerción de tipos:** Se asegura que cada columna tenga el tipo de dato correcto (ej. `ts` a `datetime`).
    -   **Validación de rangos/dominios:** Se aplican reglas de negocio (ej. `user_id` no puede ser nulo) y se normalizan los valores (ej. `path` a minúsculas).
    -   **Deduplicación:** Se eliminan registros duplicados aplicando una política de **“último gana”** basada en el `_ingest_ts`.

## Capa Oro (Analytics Data)

-   **Propósito:** Almacenar datasets agregados y enriquecidos, listos para ser consumidos directamente por reportes o herramientas de BI.
-   **Transformaciones aplicadas:**
    -   **Campos Derivados:** Se crean nuevos campos con lógica de negocio (ej. `session_id`).
    -   **Agregaciones:** Los datos se agrupan para calcular métricas clave (ej. sesiones por día, conteo de visitas por página, embudo de conversión).

## Principios Clave

-   **Idempotencia:** El pipeline está diseñado para que, si se vuelve a ejecutar sobre los mismos datos, el resultado final no cambie. Esto se logra mediante el uso de `batch_id` para la ingestión y políticas de `UPSERT` o deduplicación.
-   **Reporte Final:** El objetivo del pipeline es alimentar un **reporte en formato Markdown** que presenta los KPIs y las tablas agregadas de la capa Oro, sin incluir visualizaciones gráficas en esta fase del proyecto.```