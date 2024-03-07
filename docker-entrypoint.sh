#!/bin/bash

wait_for_postgis() {
    echo "Waiting for PostGIS to be ready..."
    while ! pg_isready -h $DATABASE_HOST -p $DATABASE_PORT -U $DATABASE_USER; do
        sleep 1
    done
}

check_dump_loaded() {
    echo "Checking if dump has already been loaded..."
    PGPASSWORD=$DATABASE_PASSWORD psql -h $DATABASE_HOST -p $DATABASE_PORT -U $DATABASE_USER -d $DATABASE_NAME -c "select 1 from pg_tables where tablename = 'dump_marker';" | grep -q 1
    return $?
}

load_database_dump() {
    echo "Loading database dump..."
    PGPASSWORD=$DATABASE_PASSWORD psql -h $DATABASE_HOST -p $DATABASE_PORT -U $DATABASE_USER -d $DATABASE_NAME -f /app/database_dump.sql
    PGPASSWORD=$DATABASE_PASSWORD psql -h $DATABASE_HOST -p $DATABASE_PORT -U $DATABASE_USER -d $DATABASE_NAME -c "CREATE TABLE dump_marker(id INT PRIMARY KEY, loaded TIMESTAMP DEFAULT CURRENT_TIMESTAMP);"
}

wait_for_postgis

if ! check_dump_loaded; then
    load_database_dump
else
    echo "Database dump has already been loaded."
fi

echo "Collecting static..."
python manage.py collectstatic
echo "Applying database migrations..."
python carebot/manage.py migrate

# Runs app start command
exec "$@"