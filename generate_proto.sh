#!/usr/bin/env bash
set -euo pipefail

PROTO_DIR="./proto"
OUT_DIR="./steampy/generated"

mkdir -p "$OUT_DIR"

python -m grpc_tools.protoc \
  -I="$PROTO_DIR" \
  --python_out="$OUT_DIR" \
  --pyi_out="$OUT_DIR" \
  $(find "$PROTO_DIR" -name "*.proto")
