#!/usr/bin/env bash


stellar contract upload \
  --wasm target/wasm32v1-none/release/lunarxy_token.wasm \
  --source <admin-secret-key> \
  --network testnet