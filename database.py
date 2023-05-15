import sqlite3
import time

def create_table():
    conn = sqlite3.connect("rfid_wms.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inbounds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT,
            name TEXT,
            quantity INTEGER,
            timestamp INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT,
            name TEXT
        )
    """)    
    conn.commit()
    conn.close()

def add_inbound(barcode, name, quantity, timestamp):
    conn = sqlite3.connect("rfid_wms.db")
    cursor = conn.cursor()
    timestamp = int(round(time.time() * 1000))
    cursor.execute("INSERT INTO inbounds (barcode, name, quantity, timestamp) VALUES (?, ?, ?, ?)", (barcode, name, quantity, timestamp))
    conn.commit()
    conn.close()

def delete_inbound(barcode):
    conn = sqlite3.connect("rfid_wms.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inbounds WHERE barcode = ?", (barcode,))
    conn.commit()
    conn.close()

def update_inbound(barcode, quantity):
    conn = sqlite3.connect("rfid_wms.db")
    c = conn.cursor()
    c.execute("UPDATE inbounds SET quantity = ? WHERE barcode = ?", (quantity, barcode))
    conn.commit()
    conn.close()    

def delete_old_data():
    conn = sqlite3.connect("rfid_wms.db")
    cursor = conn.cursor()
    now = int(time.time())
    two_days_ago = now - 2 * 24 * 60 * 60
    cursor.execute("DELETE FROM inbounds WHERE timestamp < ?", (two_days_ago,))
    conn.commit()
    conn.close()

def get_inbound_name(barcode):
    conn = sqlite3.connect("rfid_wms.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM inbounds WHERE barcode = ?", (barcode,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return None

def get_inbound_barcode(name):
    conn = sqlite3.connect("rfid_wms.db")
    cursor = conn.cursor()
    cursor.execute("SELECT barcode FROM inbounds WHERE name = ?", (name,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return None

def get_inbounds():
    conn = sqlite3.connect("rfid_wms.db")
    cursor = conn.cursor()
    cursor.execute("SELECT barcode, name, quantity, timestamp FROM inbounds")
    results = cursor.fetchall()
    conn.close()
    return results

def add_product(barcode, name):
    conn = sqlite3.connect("rfid_wms.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (barcode, name) VALUES (?, ?)", (barcode, name))
    conn.commit()
    conn.close()

def delete_product(barcode):
    conn = sqlite3.connect("rfid_wms.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE barcode = ?", (barcode,))
    conn.commit()
    conn.close()

def update_product(barcode, name):
    conn = sqlite3.connect("rfid_wms.db")
    c = conn.cursor()
    c.execute("UPDATE products SET name = ? WHERE barcode = ?", (name, barcode))
    conn.commit()
    conn.close()    

def get_product_name(barcode):
    conn = sqlite3.connect("rfid_wms.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM products WHERE barcode = ?", (barcode,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return None

def get_product_barcode(name):
    conn = sqlite3.connect("rfid_wms.db")
    cursor = conn.cursor()
    cursor.execute("SELECT barcode FROM products WHERE name = ?", (name,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return None

def get_products():
    conn = sqlite3.connect("rfid_wms.db")
    cursor = conn.cursor()
    cursor.execute("SELECT barcode, name FROM products")
    results = cursor.fetchall()
    conn.close()
    return results    