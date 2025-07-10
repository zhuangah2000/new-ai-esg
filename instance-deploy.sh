#!/bin/bash

INSTANCE=$1
PORT=$2
PROTOCOL=${3:-http}  # optional third argument: http (default) or https

if [ -z "$INSTANCE" ] || [ -z "$PORT" ]; then
    echo "Usage: ./instance-deploy.sh <instance-id> <api-port> [http|https]"
    exit 1
fi

ENV_FILE=".env-$INSTANCE"
DATA_DIR="instance_data/$INSTANCE/db"
DIST_DIR="instance_data/$INSTANCE/dist"
DOMAIN="$INSTANCE.macrovention.com"
API_BASE_URL="$PROTOCOL://$DOMAIN/api"

# 1. Generate instance-specific env file
cp .env-template $ENV_FILE
sed -i "s/^INSTANCE_ID=.*/INSTANCE_ID=$INSTANCE/" $ENV_FILE
sed -i "s/^API_PORT=.*/API_PORT=$PORT/" $ENV_FILE
sed -i "s/^DOMAIN=.*/DOMAIN=$DOMAIN/" $ENV_FILE

# 2. Make sure db and dist directories exist
mkdir -p $DATA_DIR
mkdir -p $DIST_DIR

# 3. Build frontend with correct API URL
echo "🔧 Building frontend for $INSTANCE with API_BASE_URL: $API_BASE_URL"
cd esg_frontend
VITE_API_BASE_URL="$API_BASE_URL" npm run build

# Copy built frontend to instance-specific folder
cd ..
rm -rf $DIST_DIR
cp -r esg_frontend/dist $DIST_DIR

# 4. Deploy with Docker Compose
echo "🐳 Deploying instance '$INSTANCE' on port $PORT with Docker..."
docker compose --env-file $ENV_FILE up -d --build
