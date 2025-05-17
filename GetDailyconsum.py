
import pandas as pd

def gdc():
    # Cargar datos
    df = pd.read_csv("datasets/datos_procesados.csv")

    # Asegúrate que Date esté en formato de fecha
    df["Date"] = pd.to_datetime(df["Date"])

    # Agrupar por día y tomar la magnitud máxima y mínima de cada día
    diario = df.groupby(df["Date"].dt.date)["Magnitud"].agg(["max", "min"])
    diario["Consumo_dia_magnitudes"] = diario["max"] - diario["min"]

    # Convertir a litros (usando la relación 10 magnitudes = 1 litro)
    diario["Consumo_dia_litros"] = diario["Consumo_dia_magnitudes"] / 10

    # Calcular el promedio diario
    consumo_prom_litros = diario["Consumo_dia_litros"].mean()

    # Y ahora convertir eso a porcentaje del tanque (de 300 L)
    consumo_prom_porcentaje = (consumo_prom_litros / 300) * 100
    
    # Mostrar resultados
    print(f"Consumo promedio por día: {consumo_prom_litros:.2f} litros ({consumo_prom_porcentaje:.2f}%)")
    
    df["Gas_%"] = (df["Magnitud"] - 112000) / (115000 - 112000) * 100
    df["Dias Restantes"] = df["Gas_%"] / consumo_prom_porcentaje

    df.to_csv("datasets/datos_procesados.csv", index=False)
    
    return consumo_prom_porcentaje
