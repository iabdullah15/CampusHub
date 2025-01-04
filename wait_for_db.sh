#!/bin/bash
set -e

host="$1"
shift
cmd="$@"

echo "Waiting for MySQL to be ready..."

while ! mysqladmin ping -h "$host" --silent; do
    echo "Still waiting for MySQL..."
    sleep 2
done

echo "MySQL is ready! Executing command..."
exec $cmd
