# Implementation Plan: User Registration

## Context

This plan implements Step 2 of the Spendly roadmap - user registration functionality. The current application has:
- A GET `/register` route that renders a registration form
- A database with a `users` table already set up (Step 1 complete)
- A registration form template with proper field names (name, email, password)
- Error display capability in the template ({% if error %})
- No POST handler for registration
- No session management configured (no app.secret_key)
- No Flask imports for request, session, redirect, url_for, or flash

The goal is to enable new users to create accounts by implementing server-side validation, secure password hashing, database insertion, and automatic login after successful registration.

## Implementation Steps

### 1. Update app.py - Add Configuration and Imports

**File:** `app.py`

**Changes needed:**

1. **Add imports at the top:**
   - `request` - to access form data
   - `session` - to store logged-in user ID
   - `redirect, url_for` - to redirect after successful registration
   - `flash` - for success/error messages
   - `generate_password_hash` from `werkzeug.security` - for password hashing
   - `sqlite3` - to catch IntegrityError for duplicate emails

2. **Add app.secret_key configuration** (after line 4, before database setup):
   - Generate a secure random secret key for session management
   - Use `secrets.token_hex(16)` or a hardcoded value for development
   - Example: `app.secret_key = 'dev-secret-key-change-in-production'`

### 2. Implement POST /register Route Handler

**File:** `app.py`

**Add a new route handler** that accepts both GET and POST methods.

**Update the existing route from:**
```python
@app.route("/register")
def register():
    return render_template("register.html")
```

**To:**
```python
@app.route("/register", methods=["GET", "POST"])
def register():
    # Implementation details below
```

**POST Handler Logic Flow:**

1. **Extract form data:**
   - Get name, email, password from request.form
   - Strip whitespace from name and email

2. **Server-side validation (in order):**
   - Check if name is empty after stripping → error: "Name is required"
   - Check if email is empty after stripping → error: "Email is required"
   - Check if password is empty → error: "Password is required"
   - Check if password length < 8 → error: "Password must be at least 8 characters"
   - Check if email format is valid (contains @ and .) → error: "Please enter a valid email address"

3. **If validation fails:**
   - Re-render `register.html` with:
     - `error=<error_message>`
     - `name=<entered_name>` (to preserve in form)
     - `email=<entered_email>` (to preserve in form)

4. **Hash the password:**
   - Use `generate_password_hash(password)` to create password_hash

5. **Insert user into database:**
   - Get database connection: `db = get_db()`
   - Use parameterized query:
     ```sql
     INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)
     ```
   - Get the new user's ID from `cursor.lastrowid`
   - Commit the transaction: `db.commit()`

6. **Handle database errors:**
   - Wrap database insert in try-except
   - Catch `sqlite3.IntegrityError` (duplicate email due to UNIQUE constraint)
   - On IntegrityError → error: "Email already registered"
   - Re-render form with error and preserve name/email

7. **On successful registration:**
   - Store user_id in session: `session['user_id'] = user_id`
   - Flash success message: `flash('Account created successfully! Welcome to Spendly.')`
   - Redirect to `/profile`: `return redirect(url_for('profile'))`

**Email validation approach:**
- Simple format check: `'@' in email and '.' in email.split('@')[1]`
- This is sufficient for basic validation (no regex needed, keeping dependencies minimal)

### 3. Update templates/register.html - Preserve Form Values

**File:** `templates/register.html`

**Changes needed:**

1. **Add flash message display** (after line 13, before the error block):
   ```jinja2
   {% with messages = get_flashed_messages() %}
     {% if messages %}
       {% for message in messages %}
       <div class="auth-success">{{ message }}</div>
       {% endfor %}
     {% endif %}
   {% endwith %}
   ```

2. **Preserve name field value** on validation error (line 24):
   - Add `value="{{ name }}"` attribute to name input
   - The value will be empty on initial GET, populated on error

3. **Preserve email field value** on validation error (line 30):
   - Add `value="{{ email }}"` attribute to email input
   - The value will be empty on initial GET, populated on error

**Note:** Password field should NOT be preserved for security reasons (standard practice).

### 4. Add CSS for Success Messages (Optional Enhancement)

**File:** `static/css/style.css`

**Add after the `.auth-error` style (around line 480):**

```css
.auth-success {
    background: var(--accent-light);
    color: var(--accent);
    border: 1px solid #c8ddd0;
    border-radius: var(--radius-sm);
    padding: 0.75rem 1rem;
    font-size: 0.875rem;
    margin-bottom: 1.25rem;
}
```

This follows the existing pattern from `.auth-error` but uses the accent colors instead of danger colors (already defined in CSS variables).

## Files to Modify

1. **app.py**
   - Add imports: request, session, redirect, url_for, flash, generate_password_hash, sqlite3
   - Add app.secret_key configuration
   - Update `/register` route to handle POST requests with validation and database insertion

2. **templates/register.html**
   - Add flash message display block
   - Add `value="{{ name }}"` to name input field
   - Add `value="{{ email }}"` to email input field

3. **static/css/style.css** (optional but recommended)
   - Add `.auth-success` style for flash success messages

## No New Files or Dependencies

- All required packages already in requirements.txt (Flask, werkzeug)
- No new files needed
- Uses existing database schema and functions from database/db.py

## Implementation Rules

- ✅ Use parameterized queries only (no string interpolation in SQL)
- ✅ Hash passwords with werkzeug.security.generate_password_hash
- ✅ Use CSS variables (--accent-light, --accent) for new styles
- ✅ No SQLAlchemy or ORMs - raw SQL with get_db()
- ✅ Server-side validation for all fields
- ✅ Graceful error handling with user-friendly messages
- ✅ Preserve form data on validation errors (except password)

## Verification & Testing

After implementation, verify the feature works by testing these scenarios:

### Test Case 1: Empty Fields Validation
1. Navigate to http://localhost:5001/register
2. Submit form with empty name → should show "Name is required" error
3. Submit form with empty email → should show "Email is required" error
4. Submit form with empty password → should show "Password is required" error
5. Verify name/email are preserved in form when showing errors

### Test Case 2: Password Length Validation
1. Enter valid name and email
2. Enter password with less than 8 characters (e.g., "pass123")
3. Submit form → should show "Password must be at least 8 characters" error
4. Verify name/email are preserved in form

### Test Case 3: Email Format Validation
1. Enter valid name
2. Enter invalid email without @ (e.g., "testuser.com")
3. Enter valid password (8+ chars)
4. Submit form → should show "Please enter a valid email address" error

### Test Case 4: Duplicate Email
1. Try to register with email "demo@spendly.com" (already exists from seed data)
2. Submit form → should show "Email already registered" error
3. Verify name/email are preserved in form

### Test Case 5: Successful Registration
1. Enter new valid data:
   - Name: "Test User"
   - Email: "test@example.com"
   - Password: "password123"
2. Submit form
3. Verify:
   - Redirected to /profile page
   - Session contains user_id (can check Flask session or test programmatically)
   - Success message displayed (if viewing on /profile with flash message display)
4. Verify in database:
   - Open expense_tracker.db
   - Query: `SELECT id, name, email, password_hash FROM users WHERE email = 'test@example.com'`
   - Confirm user exists and password_hash is a hashed value (not plain text)

### Test Case 6: Auto-login After Registration
1. After successful registration from Test Case 5
2. Check that session['user_id'] is set
3. Verify user is considered "logged in" for future features

### Running the App
```bash
python app.py
```
Access at: http://localhost:5001

### Database Verification
To verify password hashing and user creation:
```bash
sqlite3 expense_tracker.db "SELECT id, name, email, substr(password_hash, 1, 20) || '...' as hash_preview FROM users;"
```

## Edge Cases Handled

1. **Whitespace-only inputs:** Strip whitespace before validation
2. **Duplicate emails:** Catch IntegrityError and show user-friendly message
3. **SQL injection:** Prevented by parameterized queries
4. **Password security:** Hashed before storage, never stored in plain text
5. **Form data preservation:** Name and email preserved on error (UX improvement)
6. **Case sensitivity:** SQLite UNIQUE constraint is case-insensitive by default for text fields

## Success Criteria (Definition of Done)

All items from the spec must pass:
- ✅ User can submit registration form with name, email, and password
- ✅ Form validates all fields are required and non-empty
- ✅ Form validates password is at least 8 characters
- ✅ Form validates email is in valid format
- ✅ Duplicate email shows "Email already registered" error
- ✅ Valid unique data creates user in database
- ✅ Password is hashed before storing
- ✅ After registration, user is logged in (session contains user_id)
- ✅ After registration, user is redirected to /profile
- ✅ Error messages display when validation fails
- ✅ Form preserves name and email on errors
- ✅ Success flow is testable via registration → session check → database check
