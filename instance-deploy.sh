#!/bin/bash

INSTANCE=$1
PORT=$2
PROTOCOL=${3:-http}  # optional: http (default) or https

if [ -z "$INSTANCE" ] || [ -z "$PORT" ]; then
    echo "Usage: ./instance-deploy.sh <instance-id> <api-port> [http|https]"
    exit 1
fi

ENV_FILE=".env-$INSTANCE"
DATA_DIR="instance_data/$INSTANCE/db"
DIST_DIR="instance_data/$INSTANCE/dist"
DOMAIN="$INSTANCE.macrovention.com"
API_BASE_URL="$PROTOCOL://$DOMAIN/api"

echo "💡 Deploying instance: $INSTANCE"
echo "🌍 API Base URL: $API_BASE_URL"
echo "📦 Port: $PORT"

# 1️⃣ Prepare .env file
cp .env-template $ENV_FILE
sed -i "s/^INSTANCE_ID=.*/INSTANCE_ID=$INSTANCE/" $ENV_FILE
sed -i "s/^API_PORT=.*/API_PORT=$PORT/" $ENV_FILE
sed -i "s/^DOMAIN=.*/DOMAIN=$DOMAIN/" $ENV_FILE

# 2️⃣ Ensure instance folders
mkdir -p $DATA_DIR
mkdir -p $DIST_DIR

# 3️⃣ Build frontend with isolated output folder
echo "🔧 Building frontend for $INSTANCE..."
cd esg_frontend
OUT_DIR=../instance_data/$INSTANCE/dist VITE_API_BASE_URL="$API_BASE_URL" npx vite build
cd ..

# 4️⃣ Start Docker container with shared image
echo "🚀 Starting Docker container for $INSTANCE..."
docker compose -p $INSTANCE --env-file $ENV_FILE up -d

echo "✅ Deployment finished for $INSTANCE!"
