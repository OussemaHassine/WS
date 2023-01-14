import sqlite3
import csv

# Connect to the database
connection = sqlite3.connect('database.db')
cursor = connection.cursor()

# Create the table
cursor.execute('''CREATE TABLE scholarships (
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    amount TEXT,
                    institution TEXT,
                    degree TEXT,
                    field TEXT,
                    students TEXT,
                    location TEXT,
                    deadline TEXT,
                    creator TEXT
                )''')

#create users table
cursor.execute('''CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, email TEXT, password TEXT)''')


# Open the CSV file
with open("scholarships.csv", "r",encoding="utf-8") as f:
    # Create a CSV reader
    reader = csv.reader(f)

    # Skip the header row
    next(reader)

    # Create a list of tuples to hold the rows from the CSV file
    rows = [(int(row[0]), row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]) for row in reader]

    # Insert the rows from the CSV file into the table
    cursor.executemany("INSERT INTO scholarships (id, title, amount, institution, degree, field, students, location, deadline) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", rows)

# Commit the changes and close the connection
connection.commit()
connection.close()
