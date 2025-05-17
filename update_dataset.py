import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

# Supongamos que estos valores se obtuvieron de calibración
magnitud_lleno = 115000  # valor de magnitud con tanque lleno (manómetro = 95)
magnitud_vacio = 112000  # valor con tanque vacío (manómetro = 5)
consumo_diario_est = 6  # porcentaje promedio diario que se consume

# Función para calcular magnitud
def calcular_magnitud(x, y, z):
    return np.sqrt(x**2 + y**2 + z**2)

# Función para normalizar magnitud a porcentaje
def calcular_porcentaje(mag, mag_min, mag_max):
    return (mag - mag_min) / (mag_max - mag_min) * 100

# Función para estimar días restantes
def estimar_dias_restantes(porcentaje, consumo_diario):
    return porcentaje / consumo_diario

# Ejemplo de lectura actual
x, y, z = 65454, 65361, 65378
magnitud_actual = calcular_magnitud(x, y, z)
porcentaje_gas = calcular_porcentaje(magnitud_actual, magnitud_vacio, magnitud_lleno)
dias_restantes = estimar_dias_restantes(porcentaje_gas, consumo_diario_est)

print(f"Gas restante: {porcentaje_gas:.2f}%")
print(f"Días aproximados restantes: {dias_restantes:.1f}")
