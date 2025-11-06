---
title: "30. Definición de Métricas y Tablas Oro - Analítica Web"
---

# Modelo de Negocio (Capa Oro)

Este documento define las tablas agregadas y los Indicadores Clave de Rendimiento (KPIs) que componen la **Capa Oro** del pipeline de analítica web. Estas métricas están diseñadas para responder preguntas de negocio sobre el comportamiento del usuario.

## Tablas Oro
-   **Fuente:** El dataset `plata/` (Parquet) con granularidad de **evento web individual**.
-   **Tablas Generadas (en `oro/`):**
    -   `sessions_per_day.parquet`: Agregación de sesiones a nivel de **día**.
    -   `top_paths.parquet`: Ranking de las páginas más visitadas.
    -   `funnel.parquet`: Tabla agregada que describe el embudo de conversión.

## Métricas (KPI) y Lógica de Construcción

### 1. Sesión
-   **Definición:** Una sesión es una secuencia de eventos (`pageviews`) generados por un mismo `user_id`, donde el tiempo transcurrido entre dos eventos consecutivos no supera los **30 minutos (1800 segundos)**.
-   **Lógica de Cálculo:**
    1.  Se agrupan los eventos por `user_id` y se ordenan cronológicamente por `ts`.
    2.  Se calcula la diferencia de tiempo entre cada evento y el anterior para ese usuario.
    3.  Si la diferencia es mayor a 30 minutos, se considera el inicio de una nueva sesión.
    4.  Se asigna un `session_id` único (compuesto por `user_id` + un contador secuencial) a cada grupo de eventos que forman una sesión.

### 2. Embudo de Conversión
-   **Definición:** Mide el porcentaje de sesiones que completan una secuencia predefinida de pasos.
-   **Secuencia del Embudo:** `Visita a Home (/)` → `Visita a Productos (/productos)` → `Visita a Checkout (/checkout)`.
-   **Lógica de Cálculo:**
    1.  Se identifica el conjunto de `session_id` únicos que visitaron `/`.
    2.  De este conjunto, se filtra para encontrar cuántos *también* visitaron `/productos`.
    3.  De este segundo conjunto, se filtra para encontrar cuántos *también* visitaron `/checkout`.
-   **KPIs Derivados:**
    -   **Tasa de Conversión (Paso a Paso):** `% de sesiones que pasan del paso N-1 al paso N`.
    -   **Tasa de Conversión (Total):** `% de sesiones que completan el paso N respecto al total que inició en el paso 1`.

### 3. Top 10 Páginas Visitadas
-   **Definición:** Ranking de las 10 rutas (`path_clean`) con mayor número de pageviews en el periodo analizado.
-   **Lógica de Cálculo:** Se realiza un conteo de ocurrencias (`value_counts()`) sobre la columna `path_clean` de la capa Plata.

## Supuestos
-   **Identificación de Usuario:** Se asume que el `user_id` proporcionado en los logs identifica de forma consistente a un mismo usuario a lo largo del tiempo.
-   **Exclusión de Bots:** En esta versión del pipeline, no se ha implementado un filtro explícito para excluir el tráfico de bots o arañas web.
-   **Definición de Sesión:** El timeout de 30 minutos es un estándar de la industria, pero es un parámetro configurable. No se tienen en cuenta otros factores para finalizar una sesión (como el cambio de fuente de tráfico a mitad de sesión).
-   **Orden del Embudo:** Se asume que los pasos del embudo deben ocurrir en la secuencia definida, aunque no necesariamente de forma consecutiva (un usuario puede visitar otras páginas entre un paso y otro).

## Lógica Conceptual (Pandas)

```python
# Lógica conceptual para sesiones por día
sessions_per_day = df.groupby('fecha')['session_id'].nunique()

# Lógica conceptual para Top Paths
top_paths = df['path_clean'].value_counts().nlargest(10)

# Lógica conceptual para el embudo
sessions_home = df[df['path_clean'] == '/']['session_id'].unique()
sessions_products = df[df['session_id'].isin(sessions_home) & (df['path_clean'] == '/productos')]['session_id'].unique()
# ... y así sucesivamente.```