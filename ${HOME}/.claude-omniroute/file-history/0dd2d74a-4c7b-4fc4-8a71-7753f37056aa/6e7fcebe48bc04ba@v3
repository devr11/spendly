# Implementation Plan: Login and Logout

## Context
This implementation plan covers Step 3 of the Spendly roadmap: User Login and Logout functionality. Building upon the completed Step 1 (Database) and Step 2 (Registration), this step enables existing users to securely authenticate with their credentials and terminate their session.

## Implementation Steps

### 1. Update Imports in `app.py`
- Import `check_password_hash` from `werkzeug.security` alongside the existing `generate_password_hash`.
- Existing session, request, flash, redirect, and url_for imports from Flask are already present.

### 2. Implement POST Handler for `/login` Route in `app.py`
- Update `@app.route("/login")` to support methods `["GET", "POST"]`.
- Extract and `.strip()` the `email` from `request.form`.
- Extract `password` from `request.form`.
- **Server-side validation:**
  - Check if email is empty → re-render `login.html` with error "Email is required" and preserve email.
  - Check if password is empty → re-render `login.html` with error "Password is required" and preserve email.
- **Database Authentication:**
  - Query database using parameterized query: `SELECT id, password_hash FROM users WHERE email = ?`.
  - Verify user exists and check password using `check_password_hash(user['password_hash'], password)`.
  - **Security Best Practice:** If user is not found or password verification fails, return the exact same generic error message: `"Invalid email or password"` to prevent account enumeration.
- **Success Flow:**
  - Store `user_id` in session: `session['user_id'] = user['id']`.
  - Flash success message: `flash('Welcome back! You are now logged in.')`.
  - Redirect to `/profile`: `return redirect(url_for('profile'))`.

### 3. Implement `/logout` Route in `app.py`
- Update `@app.route("/logout")` placeholder to actual functionality:
  - Remove user session: `session.pop('user_id', None)`.
  - Flash info message: `flash('You have been logged out.')`.
  - Redirect to landing page: `return redirect(url_for('landing'))`.

### 4. Update `templates/login.html`
- **Flash Messages:** Add Jinja block to render flashed messages using the existing `.auth-success` CSS class.
- **Form Preservation:** Add `value="{{ email if email else '' }}"` to the email input field so the user's email is preserved on validation error (leaving password empty for security).

## Verification & Testing Checklist
- [ ] Submitting empty email or password shows appropriate validation error.
- [ ] Submitting non-existent email sh
ows "Invalid email or password".
- [ ] Submitting incorrect password shows "Invalid email or password".
- [ ] Submitting valid credentials (e.g., demo@spendly.com / demo123) logs the user in, sets `session['user_id']`, flashes success message, and redirects to `/profile`.
- [ ] Accessing `/logout` clears `user_id` from session, flashes logout message, and redirects to landing page.
- [ ] Email input preserves entered value on validation failure.
