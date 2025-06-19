#!/bin/sh
set -e

if [ "$MODE" = "app" ]; then
  spendymgr run -p $PORT -h $HOST
else
  echo "ERROR: \$MODE is not set to \"app\"."
  exit 1
fi
