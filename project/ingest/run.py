import pandas as pd
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime, timezone
import json
import pyarrow as pa
import pyarrow.dataset as ds
from tabulate import tabulate
import re

# ==============================================================================
# FASE 0: CONFIGURACIÓN INICIAL
# ==============================================================================

def find_project_root(marker=".gitignore"):
    """Sube niveles hasta encontrar el fichero marcador de la raíz del proyecto."""
    current_path = Path(__file__).resolve()
    while current_path != current_path.parent:
        if (current_path / marker).exists():
            return current_path
        current_path = current_path.parent
    raise FileNotFoundError(f"No se pudo encontrar la raíz del proyecto (marcador: {marker})")

# --- LÓGICA DE RUTAS ROBUSTA ---
PROJECT_ROOT = find_project_root()
DATA_DIR = PROJECT_ROOT / "project" / "data"
OUTPUT_DIR = PROJECT_ROOT / "project" / "output"
DB_PATH = OUTPUT_DIR / "ut1.db"

# Creación de directorios de salida si no existen.
OUTPUT_DIR.mkdir(exist_ok=True)
(OUTPUT_DIR / "plata").mkdir(exist_ok=True)
(OUTPUT_DIR / "oro").mkdir(exist_ok=True)
(OUTPUT_DIR / "quarantine").mkdir(exist_ok=True)

def setup_database():
    """
    Inicializa la base de datos SQLite.
    Para este proyecto, borra la tabla de historial en cada ejecución.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS ingest_history;")
    cursor.execute("""
    CREATE TABLE ingest_history (
        batch_id TEXT PRIMARY KEY,
        source_file TEXT NOT NULL,
        processed_ts TEXT NOT NULL
    );
    """)
    conn.commit()
    print("Tabla 'ingest_history' reseteada.")
    return conn

# ==============================================================================
# FASE 1: INGESTIÓN Y ALMACENAMIENTO (EJERCICIO 1)
# ==============================================================================

def get_batch_id(file_path: Path) -> str:
    """Crea un identificador único para un fichero basado en su ruta, tamaño y fecha de modificación."""
    stats = file_path.stat()
    file_info = f"{file_path.resolve()}|{stats.st_size}|{stats.st_mtime_ns}"
    return hashlib.md5(file_info.encode('utf-8')).hexdigest()

def ingest_data(conn: sqlite3.Connection):
    """
    Orquesta el proceso de ingestión: descubre nuevos ficheros, valida los datos,
    aparta los registros erróneos (cuarentena) y recopila los válidos para la siguiente fase.
    """
    print("--- Iniciando Fase 1: Ingestión de Datos ---")
    cursor = conn.cursor()
    
    drop_zone = DATA_DIR / "drops"
    print(f"Buscando ficheros .ndjson en: {drop_zone.resolve()}")
    source_files = list(drop_zone.glob("**/*.ndjson"))

    if not source_files:
        print("No se encontraron nuevos ficheros para ingestar.")
        return None

    all_valid_records = []
    
    for file_path in source_files:
        batch_id = get_batch_id(file_path)
        
        cursor.execute("SELECT 1 FROM ingest_history WHERE batch_id = ?", (batch_id,))
        if cursor.fetchone():
            print(f"OMITIENDO: El fichero {file_path.name} con batch_id {batch_id} ya fue procesado.")
            continue
            
        print(f"PROCESANDO: {file_path.name} con batch_id {batch_id}")
        
        valid_records = []
        quarantined_records = []
        ingest_ts = datetime.now(tz=timezone.utc).isoformat()
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                try:
                    record = json.loads(line)
                    
                    dt_obj = pd.to_datetime(record['ts'])
                    if dt_obj.tzinfo is None:
                        raise ValueError("Timestamp no contiene información de zona horaria")
                    
                    if not record.get('user_id') or not record.get('path'):
                        raise ValueError("user_id o path están vacíos o son nulos")
                    
                    record['_ingest_ts'] = ingest_ts
                    record['_source_file'] = str(file_path)
                    record['_batch_id'] = batch_id
                    valid_records.append(record)
                    
                except (json.JSONDecodeError, ValueError, KeyError, TypeError) as e:
                    quarantined_records.append({
                        "source_file": str(file_path),
                        "line": i,
                        "data": line.strip(),
                        "error": str(e)
                    })
        
        if valid_records:
            all_valid_records.extend(valid_records)

        if quarantined_records:
            quarantine_file = OUTPUT_DIR / f"quarantine/{file_path.stem}_errors.jsonl"
            with open(quarantine_file, 'w', encoding='utf-8') as qf:
                for qr in quarantined_records:
                    qf.write(json.dumps(qr) + '\n')
            print(f" -> {len(quarantined_records)} registros enviados a cuarentena en {quarantine_file.name}")

        cursor.execute("INSERT INTO ingest_history (batch_id, source_file, processed_ts) VALUES (?, ?, ?)",
                       (batch_id, str(file_path), ingest_ts))
        conn.commit()

    if not all_valid_records:
        print("No se encontraron registros válidos para procesar.")
        return None

    print("--- Fase 1 Completada ---\n")
    return pd.DataFrame(all_valid_records)

# ==============================================================================
# ... (El resto de las funciones clean_and_model, generate_report y main no necesitan cambios)
# PEGA AQUÍ LAS FUNCIONES clean_and_model(), generate_report() y main() DE LA VERSIÓN ANTERIOR.
# ==============================================================================
def clean_and_model(df: pd.DataFrame):
    """
    Toma los datos ingeridos, los limpia (Capa Plata) y luego los modela para
    el análisis de negocio (Capa Oro).
    Persiste los resultados tanto en Parquet como en SQLite.
    """
    print("--- Iniciando Fase 2: Limpieza y Modelado ---")
    
    # --- 2.1. CAPA PLATA: Limpieza y Estandarización ---
    print("Generando Capa Plata...")
    df['ts'] = pd.to_datetime(df['ts'])
    df['path_clean'] = df['path'].str.lower().str.split('?').str[0]
    
    df = df.sort_values(by='_ingest_ts', ascending=True)
    df = df.drop_duplicates(subset=['user_id', 'ts', 'path'], keep='last')
    
    # Creamos una columna 'fecha' de tipo texto para compatibilidad con SQLite y Parquet.
    df['fecha'] = df['ts'].dt.strftime('%Y-%m-%d')
    
    # --- Almacenamiento de Capa Plata (Parquet y SQLite) ---
    
    # 1. Almacenamiento en Parquet Particionado
    plata_path = OUTPUT_DIR / "plata"
    df_plata_parquet = df.copy()
    df_plata_parquet['fecha'] = pd.to_datetime(df_plata_parquet['fecha']).dt.date # Para particionamiento
    
    table = pa.Table.from_pandas(df_plata_parquet, preserve_index=False)
    ds.write_dataset(
        table,
        base_dir=plata_path,
        format="parquet",
        partitioning=["fecha"],
        partitioning_flavor='hive',
        existing_data_behavior='overwrite_or_ignore'
    )
    print(f" -> Datos de Capa Plata guardados en Parquet: {plata_path}")
    
    # 2. Almacenamiento en SQLite
    conn = sqlite3.connect(DB_PATH)
    # Usamos 'replace' para que la tabla se borre y se vuelva a crear en cada ejecución.
    df.to_sql('plata_events', conn, if_exists='replace', index=False)
    conn.close()
    print(f" -> Datos de Capa Plata guardados en SQLite: ut1.db (tabla: plata_events)")

    # --- 2.2. CAPA ORO: Modelado de Negocio ---
    print("Generando Capa Oro...")
    # Construcción de Sesiones
    df = df.sort_values(by=['user_id', 'ts'])
    time_diff = df.groupby('user_id')['ts'].diff().dt.total_seconds().fillna(0)
    new_session_mark = (time_diff > 30 * 60).astype(int)
    session_group = new_session_mark.groupby(df['user_id']).cumsum()
    df['session_id'] = df['user_id'] + '_' + session_group.astype(str)
    
    # Agregaciones para el reporte
    top_paths = df['path_clean'].value_counts().nlargest(10).reset_index()
    top_paths.columns = ['path', 'visitas']
    
    sessions_per_day = df.groupby('fecha')['session_id'].nunique().reset_index()
    sessions_per_day.columns = ['fecha', 'sesiones_unicas']

    sessions_with_home = df[df['path_clean'] == '/']['session_id'].unique()
    sessions_with_products = df[
        (df['session_id'].isin(sessions_with_home)) &
        (df['path_clean'] == '/productos')
    ]['session_id'].unique()
    sessions_with_checkout = df[
        (df['session_id'].isin(sessions_with_products)) &
        (df['path_clean'] == '/checkout')
    ]['session_id'].unique()

    funnel_data = {
        'Paso': ['1. Visita a Home (/)', '2. Visita a Productos', '3. Visita a Checkout'],
        'Sesiones': [len(sessions_with_home), len(sessions_with_products), len(sessions_with_checkout)]
    }
    funnel_df = pd.DataFrame(funnel_data)
    funnel_df['Tasa_Conversion_Paso_Anterior'] = (funnel_df['Sesiones'] / funnel_df['Sesiones'].shift(1).fillna(funnel_df['Sesiones'][0])) * 100
    funnel_df['Tasa_Conversion_Total'] = (funnel_df['Sesiones'] / funnel_df['Sesiones'][0]) * 100

    # --- Almacenamiento de Capa Oro (Parquet y SQLite) ---
    
    # 1. Almacenamiento en Parquet
    oro_path = OUTPUT_DIR / "oro"
    top_paths.to_parquet(oro_path / "top_paths.parquet", index=False)
    sessions_per_day.to_parquet(oro_path / "sessions_per_day.parquet", index=False)
    funnel_df.to_parquet(oro_path / "funnel.parquet", index=False)
    print(f" -> Agregados de Capa Oro guardados en Parquet: {oro_path}")

    # 2. Almacenamiento en SQLite
    conn = sqlite3.connect(DB_PATH)
    top_paths.to_sql('oro_top_paths', conn, if_exists='replace', index=False)
    sessions_per_day.to_sql('oro_sessions_per_day', conn, if_exists='replace', index=False)
    funnel_df.to_sql('oro_funnel', conn, if_exists='replace', index=False)
    conn.close()
    print(f" -> Agregados de Capa Oro guardados en SQLite: ut1.db")
    
    print("--- Fase 2 Completada ---\n")

def generate_report():
    """
    Lee los datos agregados de la Capa Oro y genera un informe en formato Markdown.
    """
    print("--- Iniciando Fase 3: Generación del Reporte ---")
    oro_path = OUTPUT_DIR / "oro"
    report_path = OUTPUT_DIR / "reporte.md"

    try:
        top_paths = pd.read_parquet(oro_path / "top_paths.parquet")
        sessions_per_day = pd.read_parquet(oro_path / "sessions_per_day.parquet")
        funnel_df = pd.read_parquet(oro_path / "funnel.parquet")
    except FileNotFoundError:
        print("ERROR: No se encontraron los ficheros de la capa Oro. Ejecuta la Fase 2 primero.")
        return

    top_paths_md = tabulate(top_paths, headers='keys', tablefmt='github', showindex=False)
    sessions_per_day_md = tabulate(sessions_per_day, headers='keys', tablefmt='github', showindex=False)
    funnel_df_md = tabulate(funnel_df, headers='keys', tablefmt='github', showindex=False, floatfmt=(".0f", ".0f", ".2f", ".2f"))
    
    periodo_inicio = sessions_per_day['fecha'].min()
    periodo_fin = sessions_per_day['fecha'].max()
    fecha_reporte = datetime.now(tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

    report_content = f"""
# Informe de Analítica Web

- **Periodo Analizado:** {periodo_inicio} a {periodo_fin}
- **Fecha de Generación:** {fecha_reporte}
- **Fuente de Datos:** Ficheros NDJSON en `project/data/drops/`

---

## Definiciones de KPIs

- **Sesión:** Una secuencia de eventos de un mismo usuario donde el tiempo entre eventos consecutivos no supera los 30 minutos.
- **Tasa de Conversión:** Porcentaje de sesiones que avanzan de un paso del embudo al siguiente.

---

## Resumen de Actividad

### Sesiones Únicas por Día

{sessions_per_day_md}

### Top 10 Páginas Más Visitadas

{top_paths_md}

### Embudo de Conversión (Home → Productos → Checkout)

{funnel_df_md}

---

## Conclusiones y Acciones (Plantilla)

- **Insight:** *[Observación clave basada en los datos, ej. "La tasa de abandono entre Productos y Checkout es del X%"]*
- **Implicación:** *[Consecuencia de negocio del insight, ej. "Estamos perdiendo una cantidad significativa de ventas potenciales en el último paso"]*
- **Acción:** *[Siguiente paso propuesto, ej. "Analizar el flujo de checkout para identificar puntos de fricción"]*
"""
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f" -> Reporte generado correctamente en: {report_path}")
    print("--- Fase 3 Completada ---")

def main():
    """Función principal que orquesta la ejecución de todo el pipeline."""
    db_conn = setup_database()
    raw_df = ingest_data(db_conn)
    db_conn.close()

    if raw_df is not None and not raw_df.empty:
        clean_and_model(raw_df)
        generate_report()
    else:
        print("Pipeline finalizado: no había nuevos datos válidos que procesar.")

if __name__ == "__main__":
    main()