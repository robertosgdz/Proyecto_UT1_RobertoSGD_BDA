---
title: "20. Reglas de Limpieza y Calidad"
---

# Reglas de Limpieza y Calidad de Datos

Este documento describe las reglas aplicadas en la **Fase 2** del pipeline para transformar los datos crudos ingeridos en la **Capa Plata**. El objetivo es garantizar la consistencia, integridad y fiabilidad de los datos antes del modelado de negocio.

## Tipos y Formatos
-   **`ts` (Timestamp):**
    -   **Validación en Ingesta:** Debe ser una cadena de texto compatible con el formato **ISO 8601** y debe incluir información de zona horaria (preferiblemente UTC, marcada con 'Z' o '+00:00').
    -   **Transformación en Capa Plata:** Se convierte a un tipo de dato `datetime64[ns, UTC]` nativo de Pandas/Arrow para permitir operaciones temporales.
-   **`user_id` y `path`:** Se validan como cadenas de texto (`string`).
-   **`referrer` y `device`:** Se tratan como cadenas de texto (`string`).

## Nulos
-   **Campos Obligatorios:** Las columnas `ts`, `user_id` y `path` se consideran obligatorias.
-   **Tratamiento:** Si un registro crudo tiene un valor nulo o una cadena vacía en cualquiera de estos tres campos, es rechazado durante la fase de ingestión y enviado a la **cuarentena** con la causa "user_id o path están vacíos o son nulos".

## Rangos y Dominios
-   **`path` (Dominio):** Para asegurar la consistencia en las agregaciones, la columna `path` se normaliza de la siguiente manera:
    1.  Se convierte todo el texto a **minúsculas**.
    2.  Se eliminan todos los parámetros de consulta de la URL (es decir, se trunca la cadena a partir del primer carácter `?`). Esto agrupa rutas como `/productos?id=123` y `/productos` en una sola categoría: `/productos`.

## Deduplicación
-   **Clave Natural:** La clave que identifica un evento de forma única se define como la tupla `(user_id, ts, path)`. Se asume que un mismo usuario no puede generar un evento idéntico en la misma ruta y en el mismo instante exacto.
-   **Política:** Se aplica una política de **“último gana”**. El proceso ordena todos los eventos por la columna de trazabilidad `_ingest_ts` (el momento en que el lote fue procesado) y, en caso de encontrar duplicados según la clave natural, conserva únicamente el registro que fue ingerido más recientemente.

## Estandarización de Texto
-   **`path`:** Como se mencionó en "Dominios", se estandariza a minúsculas.
-   **Otros campos:** No se aplican otras transformaciones de texto (como `trim` o normalización de tildes) en este pipeline, ya que los `user_id`, `referrer` y `device` se tratan como identificadores o categorías literales.

## Trazabilidad
-   Las columnas de metadatos generadas en la fase de ingestión se mantienen intactas en la Capa Plata:
    -   `_ingest_ts`
    -   `_source_file`
    -   `_batch_id`
-   Esto permite auditar cualquier registro en la capa limpia hasta su origen.

## QA Rápida (Monitoreo)
-   **% de Filas a Cuarentena:** El log del pipeline informa del número de registros enviados a cuarentena por cada fichero. Un aumento anómalo en este número sería una señal de alerta sobre la calidad de los datos de origen.
-   **Conteos por Día:** Durante la creación de la Capa Oro, se calcula el número de sesiones por día. Una desviación drástica de la media esperada (ej. un día con cero sesiones o con 10 veces más de lo normal) podría indicar un problema en el procesamiento o en los datos de entrada.