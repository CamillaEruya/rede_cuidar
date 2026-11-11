#!/bin/sh
set -eu

: "${DB_USERNAME:?Defina DB_USERNAME no .env do backend}"
: "${DB_PASSWORD:?Defina uma senha em DB_PASSWORD no .env do backend}"
: "${DB_DATABASE:?Defina DB_DATABASE no .env do backend}"

export MARIADB_DATABASE="$DB_DATABASE"
export MARIADB_ROOT_PASSWORD="$DB_PASSWORD"

if [ "$DB_USERNAME" = "root" ]; then
    export MARIADB_ROOT_HOST='%'
    unset MARIADB_USER MARIADB_PASSWORD
else
    export MARIADB_USER="$DB_USERNAME"
    export MARIADB_PASSWORD="$DB_PASSWORD"
fi

# Generate SQL instead of executing a mounted .sh: on Windows/WSL mounted
# scripts may be executable and run outside the official entrypoint's shell.
if [ ! -d /var/lib/mysql/mysql ]; then
    sed -e '/^CREATE DATABASE /d' -e '/^USE /d' \
        /opt/rede-cuidar/dump.sql > /docker-entrypoint-initdb.d/01-import.sql
else
    # Apply the .env credentials even when the data volume already exists.
    # init-file runs locally before the server accepts external connections.
    sql_user=$(printf '%s' "$DB_USERNAME" | sed "s/'/''/g")
    sql_password=$(printf '%s' "$DB_PASSWORD" | sed "s/'/''/g")
    sql_database=$(printf '%s' "$DB_DATABASE" | sed 's/`/``/g')
    umask 077
    cat > /tmp/rede-cuidar-credentials.sql <<EOF
SET SESSION sql_mode='NO_BACKSLASH_ESCAPES';
CREATE DATABASE IF NOT EXISTS \`$sql_database\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '$sql_user'@'%' IDENTIFIED BY '$sql_password';
ALTER USER '$sql_user'@'%' IDENTIFIED BY '$sql_password';
GRANT ALL PRIVILEGES ON \`$sql_database\`.* TO '$sql_user'@'%';
EOF
    if [ "$DB_USERNAME" = "root" ]; then
        printf "ALTER USER 'root'@'localhost' IDENTIFIED BY '%s';\n" "$sql_password" >> /tmp/rede-cuidar-credentials.sql
    fi
    chown mysql:mysql /tmp/rede-cuidar-credentials.sql
    set -- "$@" --init-file=/tmp/rede-cuidar-credentials.sql
fi

exec /usr/local/bin/docker-entrypoint.sh "$@"
