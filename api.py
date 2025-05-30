from flask import Flask, jsonify, request
import mysql.connector
from datetime import datetime

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

        cursor.execute("""
            SELECT Nivel, Fecha
            FROM Lecturas_Dispositivo
            WHERE DispositivoID = %s
            ORDER BY Fecha DESC
            LIMIT 5
        """, (dispositivo_id,))
        lecturas = cursor.fetchall()

        promedio_diario = 0
        if len(lecturas) >= 2:
            consumos = []
            for i in range(len(lecturas) - 1):
                nivel_actual = float(lecturas[i]['Nivel'])
                nivel_anterior = float(lecturas[i + 1]['Nivel'])
                consumo = nivel_anterior - nivel_actual
                if consumo > 0:
                    consumos.append(consumo)
            if consumos:
                promedio_diario = sum(consumos) / len(consumos)

        cursor.close()
        conn.close()

        if resultado:
            porcentaje_actual = resultado['porcentaje']
            fecha_lectura = resultado['Fecha'].strftime("%Y-%m-%d %H:%M:%S")

            # 🚨 Corrección aquí: usar consumo mínimo si no hay histórico
            consumo_diario_estimado = promedio_diario if promedio_diario > 0 else 1.0
            dias_estimados = round((porcentaje_actual / 100) * capacidad / consumo_diario_estimado, 1)

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
