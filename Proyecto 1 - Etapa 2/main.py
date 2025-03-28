from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from joblib import load
import uvicorn
from utils import FiltrarTexto
from joblib import dump
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.model_selection import train_test_split
from typing import Union
import streamlit as st
import json
import requests

# Cargar el modelo previamente entrenado y exportado

EXCEL_PATH = "tokens_combinados_label.xlsx"
df_original = pd.read_excel(EXCEL_PATH)

MODEL_PATH = "RandomForest.joblib"
model = load(MODEL_PATH)

VECTORIZER_PATH = "vectorizer.joblib"
vectorizer = load(VECTORIZER_PATH)
# Definir la aplicación FastAPI
app = FastAPI()


# Definir el esquema de datos esperados en la solicitud
class DataModel(BaseModel):
    ID: str
    Titulo: str
    Descripcion: str
    Fecha: str

    def columns(self):
        return ["ID", "Titulo", "Descripcion", "Fecha"]


class TrainDataModel(DataModel):
    Label: int


# Endpoint de prueba
@app.get("/")
def home():
    return {"message": "API funcionando correctamente"}


@app.post("/predict")
def make_predictions(data: Union[DataModel, list[DataModel]]):
    try:
        if isinstance(data, DataModel):  # Si es un solo objeto, lo convertimos en lista
            data = [data]

        df = pd.DataFrame([item.dict() for item in data])
        texto, sobra = FiltrarTexto(df)
        print(texto)	
        texto_vectorizado = vectorizer.transform(texto)
        result = model.predict(texto_vectorizado)
        return {"predictions": result.tolist()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint para reentrenar el modelo
@app.post("/train")
def make_train_again(
    train_data: list[TrainDataModel],
):  # Recibe una lista de TrainDataModel
    try:

        df_nuevo = pd.DataFrame([item.dict() for item in train_data])
        columnas_comunes = df_original.columns.intersection(df_nuevo.columns)
        df_nuevo = df_nuevo[columnas_comunes]
        df_actualizado = pd.concat([df_original, df_nuevo], ignore_index=True)
        df_actualizado.to_excel(EXCEL_PATH, index=False)

        x_original, y_original = FiltrarTexto(df_original)

        x_nuevo, y_nuevo = FiltrarTexto(df_nuevo)

        x_completo = x_original + x_nuevo
        y_completo = pd.concat([y_original, y_nuevo], ignore_index=True)

        texto_vectorizado_completo = vectorizer.transform(x_completo)

        if len(x_completo) != len(y_completo):
            raise ValueError("El número de textos y etiquetas no coincide.")

        X_train, X_test, y_train, y_test = train_test_split(
            texto_vectorizado_completo, y_completo, test_size=0.2, random_state=42
        )

        model.fit(X_train, y_train)
        dump(model, MODEL_PATH)
        dump(vectorizer, VECTORIZER_PATH)

        # Hacer predicciones en el conjunto de prueba
        y_pred = model.predict(X_test)

        # Calcular métri~cas
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average="weighted")
        recall = recall_score(y_test, y_pred, average="weighted")
        f1 = f1_score(y_test, y_pred, average="weighted")
        return {
            "message": "Modelo reentrenado correctamente",
            "metrics": {
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1_score": f1,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
