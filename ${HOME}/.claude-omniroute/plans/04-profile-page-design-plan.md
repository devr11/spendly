# Step 4 — Profile Page Design (Spendly)

## Context

`/profile` is currently a stub returning the plain string `"Profile page — coming in Step 4"` (`app.py:136-138`). Step 4 replaces it with a fully designed, **statically-populated** profile page so the complete UI layout — identity card, summary stats, transaction table, category breakdown — can be reviewed and signed off before Step 5 wires in real `get_db()` queries. Building the UI against hardcoded Python data first means Step 5 becomes a data-source swap rather than a redesign.

Sources driving this plan: the spec at `${HOME}/.claude-omniroute/specs/04-profile-page-design.md`, the `spendly-ui-designer` skill at `${HOME}/.claude-omniroute/skills/frontend-desgin/SKILL.md`, and the existing code (`app.py`, `database/db.py`, `templates/base.html`, all 752 lines of `static/css/style.css`).

**Confirmed decisions:** username comes from `session['user_name']`; no Lucide — stay typographic; new CSS appends to `static/css/style.css`; auth guard is a reusable `@login_required` decorator.

### Skill-vs-spec conflicts, resolved
- The skill's *default* palette (indigo `#6366F1`, Inter, `#F7F8FA`) is **discarded**. The skill itself says existing tokens win, and Spendly already has a warm paper/ink/forest-green system. We extend it, not replace it.
- The skill suggests Lucide icons; the spec says no new dependencies. **Spec wins** (per decision above).
- `landing.html:52` sets bar widths with `style="width: 78%"`. The spec forbids inline styles, so that pattern is **not** copied — see "No-inline-style bar widths" below.

---

## Step 0 — Copy this plan into the project

The harness restricted plan-mode writes to this file only. First action on execution:

```
cp "C:/Users/devr8/.claude/plans/read-the-claude-md-file-mellow-moonbeam.md" \
   "C:/Users/devr8/Downloads/expense-tracker/expense-tracker/${HOME}/.claude-omniroute/plans/04-profile-page-design.md"
```

(`${HOME}` is a **literal** directory inside the repo — that's where the existing `specs/` and `plans/` live.)

---

## 1. `app.py` — auth guard, session name, profile view

### 1a. Imports
Add `from functools import wraps` alongside the existing imports (`app.py:1-4`).

### 1b. `login_required` decorator
Place after `app.teardown_appcontext(close_db)`, before the routes section. `@wraps` is required so Flask keeps distinct endpoint names across the three routes that adopt this in Steps 7-9.

```python
def login_required(view):
    """Redirect anonymous visitors to the login page."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please sign in to view that page.")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped
```

### 1c. Make the username available to the navbar
Two one-line changes; **no new queries**.

- `app.py:99` — widen the existing login SELECT to `'SELECT id, name, password_hash FROM users WHERE email = ?'`, then add `session['user_name'] = user['name']` next to `session['user_id'] = user['id']` (`app.py:108`).
- `app.py:69` — `register()` already holds `name`, so add `session['user_name'] = name` beside `session['user_id'] = user_id`.

Templates read it as `session.get('user_name', 'Account')`, so sessions created before this change degrade gracefully instead of raising.

### 1d. Hardcoded profile data
Module-level constants above the routes. Mirror `seed_db()`'s demo user and its 8 expenses (`database/db.py:104-120`) exactly, so Step 5's swap to real rows produces the same page.

```python
PROFILE_USER = {
    "name": "Demo User",
    "email": "demo@spendly.com",
    "member_since": "September 2026",
}

# Newest first — the order a real `ORDER BY date DESC` will return in Step 5.
PROFILE_TRANSACTIONS = [
    {"date": "2026-09-18", "date_label": "18 Sep 2026", "description": "Coffee",                 "category": "Food",          "amount": 8.75},
    {"date": "2026-09-17", "date_label": "17 Sep 2026", "description": "Miscellaneous",          "category": "Other",         "amount": 25.00},
    {"date": "2026-09-16", "date_label": "16 Sep 2026", "description": "Bus fare",               "category": "Transport",     "amount": 12.50},
    {"date": "2026-09-15", "date_label": "15 Sep 2026", "description": "Weekly grocery shopping","category": "Food",          "amount": 45.99},
    {"date": "2026-09-14", "date_label": "14 Sep 2026", "description": "Concert tickets",        "category": "Entertainment", "amount": 89.00},
    {"date": "2026-09-13", "date_label": "13 Sep 2026", "description": "Pharmacy",               "category": "Health",        "amount": 35.00},
    {"date": "2026-09-12", "date_label": "12 Sep 2026", "description": "New shoes",              "category": "Shopping",      "amount": 200.00},
    {"date": "2026-09-10", "date_label": "10 Sep 2026", "description": "Internet bill",          "category": "Bills",         "amount": 150.00},
]
```

**Conventions and why:**
- **Amounts stay `float`.** SQLite's `amount` column is `REAL`, so Step 5 passes rows straight through. Formatting happens at render: `₹{{ "%.2f"|format(t.amount) }}`.
- **`date_label` is pre-computed in Python.** Jinja can't parse a `TEXT` date without a custom filter; Step 5 will produce the same key via `datetime.strptime(row["date"], "%Y-%m-%d").strftime("%d %b %Y")`. The raw `date` key is kept for ordering.
- **Stats are derived, not typed in.** Keeps the page self-consistent if a row is edited, and the derivation lines survive into Step 5 unchanged:

```python
def _build_profile_context():
    txns = PROFILE_TRANSACTIONS                       # Step 5: swap for a get_db() query
    total = sum(t["amount"] for t in txns)

    totals = {}
    for t in txns:
        totals[t["category"]] = totals.get(t["category"], 0.0) + t["amount"]

    peak = max(totals.values()) if totals else 0.0
    categories = [
        {
            "name": name,
            "slug": name.lower().replace(" ", "-"),
            "amount": amount,
            "share": round(amount / total * 100) if total else 0,
            # width bucket, snapped to 5% so a CSS class can carry it
            "bar_step": int(round(amount / peak * 20) * 5) if peak else 0,
        }
        for name, amount in sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
    ]

    name = PROFILE_USER["name"]
    initials = "".join(part[0] for part in name.split()[:2]).upper() or "?"

    return {
        "user": {**PROFILE_USER, "initials": initials},
        "transactions": txns,
        "total_spent": total,
        "transaction_count": len(txns),
        "top_category": categories[0]["name"] if categories else "—",
        "categories": categories,
    }
```

> **Stated assumption:** `bar_step` is each category's share of the **largest** category, not of the total. With 7 categories the largest real share is only 35% (₹200 of ₹566.24), which makes every bar look stunted. Scaling to the peak gives Shopping a full bar and keeps the others legible; the true share-of-total is still shown as the `%` text beside each row.

### 1e. The view
Replaces `app.py:136-138`.

```python
@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", **_build_profile_context())
```

Leave `/expenses/*` stubs alone — they adopt `@login_required` in Steps 7-9.

---

## 2. `templates/base.html` — navbar logged-in state

Replace the logged-in branch (`base.html:22-23`), which currently shows only "Sign out":

```jinja
{% if session.get('user_id') %}
<a href="{{ url_for('profile') }}" class="nav-user">
    <span class="nav-avatar">{{ session.get('user_name', 'Account')[0]|upper }}</span>
    <span class="nav-user-name">{{ session.get('user_name', 'Account') }}</span>
</a>
<a href="{{ url_for('logout') }}" class="nav-cta">Sign out</a>
{% else %}
```

No other base.html change — CSS lands in `style.css`, and the page needs no JS, so `{% block head %}` and `{% block scripts %}` stay unused.

> **Trap:** `style.css:597` is `.nav-links a:not(.nav-cta) { display: none; }` at ≤600px. That would hide the whole profile link on mobile. The responsive rules below keep `.nav-user` visible and hide only `.nav-user-name`, leaving the avatar circle as a tappable target.

---

## 3. `templates/profile.html` (new)

Extends `base.html`; uses `{% block title %}` and `{% block content %}` only. No inline styles, no hex, no `<style>` tag.

```
<section class="profile-section">
  <header class="profile-header">
      h1.profile-title      "Your profile"
      p.profile-subtitle    "Your account details and spending at a glance."

  {# flash messages — reuses the existing .auth-success class #}

  <div class="profile-identity">              ← card
      span.profile-avatar       {{ user.initials }}
      div.profile-identity-text
          h2.profile-identity-name   {{ user.name }}
          p.profile-identity-email   {{ user.email }}
          p.profile-identity-meta    "Member since {{ user.member_since }}"
      a.btn-ghost  "Edit profile"  (href="#", placeholder for a later step)

  <div class="profile-stats">                 ← 3 tiles
      Total spent        ₹{{ "%.2f"|format(total_spent) }}   / "all time"
      Transactions       {{ transaction_count }}             / "recorded"
      Top category       {{ top_category }}                  / "most spent"

  <div class="profile-grid">                  ← 2fr / 1fr
      <div class="profile-card">              ← transaction history
          .profile-card-head → h2.profile-card-title "Transaction history"
                               span.profile-card-note "{{ transaction_count }} entries"
          .tx-table-wrap > table.tx-table
              thead: Date | Description | Category | Amount(th.tx-amount)
              tbody: {% for t in transactions %} … {% endfor %}
      <div class="profile-card">              ← category breakdown
          .profile-card-head → "Spending by category"
          .cat-list > {% for c in categories %} .cat-row {% endfor %}
```

### Category badge without an `{% if %}` chain

```jinja
<span class="cat-badge cat-{{ t.category|lower|replace(' ', '-') }}">{{ t.category }}</span>
```

`.cat-badge` carries neutral base styling (paper-warm background, muted text); the `.cat-food` / `.cat-transport` / … modifiers only override the two colours. An **unknown category simply matches no modifier** and renders as a tidy neutral pill — no breakage, no fallback logic. `|replace(' ', '-')` guards against multi-word categories a user might add later.

### No-inline-style bar widths

The spec forbids inline styles, so width travels as a class from a 21-rule ladder (`.bar-w-0` … `.bar-w-100`, step 5) generated once in CSS:

```jinja
<div class="cat-row">
    <div class="cat-row-head">
        <span class="cat-badge cat-{{ c.slug }}">{{ c.name }}</span>
        <span class="cat-row-amount">₹{{ "%.2f"|format(c.amount) }}
            <span class="cat-row-share">{{ c.share }}%</span>
        </span>
    </div>
    <div class="cat-bar-track" role="img"
         aria-label="{{ c.name }}: {{ c.share }}% of total spending">
        <div class="cat-bar-fill cat-{{ c.slug }} bar-w-{{ c.bar_step }}"></div>
    </div>
</div>
```

This needs zero JS and works with scripting disabled. (Considered and rejected: `style="--pct:78%"` — still a `style` attribute; and a `data-pct` + JS approach — adds a script for something CSS can do.)

### Table semantics
`<th scope="col">` on every header; amount column gets `class="tx-amount"` on both `th` and `td` for right-alignment; `.tx-table-wrap` provides horizontal scroll on narrow screens.

---

## 4. `static/css/style.css` — append one `/* Profile page */` section

Place it at the end of the file, matching the existing `/* ---- */` banner-comment style.

### 4a. New `:root` tokens
Added to the existing block (`style.css:5-31`). Seven category pairs — deliberately desaturated so they sit inside the warm paper/forest palette rather than fighting it — plus the one shadow token the skill permits.

```css
--cat-food: #a8552f;          --cat-food-light: #faeee7;
--cat-transport: #1f5f63;     --cat-transport-light: #e5f0f1;
--cat-bills: #3b4a7a;         --cat-bills-light: #eaedf6;
--cat-health: #2f6b45;        --cat-health-light: #e8f0eb;
--cat-entertainment: #6d3d6b; --cat-entertainment-light: #f3eaf2;
--cat-shopping: #9a6416;      --cat-shopping-light: #fdf3e3;
--cat-other: #5f5f5f;         --cat-other-light: #eeebe4;

--shadow-card: 0 1px 2px rgba(0,0,0,0.04), 0 1px 3px rgba(0,0,0,0.06);
```

`--cat-health` / `--cat-shopping` are intentionally near `--accent` / `--accent-2` so the two brand hues reappear in the category set. No spacing-scale tokens are introduced — the rest of the stylesheet uses ad-hoc `rem` values, and adding a scale used by one page only would make things *less* consistent. New rules stick to the 8px grid via `rem` multiples of `0.5`.

### 4b. New classes

| Class | Key properties |
|---|---|
| `.profile-section` | `max-width: var(--max-width)`, `margin: 0 auto`, `padding: 3rem 2rem 4rem` |
| `.profile-header` | `margin-bottom: 2rem` |
| `.profile-title` | `var(--font-display)`, `clamp(1.75rem, 3.5vw, 2.5rem)` — mirrors `.legal-title` |
| `.profile-subtitle` | `0.95rem`, `var(--ink-muted)` |
| `.profile-card` | `var(--paper-card)`, `1px solid var(--border)`, `var(--radius-md)`, `padding: 1.5rem`, `var(--shadow-card)` |
| `.profile-identity` | same card surface + `display:flex`, `align-items:center`, `gap:1.5rem` |
| `.profile-avatar` | `64px` circle, `var(--accent-light)` bg, `var(--accent)` text, `var(--font-display)`, `1.5rem`, flex-centred |
| `.profile-identity-name` | `var(--font-display)`, `1.5rem` |
| `.profile-identity-email` | `0.9rem`, `var(--ink-muted)` |
| `.profile-identity-meta` | `0.8rem`, `var(--ink-faint)`, `margin-top: 0.35rem` |
| `.profile-identity .btn-ghost` | `margin-left: auto` (reuses the existing button) |
| `.profile-stats` | `grid`, `repeat(auto-fit, minmax(190px, 1fr))`, `gap: 1rem`, `margin: 1.5rem 0` |
| `.profile-stat` | card surface, `padding: 1.25rem` |
| `.profile-stat-label` | `0.72rem`, `var(--ink-faint)`, `uppercase`, `letter-spacing: .06em` |
| `.profile-stat-value` | `1.75rem`, `600`, `font-variant-numeric: tabular-nums` |
| `.profile-stat-meta` | `0.8rem`, `var(--ink-muted)` |
| `.profile-grid` | `grid`, `grid-template-columns: 2fr 1fr`, `gap: 1.5rem`, `align-items: start` |
| `.profile-card-head` | `flex`, `space-between`, `border-bottom: 1px solid var(--border-soft)`, `padding/margin-bottom: .875rem` |
| `.profile-card-title` | `var(--font-display)`, `1.15rem` |
| `.profile-card-note` | `0.8rem`, `var(--ink-faint)` |
| `.tx-table-wrap` | `overflow-x: auto` |
| `.tx-table` | `width:100%`, `border-collapse: collapse`, `font-size: .9rem` |
| `.tx-table th` | `0.72rem`, uppercase, `letter-spacing:.06em`, `var(--ink-faint)`, left-aligned, `border-bottom: 1px solid var(--border)` |
| `.tx-table td` | `padding: .75rem`, `border-bottom: 1px solid var(--border-soft)`, `var(--ink-soft)`; `:first-child`/`:last-child` zero out the outer padding |
| `.tx-table tbody tr` | `transition: background .15s`; `:hover { background: var(--paper); }` |
| `.tx-table tbody tr:last-child td` | `border-bottom: none` |
| `.tx-date` | `var(--ink-muted)`, `white-space: nowrap` |
| `.tx-desc` | `var(--ink)`, `font-weight: 500` |
| `.tx-amount` | `text-align: right`, `tabular-nums`, `font-weight: 500` |
| `.cat-badge` | `inline-block`, `.72rem`, `500`, `padding: .25rem .6rem`, `border-radius: 999px`, neutral `var(--paper-warm)` / `var(--ink-muted)` |
| `.cat-badge.cat-food` … `.cat-other` | `background: var(--cat-X-light)`, `color: var(--cat-X)` |
| `.cat-list` | `flex column`, `gap: 1.1rem` |
| `.cat-row-head` | `flex`, `space-between`, `align-items: baseline`, `margin-bottom: .45rem` |
| `.cat-row-amount` | `.85rem`, `500`, `tabular-nums` |
| `.cat-row-share` | `.75rem`, `var(--ink-faint)`, `margin-left: .35rem` |
| `.cat-bar-track` | `height: 8px`, `var(--paper-warm)`, `border-radius: 999px`, `overflow: hidden` |
| `.cat-bar-fill` | `height: 100%`, `border-radius: 999px`, `background: var(--ink-faint)` (neutral default), `transition: width .6s ease` |
| `.cat-bar-fill.cat-food` … | `background: var(--cat-X)` (solid, not the light tint) |
| `.bar-w-0` … `.bar-w-100` | 21 rules, `width: N%` in 5% steps |
| `.nav-user` | `flex`, `gap: .5rem`, `align-items: center`, `font-weight: 500` |
| `.nav-avatar` | `26px` circle, `var(--accent-light)` / `var(--accent)`, `.72rem`, `600`, flex-centred |

The badge/bar modifiers share the `.cat-X` class name but differ by context (`.cat-badge.cat-food` tints, `.cat-bar-fill.cat-food` fills solid) — one slug from Python drives both.

### 4c. Responsive — reuse the existing breakpoints
Add to the **existing** `@media (max-width: 900px)` and `(max-width: 600px)` blocks (`style.css:583-599`) rather than inventing new ones. The 768px breakpoint is video-modal-only; table scrolling is handled by `.tx-table-wrap` at every width, so no new breakpoint is needed.

- **≤900px:** `.profile-grid { grid-template-columns: 1fr; }`
- **≤600px:** `.profile-section { padding: 2rem 1rem 3rem; }`; `.profile-identity { flex-direction: column; align-items: flex-start; }` and its `.btn-ghost { margin-left: 0; }`; `.tx-table { font-size: .85rem; }`; plus the navbar override:

```css
.nav-links a.nav-user { display: flex; }   /* beat the :not(.nav-cta) hide rule */
.nav-user-name { display: none; }          /* avatar only on small screens */
```

### 4d. Deliberately *not* reused
`.stat-card` / `.stat-value` / `.mock-bar-track` / `.mock-bar-*` (`style.css:234-300`) already implement stat tiles and progress bars — but they hardcode `white`, `#e8e8e8`, `#999`, `#ffa94d` etc., which violates the spec's token rule, and they're authored for the landing-page mock. New token-pure classes are used instead. Worth a follow-up ticket to migrate those mock classes onto tokens and collapse the duplication; out of scope here.

---

## 5. Verification

```bash
python app.py        # http://localhost:5001
```

| DoD item | How to confirm |
|---|---|
| Anonymous → `/login` | Fresh/incognito window → `http://localhost:5001/profile` lands on `/login`. CLI: `curl -si localhost:5001/profile \| head -5` → `302` + `Location: /login` |
| Logged in → 200 | Sign in `demo@spendly.com` / `demo123`, then `/profile` renders |
| Name + email card | Visible in `.profile-identity`, with a `DU` initials avatar |
| ≥3 summary stats | Total spent ₹566.24 · 8 transactions · Top category Shopping |
| ≥3 table rows | 8 rows render, newest (18 Sep) first |
| ≥3 breakdown categories | 7 categories, Shopping's bar full-width |
| Navbar logged-in state | Avatar + "Demo User" linking to `/profile`, beside "Sign out" |
| No hex in `profile.html` | `grep -nE "#[0-9a-fA-F]{3,8}" templates/profile.html` → **no output** |
| No inline styles | `grep -n 'style=' templates/profile.html` → **no output** |

Also check: `/` and `/login` still render unchanged (base.html was touched); resize to 1200 / 900 / 600px and confirm the grid collapses, the identity card stacks, the table scrolls rather than overflowing, and the navbar shows the avatar without the name.

Optional, since `pytest` + `pytest-flask` are already in `requirements.txt`: a `tests/test_profile.py` asserting `302` → `/login` for anonymous and `200` + `b"Demo User"` with `session["user_id"] = 1` set via `client.session_transaction()`. The spec doesn't require it; say the word and it goes in.

---

## 6. Risks and judgement calls

1. **Pre-existing flash bug.** `flash()` fires in `login`, `register` and `logout`, all of which redirect to `landing` — but only `login.html:16` and `register.html:16` render `get_flashed_messages()`, and `base.html` renders none. So every one of those messages is currently dropped or surfaces later on an auth page. `@login_required`'s "Please sign in" flash *does* land on `/login`, but styled with `.auth-success` (green) for what is really a notice. **Not fixed here** — the clean fix is moving flash rendering into `base.html` and deleting it from the two auth templates, which touches three files beyond this spec. Flagging it as the natural Step 5 cleanup.
2. **Pre-change sessions.** Anyone already logged in has no `session['user_name']`; the navbar shows "Account" until they re-login. Acceptable in a dev-only app.
3. **Currency.** The spec never names one. Using **₹**, following the footer tagline ("Track every rupee") and `landing.html:34` (`₹18,240`). Note the seeded amounts (8.75–200.00) read as dollar-scale; re-scaling the seed data is a separate call.
4. **Table-vs-list for the breakdown.** The spec allows either; progress-bar rows are chosen because they echo the landing-page hero mock, which is what a visitor has already seen.
5. **`seed_db()` at import.** `app.py:13-15` runs `init_db()` + `seed_db()` at import time, so the Flask reloader executes them twice per restart. Harmless (`seed_db` is idempotent) but out of scope.
6. **Hardcoded `secret_key`** (`app.py:7`) is a dev placeholder — unchanged by this step, worth addressing before any deployment.
