import pandas as pd
import re
import unicodedata
import contractions
from sklearn.feature_extraction.text import CountVectorizer
from joblib import load
import string
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from joblib import dump
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)
from joblib import dump
from sklearn.model_selection import train_test_split
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer


def to_lowercase(words):
    return [word.lower() for word in words]


def replace_numbers(words):
    return ["NUM" if word.isdigit() else word for word in words]


def remove_punctuation(words):
    return [word.translate(str.maketrans("", "", string.punctuation)) for word in words]


def remove_non_ascii(words):
    return ["".join(char for char in word if ord(char) < 128) for word in words]


def remove_stopwords(words):
    stopwords = {
        "lo",
        "sus",
        "este",
        "esta",
        "como",
        "no",
        "mas",
        "del",
        "para",
        "se",
        "al",
        "su",
        "ha",
        "que",
        "el",
        "la",
        "los",
        "las",
        "de",
        "y",
        "en",
        "a",
        "un",
        "una",
        "es",
        "por",
        "con",
        "the",
    }  # Agrega más si es necesario
    return [word for word in words if word not in stopwords]


def preprocessing(words):
    words = to_lowercase(words)
    words = replace_numbers(words)
    words = remove_punctuation(words)
    words = remove_non_ascii(words)
    words = remove_stopwords(words)
    return words


def tokenizar_texto(df):
    df["Tokens_Titulo"] = df["Titulo"].astype(str).apply(lambda x: x.split())
    df["Tokens_Descripcion"] = df["Descripcion"].astype(str).apply(lambda x: x.split())
    return df


abreviaciones = {
    "q": "que",
    "xq": "porque",
    "d": "de",
    "tb": "también",
    "mñn": "mañana",
    "uds": "ustedes",
    "pa": "para",
    "st": "esto",
    "ntp": "no te preocupes",
    "msj": "mensaje",
}


def limpiar_texto(texto):
    cambios = 0  # Contador de cambios
    if pd.notnull(texto):
        original = texto  # Guardar el texto original
        texto = texto.lower()
        texto = "".join(
            c
            for c in unicodedata.normalize("NFD", texto)
            if unicodedata.category(c) != "Mn"
        )

        palabras = texto.split()
        nuevas_palabras = []
        for p in palabras:
            if p in abreviaciones:
                cambios += 1  # Contar si hubo un cambio
            nuevas_palabras.append(abreviaciones.get(p, p))
        texto = " ".join(nuevas_palabras)

        texto = re.sub(r"[^a-zA-Z\s]", "", texto)

        if texto != original:
            cambios += 1  # Contar si hubo otro cambio en la limpieza final

        return texto, cambios
    return texto, 0


def convertir_a_vector_binario(x_data_text, vocabulario):
    """
    Convierte una lista de textos en una matriz binaria donde cada entrada representa
    la presencia (1) o ausencia (0) de palabras de x_data_text.

    :param x_data_text: Lista con todas las palabras del vocabulario (en un solo string).
    :param x_datos_text: Lista de strings con textos a convertir en vectores binarios.
    :return: Lista de listas binarias representando la presencia de palabras.
    """
    vocabulario = set(x_data_text.split())

    def texto_a_binario(texto):
        palabras_texto = set(texto.split())
        return [1 if palabra in palabras_texto else 0 for palabra in vocabulario]

    matriz_binaria = [texto_a_binario(texto) for texto in vocabulario]

    return matriz_binaria, list(vocabulario)


def FiltrarTexto(df):
    texto = df.copy()
    texto.dropna(inplace=True)
    texto.drop_duplicates(inplace=True)
    texto[["Titulo", "Cambios_Titulo"]] = texto["Titulo"].apply(
        lambda x: pd.Series(limpiar_texto(x))
    )
    texto[["Descripcion", "Cambios_Descripcion"]] = texto["Descripcion"].apply(
        lambda x: pd.Series(limpiar_texto(x))
    )
    texto["Titulo"] = texto["Titulo"].apply(contractions.fix)
    texto["Descripcion"] = texto["Descripcion"].apply(contractions.fix)
    texto = tokenizar_texto(texto)
    texto["Tokens_Titulo_Sin_Ruido"] = texto["Tokens_Titulo"].apply(preprocessing)
    texto["Tokens_Descripcion_Sin_Ruido"] = texto["Tokens_Descripcion"].apply(
        preprocessing
    )
    texto["Tokens_Combinados_Sin_Ruido"] = (
        texto["Tokens_Titulo_Sin_Ruido"] + texto["Tokens_Descripcion_Sin_Ruido"]
    )
    texto["Tokens_Combinados_Sin_Ruido"] = texto["Tokens_Combinados_Sin_Ruido"].apply(
        lambda x: sorted(set(x), key=x.index)
    )
    x_datos = texto["Tokens_Combinados_Sin_Ruido"]
    x_datos_text = [
        " ".join(words) if isinstance(words, list) else str(words) for words in x_datos
    ]
    return x_datos_text


def entrenar_modelo():
    # Cargar los datos
    EXCEL_PATH = "tokens_combinados_label.xlsx"
    df = pd.read_excel(EXCEL_PATH)

    # Descomentar en caso de que se quiera reducir los datos de
    # entrenamiento para que no dure tanto el entrenamiento

    df = df.iloc[: len(df) // 10]
    df.to_excel(EXCEL_PATH, index=False)

    # Filtrar y preparar datos
    x_data = FiltrarTexto(df)
    vectorizer = CountVectorizer(binary=True)
    x_data = vectorizer.fit_transform(x_data)
    y_data = df["Label"]

    # Dividir en conjunto de entrenamiento y prueba (90%-10%)
    x_train, x_test, y_train, y_test = train_test_split(
        x_data, y_data, test_size=0.1, random_state=42
    )

    # Entrenar el modelo RandomForest
    modelo = RandomForestClassifier(n_estimators=200, max_depth=None, random_state=42)
    modelo.fit(x_train, y_train)

    # Hacer predicciones en el conjunto de prueba
    y_pred = modelo.predict(x_test)

    # Calcular métricas de evaluación
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average="weighted")
    recall = recall_score(y_test, y_pred, average="weighted")
    f1 = f1_score(y_test, y_pred, average="weighted")
    matriz_confusion = confusion_matrix(y_test, y_pred)

    # Imprimir métricas
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1-score: {f1:.4f}")
    print("Matriz de Confusión:")
    print(matriz_confusion)

    # Guardar el modelo entrenado
    dump(modelo, "RandomForest.joblib")
    dump(vectorizer, "vectorizer.joblib")
    print(
        "El modelo ha sido exportado como 'RandomForest.joblib' en el directorio actual."
    )


# Descomentar y correr por primera vez para que se carguen los modelos en el directorio actual
entrenar_modelo()
