# Proyecto01-BI

## Video FASE 2
https://youtu.be/8iGxXS5rUCY

## Pasos para ejecutar la aplicación
1) Primero se debe ejecutar el archivo utils.py ya que en este se carga el modelo joblib al computador local ya que este pesa mucho para subirse a github, por lo tanto para la primera vez que se vaya a correr se debe descomentar la linea 238 para ejecutar el archivo, despues de que se ejecute se **debe volver a comentar** esta linea.
2) Segundo se ejecuta el archivo main con el comando uvicorn main:app --reload para que la API este lista.
3) Por ultimo, se corre el dashboard.app como un archivo de python normal, se abre en el buscador la dirección dada por el terminal y se prueba con los archivos de prueba.
