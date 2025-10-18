# 🛠️ Utility Scripts

Collection of utility scripts for database management and testing.

---

## 📄 Available Scripts

### 1. `delete_user_by_mobile.sh`

Delete a user and all associated data from the database by mobile number.

**Usage:**

```bash
# Method 1: Pass mobile number as argument
./scripts/delete_user_by_mobile.sh 6297369832

# Method 2: Run without arguments (will prompt for mobile number)
./scripts/delete_user_by_mobile.sh
```

**Features:**
- ✅ Validates mobile number format (10 digits)
- ✅ Shows user information before deletion
- ✅ Shows count of associated records (allocations, transactions, budgets)
- ✅ Requires confirmation before deleting
- ✅ Deletes all related data:
  - User allocations
  - Transactions
  - Monthly budgets
  - Chat history
  - User account
- ✅ Verifies deletion was successful
- ✅ Colored output for better readability
- ✅ Error handling and validation

**Example Output:**

```
══════════════════════════════════════════════════════════
🔍 Searching for mobile number: 6297369832
══════════════════════════════════════════════════════════

✅ User Found:
   ID:           02e118ac-2271-4e91-9927-9d5df6829452
   Mobile:       6297369832
   Name:         sourav halder
   Created:      2025-10-14 12:00:31.434108

Associated Data:
   Allocations:  15 records
   Transactions: 42 records
   Budgets:      3 records

⚠️  WARNING: This will permanently delete the user and ALL associated data!
Are you sure you want to continue? (yes/no)
yes

══════════════════════════════════════════════════════════
🗑️  Deleting user: 6297369832
══════════════════════════════════════════════════════════

✅ Deleted 15 user allocations
✅ Deleted 42 transactions
✅ Deleted 3 monthly budgets
✅ Deleted 0 chat history records
✅ Deleted user account

══════════════════════════════════════════════════════════
✅ SUCCESS: User 6297369832 completely removed from database
══════════════════════════════════════════════════════════
```

**Safety Features:**
- Requires exact "yes" confirmation
- Shows all data that will be deleted
- Validates mobile number format
- Verifies deletion was successful

---

## 🔐 Security Notes

- These scripts require `.env` file with `DATABASE_URL` configured
- Scripts automatically activate the Python virtual environment
- All operations use parameterized queries to prevent SQL injection
- Deletion operations use `AUTOCOMMIT` mode for reliability

---

## 📝 Adding New Scripts

When adding new scripts to this directory:

1. **Make it executable:**
   ```bash
   chmod +x scripts/your_script.sh
   ```

2. **Add shebang at the top:**
   ```bash
   #!/bin/bash
   ```

3. **Include usage documentation** in the script header

4. **Update this README** with script description and usage

5. **Use colors for output:**
   ```bash
   RED='\033[0;31m'
   GREEN='\033[0;32m'
   YELLOW='\033[1;33m'
   BLUE='\033[0;34m'
   NC='\033[0m' # No Color
   ```

---

## 🐛 Troubleshooting

### "Permission denied" error

Make sure the script is executable:
```bash
chmod +x scripts/delete_user_by_mobile.sh
```

### "DATABASE_URL not found" error

Ensure your `.env` file exists in the project root with `DATABASE_URL` configured:
```env
DATABASE_URL=postgresql://user:password@host:5432/database
```

### "Virtual environment not found" error

Create and activate the virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📚 Related Documentation

- [Performance Optimization](../PERFORMANCE_OPTIMIZATION.md)
- [AI Assistant Integration](../AI_ASSISTANT_INTEGRATION.md)
- [API Documentation](../ALLOCATIONS_API_DOCUMENTATION.md)

---

**Last Updated:** October 17, 2025
