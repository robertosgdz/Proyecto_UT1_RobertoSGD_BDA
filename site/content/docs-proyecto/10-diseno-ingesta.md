---
title: "10. Diseño de Ingestión"
---

# Diseño de Ingestión: Pipeline de Analítica Web

## Resumen
Este documento describe el proceso de ingestión para los datos de logs de analítica web. El sistema está diseñado para procesar ficheros en lotes (`batch`), garantizando la idempotencia, la trazabilidad y el manejo de datos erróneos a través de una cuarentena.

## Fuente
- **Origen:** Ficheros de log depositados en un directorio `dropzone`. La ruta de ejemplo es `project/data/drops/YYYY-MM-DD/events.ndjson`.
- **Formato:** **NDJSON** (Newline Delimited JSON). Cada línea del fichero es un registro de evento en formato JSON.
- **Frecuencia:** Se simula una entrega diaria de ficheros, aunque el pipeline está diseñado para ser ejecutado en modo **batch** a una frecuencia configurable (ej. cada hora o una vez al día).

## Estrategia
- **Modo:** Se ha implementado un proceso **batch**.
- **Justificación:** Para el análisis de comportamiento web (sesiones, embudos), una latencia de horas es generalmente aceptable. El modo batch simplifica la arquitectura, mejora la robustez y es más eficiente para procesar grandes volúmenes de datos de una sola vez en comparación con un enfoque de streaming puro.
- **Incremental:** El proceso es incremental a nivel de fichero. El pipeline descubre y procesa únicamente los ficheros nuevos que no han sido ingeridos previamente, basándose en su `batch_id`.
- **Particionado:** Aunque el particionado se aplica en la capa Plata, la estructura de la fuente (`/YYYY-MM-DD/`) ya sugiere una organización temporal que el pipeline podría aprovechar.

## Idempotencia y Deduplicación
- **`batch_id`:** Se genera un hash **MD5** único para cada fichero de entrada, calculado a partir de la concatenación de su ruta absoluta, su tamaño y su fecha de última modificación. Esto asegura que si el pipeline se re-ejecuta, no volverá a procesar un fichero que no ha cambiado.
- **Clave Natural (para deduplicación en la siguiente fase):** La clave natural de un evento se define como la tupla `(user_id, ts, path)`.
- **Política de Deduplicación:** Se aplica una política de **“último gana por `_ingest_ts`”**. Esto se implementará en la fase de limpieza (Capa Plata), pero la decisión se documenta aquí ya que afecta al diseño global.

## Checkpoints y Trazabilidad
- **Checkpoints:** El mecanismo de checkpoint para el proceso batch es la tabla `ingest_history` en la base de datos `ut1.db`. Almacena los `batch_id` de los ficheros ya procesados, actuando como la "memoria" del pipeline.
- **Trazabilidad:** A cada registro válido se le añaden las siguientes columnas de metadatos durante la ingestión:
    - `_ingest_ts`: Timestamp ISO 8601 (UTC) del momento en que se ejecuta el lote.
    - `_source_file`: Ruta completa del fichero de origen.
    - `_batch_id`: El `batch_id` del fichero del que proviene el registro.
- **DLQ/Quarantine:** Los registros que fallan la validación inicial (ej. formato de fecha incorrecto, campos obligatorios nulos) se desvían a un fichero `.jsonl` en el directorio `project/output/quarantine/`. Cada registro en cuarentena incluye el dato original, el motivo del error y el fichero/línea de origen.

## SLA (Acuerdo de Nivel de Servicio)
- **Disponibilidad:** Dado que es un proceso batch, se podría programar para ejecutarse cada hora. Los datos estarían disponibles para análisis con una latencia máxima de aproximadamente 1 hora.
- **Alertas:** No se implementan alertas automáticas en esta fase. El monitoreo se realizaría revisando los ficheros en la carpeta de cuarentena.

## Riesgos / Antipatrones
- **Necesidad de baja latencia:** Este diseño **no es adecuado** si se requieren métricas en tiempo real (latencia de segundos). En ese caso, se debería migrar a un enfoque de micro-batch o streaming.
- **Falta de clave natural:** El diseño depende de la existencia de una clave natural fiable para la deduplicación posterior. Si los eventos no tuvieran una combinación de campos que los identifique de forma única, sería necesario generar un `event_id` en el origen.