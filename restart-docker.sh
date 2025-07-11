#!/bin/bash

# restart-all.sh
# Restart Docker containers esg-kvc1021-backend to esg-kvc1030-backend

for i in {21..30}; do
  container="esg-kvc10$i-backend"
  echo "🔄 Restarting $container ..."
  docker restart $container
  if [ $? -eq 0 ]; then
    echo "✅ Successfully restarted $container"
  else
    echo "⚠️ Failed to restart $container"
  fi
done

echo "🎉 All restarts completed!"
