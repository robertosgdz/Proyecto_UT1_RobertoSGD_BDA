---
title: "99. Lecciones Aprendidas"
---

# Lecciones Aprendidas y Retrospectiva del Proyecto

Este documento recoge las principales conclusiones, desafíos y aprendizajes obtenidos durante el desarrollo del pipeline de analítica web.

## Qué Salió Bien

1.  **Arquitectura de Capas Clara (Bronce → Plata → Oro):** La separación de responsabilidades funcionó muy bien. Permitió aislar la lógica de ingestión de la de limpieza y de la de negocio, haciendo el código más modular y fácil de depurar.

2.  **Idempotencia Robusta:** El mecanismo de `batch_id` con una base de datos SQLite para el historial de ingesta demostró ser muy eficaz. Evitó el reprocesamiento de datos y funcionó exactamente como se esperaba cuando se relanzó el pipeline.

3.  **Eficiencia de Parquet Particionado:** La decisión de usar Parquet para las capas Plata y Oro fue acertada. Aunque el dataset de prueba es pequeño, la implementación del particionado por fecha sienta las bases para un sistema que escalaría bien con volúmenes de datos mucho mayores.

4.  **Automatización del Reporte:** La generación automática del `reporte.md` a partir de los datos de la capa Oro es uno de los puntos fuertes del proyecto. Asegura que el informe final sea siempre consistente, reproducible y esté libre de errores manuales.

## Qué Mejorar / Desafíos Encontrados

1.  **Problemas de Entorno Inicial:** El principal obstáculo inicial fue la configuración del entorno de desarrollo en Windows, específicamente con la versión de Python. La falta de "wheels" pre-compilados para Python 3.13 provocó errores de compilación.
    -   **Lección:** Para proyectos con dependencias científicas (como `pandas`), es más seguro y rápido comenzar con una versión de Python LTS (Long-Term Support) o ligeramente más antigua (ej. 3.11), que garantiza una mayor compatibilidad de paquetes.

2.  **Diagnóstico de Problemas de Escritura de Ficheros:** Se encontró un problema donde los ficheros generados aparecían vacíos en los editores gráficos (VS Code, Bloc de Notas) a pesar de tener contenido en el disco.
    -   **Lección:** La línea de comandos (`Get-Content` en PowerShell) es una herramienta de diagnóstico más fiable que las interfaces gráficas para verificar el estado real de un fichero, ya que no se ve afectada por cachés de UI o interferencias de software de sincronización (como OneDrive).

3.  **Lógica de Sesiones en Pandas:** La implementación de la construcción de sesiones es funcional, pero para datasets extremadamente grandes (cientos de millones de eventos), el uso de `groupby().diff()` en Pandas podría consumir mucha memoria.
    -   **Mejora Futura:** Para escalar, esta lógica debería migrarse a un motor de procesamiento distribuido como Spark o Dask, que pueden manejar agrupaciones y funciones de ventana sobre grandes volúmenes de datos de manera más eficiente.

## Siguientes Pasos (Mejoras Futuras)

1.  **Implementar un Programador (Scheduler):** Para convertir este script en un pipeline verdaderamente automático, el siguiente paso sería integrarlo con un orquestador como **Airflow**, **Prefect**, o incluso una simple tarea programada (cron job o Tareas Programadas de Windows) para que se ejecute cada hora.

2.  **Monitoreo y Alertas:** Añadir un sistema de alertas. Por ejemplo, enviar una notificación (por email o Slack) si el número de registros en la cuarentena supera un cierto umbral, indicando un problema en la calidad de los datos de origen.

3.  **Enriquecimiento de Datos:** El pipeline podría enriquecerse añadiendo información externa. Por ejemplo, cruzar la IP del usuario (si estuviera disponible) con una base de datos de geolocalización para obtener el país o la ciudad de la sesión.

4.  **Publicación en Quartz/Pages:** Completar el paso opcional de configurar un sitio estático con Quartz o MkDocs para publicar la documentación y el reporte de forma accesible para todo el equipo.

## Apéndice (Evidencias)

-   **Ejemplo de registro en cuarentena:**
    ```json
    {"source_file": "...", "line": 2, "data": "{\"ts\": \"2025-01-03T11:20:00\", ...}", "error": "Timestamp no contiene información de zona horaria"}
    ```
-   **Ejemplo de log de ejecución exitosa:**
    ```
    --- Iniciando Fase 1: Ingestión de Datos ---
    PROCESANDO: events.ndjson con batch_id 4aefefdf...
    --- Fase 1 Completada ---
    ...
    --- Fase 3 Completada ---
    ```