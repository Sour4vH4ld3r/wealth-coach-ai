#!/bin/bash

################################################################################
# Delete User by Mobile Number
#
# Usage: ./scripts/delete_user_by_mobile.sh [MOBILE_NUMBER]
#
# If no mobile number is provided, the script will prompt for one.
# This script will delete the user and all associated data.
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Load environment variables
if [ -f "$PROJECT_DIR/.env" ]; then
    export $(grep -v '^#' "$PROJECT_DIR/.env" | xargs)
else
    echo -e "${RED}❌ Error: .env file not found${NC}"
    exit 1
fi

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}❌ Error: DATABASE_URL not found in .env${NC}"
    exit 1
fi

# Get mobile number from argument or prompt
if [ -z "$1" ]; then
    echo -e "${BLUE}Enter mobile number to delete:${NC}"
    read -r MOBILE_NUMBER
else
    MOBILE_NUMBER="$1"
fi

# Validate mobile number (basic validation)
if ! [[ "$MOBILE_NUMBER" =~ ^[0-9]{10}$ ]]; then
    echo -e "${RED}❌ Error: Invalid mobile number format. Must be 10 digits.${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}🔍 Searching for mobile number: ${MOBILE_NUMBER}${NC}"
echo -e "${BLUE}══════════════════════════════════════════════════════════${NC}"
echo ""

# Activate virtual environment
cd "$PROJECT_DIR"
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo -e "${RED}❌ Error: Virtual environment not found${NC}"
    exit 1
fi

# Check if user exists and get details
USER_INFO=$(python3 << END
from sqlalchemy import create_engine, text
import os
import sys
import json

DATABASE_URL = os.getenv('DATABASE_URL')
mobile = '$MOBILE_NUMBER'

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text('''
            SELECT id, mobile_number, full_name, created_at
            FROM users
            WHERE mobile_number = :mobile
        '''), {'mobile': mobile})

        user = result.fetchone()

        if user:
            # Get related data counts
            user_id = user[0]

            allocations = conn.execute(text(
                'SELECT COUNT(*) FROM user_allocations WHERE user_id = :id'
            ), {'id': user_id}).scalar()

            transactions = conn.execute(text(
                'SELECT COUNT(*) FROM transactions WHERE user_id = :id'
            ), {'id': user_id}).scalar()

            budgets = conn.execute(text(
                'SELECT COUNT(*) FROM monthly_budgets WHERE user_id = :id'
            ), {'id': user_id}).scalar()

            print(json.dumps({
                'found': True,
                'id': user[0],
                'mobile': user[1],
                'name': user[2],
                'created': str(user[3]),
                'allocations': allocations,
                'transactions': transactions,
                'budgets': budgets
            }))
        else:
            print(json.dumps({'found': False}))
except Exception as e:
    print(json.dumps({'error': str(e)}), file=sys.stderr)
    sys.exit(1)
END
)

# Parse JSON response
if echo "$USER_INFO" | grep -q '"error"'; then
    echo -e "${RED}❌ Database error occurred${NC}"
    echo "$USER_INFO"
    exit 1
fi

if echo "$USER_INFO" | grep -q '"found": false'; then
    echo -e "${YELLOW}⚠️  No user found with mobile number: ${MOBILE_NUMBER}${NC}"
    exit 0
fi

# Extract user details
USER_ID=$(echo "$USER_INFO" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
USER_NAME=$(echo "$USER_INFO" | python3 -c "import sys, json; print(json.load(sys.stdin)['name'])")
USER_CREATED=$(echo "$USER_INFO" | python3 -c "import sys, json; print(json.load(sys.stdin)['created'])")
ALLOCATIONS_COUNT=$(echo "$USER_INFO" | python3 -c "import sys, json; print(json.load(sys.stdin)['allocations'])")
TRANSACTIONS_COUNT=$(echo "$USER_INFO" | python3 -c "import sys, json; print(json.load(sys.stdin)['transactions'])")
BUDGETS_COUNT=$(echo "$USER_INFO" | python3 -c "import sys, json; print(json.load(sys.stdin)['budgets'])")

# Display user information
echo -e "${GREEN}✅ User Found:${NC}"
echo -e "   ${BLUE}ID:${NC}           $USER_ID"
echo -e "   ${BLUE}Mobile:${NC}       $MOBILE_NUMBER"
echo -e "   ${BLUE}Name:${NC}         $USER_NAME"
echo -e "   ${BLUE}Created:${NC}      $USER_CREATED"
echo ""
echo -e "${YELLOW}Associated Data:${NC}"
echo -e "   ${BLUE}Allocations:${NC}  $ALLOCATIONS_COUNT records"
echo -e "   ${BLUE}Transactions:${NC} $TRANSACTIONS_COUNT records"
echo -e "   ${BLUE}Budgets:${NC}      $BUDGETS_COUNT records"
echo ""

# Confirmation prompt
echo -e "${RED}⚠️  WARNING: This will permanently delete the user and ALL associated data!${NC}"
echo -e "${YELLOW}Are you sure you want to continue? (yes/no)${NC}"
read -r CONFIRMATION

if [ "$CONFIRMATION" != "yes" ]; then
    echo -e "${BLUE}❌ Deletion cancelled${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}══════════════════════════════════════════════════════════${NC}"
echo -e "${RED}🗑️  Deleting user: ${MOBILE_NUMBER}${NC}"
echo -e "${BLUE}══════════════════════════════════════════════════════════${NC}"
echo ""

# Delete user and associated data
python3 << END
from sqlalchemy import create_engine, text
import os
import sys

DATABASE_URL = os.getenv('DATABASE_URL')
user_id = '$USER_ID'

try:
    engine = create_engine(DATABASE_URL, isolation_level='AUTOCOMMIT')

    with engine.connect() as conn:
        # Delete user_allocations
        result = conn.execute(text('''
            DELETE FROM user_allocations WHERE user_id = :user_id
        '''), {'user_id': user_id})
        print(f'✅ Deleted {result.rowcount} user allocations')

        # Delete transactions
        result = conn.execute(text('''
            DELETE FROM transactions WHERE user_id = :user_id
        '''), {'user_id': user_id})
        print(f'✅ Deleted {result.rowcount} transactions')

        # Delete monthly_budgets
        result = conn.execute(text('''
            DELETE FROM monthly_budgets WHERE user_id = :user_id
        '''), {'user_id': user_id})
        print(f'✅ Deleted {result.rowcount} monthly budgets')

        # Delete chat_history (if exists)
        try:
            result = conn.execute(text('''
                DELETE FROM chat_history WHERE user_id = :user_id
            '''), {'user_id': user_id})
            print(f'✅ Deleted {result.rowcount} chat history records')
        except Exception:
            pass  # Table might not exist

        # Finally delete the user
        result = conn.execute(text('''
            DELETE FROM users WHERE id = :user_id
        '''), {'user_id': user_id})
        print(f'✅ Deleted user account')

except Exception as e:
    print(f'❌ Error: {e}', file=sys.stderr)
    sys.exit(1)
END

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${BLUE}══════════════════════════════════════════════════════════${NC}"

    # Verify deletion
    VERIFY=$(python3 << END
from sqlalchemy import create_engine, text
import os

DATABASE_URL = os.getenv('DATABASE_URL')
mobile = '$MOBILE_NUMBER'

engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    result = conn.execute(text('''
        SELECT COUNT(*) FROM users WHERE mobile_number = :mobile
    '''), {'mobile': mobile})
    print(result.scalar())
END
    )

    if [ "$VERIFY" = "0" ]; then
        echo -e "${GREEN}✅ SUCCESS: User ${MOBILE_NUMBER} completely removed from database${NC}"
    else
        echo -e "${RED}⚠️  WARNING: Verification failed. User may still exist.${NC}"
    fi

    echo -e "${BLUE}══════════════════════════════════════════════════════════${NC}"
else
    echo -e "${RED}❌ Deletion failed. Check error messages above.${NC}"
    exit 1
fi
