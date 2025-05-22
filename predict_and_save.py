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
    lectura_id = lectura['LecturaID']
    x = lectura['Coordenada_X']
    y = lectura['Coordenada_Y']
    z = lectura['Coordenada_Z']
    magnitud = float(lectura['Nivel'])

    df = pd.DataFrame([{
        'X': x,
        'Y': y,
        'Z': z,
        'Magnitud': magnitud
    }])

    prediccion = model.predict(df)[0]
    porcentaje = max(0, min(100, (prediccion / 30) * 100))

    resultados.append((dispositivo_id, lectura_id, magnitud, round(porcentaje, 2), datetime.now()))

# Guardar predicciones
insert_query = """
INSERT INTO Resultados_Lecturas (DispositivoID, LecturaID, magnitud, Resultado, Fecha)
VALUES (%s, %s, %s, %s, %s)
"""

cursor.executemany(insert_query, resultados)
conn.commit()

cursor.close()
conn.close()
