from flask import Flask, jsonify, request
import mysql.connector
from datetime import datetime
from GetDailyconsum import calcular_consumo_diario  # 👈 Se importa aquí

app = Flask(__name__)

DB_CONFIG = {
    'host': 'localhost',
    'user': 'montse',
    'password': '123456',
    'database': 'DBGasWise'
}

@app.route('/gas-info', methods=['GET'])
def get_gas_info():
    usuario_id = request.args.get('usuario_id', type=int)

    if not usuario_id:
        return jsonify({"error": "Falta el parámetro usuario_id"}), 400

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT DispositivoID, Capacidad_litros
            FROM Dispositivo_Usuario
            WHERE UsuarioID = %s AND Status = 1
            ORDER BY Fecha_Asignacion DESC
            LIMIT 1
        """, (usuario_id,))
        dispositivo = cursor.fetchone()

        if not dispositivo:
            return jsonify({"error": "No se encontró un dispositivo activo para el usuario"}), 404

        dispositivo_id = dispositivo['DispositivoID']
        capacidad = float(dispositivo['Capacidad_litros'])

        cursor.execute("""
            SELECT Resultado AS porcentaje, Fecha
            FROM Resultados_Lecturas
            WHERE DispositivoID = %s
            ORDER BY Fecha DESC
            LIMIT 1
        """, (dispositivo_id,))
        resultado = cursor.fetchone()

        cursor.close()
        conn.close()

        # 👉 Obtener promedio desde IA
        promedio_diario = calcular_consumo_diario()

        if resultado:
            porcentaje_actual = resultado['porcentaje']
            fecha_lectura = resultado['Fecha'].strftime("%Y-%m-%d %H:%M:%S")

            # Si el promedio es válido, calcular los días
            if promedio_diario > 0:
                dias_estimados = round((porcentaje_actual / 100) * capacidad / promedio_diario, 1)
            else:
                dias_estimados = 0  # No mostrar "+90", sino que forzamos a 0 si no hay base

            return jsonify({
                "porcentaje_actual": round(porcentaje_actual, 1),
                "dias_restantes": dias_estimados,
                "fecha": fecha_lectura,
                "promedio_diario": round(promedio_diario, 2),
                "capacidad_tanque": capacidad
            })
        else:
            return jsonify({"error": "No hay resultados para este dispositivo"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/grafica-consumo', methods=['GET'])
def grafica_consumo():
    usuario_id = request.args.get('usuario_id', type=int)

    if not usuario_id:
        return jsonify({"error": "Falta el parámetro usuario_id"}), 400

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT DispositivoID
            FROM Dispositivo_Usuario
            WHERE UsuarioID = %s AND Status = 1
            ORDER BY Fecha_Asignacion DESC
            LIMIT 1
        """, (usuario_id,))
        dispositivo = cursor.fetchone()

        if not dispositivo:
            return jsonify({"error": "No se encontró dispositivo activo"}), 404

        dispositivo_id = dispositivo["DispositivoID"]

        cursor.execute("""
            SELECT Fecha, Resultado
            FROM Resultados_Lecturas
            WHERE DispositivoID = %s
            ORDER BY Fecha ASC
            LIMIT 30
        """, (dispositivo_id,))
        resultados = cursor.fetchall()

        datos = []
        ultimo_porcentaje = None
        for idx in range(30):
            if idx < len(resultados):
                porcentaje = float(resultados[idx]["Resultado"])
                ultimo_porcentaje = porcentaje
            else:
                porcentaje = ultimo_porcentaje if ultimo_porcentaje is not None else 0
            datos.append({
                "dia": idx + 1,
                "porcentaje": porcentaje
            })

        cursor.close()
        conn.close()

        return jsonify(datos)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
