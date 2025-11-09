import pandas as pd
import numpy as np
import json
from pathlib import Path

def find_project_root(marker=".gitignore"):
    """Sube niveles hasta encontrar el fichero marcador de la raíz del proyecto."""
    current_path = Path(__file__).resolve()
    while current_path != current_path.parent:
        if (current_path / marker).exists():
            return current_path
        current_path = current_path.parent
    raise FileNotFoundError(f"No se pudo encontrar la raíz del proyecto (marcador: {marker})")

import pandas as pd
import numpy as np
import json
from pathlib import Path

def find_project_root(marker=".gitignore"):
    """Sube niveles hasta encontrar el fichero marcador de la raíz del proyecto."""
    current_path = Path(__file__).resolve()
    while current_path != current_path.parent:
        if (current_path / marker).exists():
            return current_path
        current_path = current_path.parent
    raise FileNotFoundError(f"No se pudo encontrar la raíz del proyecto (marcador: {marker})")

def generate_web_analytics_data_large():
    """
    Genera un fichero de datos de prueba (events.ndjson) a mayor escala (10,000 registros),
    con una variedad de registros inválidos para probar la cuarentena.
    """
    # 1. Configuración (sin cambios)
    np.random.seed(42)
    N = 10_000
    PROJECT_ROOT = find_project_root()
    output_dir = PROJECT_ROOT / "project" / "data" / "drops" / "2025-01-03"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "events.ndjson"

    # 2. Universos de Datos (sin cambios)
    users = [f'u{str(i).zfill(4)}' for i in range(1, 501)]
    paths = ['/', '/productos', '/checkout', '/contacto', '/blog', '/ayuda', '/login']
    paths_prob = [0.4, 0.25, 0.1, 0.1, 0.05, 0.05, 0.05]
    referrers = ['direct', 'google', 'twitter', 'facebook', '/', '/productos']
    devices = ['mobile', 'desktop', 'tablet']
    timestamps = pd.to_datetime(pd.date_range('2025-01-03T00:00:00Z', periods=1440, freq='T'))

    # 3. Generación del DataFrame con Datos Válidos (sin cambios)
    print(f"Generando {N} eventos...")
    df = pd.DataFrame({
        'ts': np.random.choice(timestamps, size=N),
        'user_id': np.random.choice(users, size=N),
        'path': np.random.choice(paths, size=N, p=paths_prob),
        'referrer': np.random.choice(referrers, size=N),
        'device': np.random.choice(devices, size=N, p=[0.6, 0.3, 0.1])
    })

    # 4. --- SECCIÓN ACTUALIZADA: Introducción de Registros Inválidos Variados ---
    print("Inyectando registros inválidos para la cuarentena...")
    num_bad_records = int(N * 0.01) # ~100 registros malos
    if num_bad_records < 4: num_bad_records = 4 # Aseguramos al menos uno de cada tipo
    
    bad_indices = np.random.choice(df.index, size=num_bad_records, replace=False)

    # Convertimos los datos a una lista de diccionarios para poder manipularlos
    records = df.to_dict('records')

    # Inyectamos los 4 tipos de errores que nuestro pipeline valida
    for i, idx in enumerate(bad_indices):
        error_type = i % 4
        
        if error_type == 0:
            # Error de formato de timestamp
            records[idx]['ts'] = "2025/01/03 10:30:00" # Formato no ISO
        elif error_type == 1:
            # Error de user_id nulo/vacío
            records[idx]['user_id'] = ""
        elif error_type == 2:
            # Error de path nulo/vacío
            records[idx]['path'] = None
        else:
            # Error de timestamp sin zona horaria
            ts_obj = pd.to_datetime(records[idx]['ts'])
            records[idx]['ts'] = ts_obj.tz_localize(None).isoformat()
    
    # Añadimos un error de JSON malformado a mano para asegurar que existe
    malformed_json_str = '{"ts": "2025-01-03T11:15:30Z", "user_id": "u004", "path": "/checkout", "device": "mobile",}' # Coma extra
    records.append(malformed_json_str)
    
    # Mezclamos todos los registros
    np.random.shuffle(records)

    # 5. Escribir los datos en el Fichero NDJSON
    print(f"Escribiendo fichero de datos en: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        for record in records:
            if isinstance(record, dict):
                if isinstance(record.get('ts'), pd.Timestamp):
                    record['ts'] = record['ts'].isoformat().replace('+00:00', 'Z')
                
                clean_record = {k: v for k, v in record.items() if pd.notna(v)}
                f.write(json.dumps(clean_record) + '\n')
            else:
                # Escribimos la línea que es directamente una cadena malformada
                f.write(str(record) + '\n')
    
    print(f"¡Hecho! Se han escrito {len(records)} registros.")
    file_size = output_file.stat().st_size / (1024 * 1024)
    print(f"Tamaño del fichero: {file_size:.2f} MB.")


if __name__ == "__main__":
    generate_web_analytics_data_large()