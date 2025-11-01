#!/bin/bash
# -------------------------
# test url request setup
# -------------------------


# -------------------------
# CONFIG
# -------------------------
USERNAME="malina123"
PASSWORD="malina123"
API_URL="http://localhost:8000"
INGREDIENTS='["tomato","cheese"]'
# -------------------------

echo "Step 1: Get JWT token..."
TOKEN_RESPONSE=$(curl -s -X POST "$API_URL/api/token/" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}")

ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access'])")

if [ -z "$ACCESS_TOKEN" ]; then
  echo "Error: Could not retrieve access token!"
  echo "Response: $TOKEN_RESPONSE"
  exit 1
fi

echo "Got token: $ACCESS_TOKEN"
echo "Step 2: Call recommend_recipes_db endpoint..."

curl -X POST "$API_URL/recommend_recipes_db/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d "{\"ingredients\": $INGREDIENTS}"
