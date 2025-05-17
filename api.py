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

def predict_remaining_days(z_value, mag_value):
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("Modelo RandomForest no encontrado.")

    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)

    input_df = pd.DataFrame([{
        'z': z_value,
        'magnitud': mag_value
    }])

    predicted_days = model.predict(input_df)[0]
    porcentaje_estimado = max(0, min(100, (predicted_days / 30) * 100))

    return custom_round(porcentaje_estimado), custom_round(predicted_days)

@app.route('/gas-info', methods=['GET'])
def get_gas_info():
    try:
        z_value = float(request.args.get('z', 3.5))
        mag_value = float(request.args.get('magnitud', 2.7))

        porcentaje, dias = predict_remaining_days(z_value, mag_value)

        return jsonify({
            "porcentaje_actual": porcentaje,
            "dias_restantes": dias
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
