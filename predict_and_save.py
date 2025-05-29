import mysql.connector
import pickle
import pandas as pd
from datetime import datetime
import os

MODEL_PATH = "/home/ubuntu/GasWiseIA/models/RandomForest.pkl"

db_config = {
    'host': 'localhost',
    'user': 'montse',
    'password': '123456',
    'database': 'DBGasWise'
}

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor(dictionary=True)

# Cargar modelo
with open(MODEL_PATH, 'rb') as f:
    model = pickle.load(f)

# Obtener la última lectura por dispositivo
query = """
SELECT ld.*
FROM Lecturas_Dispositivo ld
INNER JOIN (
    SELECT DispositivoID, MAX(LecturaID) AS UltimaLectura
    FROM Lecturas_Dispositivo
    GROUP BY DispositivoID
) sub ON ld.DispositivoID = sub.DispositivoID AND ld.LecturaID = sub.UltimaLectura;
"""

cursor.execute(query)
lecturas = cursor.fetchall()

resultados = []

for lectura in lecturas:
    dispositivo_id = lectura['DispositivoID']
    usuario_id = lectura['UsuarioID']
    lectura_id = lectura['LecturaID']
    x = lectura['Coordenada_X']
    y = lectura['Coordenada_Y']
    z = lectura['Coordenada_Z']
    magnitud = float(lectura['Nivel'])

    # Verificar que el dispositivo le pertenece al usuario
    cursor.execute("""
        SELECT 1 FROM Dispositivo_Usuario
        WHERE DispositivoID = %s AND UsuarioID = %s
        LIMIT 1;
    """, (dispositivo_id, usuario_id))
    validacion = cursor.fetchone()

    if not validacion:
        print(f"Dispositivo {dispositivo_id} no pertenece al usuario {usuario_id}. Se omite.")
        continue

    # Generar predicción
    df = pd.DataFrame([{
        'X': x,
        'Y': y,
        'Z': z,
        'Magnitud': magnitud
    }])
    prediccion = model.predict(df)[0]
    porcentaje = round(max(0, min(100, (prediccion / 30) * 100)), 2)

    # Consultar el último resultado para comparar
    cursor.execute("""
        SELECT Resultado FROM Resultados_Lecturas
        WHERE DispositivoID = %s
        ORDER BY Fecha DESC
        LIMIT 1;
    """, (dispositivo_id,))
    ultimo = cursor.fetchone()

    if ultimo and round(ultimo['Resultado'], 2) == porcentaje:
        print(f"🔁 Porcentaje igual al anterior ({porcentaje}%), no se guarda para dispositivo {dispositivo_id}.")
        continue  # No insertar si el valor no ha cambiado

    # Agregar a lista de inserción
    resultados.append((dispositivo_id, lectura_id, magnitud, porcentaje, datetime.now()))

# Guardar predicciones válidas
if resultados:
    insert_query = """
    INSERT INTO Resultados_Lecturas (DispositivoID, LecturaID, magnitud, Resultado, Fecha)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.executemany(insert_query, resultados)
    conn.commit()
    print(f"✅ {len(resultados)} resultados guardados.")
else:
    print("⚠️ No se generaron nuevas predicciones (sin cambios).")

cursor.close()
conn.close()
