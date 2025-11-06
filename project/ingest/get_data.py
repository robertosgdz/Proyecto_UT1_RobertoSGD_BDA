import pandas as pd
import numpy as np
import json
from pathlib import Path

def generate_web_analytics_data():
    """
    Genera un fichero de datos de prueba (events.ndjson) para el proyecto de Web Analytics.
    Crea 15 registros válidos y 5 inválidos para probar el pipeline de ingestión y cuarentena.
    El resultado se guarda en 'project/data/drops/2025-01-03/events.ndjson'.
    """
    # 1. Configuración de Reproducibilidad y Parámetros
    # Fijamos la semilla para que los datos "aleatorios" sean siempre los mismos.
    np.random.seed(42)
    output_dir = Path("project/data/drops/2025-01-03")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "events.ndjson"

    # 2. Universos de Datos para los Registros Válidos
    users = [f'u{str(i).zfill(3)}' for i in range(1, 6)] # u001, u002, ...
    paths = ['/', '/productos', '/productos?id=123', '/checkout', '/contacto?utm=google']
    referrers = ['direct', 'google', 'twitter', '/', '/productos']
    devices = ['mobile', 'desktop', 'tablet']
    
    # Rango de timestamps para simular actividad en un periodo corto
    timestamps = pd.to_datetime(pd.date_range('2025-01-03T10:00:00Z', periods=30, freq='2min'))

    # 3. Generación de 15 Registros Válidos
    # Usamos la lógica de Pandas/Numpy vista en el Colab UT1_Punto3.
    good_records_df = pd.DataFrame({
        'ts': np.random.choice(timestamps, size=15),
        'user_id': np.random.choice(users, size=15),
        'path': np.random.choice(paths, size=15),
        'referrer': np.random.choice(referrers, size=15),
        'device': np.random.choice(devices, size=15, p=[0.6, 0.3, 0.1])
    })
    
    # Convertimos el DataFrame a una lista de diccionarios para poder mezclarlo con los datos malos.
    good_records = good_records_df.to_dict('records')

    # 4. Creación de 5 Registros Inválidos (para la cuarentena)
    # Cada registro está diseñado para fallar una de las reglas de validación.
    bad_records = [
        # Error 1: Formato de timestamp inválido. No es ISO 8601.
        {"ts": "2025/01/03 11:00:00", "user_id": "u001", "path": "/", "referrer": "direct", "device": "mobile"},
        
        # Error 2: user_id está vacío. Es un campo obligatorio.
        {"ts": "2025-01-03T11:05:10Z", "user_id": "", "path": "/productos", "referrer": "/", "device": "desktop"},
        
        # Error 3: path es nulo (None). Es un campo obligatorio.
        {"ts": "2025-01-03T11:10:20Z", "user_id": "u003", "path": None, "referrer": "google", "device": "tablet"},
        
        # Error 4: La línea no es un JSON válido (está malformada).
        '{"ts": "2025-01-03T11:15:30Z", "user_id": "u004", "path": "/checkout", "device": "mobile",}', # Coma extra al final
        
        # Error 5: Timestamp sin zona horaria (no cumple el requisito de ser UTC).
        {"ts": "2025-01-03T11:20:00", "user_id": "u005", "path": "/", "referrer": "direct", "device": "desktop"}
    ]

    # 5. Combinar y Mezclar todos los Registros
    # Juntamos los registros buenos y malos y los mezclamos para que el fichero de log sea más realista.
    all_records = good_records + bad_records
    np.random.shuffle(all_records)

    # 6. Escribir los datos en el Fichero NDJSON
    print(f"Generando fichero de datos en: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        for record in all_records:
            if isinstance(record, dict):
                # Para los registros buenos y los malos que son diccionarios, convertimos la fecha a string
                if 'ts' in record and isinstance(record['ts'], pd.Timestamp):
                    record['ts'] = record['ts'].isoformat().replace('+00:00', 'Z')
                f.write(json.dumps(record) + '\n')
            else:
                # Para el registro que es una cadena malformada
                f.write(record + '\n')
    
    print(f"¡Hecho! Se han escrito {len(all_records)} registros (15 válidos, 5 para cuarentena).")


if __name__ == "__main__":
    generate_web_analytics_data()