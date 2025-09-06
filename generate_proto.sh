#!/usr/bin/env bash
set -e

PROTO_DIR="./proto"
OUT_DIR="./generated"

# создаём директорию для сгенерированных файлов, если её ещё нет
mkdir -p "$OUT_DIR"

# находим все .proto и компилируем
python -m grpc_tools.protoc \
  -I="$PROTO_DIR" \
  --pyi_out=./generated \
  --python_out="$OUT_DIR" \
  $(find "$PROTO_DIR" -name "*.proto")
