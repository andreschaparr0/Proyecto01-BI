import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import requests
import json

app = dash.Dash(__name__)
server = app.server
app.title = "Clasificador de Noticias"

app.layout = html.Div(
    style={
        "fontFamily": "Arial, sans-serif",
        "backgroundColor": "#f4f4f4",
        "padding": "40px",
        "display": "flex",
        "justifyContent": "center",
    },
    children=[
        html.Div(
            style={
                "backgroundColor": "#fff",
                "padding": "30px",
                "borderRadius": "10px",
                "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)",
                "width": "600px",
            },
            children=[
                html.H1(
                    "Clasificador de Noticias",
                    style={"textAlign": "center", "color": "#333"},
                ),
                html.P(
                    "Bienvenido/a a esta herramienta de verificación de noticias. "
                    "Aquí podrás ingresar el título y la descripción de una noticia para saber si es verdadera o falsa. "
                    "Ideal para detectar desinformación de forma rápida y sencilla.",
                    style={
                        "textAlign": "center",
                        "color": "#555",
                        "fontSize": "16px",
                        "marginTop": "10px",
                        "marginBottom": "30px",
                    },
                ),
                html.Label("Título", style={"marginTop": "20px", "fontWeight": "bold"}),
                dcc.Input(
                    id="input-titulo",
                    type="text",
                    placeholder="Escribe el título aquí...",
                    style={
                        "width": "100%",
                        "padding": "10px",
                        "marginTop": "5px",
                        "borderRadius": "5px",
                        "border": "1px solid #ccc",
                    },
                ),
                html.Label(
                    "Descripción", style={"marginTop": "20px", "fontWeight": "bold"}
                ),
                dcc.Textarea(
                    id="input-descripcion",
                    placeholder="Escribe la descripción aquí...",
                    style={
                        "width": "100%",
                        "height": "120px",
                        "padding": "10px",
                        "marginTop": "5px",
                        "borderRadius": "5px",
                        "border": "1px solid #ccc",
                        "resize": "none",
                    },
                ),
                html.Button(
                    "Predecir",
                    id="predict-button",
                    n_clicks=0,
                    style={
                        "marginTop": "20px",
                        "padding": "10px 20px",
                        "backgroundColor": "#4CAF50",
                        "color": "white",
                        "border": "none",
                        "borderRadius": "5px",
                        "cursor": "pointer",
                        "fontWeight": "bold",
                    },
                ),
                html.Div(
                    id="output-pred",
                    style={
                        "marginTop": "30px",
                        "fontSize": "22px",
                        "fontWeight": "bold",
                        "color": "#333",
                        "textAlign": "center",
                    },
                ),
                # 🧾 Ejemplos
                html.Div(
                    id="ejemplos",
                    style={"marginTop": "40px"},
                    children=[
                        html.H3(
                            "🧾 Ejemplos de noticias",
                            style={"textAlign": "center", "color": "#444"},
                        ),
                        html.Div(
                            style={
                                "display": "flex",
                                "justifyContent": "space-between",
                                "gap": "20px",
                                "marginTop": "20px",
                            },
                            children=[
                                html.Div(
                                    style={
                                        "backgroundColor": "#ffe5e5",
                                        "padding": "20px",
                                        "borderRadius": "10px",
                                        "width": "48%",
                                        "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
                                        "borderLeft": "5px solid #e53935",
                                    },
                                    children=[
                                        html.H4(
                                            "❌ Noticia Falsa",
                                            style={"color": "#b71c1c"},
                                        ),
                                        html.P("Título:", style={"fontWeight": "bold"}),
                                        html.P(
                                            "FAC se vuelca con Mónica Oltra en su reaparición en los juzgados mientras Susana Díaz se pone de perfil"
                                        ),
                                        html.P(
                                            "Descripción:", style={"fontWeight": "bold"}
                                        ),
                                        html.P(
                                            "La ex-vicepresidenta se reafirma en su inocencia en un exhaustivo interrogatorio del juez de más de cuatro horas."
                                        ),
                                    ],
                                ),
                                html.Div(
                                    style={
                                        "backgroundColor": "#e5ffe5",
                                        "padding": "20px",
                                        "borderRadius": "10px",
                                        "width": "48%",
                                        "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
                                        "borderLeft": "5px solid #43a047",
                                    },
                                    children=[
                                        html.H4(
                                            "✅ Noticia Verdadera",
                                            style={"color": "#2e7d32"},
                                        ),
                                        html.P("Título:", style={"fontWeight": "bold"}),
                                        html.P(
                                            "'Si no te duele, no eres de izquierdas'"
                                        ),
                                        html.P(
                                            "Descripción:", style={"fontWeight": "bold"}
                                        ),
                                        html.P(
                                            "El portavoz de ERC en el Congreso, Gabriel Rufián, presenta su libro Ser de izquierdas es ser el último de la fila (y saberlo), donde reflexiona sobre los retos, el pasado, presente y futuro de la izquierda y su relación con el republicanismo catalán."
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
                # Reentrenamiento
                html.Hr(style={"marginTop": "50px"}),
                html.H3(
                    "🛠 Reentrenar el modelo con nuevas noticias",
                    style={"textAlign": "center", "color": "#333"},
                ),
                html.P(
                    "Pega aquí una lista en formato JSON con nuevas noticias y sus etiquetas (Label: 0 para falsa, 1 para verdadera):",
                    style={"color": "#555", "fontSize": "15px"},
                ),
                dcc.Textarea(
                    id="train-json-input",
                    placeholder='[\n  {\n    "ID": "001",\n    "Titulo": "Ejemplo",\n    "Descripcion": "Contenido",\n    "Fecha": "2025-03-27",\n    "Label": 1\n  }\n]',
                    style={
                        "width": "100%",
                        "height": "200px",
                        "padding": "10px",
                        "borderRadius": "5px",
                        "border": "1px solid #ccc",
                        "marginTop": "10px",
                    },
                ),
                html.Button(
                    "Reentrenar modelo",
                    id="train-button",
                    n_clicks=0,
                    style={
                        "marginTop": "15px",
                        "padding": "10px 20px",
                        "backgroundColor": "#1976D2",
                        "color": "white",
                        "border": "none",
                        "borderRadius": "5px",
                        "cursor": "pointer",
                        "fontWeight": "bold",
                    },
                ),
                html.Div(
                    id="train-output",
                    style={
                        "marginTop": "20px",
                        "color": "#333",
                        "textAlign": "center",
                        "fontWeight": "bold",
                    },
                ),
                # Múltiples noticias
                html.Hr(style={"marginTop": "50px"}),
                html.H3(
                    "📥 Predecir múltiples noticias",
                    style={"textAlign": "center", "color": "#333"},
                ),
                html.P(
                    "Pega aquí un arreglo de objetos en formato JSON con noticias para predecir:",
                    style={"color": "#555", "fontSize": "15px"},
                ),
                dcc.Textarea(
                    id="multi-json-input",
                    placeholder='[\n  {\n    "ID": "002",\n    "Titulo": "Ejemplo",\n    "Descripcion": "Texto...",\n    "Fecha": "2025-03-27"\n  }\n]',
                    style={
                        "width": "100%",
                        "height": "200px",
                        "padding": "10px",
                        "borderRadius": "5px",
                        "border": "1px solid #ccc",
                        "marginTop": "10px",
                    },
                ),
                html.Button(
                    "Predecir múltiples",
                    id="multi-predict-button",
                    n_clicks=0,
                    style={
                        "marginTop": "15px",
                        "padding": "10px 20px",
                        "backgroundColor": "#FF9800",
                        "color": "white",
                        "border": "none",
                        "borderRadius": "5px",
                        "cursor": "pointer",
                        "fontWeight": "bold",
                    },
                ),
                html.Div(
                    id="multi-output",
                    style={
                        "marginTop": "20px",
                        "color": "#333",
                        "textAlign": "left",
                        "whiteSpace": "pre-wrap",
                        "fontSize": "16px",
                        "lineHeight": "1.6",
                    },
                ),
            ],
        )
    ],
)

# ==================== Callbacks ====================


@app.callback(
    Output("output-pred", "children"),
    Input("predict-button", "n_clicks"),
    State("input-titulo", "value"),
    State("input-descripcion", "value"),
)
def update_prediction(n_clicks, titulo, descripcion):
    if n_clicks == 0 or not titulo or not descripcion:
        return ""
    try:
        response = requests.post(
            "http://127.0.0.1:8000/predict",
            json={
                "ID": "1",
                "Titulo": titulo,
                "Descripcion": descripcion,
                "Fecha": "2025-03-27",
            },
        )
        data = response.json()
        pred = data["predictions"][0]
        return f"🔎 Predicción: {'✅ Noticia verdadera' if pred == 1 else '❌ Noticia falsa'}"
    except Exception as e:
        return f"⚠️ Error: {str(e)}"


@app.callback(
    Output("train-output", "children"),
    Input("train-button", "n_clicks"),
    State("train-json-input", "value"),
)
def reentrenar_modelo(n_clicks, raw_json):
    if n_clicks == 0 or not raw_json:
        return ""
    try:
        data = json.loads(raw_json)
        response = requests.post("http://127.0.0.1:8000/train", json=data)
        result = response.json()

        if "metrics" in result:
            metrics = result["metrics"]
            return (
                f"✅ Reentrenamiento completo.\n"
                f"📊 Métricas del modelo:\n"
                f"  - 🎯 Accuracy: {metrics['accuracy']:.2f}\n"
                f"  - 🎭 Precision: {metrics['precision']:.2f}\n"
                f"  - 🔄 Recall: {metrics['recall']:.2f}\n"
                f"  - ⚖️ F1-score: {metrics['f1_score']:.2f}"
            )

        return f"⚠️ Respuesta inesperada: {result}"
    
    except Exception as e:
        return f"❌ Error en el reentrenamiento: {str(e)}"


@app.callback(
    Output("multi-output", "children"),
    Input("multi-predict-button", "n_clicks"),
    State("multi-json-input", "value"),
)
def predict_multiple(n_clicks, raw_json):
    if n_clicks == 0 or not raw_json:
        return ""
    try:
        data = json.loads(raw_json)
        response = requests.post("http://127.0.0.1:8000/predict", json=data)
        result = response.json()
        predicciones = result.get("predictions", [])
        salida = [
            f"📰 Noticia {i+1}: {'✅ Verdadera' if p == 1 else '❌ Falsa'}"
            for i, p in enumerate(predicciones)
        ]
        return "\n".join(salida)
    except Exception as e:
        return f"⚠️ Error: {str(e)}"


# ==================== Run App ====================

if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
