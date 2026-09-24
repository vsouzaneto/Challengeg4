#!/bin/sh
set -eu

PGDATA=/var/lib/postgresql/data
PGSOCKET=/run/postgresql
export DB_HOST=127.0.0.1
export DB_PORT=5432
export DB_NAME=lead_scorer
export DB_USER=lead_scorer
export DB_PASSWORD=lead_scorer
export DATA_DIR=/app/data
export PORT=3000
export COOKIE_SECURE=${COOKIE_SECURE:-false}

mkdir -p "$PGDATA" "$PGSOCKET"
chown -R postgres:postgres /var/lib/postgresql "$PGSOCKET"

if [ ! -s "$PGDATA/PG_VERSION" ]; then
    su-exec postgres initdb -D "$PGDATA" --auth-local=trust --auth-host=scram-sha-256
fi

su-exec postgres postgres -D "$PGDATA" -c listen_addresses='127.0.0.1' &
POSTGRES_PID=$!

until pg_isready -h 127.0.0.1 -p 5432 -U lead_scorer -d postgres >/dev/null 2>&1; do
    sleep 1
done

ROLE_EXISTS=$(su-exec postgres psql -d postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname = 'lead_scorer'")
if [ "$ROLE_EXISTS" != "1" ]; then
    su-exec postgres psql -d postgres -c "CREATE ROLE lead_scorer LOGIN PASSWORD 'lead_scorer'"
else
    su-exec postgres psql -d postgres -c "ALTER ROLE lead_scorer WITH LOGIN PASSWORD 'lead_scorer'"
fi

DATABASE_EXISTS=$(su-exec postgres psql -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname = 'lead_scorer'")
if [ "$DATABASE_EXISTS" != "1" ]; then
    su-exec postgres createdb -O lead_scorer lead_scorer
fi

cd /app/backend
npm run db:setup
npm start &
BACKEND_PID=$!

cd /app/frontend
npm run preview &
FRONTEND_PID=$!

shutdown() {
    trap - TERM INT
    kill -TERM "$POSTGRES_PID" "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
    wait "$POSTGRES_PID" "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
    exit 0
}

trap shutdown TERM INT

set +e
wait -n
STATUS=$?
set -e
kill -TERM "$POSTGRES_PID" "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
wait "$POSTGRES_PID" "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
exit "$STATUS"
