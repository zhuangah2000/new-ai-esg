#!/bin/bash

INSTANCE=$1
PORT=$2
PROTOCOL=${3:-https}  # default to https if not passed

if [ -z "$INSTANCE" ] || [ -z "$PORT" ]; then
    echo "Usage: ./instance-deploy.sh <instance-id> <api-port> [http|https]"
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

# 2. Ensure db directory exists
mkdir -p $DATA_DIR

# 3. Build frontend with correct protocol
echo "🔧 Building frontend with API endpoint: $PROTOCOL://$DOMAIN/api"
cd esg_frontend
VITE_API_BASE_URL="$PROTOCOL://$DOMAIN/api" npm run build
cd ..

# 4. Start Docker
echo "🐳 Deploying $INSTANCE on port $PORT..."
docker compose --env-file $ENV_FILE up -d --build
