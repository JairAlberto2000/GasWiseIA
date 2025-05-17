
import os
import pickle
import seaborn as sns
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
   
MODELS_PATH = "models/"
DATASET_PATH = "datasets/datos_procesados.csv" 
modelos = {
    "LinearRegression": LinearRegression(),
    "RandomForest": RandomForestRegressor(),
    "KNN": KNeighborsRegressor(n_neighbors=3),
    "DecisionTree": DecisionTreeRegressor(),
    "SVM": SVR()
}

feature_sets = {
    "Magnitud": ["Magnitud"],
    "XYZ": ["X", "Y", "Z"],
    "XYZ+Magnitud": ["X", "Y", "Z", "Magnitud"]
}

os.makedirs("models", exist_ok=True)
os.makedirs("metricas", exist_ok=True)

df = pd.read_csv(DATASET_PATH)
    
    
def create_model():
    # Ejemplo de predicción con el modelo lineal sobre todas las features
    X_sample = df[["X", "Y", "Z", "Magnitud"]]
    y_sample = df["Dias Restantes"]
    X_train, X_test, y_train, y_test = train_test_split(X_sample, y_sample, test_size=0.25, random_state=42)

    # Entrenar y guardar modelos simples
    for nombre, modelo in modelos.items():
        modelo.fit(X_train, y_train)
        pred = modelo.predict(X_test)
        mae = mean_absolute_error(y_test, pred)
        r2 = r2_score(y_test, pred)

        print(f"{nombre} - MAE: {mae:.2f} | R²: {r2:.2f}")

        # Guardar modelo
        with open(f"{MODELS_PATH}{nombre}.pkl", 'wb') as f:
            pickle.dump(modelo, f)

        """
            # Probar una predicción con el modelo lineal
            modelo_ejemplo = LinearRegression()
            modelo_ejemplo.fit(X_train, y_train)
            ejemplo = X_sample.sample(n=1, random_state=42)
            dias_predichos = modelo_ejemplo.predict(ejemplo)
            print(f"\nDías restantes para entrada de ejemplo: {dias_predichos[0]:.2f} días")
        """

    # Calcular y guardar métricas por modelo y feature set
    print ("\n\nMétricas por modelo y feature set:")
    for f_name, features in feature_sets.items():
        X = df[features]
        y = df["Dias Restantes"]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        for m_name, modelo_base in modelos.items():
            modelo = modelo_base.__class__()  # Crear nueva instancia
            modelo.fit(X_train, y_train)
            y_pred = modelo.predict(X_test)

            # Métricas
            mae = mean_absolute_error(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            r2 = r2_score(y_test, y_pred)

            carpeta = f"metricas/{m_name}_{f_name}"
            os.makedirs(carpeta, exist_ok=True)

            with open(f"{carpeta}/metricas.txt", "w") as f:
                f.write(f"MAE: {mae:.4f}\n")
                f.write(f"MSE: {mse:.4f}\n")
                f.write(f"RMSE: {rmse:.4f}\n")
                f.write(f"R2 Score: {r2:.4f}\n")

            # Feature importance si aplica
            if hasattr(modelo, "feature_importances_"):
                importancia = modelo.feature_importances_
                plt.figure(figsize=(6, 4))
                plt.bar(features, importancia)
                plt.title(f"Feature Importance - {m_name} ({f_name})")
                plt.ylabel("Importancia")
                plt.tight_layout()
                plt.savefig(f"{carpeta}/feature_importance.png")
                plt.close()

            print(f"{m_name} ({f_name}) → R2: {r2:.2f} | MAE: {mae:.2f}")

def create_metrics():
    # Configuración de estilos para gráficos
    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 6))

    # Diccionario para almacenar métricas y comparar después
    metricas_comparativas = []

    for f_name, features in feature_sets.items():
        X = df[features]
        y = df["Dias Restantes"]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        for m_name, modelo_base in modelos.items():
            modelo = modelo_base.__class__()  # Nueva instancia
            modelo.fit(X_train, y_train)
            y_pred = modelo.predict(X_test)

            # Cálculo de métricas
            mae = mean_absolute_error(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            r2 = r2_score(y_test, y_pred)
            
            # Almacenar métricas para comparación global
            metricas_comparativas.append({
                "Modelo": m_name,
                "Feature Set": f_name,
                "MAE": mae,
                "RMSE": rmse,
                "R2": r2
            })

            directory = f"metricas/{m_name}_{f_name}"
            if not os.path.exists(directory):
                os.makedirs(directory)
           
            # --- Gráfico 1: Predicciones vs Valores Reales ---
            plt.figure(figsize=(8, 6))
            sns.scatterplot(x=y_test, y=y_pred, alpha=0.6)
            plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--')  # Línea de referencia
            plt.title(f"{m_name} ({f_name})\nPredicciones vs Real (R2: {r2:.2f})")
            plt.xlabel("Valor Real")
            plt.ylabel("Predicción")
            plt.tight_layout()
            plt.savefig(f"metricas/{m_name}_{f_name}/pred_vs_real.png")
            plt.close()

            # --- Gráfico 2: Distribución de Errores ---
            errores = y_test - y_pred
            plt.figure(figsize=(8, 6))
            sns.histplot(errores, kde=True, bins=30)
            plt.title(f"{m_name} ({f_name})\nDistribución de Errores (MAE: {mae:.2f})")
            plt.xlabel("Error (Real - Predicción)")
            plt.tight_layout()
            plt.savefig(f"metricas/{m_name}_{f_name}/distribucion_errores.png")
            plt.close()

            # --- Feature Importance (si aplica) ---
            if hasattr(modelo, "feature_importances_"):
                importancia = modelo.feature_importances_
                plt.figure(figsize=(8, 4))
                sns.barplot(
                    x=importancia, 
                    y=features, 
                    hue=features,  # Asignamos `hue` para usar `palette`
                    palette="viridis", 
                    legend=False  # Desactivamos la leyenda (redundante)
                )
                plt.title(f"Feature Importance - {m_name} ({f_name})")
                plt.tight_layout()
                plt.savefig(f"metricas/{m_name}_{f_name}/feature_importance.png")
                plt.close()

    # --- Gráfico 3: Comparativa Global de Modelos ---
    df_metricas = pd.DataFrame(metricas_comparativas)
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df_metricas, x="Modelo", y="R2", hue="Feature Set", palette="rocket")
    plt.title("Comparativa de R2 entre Modelos y Feature Sets")
    plt.ylim(0, 1)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig("metricas/comparativa_r2.png")
    plt.close()
    
    # Seleccionar columnas relevantes (características y variable objetivo)
    relevant_columns = ["X", "Y", "Z", "Magnitud", "Dias Restantes"]
    correlation_data = df[relevant_columns]
    
    # Calcular matriz de correlación
    correlation_matrix = correlation_data.corr()
    
    # Crear mapa de calor
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        correlation_matrix, 
        annot=True,  # Mostrar valores de correlación
        cmap="coolwarm",  # Esquema de color
        vmin=-1, vmax=1,  # Rango de valores
        fmt=".2f",  # Formato de números (2 decimales)
        linewidths=0.5,  # Grosor de líneas separadoras
        square=True  # Celdas cuadradas
    )
    plt.title("Mapa de Calor de Correlaciones", fontsize=16)
    plt.tight_layout()
    
    # Guardar visualización
    plt.savefig("metricas/correlation_heatmap.png", dpi=300)
    plt.close()
    
    print("Mapa de calor de correlaciones creado en 'visualizaciones/correlation_heatmap.png'")
    
    # Mostrar las correlaciones con la variable objetivo ordenadas por magnitud
    target_correlations = correlation_matrix["Dias Restantes"].drop("Dias Restantes").sort_values(ascending=False)
    print("\nCorrelaciones con 'Dias Restantes':")
    for feature, corr in target_correlations.items():
        print(f"{feature}: {corr:.4f}")