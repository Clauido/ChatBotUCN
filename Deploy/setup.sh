#!/bin/bash

#variables de entorno
SCRIPT_DIR=$(dirname "$0")
if [ -f .env ]; then
    set -o allexport
    source .env
    set +o allexport
fi

if [[ -z "$PGV_USER" || -z "$PGV_PASSWORD" || -z "$PGV_HOST" || -z "$PGV_PORT" || -z "$PGV_DATABASE_NAME" || -z "$MODEL_NAME" ]]; then
    echo "Faltan variables de entorno necesarias. Asegúrate de que .env está correctamente configurado."
    exit 1
fi


#Consideraciones:
#Debes de tener ollama en "sirviendo" ollama serve
#Debes de tener el archivo "Modelfile" en el mismo directorio que el .sh
#Sugerencia: crear un entorno python


##Crear el modelo "ucenin"

ollama create $MODEL_NAME --file $SCRIPT_DIR/Modelfile #En este directorio buscará por el Modelfile

#Levantar base de datos(Docker) - puedes hacer el docker - compose si gustas

docker run --name pgvector -e POSTGRES_USER=$PGV_USER -e POSTGRES_PASSWORD=$PGV_PASSWORD -e POSTGRES_DB=$PGV_DATABASE_NAME -p $PGV_PORT:5432 -d pgvector/pgvector:pg16

##Descargar dependencias para poblar la bd y la api

pip install -r "$SCRIPT_DIR/requirements.txt" 

##Poblar BD

python "$SCRIPT_DIR/poblate.py"

##Iniciar API

python "$SCRIPT_DIR/Ucenin.py"