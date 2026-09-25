# Spec: Login and Logout

## Overview
This feature implements user login and logout functionality for Spendly, allowing existing users to authenticate with their email and password, and to securely log out. Login is Step 3 in the Spendly roadmap and completes the basic authentication flow started with registration. The feature validates credentials against the database, verifies passwords using secure hashing, manages user sessions, and provides a logout mechanism that clears the session.

## Depends on
- Step 1: Database setup (users table must exist)
- Step 2: Registration (users can register and passwords are hashed)

## Routes
- `POST /login` — Handles login form submission — public access
- `GET /login` — Already exists, renders login form — public access
- `GET /logout` — Clears session and logs user out — logged-in users only

## Database changes
No database changes. The `users` table already exists with the required schema for authentication:
- `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
- `email` (TEXT UNIQUE NOT NULL)
- `password_hash` (TEXT NOT NULL)

## Templates
- **Modify:** `templates/login.html`
  - Keep existing form structure and styling
  - Add flash message rendering for success/info messages
  - Add `value="{{ email }}"` to email input to preserve on error
  - Error display already exists ({% if error %} block)

## Files to change
- `app.py` — Add POST handler for `/login` route, implement `/logout` route, import `check_password_hash`
- `templates/login.html` — Add flash message display and preserve email field value on error

## Files to create
No new files needed.

## New dependencies
No new dependencies. Required packages already in `requirements.txt`:
- Flask (for session management and flash messages)
- werkzeug (for password verification via `check_password_hash`)

## Rules for implementation
- No SQLAlchemy or ORMs — use raw SQL with `get_db()` from `database/db.py`
- Use parameterised queries only — never string interpolation in SQL
- Verify passwords with `werkzeug.security.check_password_hash(stored_hash, provided_password)`
- Use CSS variables from `static/css/style.css` — never hardcode hex values
- All templates must extend `base.html`
- Use Flask's `session` to store and clear user_id
- Use Flask's `flash()` for error and success messages
- Login validation:
  - Email: required, non-empty after stripping whitespace
  - Password: required, non-empty
  - Query database for user by email
  - If user not found: show error "Invalid email or password"
  - If user found but password incorrect: show error "Invalid email or password"
  - Use same error message for both cases (security best practice - don't reveal which field is wrong)
- On validation failure: re-render form with error message, preserve entered email
- On success: store user_id in session, flash success message, redirect to `/profile`
- Logout:
  - Clear the session with `session.clear()` or `session.pop('user_id', None)`
  - Flash info message: "You have been logged out"
  - Redirect to landing page `/`
- Handle database errors gracefully

## Definition of done
- [ ] User can submit login form with email and password
- [ ] Form validates that both fields are required and non-empty
- [ ] Submitting with non-existent email shows error: "Invalid email or password"
- [ ] Submitting with wrong password shows error: "Invalid email or password"
- [ ] Submitting with correct credentials logs user in (session contains user_id)
- [ ] After successful login, user is redirected to `/profile`
- [ ] After successful login, success message is displayed
- [ ] Error messages display on the form when validation fails
- [ ] Form preserves entered email when showing errors (password not preserved)
- [ ] User can access `/logout` route
- [ ] Logout clears the session (user_id removed from session)
- [ ] After logout, user is redirected to landing page
- [ ] After logout, logout message is displayed
- [ ] Login can be tested with demo user (email: demo@spendly.com, password: demo123)
- [ ] Full flow works: register → logout → login with same credentials
