#!/usr/bin/env python3
"""
Script to seed random expenses for a specific user.
Usage: python seed_expenses.py <user_id> <count> <months>
"""

import sqlite3
import random
import sys
from datetime import datetime, timedelta

# Import the database filename from db.py
from database.db import DATABASE

# Category configurations with realistic Indian amounts (in ₹) and descriptions
CATEGORIES = {
    'Food': {
        'weight': 35,  # Most common
        'amount_range': (50, 800),
        'descriptions': [
            'Grocery shopping', 'Restaurant dinner', 'Street food', 'Breakfast at cafe',
            'Lunch delivery', 'Tea and snacks', 'Dinner takeout', 'Fresh vegetables',
            'Milk and bread', 'Biryani order', 'Dosa breakfast', 'Paneer dishes',
            'Fruit purchase', 'Sweets from local shop', 'Coffee shop'
        ]
    },
    'Transport': {
        'weight': 25,
        'amount_range': (20, 500),
        'descriptions': [
            'Auto rickshaw fare', 'Metro card recharge', 'Bus pass', 'Uber ride',
            'Ola cab', 'Petrol refill', 'Bike maintenance', 'Parking fee',
            'Railway ticket', 'Local train pass', 'Rapido bike taxi'
        ]
    },
    'Bills': {
        'weight': 15,
        'amount_range': (200, 3000),
        'descriptions': [
            'Electricity bill', 'Internet bill', 'Mobile recharge', 'DTH recharge',
            'Water bill', 'Gas cylinder', 'Broadband payment', 'Phone bill',
            'Postpaid mobile', 'Netflix subscription', 'Amazon Prime'
        ]
    },
    'Shopping': {
        'weight': 12,
        'amount_range': (200, 5000),
        'descriptions': [
            'Clothing purchase', 'Shoes', 'Electronics', 'Home decor',
            'Flipkart order', 'Amazon shopping', 'Myntra clothes', 'Books',
            'Kitchen items', 'Accessories', 'Gadgets', 'Furniture'
        ]
    },
    'Entertainment': {
        'weight': 8,
        'amount_range': (100, 1500),
        'descriptions': [
            'Movie tickets', 'Concert', 'Cricket match', 'Gaming',
            'Weekend outing', 'Amusement park', 'Museum entry', 'Sports event',
            'Theatre show', 'Music streaming', 'OTT subscription'
        ]
    },
    'Health': {
        'weight': 8,
        'amount_range': (100, 2000),
        'descriptions': [
            'Pharmacy medicines', 'Doctor consultation', 'Lab tests',
            'Health checkup', 'Dental visit', 'Eye checkup', 'Gym membership',
            'Vitamins and supplements', 'First aid supplies', 'Medical supplies'
        ]
    },
    'Other': {
        'weight': 7,
        'amount_range': (50, 1000),
        'descriptions': [
            'Miscellaneous', 'Gifts', 'Donations', 'Repairs',
            'Stationery', 'Personal care', 'Salon visit', 'Pet supplies',
            'Household items', 'Laundry', 'Dry cleaning'
        ]
    }
}


def get_db_connection():
    """Get a direct database connection"""
    conn = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def verify_user_exists(conn, user_id):
    """Check if user exists in the database"""
    cursor = conn.execute('SELECT id, name, email FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    return user


def generate_random_date(months_back):
    """Generate a random date within the past N months"""
    today = datetime.now()
    earliest = today - timedelta(days=months_back * 30)

    # Random number of days between earliest and today
    days_diff = (today - earliest).days
    random_days = random.randint(0, days_diff)

    random_date = earliest + timedelta(days=random_days)
    return random_date.strftime('%Y-%m-%d')


def select_category():
    """Select a category based on weights"""
    categories = list(CATEGORIES.keys())
    weights = [CATEGORIES[cat]['weight'] for cat in categories]
    return random.choices(categories, weights=weights, k=1)[0]


def generate_expense(user_id, months_back):
    """Generate a single random expense"""
    category = select_category()
    config = CATEGORIES[category]

    # Random amount within range
    amount = round(random.uniform(*config['amount_range']), 2)

    # Random description
    description = random.choice(config['descriptions'])

    # Random date
    date = generate_random_date(months_back)

    return (user_id, amount, category, date, description)


def insert_expenses(conn, user_id, count, months):
    """Generate and insert expenses in a single transaction"""
    try:
        # Generate all expenses
        expenses = [generate_expense(user_id, months) for _ in range(count)]

        # Sort by date for cleaner output
        expenses.sort(key=lambda x: x[3])

        # Insert all in one transaction
        cursor = conn.cursor()
        for expense in expenses:
            cursor.execute(
                '''INSERT INTO expenses (user_id, amount, category, date, description)
                   VALUES (?, ?, ?, ?, ?)''',
                expense
            )

        conn.commit()
        return expenses

    except Exception as e:
        conn.rollback()
        raise e


def main():
    """Main function"""
    # Parse arguments
    if len(sys.argv) != 4:
        print("Usage: /seed-expenses <user_id> <count> <months>")
        print("Example: /seed-expenses 1 50 6")
        sys.exit(1)

    try:
        user_id = int(sys.argv[1])
        count = int(sys.argv[2])
        months = int(sys.argv[3])
    except ValueError:
        print("Usage: /seed-expenses <user_id> <count> <months>")
        print("Example: /seed-expenses 1 50 6")
        sys.exit(1)

    # Connect to database
    conn = get_db_connection()

    # Verify user exists
    user = verify_user_exists(conn, user_id)
    if not user:
        print(f"No user found with id {user_id}.")
        conn.close()
        sys.exit(1)

    # Generate and insert expenses
    try:
        expenses = insert_expenses(conn, user_id, count, months)

        # Calculate date range
        dates = [exp[3] for exp in expenses]
        date_range = f"{min(dates)} to {max(dates)}"

        # Print confirmation
        print(f"Successfully inserted {count} expenses for user {user_id} ({user['name']})")
        print(f"Date range: {date_range}")
        print(f"\nSample of 5 expenses:")
        print(f"{'Date':<12} {'Category':<15} {'Amount':>10} {'Description':<30}")
        print("-" * 70)

        # Show up to 5 samples, evenly distributed
        sample_size = min(5, len(expenses))
        if sample_size > 0:
            step = len(expenses) // sample_size if sample_size > 1 else 1
            sample_indices = [i * step for i in range(sample_size)]

            for idx in sample_indices[:sample_size]:
                user_id, amount, category, date, description = expenses[idx]
                print(f"{date:<12} {category:<15} Rs.{amount:>7.2f} {description:<30}")

    except Exception as e:
        print(f"Error inserting expenses: {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == '__main__':
    main()
