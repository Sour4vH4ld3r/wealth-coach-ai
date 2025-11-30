#!/bin/bash

# ============================================================================
# Wealth Coach AI - Endpoint Testing Script
# Tests various endpoints to identify 502 Bad Gateway issues
# ============================================================================

API_BASE="https://api.wealthwarriorshub.in"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "================================================"
echo "Wealth Coach AI - Endpoint Testing"
echo "================================================"
echo ""

# Function to test endpoint
test_endpoint() {
    local method=$1
    local path=$2
    local data=$3
    local desc=$4
    local max_time=$5

    echo -n "Testing: $desc ... "

    if [ "$method" = "GET" ]; then
        response=$(curl -X GET "$API_BASE$path" \
            -w "\n%{http_code}|%{time_total}" \
            -s --max-time 30 2>&1)
    else
        response=$(curl -X POST "$API_BASE$path" \
            -H 'Content-Type: application/json' \
            -d "$data" \
            -w "\n%{http_code}|%{time_total}" \
            -s --max-time 30 2>&1)
    fi

    # Extract status code and time
    status=$(echo "$response" | tail -1 | cut -d'|' -f1)
    time=$(echo "$response" | tail -1 | cut -d'|' -f2)
    body=$(echo "$response" | head -n -1)

    # Check result
    if [ "$status" = "200" ] || [ "$status" = "201" ]; then
        if (( $(echo "$time > $max_time" | bc -l) )); then
            echo -e "${YELLOW}SLOW${NC} (${time}s > ${max_time}s) - Status: $status"
        else
            echo -e "${GREEN}OK${NC} (${time}s) - Status: $status"
        fi
    elif [ "$status" = "502" ]; then
        echo -e "${RED}502 BAD GATEWAY${NC} - Time: ${time}s"
        echo "  Response: $body"
    elif [ "$status" = "401" ] || [ "$status" = "403" ]; then
        echo -e "${YELLOW}AUTH REQUIRED${NC} (${time}s) - Status: $status (expected)"
    else
        echo -e "${RED}FAILED${NC} - Status: $status, Time: ${time}s"
        echo "  Response: $body"
    fi

    sleep 1
}

echo "=== PUBLIC ENDPOINTS (No Auth Required) ==="
echo ""

test_endpoint "GET" "/health" "" "Health Check" 1
test_endpoint "GET" "/api/v1/health" "" "API Health Check" 1
test_endpoint "GET" "/api/v1/health/detailed" "" "Detailed Health Check" 2
test_endpoint "POST" "/api/v1/auth/send-otp" '{"mobile_number": "9999999999"}' "Send OTP" 2

echo ""
echo "=== PROTECTED ENDPOINTS (Auth Required - Expect 401) ==="
echo ""

test_endpoint "GET" "/api/v1/users/me" "" "Get User Profile" 1
test_endpoint "GET" "/api/v1/chat/sessions" "" "Get Chat Sessions" 1
test_endpoint "POST" "/api/v1/chat/message" '{"message": "test"}' "Send Chat Message (triggers RAG)" 15
test_endpoint "GET" "/api/v1/allocations" "" "Get Allocations" 1
test_endpoint "GET" "/api/v1/transactions" "" "Get Transactions" 1

echo ""
echo "=== STRESS TEST - Multiple Rapid Requests ==="
echo ""

for i in {1..10}; do
    echo -n "Request $i: "
    curl -X GET "$API_BASE/health" \
        -w "Status: %{http_code} | Time: %{time_total}s\n" \
        -s -o /dev/null
    sleep 0.5
done

echo ""
echo "================================================"
echo "Testing Complete"
echo "================================================"
echo ""
echo "Common Issues:"
echo "- 502 errors: Backend timeout or crash"
echo "- Slow responses (>5s): Resource loading issues"
echo "- 401/403: Authentication required (expected for protected endpoints)"
echo ""
