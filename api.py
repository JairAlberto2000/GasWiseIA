from flask import Flask, jsonify
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
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT porcentaje_restante AS porcentaje, dias_estimados AS dias, Fecha
            FROM Resultados_Lecturas
            ORDER BY Fecha DESC
            LIMIT 1
        """
        cursor.execute(query)
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            return jsonify({
                "porcentaje_actual": result["porcentaje"],
                "dias_restantes": result["dias"],
                "fecha": result["Fecha"].strftime("%Y-%m-%d %H:%M:%S")
            })
        else:
            return jsonify({"error": "No hay registros de predicción"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
