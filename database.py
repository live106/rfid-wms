import sqlite3
import time

# Define a function to connect to sqlite database and create a cursor object
def connect_db():
    conn = sqlite3.connect("warehouse.db")
    cursor = conn.cursor()
    return conn, cursor

# Define a function to create a table if it does not exist with columns for barcode, product name, quantity and timestamp
def create_table():
    conn, cursor = connect_db()
    cursor.execute("CREATE TABLE IF NOT EXISTS in_storage (barcode TEXT PRIMARY KEY, product TEXT NOT NULL, quantity INTEGER NOT NULL DEFAULT 1, timestamp INTEGER NOT NULL)")
    conn.commit()
    conn.close()

# Define a function to insert data into the table using parameterized query
def insert_data(barcode, product, quantity):
    conn, cursor = connect_db()
    timestamp = int(time.time())
    cursor.execute("INSERT INTO in_storage (barcode, product, quantity, timestamp) VALUES (?, ?, ?, ?)", (barcode, product, quantity, timestamp))
    conn.commit()
    conn.close()

# Define a function to delete data from the table using parameterized query
def delete_data(barcode):
    conn, cursor = connect_db()
    cursor.execute("DELETE FROM in_storage WHERE barcode = ?", (barcode,))
    conn.commit()
    conn.close()

# Define a function to delete data from the table that are older than 2 days
def delete_old_data():
    conn, cursor = connect_db()
    
    # Get the current timestamp in seconds
    now = int(time.time())
    
    # Calculate the timestamp of 2 days ago
    two_days_ago = now - 2 * 24 * 60 * 60
    
    # Delete the data that have timestamp less than two_days_ago
    cursor.execute("DELETE FROM in_storage WHERE timestamp < ?", (two_days_ago,))
    conn.commit()
    conn.close()
