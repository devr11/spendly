# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Spendly** is a Flask-based expense tracking web application. The app is structured as an educational project with some features completed (landing page, authentication pages, legal pages) and others marked as placeholders for future implementation.

## Development Commands

### Setup
```bash
# Create and activate virtual environment (if not already created)
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
source venv/bin/activate      # Unix/Mac

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Run the Flask development server
python app.py
# Server runs on http://localhost:5001
```

### Testing
```bash
# Run tests (pytest configured in requirements.txt)
pytest

# Run specific test file
pytest tests/test_name.py

# Run with verbose output
pytest -v
```

## Architecture

### Application Structure

- **app.py**: Main Flask application file containing all routes. Currently implements:
  - Landing page, login, register, terms, privacy routes
  - Placeholder routes for logout, profile, and expense CRUD operations (marked for future implementation)
  - Runs on port 5001 with debug mode enabled

- **database/**: Database module (not yet implemented)
  - `db.py`: Placeholder for SQLite database functions (get_db, init_db, seed_db)
  - Uses SQLite as the database (file: `expense_tracker.db`, gitignored)

- **templates/**: Jinja2 HTML templates
  - `base.html`: Base template with navbar, footer, and common layout
  - Individual pages: landing, login, register, terms, privacy
  - All pages extend base.html and use Jinja2 template blocks

- **static/**: Frontend assets
  - `css/style.css`: Custom CSS with design system variables (colors, fonts, spacing)
  - `js/main.js`: JavaScript file (currently minimal, placeholder for future features)

### Design System

The application uses a custom design system defined in CSS variables:
- **Colors**: Ink (text), Paper (background), Accent (primary green #1a472a), Accent-2 (orange #c17f24), Danger (red)
- **Typography**: DM Serif Display (headings), DM Sans (body text) from Google Fonts
- **Brand**: "Spendly" with diamond icon (◈)
- **Layout**: Max width 1200px for main content, 440px for auth forms

### Route Structure

**Implemented routes:**
- `/` - Landing page
- `/register` - User registration page
- `/login` - User login page
- `/terms` - Terms and conditions
- `/privacy` - Privacy policy

**Placeholder routes (not yet functional):**
- `/logout` - User logout
- `/profile` - User profile page
- `/expenses/add` - Add new expense
- `/expenses/<id>/edit` - Edit expense by ID
- `/expenses/<id>/delete` - Delete expense by ID

## Development Notes

- The database layer is not yet implemented. When implementing `database/db.py`, ensure:
  - `get_db()` returns a SQLite connection with `row_factory` set and foreign keys enabled
  - `init_db()` creates tables using `CREATE TABLE IF NOT EXISTS`
  - `seed_db()` inserts sample development data

- Session management and authentication are not yet implemented

- The application expects to grow with user authentication, expense tracking, and profile management features

- All placeholder routes return plain text strings indicating they are "coming in Step X" - these should be replaced with actual implementations

## Python Environment

- Uses Python virtual environment (venv)
- Flask 3.1.3, Werkzeug 3.1.6
- Testing with pytest 8.3.5 and pytest-flask 1.3.0
