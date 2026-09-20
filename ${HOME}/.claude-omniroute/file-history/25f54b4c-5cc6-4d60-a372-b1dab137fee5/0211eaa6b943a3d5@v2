# Implementation Plan: Database Setup for Spendly

## Context

This is the foundational step for the Spendly expense tracking application. Currently, `database/db.py` contains only comments indicating where students should implement database functions. The application needs a working SQLite database layer to support user authentication and expense tracking features in future steps.

The spec at `.claude-omniroute/specs/01-database-setup.md` provides comprehensive requirements for:
- Database schema (users and expenses tables)
- Three core database functions (get_db, init_db, seed_db)
- Integration with the Flask app startup
- Seed data with demo user and 8 sample expenses

This implementation establishes the data layer that all future features depend on.

---

## Files to Modify

### 1. `database/db.py`
**Current state:** Contains only stub comments (lines 1-6)

**Changes needed:**
- Import `sqlite3`, `werkzeug.security.generate_password_hash`, and `flask.g`
- Implement `get_db()` function:
  - Connect to `expense_tracker.db` in project root (per CLAUDE.md)
  - Set `row_factory = sqlite3.Row` for dict-like access
  - Execute `PRAGMA foreign_keys = ON`
  - Store connection in Flask's `g` object for request context
  - Return the connection
- Implement `close_db(e=None)` helper:
  - Remove connection from `g` and close it
  - Will be registered as teardown function in app.py
- Implement `init_db()` function:
  - Call `get_db()` to get connection
  - Create `users` table with columns: id (PK), name, email (UNIQUE), password_hash, created_at
  - Create `expenses` table with columns: id (PK), user_id (FK→users.id), amount (REAL), category, date, description (nullable), created_at
  - Use `CREATE TABLE IF NOT EXISTS` for idempotency
  - Add indexes on user_id, date, and category for performance
  - Commit changes
- Implement `seed_db()` function:
  - Check if users table already has data (prevent duplicates)
  - If empty, insert demo user:
    - name: "Demo User"
    - email: "demo@spendly.com"
    - password_hash: hashed version of "demo123" using `generate_password_hash()`
  - Insert 8 sample expenses for demo user covering categories: Food, Transport, Bills, Health, Entertainment, Shopping, Other
  - Use dates in YYYY-MM-DD format spread across September 2026
  - Use parameterized queries for all inserts
  - Commit changes

### 2. `app.py`
**Current state:** Basic Flask app with routes (lines 1-66), no database integration

**Changes needed:**
- Add imports (after line 1):
  ```python
  from database.db import get_db, init_db, seed_db, close_db
  ```
- Add database initialization (before the routes section, around line 4):
  ```python
  # Register database teardown
  app.teardown_appcontext(close_db)
  
  # Initialize database on startup
  with app.app_context():
      init_db()
      seed_db()
  ```

---

## Database Schema Details

### users table
```sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
)
```

### expenses table
```sql
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    date TEXT NOT NULL,
    description TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
)
```

### Indexes
- `idx_expenses_user_id` on expenses(user_id)
- `idx_expenses_date` on expenses(date)
- `idx_expenses_category` on expenses(category)

---

## Sample Data Requirements

**Demo User:**
- Name: Demo User
- Email: demo@spendly.com
- Password: demo123 (store hashed)

**8 Sample Expenses** (all for demo user):
1. Food - reasonable amount, e.g., $45.99 - "Weekly grocery shopping"
2. Transport - e.g., $12.50 - "Bus fare"
3. Bills - e.g., $150.00 - "Internet bill"
4. Health - e.g., $35.00 - "Pharmacy"
5. Entertainment - e.g., $89.00 - "Concert tickets"
6. Shopping - e.g., $200.00 - "New shoes"
7. Other - e.g., $25.00 - "Miscellaneous"
8. Food - e.g., $8.75 - "Coffee" (second food entry to show variety)

All dates: September 2026, spread across different days (e.g., 2026-09-10 through 2026-09-18)

---

## Implementation Rules (from spec)

1. **No ORMs** - Use raw SQL with sqlite3
2. **Parameterized queries only** - Never use string formatting in SQL
3. **Foreign keys enabled** - `PRAGMA foreign_keys = ON` on every connection
4. **Amount as REAL** - Store decimal values, not integers
5. **Password hashing** - Use `werkzeug.security.generate_password_hash()`
6. **Idempotent operations** - `init_db()` and `seed_db()` safe to run multiple times
7. **Date format** - YYYY-MM-DD consistently
8. **Categories** - Use fixed list: Food, Transport, Bills, Health, Entertainment, Shopping, Other

---

## Verification Steps

After implementation:

1. **Database file creation:**
   ```bash
   ls expense_tracker.db
   ```
   Should exist in project root

2. **Table structure:**
   ```bash
   sqlite3 expense_tracker.db ".schema"
   ```
   Should show both tables with correct columns and constraints

3. **Seed data verification:**
   ```bash
   sqlite3 expense_tracker.db "SELECT COUNT(*) FROM users;"
   sqlite3 expense_tracker.db "SELECT COUNT(*) FROM expenses;"
   ```
   Should show 1 user and 8 expenses

4. **Demo user check:**
   ```bash
   sqlite3 expense_tracker.db "SELECT name, email FROM users WHERE email='demo@spendly.com';"
   ```
   Should return Demo User record

5. **Foreign key enforcement:**
   ```bash
   sqlite3 expense_tracker.db "INSERT INTO expenses (user_id, amount, category, date) VALUES (999, 50.0, 'Food', '2026-09-20');"
   ```
   Should fail with foreign key constraint error

6. **App startup:**
   ```bash
   python app.py
   ```
   Should start without errors on port 5001

7. **Idempotency test:**
   - Run app twice
   - Check database still has only 1 user and 8 expenses (no duplicates)

8. **Unique constraint test:**
   Try inserting duplicate email - should fail

---

## Expected Outcomes

- Database file `expense_tracker.db` created in project root
- Both tables exist with proper schema, constraints, and indexes
- Demo user exists with securely hashed password
- 8 diverse sample expenses spanning multiple categories
- App starts successfully and initializes database automatically
- No errors or warnings during startup
- Database properly enforces uniqueness and foreign key constraints
- Repeated app restarts don't duplicate seed data
