import numpy as np
import pandas as pd

df = pd.read_csv('datasets/raw_data.csv')

# 1. Limpiar "a. m." / "p. m." y convertir a datetime
df["Date"] = df["Date"].str.replace("a. m.", "AM").str.replace("p. m.", "PM")
df["DateTime"] = pd.to_datetime(df["Date"], format="%d/%m/%Y %I:%M:%S %p")

# 2. Extraer el valor numérico de la columna "X" (que contiene X, Y, Z)
df["Value"] = df["X"].str.extract(r"(\d+)").astype(float)

# 3. Identificar si la fila es X, Y o Z (para pivotear después)
df["Axis"] = df["X"].str.extract(r"Magnetic Field in (.)-Axis")

# 4. Pivotar la tabla para tener X, Y, Z como columnas
df_pivoted = df.pivot_table(
    index=["DateTime"],  # Agrupar por fecha/hora
    columns="Axis",      # Crear columnas X, Y, Z
    values="Value",      # Valores numéricos
    aggfunc="first"      # Tomar el primer valor (no duplicados)
).reset_index()

# 5. Separar fecha y hora
df_pivoted["Date"] = df_pivoted["DateTime"].dt.date
df_pivoted["Time"] = df_pivoted["DateTime"].dt.time

# 6. Eliminar columnas temporales y reordenar
df_final = df_pivoted.drop("DateTime", axis=1)
df_final = df_final[["Date", "Time", "X", "Y", "Z"]]

# ----------------------------------------------------------------------
# Calcular magnitud (opcional)
df_final["X"] = pd.to_numeric(df_final["X"], errors="coerce")  # Convierte a número, si falla pone NaN
df_final["Y"] = pd.to_numeric(df_final["Y"], errors="coerce")
df_final["Z"] = pd.to_numeric(df_final["Z"], errors="coerce")

df_final["Magnitud"] = np.sqrt(df_final["X"]**2 + df_final["Y"]**2 + df_final["Z"]**2)
df_final = df_final.dropna(subset=["X", "Y", "Z"])  # Elimina filas con valores NaN en X, Y o Z

print (df_final.head())
print (df_final.describe())

df_final.to_csv("datasets/datos_procesados.csv", index=False)