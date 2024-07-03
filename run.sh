#!/bin/bash

echo "Spinning up docker..."
sleep 1

docker compose up --detach --build --force-recreate