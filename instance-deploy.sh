#!/bin/bash

INSTANCE=$1
PORT=$2

if [ -z "$INSTANCE" ] || [ -z "$PORT" ]; then
    echo "Usage: ./instance-deploy.sh <instance-id> <api-port>"
    exit 1
fi

ENV_FILE=".env-$INSTANCE"
DATA_DIR="instance_data/$INSTANCE/db"
DOMAIN="$INSTANCE.macrovention.com"

# 1. Generate instance-specific env file
cp .env-template $ENV_FILE
sed -i "s/^INSTANCE_ID=.*/INSTANCE_ID=$INSTANCE/" $ENV_FILE
sed -i "s/^API_PORT=.*/API_PORT=$PORT/" $ENV_FILE
sed -i "s/^DOMAIN=.*/DOMAIN=$DOMAIN/" $ENV_FILE

# 2. Make sure db directory exists
mkdir -p $DATA_DIR

# 3. Build frontend with correct domain
echo "🔧 Building frontend with API endpoint: https://$DOMAIN/api"
cd esg_frontend
VITE_API_BASE_URL="http://$DOMAIN/api" npm run build
cd ..

# 4. Build and start docker
echo "🐳 Deploying $INSTANCE on port $PORT..."
docker compose --env-file $ENV_FILE up -d --build
