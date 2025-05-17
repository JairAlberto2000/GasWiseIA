import pandas as pd

df = pd.read_csv('datasets/datos_procesados.csv')

x_max = df['X'].max()
y_max = df['Y'].max()
z_max = df['Z'].max()

x_min = df['X'].min()
y_min = df['Y'].min()
z_min = df['Z'].min()

print(f"X max: {x_max}, X min: {x_min}")
print(f"Y max: {y_max}, Y min: {y_min}")
print(f"Z max: {z_max}, Z min: {z_min}")

print (df.head(20))
