import pymysql
import pandas as pd
import pickle
import os
import math
from datetime import datetime

# Configuración de la base de datos
DB_CONFIG = {
    "host": "localhost",
    "user": "montse",
    "password": "123456",
    "database_lecturas": "DBGasWise",
    "database_resultados": "Resultados_Lecturas"
}

MODEL_PATH = "models/RandomForest.pkl"

def custom_round(value):
    decimal = value - int(value)
    if decimal <= 0.5:
        return math.floor(value)
    elif decimal >= 0.6:
        return math.ceil(value)
    else:
        return round(value)

def predict_and_save():
    try:
        # Conectar a la base de datos de lecturas
        conn_lecturas = pymysql.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["montse"],
            password=DB_CONFIG["123456"],
            database=DB_CONFIG["database_lecturas"]
        )

        # Leer última lectura
        df = pd.read_sql("SELECT * FROM Lecturas_Dispositivo ORDER BY fecha DESC LIMIT 1", conn_lecturas)
        conn_lecturas.close()

        if df.empty:
            print("No hay lecturas disponibles.")
            return

        lectura = df.iloc[0]
        x, y, z, magnitud = lectura["X"], lectura["Y"], lectura["Z"], lectura["Magnitud"]

        # Cargar modelo
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError("Modelo RandomForest no encontrado.")

        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)

        input_df = pd.DataFrame([{
            "X": x,
            "Y": y,
            "Z": z,
            "Magnitud": magnitud
        }])

        predicted_days = model.predict(input_df)[0]
        porcentaje = max(0, min(100, (predicted_days / 30) * 100))

        # Conectar a la base de datos de resultados
        conn_resultados = pymysql.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["montse"],
            password=DB_CONFIG["123456"],
            database=DB_CONFIG["database_resultados"]
        )

        cursor = conn_resultados.cursor()
        insert_query = """
            INSERT INTO Resultados_Lecturas (fecha, porcentaje_restante, dias_estimados)
            VALUES (%s, %s, %s)
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(insert_query, (now, custom_round(porcentaje), custom_round(predicted_days)))
        conn_resultados.commit()
        cursor.close()
        conn_resultados.close()

        print("Predicción guardada con éxito.")

    except Exception as e:
        print(f"Error durante la predicción: {e}")

if __name__ == "__main__":
    predict_and_save()
