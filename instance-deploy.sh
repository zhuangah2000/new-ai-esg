#!/bin/bash

INSTANCE=$1
PORT=$2
PROTOCOL=${3:-http}

if [ -z "$INSTANCE" ] || [ -z "$PORT" ]; then
    echo "Usage: ./instance-deploy.sh <instance-id> <api-port> [http|https]"
    exit 1
fi

ENV_FILE=".env-$INSTANCE"
DATA_DIR="instance_data/$INSTANCE/db"
DIST_DIR="instance_data/$INSTANCE/dist"
DOMAIN="$INSTANCE.macrovention.com"
API_BASE_URL="$PROTOCOL://$DOMAIN/api"

# 1️⃣ Create .env file
cp .env-template $ENV_FILE
sed -i "s/^INSTANCE_ID=.*/INSTANCE_ID=$INSTANCE/" $ENV_FILE
sed -i "s/^API_PORT=.*/API_PORT=$PORT/" $ENV_FILE
sed -i "s/^DOMAIN=.*/DOMAIN=$DOMAIN/" $ENV_FILE

# 2️⃣ Ensure db + dist folders
mkdir -p $DATA_DIR
mkdir -p $DIST_DIR

# 3️⃣ Build frontend
echo "🔧 Building frontend for $INSTANCE with API_BASE_URL=$API_BASE_URL"
cd esg_frontend
VITE_API_BASE_URL="$API_BASE_URL" npm run build
cd ..

# 4️⃣ Copy built frontend to instance folder
rm -rf $DIST_DIR
cp -r esg_frontend/dist $DIST_DIR

# 5️⃣ Build Docker image with build-arg
echo "🐳 Building Docker image for $INSTANCE"
docker compose --env-file $ENV_FILE build --build-arg INSTANCE_ID=$INSTANCE

# 6️⃣ Start the container
echo "🚀 Starting Docker container for $INSTANCE"
docker compose --env-file $ENV_FILE up -d
