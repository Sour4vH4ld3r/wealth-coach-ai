#!/bin/bash

###############################################################################
# Wealth Coach AI Assistant - Query Testing Script
###############################################################################
# This script tests the API with various sample queries to demonstrate
# the AI assistant's financial advisory capabilities
###############################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"
API_KEY="${API_KEY:-dev-key-12345}"

# Check if server is running
check_server() {
    echo -e "${YELLOW}Checking if server is running...${NC}"
    if curl -s "${API_BASE_URL}/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Server is running${NC}"
        echo ""
        return 0
    else
        echo -e "${RED}✗ Server is not running!${NC}"
        echo "Start the server with: ./start.sh"
        exit 1
    fi
}

# Function to print section header
print_header() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║ $1${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Function to run a query
run_query() {
    local query="$1"
    local description="$2"

    echo -e "${CYAN}Question: ${NC}${query}"
    echo -e "${YELLOW}Testing: ${description}${NC}"
    echo ""

    response=$(curl -s -X POST "${API_BASE_URL}/api/v1/chat/message" \
        -H "Content-Type: application/json" \
        -H "X-API-Key: ${API_KEY}" \
        -d "{\"message\": \"${query}\"}")

    if [ $? -eq 0 ]; then
        # Extract and format the response
        answer=$(echo "$response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'response' in data:
        print(data['response'])
    elif 'error' in data:
        print('ERROR: ' + data.get('message', 'Unknown error'))
    else:
        print(json.dumps(data, indent=2))
except:
    print(sys.stdin.read())
")
        echo -e "${GREEN}Answer:${NC}"
        echo "$answer" | fold -w 70 -s
        echo ""

        # Show metadata if available
        metadata=$(echo "$response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'metadata' in data:
        print('Sources used: ' + str(data['metadata'].get('sources_count', 0)))
        print('Response time: ' + str(data['metadata'].get('response_time', 0))[:4] + 's')
except:
    pass
" 2>/dev/null)

        if [ ! -z "$metadata" ]; then
            echo -e "${YELLOW}${metadata}${NC}"
            echo ""
        fi

    else
        echo -e "${RED}✗ Query failed${NC}"
        echo ""
    fi

    echo "────────────────────────────────────────────────────────────────"
    echo ""
}

# Function to test authentication
test_auth() {
    print_header "Testing Authentication Endpoints"

    echo -e "${CYAN}Registering a new user...${NC}"
    register_response=$(curl -s -X POST "${API_BASE_URL}/api/v1/auth/register" \
        -H "Content-Type: application/json" \
        -d '{
            "email": "test@example.com",
            "password": "SecurePass123!",
            "full_name": "Test User"
        }')

    echo "$register_response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'access_token' in data:
        print('✓ User registered successfully')
        print('Access Token: ' + data['access_token'][:30] + '...')
    else:
        print('Response: ' + json.dumps(data, indent=2))
except:
    print(sys.stdin.read())
"
    echo ""
    echo "────────────────────────────────────────────────────────────────"
    echo ""
}

# Function to test health endpoints
test_health() {
    print_header "Testing Health Check Endpoints"

    echo -e "${CYAN}1. Basic Health Check${NC}"
    curl -s "${API_BASE_URL}/health" | python3 -m json.tool
    echo ""
    echo ""

    echo -e "${CYAN}2. Detailed Health Check${NC}"
    curl -s "${API_BASE_URL}/api/v1/health/detailed" | python3 -m json.tool
    echo ""
    echo "────────────────────────────────────────────────────────────────"
    echo ""
}

# Main execution
main() {
    clear

    print_header "       Wealth Coach AI Assistant - Query Testing Tool      "

    check_server

    # Test health endpoints
    test_health

    # Test authentication (optional - may fail if user already exists)
    # test_auth

    # Financial Q&A Tests
    print_header "Financial Q&A Tests"

    run_query \
        "What is a 401k?" \
        "Basic retirement account explanation"

    run_query \
        "How much should I save for retirement?" \
        "Retirement savings guidance"

    run_query \
        "What is the difference between a Roth IRA and Traditional IRA?" \
        "Investment account comparison"

    run_query \
        "Should I pay off my credit card debt or invest?" \
        "Debt vs investment prioritization"

    run_query \
        "What is dollar-cost averaging?" \
        "Investment strategy explanation"

    # Budgeting Tests
    print_header "Budgeting & Money Management Tests"

    run_query \
        "How do I create a monthly budget?" \
        "Budgeting basics"

    run_query \
        "What is the 50/30/20 budget rule?" \
        "Budget allocation strategy"

    run_query \
        "How much should I keep in an emergency fund?" \
        "Emergency savings guidance"

    # Investment Tests
    print_header "Investment Education Tests"

    run_query \
        "What is diversification and why is it important?" \
        "Investment risk management"

    run_query \
        "What is an index fund?" \
        "Investment vehicle explanation"

    run_query \
        "What is compound interest?" \
        "Financial concept explanation"

    # Tax Optimization Tests
    print_header "Tax Optimization Tests"

    run_query \
        "What are tax-advantaged retirement accounts?" \
        "Tax-efficient investing"

    run_query \
        "What is a Health Savings Account (HSA)?" \
        "Tax-advantaged health account"

    # Summary
    print_header "Testing Complete!"

    echo -e "${GREEN}All queries have been executed.${NC}"
    echo ""
    echo -e "Additional commands you can try:"
    echo -e "  ${CYAN}• View API Docs:${NC}     http://localhost:8000/docs"
    echo -e "  ${CYAN}• Health Check:${NC}      curl ${API_BASE_URL}/health"
    echo -e "  ${CYAN}• Custom Query:${NC}      curl -X POST ${API_BASE_URL}/api/v1/chat/message \\"
    echo -e "                         -H 'Content-Type: application/json' \\"
    echo -e "                         -H 'X-API-Key: ${API_KEY}' \\"
    echo -e "                         -d '{\"message\": \"Your question here\"}'"
    echo ""
}

# Run main function
main
