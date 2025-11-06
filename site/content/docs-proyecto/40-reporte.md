---
title: "40. Plantilla de Reporte"
---

# Plantilla de Reporte de Analítica Web

> **Titular:** [Insight principal del periodo] + [Implicación de negocio].
>
> *Ejemplo: **La conversión a checkout cae un 15%** esta semana; se sugiere revisar el rendimiento de la pasarela de pago.*

---

## 1. Métricas Clave de Actividad

-   **Sesiones Únicas Totales:** `___` (↑/↓ vs. periodo anterior)
-   **Pageviews Totales:** `___`
-   **Duración Media de Sesión (aprox.):** `___` minutos
-   **Usuarios Únicos:** `___`

*Definiciones:*
-   *Sesión:* Actividad de un usuario con pausas no mayores a 30 minutos.
-   *Usuario Único:* Conteo de `user_id` distintos en el periodo.

---

## 2. Contenido Más Visitado (Top 5 Paths)

| Ruta (Path) | Nº de Visitas | % del Total |
| :---------- | ------------: | ----------: |
| `/`         |           `—` |         `—` |
| `/productos`|           `—` |         `—` |
| `/checkout` |           `—` |         `—` |
| `...`       |           `—` |         `—` |
| `...`       |           `—` |         `—` |

---

## 3. Embudo de Conversión (Home → Productos → Checkout)

| Paso del Embudo         | Nº de Sesiones | Tasa de Conversión (vs. Paso Anterior) | Tasa de Conversión (Total) |
| :---------------------- | -------------: | -------------------------------------: | -------------------------: |
| 1. Visita a Home        |            `—` |                                `100.0%`|                    `100.0%`|
| 2. Visita a Productos   |            `—` |                                    `—%`|                       `—%`|
| 3. Visita a Checkout    |            `—` |                                    `—%`|                       `—%`|

---

## 4. Calidad y Procesamiento de Datos

-   **Ficheros Procesados:** `___`
-   **Eventos Recibidos (Crudo):** `___`
-   **Eventos Válidos (Limpios):** `___`
-   **Eventos a Cuarentena:** `___` (`___`% del total)
-   **Motivos Principales de Cuarentena:** `[Listar motivos, ej. "Formato de fecha inválido", "user_id nulo"]`

---

## 5. Próximos Pasos / Acciones Recomendadas

-   **Acción 1:** `[Ej: Investigar la alta tasa de abandono en el paso de Productos a Checkout]`
    -   **Responsable:** `[Equipo de Producto]`
-   **Acción 2:** `[Ej: Analizar las fuentes de tráfico (referrer) de las páginas con más visitas]`
    -   **Responsable:** `[Equipo de Marketing]`
-   **Acción 3:** `[Ej: Revisar logs de cuarentena para identificar problemas en el origen de los datos]`
    -   **Responsable:** `[Equipo de Datos]`