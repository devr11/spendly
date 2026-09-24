# Spec: Registration

## Overview
This feature implements user registration functionality for Spendly, allowing new users to create accounts with their name, email, and password. Registration is Step 2 in the Spendly roadmap and establishes the foundation for user authentication. The feature validates user input, ensures email uniqueness, securely hashes passwords, and stores user records in the database.

## Depends on
- Step 1: Database setup (users table must exist)

## Routes
- `POST /register` — Handles registration form submission — public access
- `GET /register` — Already exists, renders registration form — public access

## Database changes
No database changes. The `users` table already exists in `database/db.py` with the required schema:
- `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
- `name` (TEXT NOT NULL)
- `email` (TEXT UNIQUE NOT NULL)
- `password_hash` (TEXT NOT NULL)
- `created_at` (TEXT DEFAULT datetime('now'))

## Templates
- **Modify:** `templates/register.html`
  - Keep existing form structure and styling
  - Add flash message rendering for success messages
  - Ensure error variable is displayed when present
  - Form already posts to `/register` with correct field names

## Files to change
- `app.py` — Add POST handler for `/register` route, import required modules
- `templates/register.html` — Add flash message display (error handling already present)

## Files to create
No new files needed.

## New dependencies
No new dependencies. Required packages already in `requirements.txt`:
- Flask (for session management and flash messages)
- werkzeug (for password hashing via `generate_password_hash`)

## Rules for implementation
- No SQLAlchemy or ORMs — use raw SQL with `get_db()` from `database/db.py`
- Use parameterised queries only — never string interpolation in SQL
- Hash passwords with `werkzeug.security.generate_password_hash` before storing
- Use CSS variables from `static/css/style.css` — never hardcode hex values
- All templates must extend `base.html`
- Use Flask's `session` to store user_id after successful registration
- Use Flask's `flash()` for error and success messages
- Set `app.secret_key` for session management
- Validate input server-side:
  - Name: required, non-empty after stripping whitespace
  - Email: required, valid email format, unique in database
  - Password: required, minimum 8 characters
- On validation failure: re-render form with error message, preserve entered name and email
- On success: log user in (store user_id in session), flash success message, redirect to `/profile`
- Handle database errors gracefully (catch IntegrityError for duplicate emails)

## Definition of done
- [ ] User can submit registration form with name, email, and password
- [ ] Form validates that all fields are required and non-empty
- [ ] Form validates that password is at least 8 characters
- [ ] Form validates that email is in valid format
- [ ] Submitting with duplicate email shows error: "Email already registered"
- [ ] Submitting with valid unique data creates user in database
- [ ] Password is hashed before storing (verify in database)
- [ ] After successful registration, user is logged in (session contains user_id)
- [ ] After successful registration, user is redirected to `/profile`
- [ ] Error messages display on the form when validation fails
- [ ] Form preserves entered name and email when showing errors
- [ ] Success flow can be tested by registering, then checking session and database
