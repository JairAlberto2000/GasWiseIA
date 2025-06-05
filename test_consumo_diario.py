from GetDailyconsum import calcular_consumo_diario

def test():
    try:
        resultado = calcular_consumo_diario()
        print(f"✅ Consumo promedio estimado por IA: {resultado:.2f} % por día")
    except Exception as e:
        print(f"❌ Error al calcular el consumo diario: {e}")

if __name__ == "__main__":
    test()
