#!/bin/bash

INSTANCE=$1
PORT=$2

if [ -z "$INSTANCE" ] || [ -z "$PORT" ]; then
    echo "Usage: ./instance-deploy.sh <instance-id> <api-port>"
    exit 1
fi

ENV_FILE=".env-$INSTANCE"
DATA_DIR="instance_data/$INSTANCE/db"

cp .env-template $ENV_FILE
sed -i "s/^INSTANCE_ID=.*/INSTANCE_ID=$INSTANCE/" $ENV_FILE
sed -i "s/^API_PORT=.*/API_PORT=$PORT/" $ENV_FILE
sed -i "s/^DOMAIN=.*/DOMAIN=$INSTANCE.macrovention.com/" $ENV_FILE

mkdir -p $DATA_DIR

docker compose --env-file $ENV_FILE up -d --build
