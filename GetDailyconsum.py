import mysql.connector
import pandas as pd
from datetime import datetime

def calcular_consumo_diario():
    # Configuración de conexión
    db_config = {
        'host': 'localhost',
        'user': 'montse',
        'password': '123456',
        'database': 'DBGasWise'
    }

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # Obtener lecturas con fecha y nivel
    cursor.execute("""
        SELECT Fecha, Nivel
        FROM Lecturas_Dispositivo
        WHERE Nivel > 0
        ORDER BY Fecha ASC
    """)
    resultados = cursor.fetchall()

    cursor.close()
    conn.close()

    if not resultados or len(resultados) < 2:
        print("No hay suficientes datos para calcular consumo.")
        return 0

    # Convertir a DataFrame
    df = pd.DataFrame(resultados)
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    df["Nivel"] = df["Nivel"].astype(float)

    # Agrupar por día y calcular consumo
    diario = df.groupby(df["Fecha"].dt.date)["Nivel"].agg(["max", "min"])
    diario["consumo_diario_litros"] = diario["max"] - diario["min"]

    # Calcular promedio (solo si hay consumo positivo)
    consumos_validos = diario[diario["consumo_diario_litros"] > 0]
    promedio_litros = consumos_validos["consumo_diario_litros"].mean()

    # Convertir a porcentaje (tanque de 300 L)
    promedio_porcentaje = (promedio_litros / 300) * 100

    print(f"📊 Promedio diario: {promedio_litros:.2f} litros ({promedio_porcentaje:.2f}%)")

    return promedio_litros
