# Spec: Profile Page Design

## Overview
The Profile Page gives logged-in users a dedicated place to view and manage their account information. At this stage of the Spendly roadmap, authentication (registration, login, logout) is complete, so the profile page is the natural next step — it lets users see their name and email, update their name, change their password, and delete their account. This rounds out the user-management story before the expense features begin.

## Depends on
- Step 02 — Registration (user creation, password hashing, `users` table)
- Step 03 — Login and Logout (session management, `session['user_id']`)

## Routes
- `GET /profile` — Render the profile page showing the user's name, email, and account creation date — **logged-in only**
- `POST /profile/update` — Update the user's name — **logged-in only**
- `POST /profile/change-password` — Change the user's password (requires current password) — **logged-in only**
- `POST /profile/delete` — Delete the user's account and all associated expenses, clear session, redirect to landing — **logged-in only**

## Database changes
No new tables or columns. The existing `users` table already contains `name`, `email`, `password_hash`, and `created_at`. The existing `expenses` table has `ON DELETE CASCADE` on the `user_id` foreign key, so deleting a user automatically removes their expenses.

## Templates
- **Create:**
  - `templates/profile.html` — Profile page with three sections:
    1. **Account info card** — displays name, email (read-only), and member-since date
    2. **Update name form** — input pre-filled with current name, submit button
    3. **Change password form** — current password, new password, confirm new password, submit button
    4. **Danger zone** — delete account button with confirmation prompt

- **Modify:**
  - `templates/base.html` — Add a "Profile" link in the navbar for logged-in users (next to "Sign out")

## Files to change
- `app.py` — Replace the placeholder `/profile` route; add `/profile/update`, `/profile/change-password`, `/profile/delete` routes; add a `login_required` helper or inline session check
- `templates/base.html` — Add profile nav link for authenticated users
- `static/css/style.css` — Add styles for the profile page layout, info card, form sections, and danger zone

## Files to create
- `templates/profile.html` — Profile page template

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs — use raw `sqlite3` via `get_db()`
- Parameterised queries only — never interpolate user input into SQL
- Passwords hashed with `werkzeug.security.generate_password_hash` / `check_password_hash`
- Use CSS variables from the existing design system — never hardcode hex colour values
- All templates extend `base.html`
- Every route must check `session.get('user_id')` and redirect to `/login` if absent — use a helper function or decorator to keep routes DRY
- Current password must be verified before allowing a password change
- New password confirmation field must match — validate server-side
- New password must meet the same 8-character minimum enforced at registration
- Account deletion must clear the session before redirecting
- Flash messages for all success and error states
- Profile page must be responsive and match the design language of the existing auth pages (card layout, spacing, typography)

## Definition of done
- [ ] Visiting `/profile` while logged out redirects to `/login`
- [ ] Visiting `/profile` while logged in shows the user's name, email, and member-since date
- [ ] The navbar shows a "Profile" link when the user is logged in
- [ ] Submitting the update-name form changes the user's name in the database and flashes a success message
- [ ] Submitting an empty name shows a validation error
- [ ] Changing password with correct current password, valid new password, and matching confirmation succeeds and flashes a success message
- [ ] Changing password with incorrect current password shows an error
- [ ] Changing password with a new password shorter than 8 characters shows an error
- [ ] Changing password where new password and confirmation don't match shows an error
- [ ] Deleting the account removes the user and their expenses from the database, clears the session, and redirects to the landing page
- [ ] All profile page styles use CSS variables — no hardcoded colours
- [ ] `pytest` passes with no errors
