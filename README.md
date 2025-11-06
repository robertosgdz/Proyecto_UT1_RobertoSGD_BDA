# Pipeline de Analítica Web - Producto Final UT1

Este repositorio contiene la implementación de un pipeline de datos de principio a fin, desarrollado como producto final para la Unidad de Trabajo 1. El proyecto ingiere, limpia, modela y reporta datos de logs de analítica web.

## Caso de Uso Elegido: Web Analytics (Logs a Lake)

El pipeline procesa eventos de navegación de un sitio web (ficheros `events.ndjson`) para generar métricas clave de negocio, como el análisis de sesiones de usuario y el rendimiento de un embudo de conversión. El flujo de trabajo sigue la arquitectura de capas **Bronce → Plata → Oro**, persistiendo los resultados en formatos optimizados para el análisis como Parquet y SQLite.

---

## Cómo Ejecutar el Pipeline

Sigue estos pasos para configurar el entorno y ejecutar el proyecto.

### 1. Requisitos Previos

-   Python 3.11+
-   `pip` y `venv` para la gestión de entornos y paquetes.

### 2. Configuración del Entorno

Se recomienda encarecidamente usar un entorno virtual para aislar las dependencias del proyecto.

```bash
# 1. Clona o descarga este repositorio y navega a la carpeta raíz.

# 2. Crea un entorno virtual
# (En Windows, puede que necesites usar 'py -3.11' en lugar de 'python')
python -m venv venv

# 3. Activa el entorno virtual
# En Windows (PowerShell):
.\venv\Scripts\Activate.ps1

```
### 3. Instalación de Dependencias

Con el entorno virtual activado, instala todas las librerías necesarias ejecutando:

```bash

pip install -r requirements.txt

```

### 4. Generación de Datos de Prueba

El proyecto incluye un script para generar un conjunto de datos de ejemplo (events.ndjson) con registros válidos e inválidos.

```bash
python get_data.py
```

Esto creará el fichero de datos en `project/data/drops/2025-01-03/`.

### 5. Ejecución del Pipeline Completo

El script principal orquesta todas las fases: ingestión, limpieza, modelado y generación del reporte.

```bash
python project/ingest/run.py
```
Al finalizar, todos los artefactos generados (capas Plata/Oro, base de datos de control, cuarentena y el reporte) se encontrarán en la carpeta project/output/.

## Estructura del proyecto

- README.md: Este mismo fichero.
- requirements.txt: Dependencias de Python.
- get_data.py: Script para generar datos de prueba.
- /docs/: Documentación detallada sobre las decisiones de diseño del pipeline.
- /project/: Contenedor principal para el código y los datos.
    - data/drops/: "Dropzone" donde se colocan los ficheros de datos crudos.
    - ingest/run.py: Script principal que orquesta todo el pipeline.
    - output/: Directorio donde se almacenan todos los artefactos generados.
        - plata/: Datos limpios en formato Parquet, particionados por fecha.
        - oro/: Datasets agregados en formato Parquet.
        - quarantine/: Ficheros con los registros que fallaron la validación.
        - ut1.db: Base de datos SQLite para control de idempotencia y almacenamiento de capas.
        - reporte.md: El informe final en formato Markdown.

## Supuestos y Decisiones de Diseño Clave

- **Formato de Fecha**: Se espera que los timestamps (ts) en los datos de origen estén en formato ISO 8601 y con zona horaria UTC.
- **Idempotencia**: El pipeline es idempotente a nivel de fichero. Un batch_id (hash MD5) se genera para cada fichero; si se re-ejecuta, los ficheros ya procesados (registrados en ut1.db) son omitidos.
- **Política de Deduplicación**: Se aplica una política de "último gana" para registros con la misma clave natural (user_id, ts, path), conservando el que fue ingerido más recientemente (_ingest_ts).
- **Definición de Sesión**: Una sesión se define como una secuencia de eventos de un usuario donde el tiempo entre eventos consecutivos no supera los 30 minutos.

Para un desglose más detallado de cada decisión, consulta la documentación en la carpeta /docs/.