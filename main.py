import os
import pickle
import pandas as pd
import GetDailyconsum as gdc
import training_model as model

class Main:
    def __init__(self):
        self.name = "Main Class"
        self.options = {
            '1': self.option1,
            '2': self.option2,
            '3': self.option3,
            '0': self.exit,
        }
        self.running = True
        self.dataset = "datasets/datos_procesados.csv"
        
    def option1(self):
        # Código para crear dataset
        pct = gdc.gdc()
        
    def option2(self):
        # Código para entrenar modelo
        model.create_model()
    
    def option3(self):
        model.create_metrics()
        
    def option4(self):
        model = input("Selecciona el modelo a usar (LinearRegression, RandomForest, KNN, DecisionTree, SVM): ")
        if model not in ["LinearRegression", "RandomForest", "KNN", "DecisionTree", "SVM"]:
            print("Modelo no válido.")
            return
        
        # Cargar el modelo
        model_path = f"models/{model}.pkl"
        if not os.path.exists(model_path):
            print(f"Modelo {model} no encontrado.")
            return
        with open(model_path, 'rb') as f:
            loaded_model = pickle.load(f)

    def exit(self):
        self.running = False

    def show_menu(self):
        print("\n")
        print("1. Obtener consumo diario")
        print("2. Entrenar modelo")
        print("3. Usar modelo")
        print("0. Salir")

    def run(self):
        while self.running:
            self.show_menu()
            choice = input("Selecciona una opción: ")
            action = self.options.get(choice)
            if action:
                action()
            else:
                print("Opción no válida.")

if __name__ == "__main__":
    app = Main()
    app.run()