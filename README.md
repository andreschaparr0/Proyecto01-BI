# Proyecto01-BI

## Video FASE 2
https://youtu.be/8iGxXS5rUCY

## Pasos para ejecutar la aplicación
1) Primero se debe ejecutar el archivo utils.py ya que en este se carga el modelo joblib al computador local ya que este pesa mucho para subirse a github, por lo tanto para la primera vez que se vaya a correr se debe descomentar la linea 238 para ejecutar el archivo, despues de que se ejecute se **debe volver a comentar** esta linea.
2) Segundo se ejecuta el archivo main con el comando uvicorn main:app --reload para que la API este lista.
3) Por ultimo, se corre el dashboard.app como un archivo de python normal, se abre en el buscador la dirección dada por el terminal y se prueba con los archivos de prueba.

### Tip
Si Se quiere correr en menor tiempo se recomienda en el paso 1 correr utils.py descomentando la linea 193 que hace que los datos de entrenamiento se reduzcan en una decima parte ya que si se corre con todos los 56 mil datos se demora alrededor de 15 minutos en entrenar al modelo y lo mismo en reentrenarlo.