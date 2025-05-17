from flask import Flask, jsonify, request
import pandas as pd
import pickle
import os
import math

app = Flask(__name__)

MODEL_PATH = "models/RandomForest.pkl"

def custom_round(value):
    decimal = value - int(value)
    if decimal <= 0.5:
        return math.floor(value)
    elif decimal >= 0.6:
        return math.ceil(value)
    else:
        return round(value)

def predict_remaining_days(x, y, z, magnitud):
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("Modelo RandomForest no encontrado.")

    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)

    input_df = pd.DataFrame([{
        'X': x,
        'Y': y,
        'Z': z,
        'Magnitud': magnitud
    }])

    predicted_days = model.predict(input_df)[0]
    porcentaje_estimado = max(0, min(100, (predicted_days / 30) * 100))

    return custom_round(porcentaje_estimado), custom_round(predicted_days)

@app.route('/gas-info', methods=['GET'])
def get_gas_info():
    try:
        x = float(request.args.get('x'))
        y = float(request.args.get('y'))
        z = float(request.args.get('z'))
        magnitud = float(request.args.get('magnitud'))

        porcentaje, dias = predict_remaining_days(x, y, z, magnitud)

        return jsonify({
            "porcentaje_actual": porcentaje,
            "dias_restantes": dias
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
