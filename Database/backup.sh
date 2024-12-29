#!/bin/bash

#variables de entorno
#La base de datos debe de estar cargada y obviamente en ejecución

PG_VECTOR_CONTAINER_ID=d4a

SCRIPT_DIR=$(dirname "$0")
DUMP_DIR="$SCRIPT_DIR/Dump"      # Marca de tiempo para el archivo dump
DUMP_FILE="dump.sql"  


if [ -f "$SCRIPT_DIR/../.env" ]; then
    set -o allexport
    source "$SCRIPT_DIR/../.env"
    set +o allexport
fi

if [[ -z "$PGV_USER" || -z "$PGV_PASSWORD" || -z "$PGV_HOST" || -z "$PGV_PORT" || -z "$PGV_DATABASE_NAME" ]]; then
    echo "Faltan variables de entorno necesarias. Asegúrate de que .env está correctamente configurado."
    exit 1
fi

# Ejecutar pg_dump dentro del contenedor
echo "Realizando el backup de la base de datos '${PGV_DATABASE_NAME}'..."
docker exec "$PG_VECTOR_CONTAINER_ID" pg_dump -U "$PGV_USER" -d "$PGV_DATABASE_NAME" > "$DUMP_DIR/$DUMP_FILE"

# Verificar si el dump fue exitoso
if [ $? -eq 0 ]; then
    echo "Backup exitoso: $DUMP_DIR/$DUMP_FILE"
else
    echo "Error al realizar el backup de la base de datos."
    exit 1
fi

# Cuando usas source o . para cargar un script, este se ejecuta en el contexto del shell actual, y $0 se convierte en el nombre del intérprete de shell actual.