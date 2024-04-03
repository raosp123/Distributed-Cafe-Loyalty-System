#!/bin/bash

docker compose down

sudo rm -rf pgdata pgdata-replica #pgdata-shard

sleep 2

docker compose up -d