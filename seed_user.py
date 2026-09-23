#!/usr/bin/env python3
"""
Script to seed a single random Indian user into the database.
Generates realistic Indian names and emails, checks for uniqueness, and inserts the user.
"""

import sqlite3
import random
from datetime import datetime
from werkzeug.security import generate_password_hash

DATABASE = 'expense_tracker.db'

# Realistic Indian first names across regions
FIRST_NAMES = [
    # North India
    'Rahul', 'Priya', 'Amit', 'Anjali', 'Vikram', 'Neha', 'Arjun', 'Pooja',
    'Rohan', 'Divya', 'Kunal', 'Sneha', 'Aditya', 'Kavya', 'Sanjay', 'Ritu',
    # South India
    'Karthik', 'Lakshmi', 'Suresh', 'Meena', 'Rajesh', 'Saranya', 'Venkat', 'Deepa',
    'Arun', 'Sowmya', 'Murali', 'Preethi', 'Kumar', 'Nisha', 'Ravi', 'Sangeetha',
    # West India
    'Jay', 'Diya', 'Chirag', 'Ananya', 'Nikhil', 'Isha', 'Karan', 'Mahek',
    'Dhruv', 'Tanvi', 'Ronak', 'Shreya', 'Veer', 'Riya', 'Harsh', 'Kiara',
    # East India
    'Arnav', 'Ria', 'Sourav', 'Anushka', 'Debashish', 'Tithi', 'Abhishek', 'Diya',
    'Subham', 'Maitreyi', 'Soham', 'Ishita', 'Aritra', 'Sanjana', 'Aniket', 'Pallavi'
]

# Common Indian surnames across regions
LAST_NAMES = [
    # North India
    'Sharma', 'Verma', 'Singh', 'Kumar', 'Gupta', 'Agarwal', 'Patel', 'Reddy',
    'Malhotra', 'Kapoor', 'Chopra', 'Joshi', 'Mehta', 'Kulkarni', 'Desai', 'Bhat',
    # South India
    'Iyer', 'Krishnan', 'Nair', 'Menon', 'Pillai', 'Rao', 'Naidu', 'Reddy',
    'Subramanian', 'Venkatesh', 'Ramesh', 'Srinivasan', 'Murthy', 'Hegde', 'Pai', 'Shetty',
    # Various regions
    'Das', 'Roy', 'Sen', 'Dutta', 'Banerjee', 'Chakraborty', 'Mukherjee', 'Ghosh'
]

# Popular email domains in India
EMAIL_DOMAINS = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com']


def get_db_connection():
    """Get a direct database connection (not using Flask's g context)"""
    conn = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def generate_indian_user():
    """Generate a realistic random Indian user"""
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    name = f"{first_name} {last_name}"

    # Generate email from name with random suffix
    email_name = f"{first_name.lower()}.{last_name.lower()}"
    suffix = random.randint(10, 999)
    domain = random.choice(EMAIL_DOMAINS)
    email = f"{email_name}{suffix}@{domain}"

    # Hash the password
    password_hash = generate_password_hash('password123')

    # Current datetime in ISO format
    created_at = datetime.now().isoformat(sep=' ', timespec='seconds')

    return {
        'name': name,
        'email': email,
        'password_hash': password_hash,
        'created_at': created_at
    }


def email_exists(conn, email):
    """Check if an email already exists in the database"""
    cursor = conn.execute('SELECT COUNT(*) as count FROM users WHERE email = ?', (email,))
    result = cursor.fetchone()
    return result['count'] > 0


def insert_user(conn, user_data):
    """Insert a user into the database"""
    cursor = conn.execute(
        'INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)',
        (user_data['name'], user_data['email'], user_data['password_hash'], user_data['created_at'])
    )
    conn.commit()
    return cursor.lastrowid


def main():
    """Main function to seed a random Indian user"""
    conn = get_db_connection()

    # Generate a unique user (retry if email exists)
    max_attempts = 100
    for attempt in range(max_attempts):
        user_data = generate_indian_user()

        if not email_exists(conn, user_data['email']):
            # Email is unique, insert the user
            user_id = insert_user(conn, user_data)

            # Print confirmation
            print("User created successfully!")
            print(f"  ID:    {user_id}")
            print(f"  Name:  {user_data['name']}")
            print(f"  Email: {user_data['email']}")

            conn.close()
            return

        # Email exists, try again
        if attempt < max_attempts - 1:
            continue
        else:
            print(f"Failed to generate unique email after {max_attempts} attempts")
            conn.close()
            return


if __name__ == '__main__':
    main()
