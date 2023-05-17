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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rfid_reader_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            port INTEGER DEFAULT 8080,
            antennas TEXT DEFAULT '1, 2',
            inventory_duration INTEGER DEFAULT 30,
            inventory_api_retries INTEGER DEFAULT 3,
            address TEXT DEFAULT '192.168.1.100',
            consecutive_count INTEGER DEFAULT 3
        )
    """)
    if not get_rfid_reader_config():
        add_rfid_reader_config()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS epcs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            epc TEXT,
            barcode TEXT,
            name TEXT,
            timestamp INTEGER DEFAULT (strftime('%s', 'now') * 1000),
            inbound_id INTEGER,
            FOREIGN KEY (inbound_id) REFERENCES inbounds(id)
        )
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS epcs_epc_idx ON epcs (epc)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS epcs_barcode_idx ON epcs (barcode)
    """)
    conn.commit()
    conn.close()

def add_inbound(barcode, name, quantity, timestamp=None):
    conn = sqlite3.connect("rfid_wms.db")
    cursor = conn.cursor()
    if not timestamp:
        timestamp = int(round(time.time() * 1000))
    cursor.execute("INSERT INTO inbounds (barcode, name, quantity, timestamp) VALUES (?, ?, ?, ?)", (barcode, name, quantity, timestamp))
    conn.commit()
    inbound_id = cursor.lastrowid
    conn.close()
    return inbound_id

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
    cursor.execute("SELECT id, barcode, name, quantity, timestamp FROM inbounds")
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

def add_rfid_reader_config(port=8080, antennas='1, 2', inventory_duration=30, inventory_api_retries=3, address='192.168.1.100', consecutive_count=3):
    conn = sqlite3.connect("rfid_wms.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO rfid_reader_config (port, antennas, inventory_duration, inventory_api_retries, address, consecutive_count) VALUES (?, ?, ?, ?, ?, ?)", (port, antennas, inventory_duration, inventory_api_retries, address, consecutive_count))
    conn.commit()
    conn.close()

def delete_rfid_reader_config():
    conn = sqlite3.connect("rfid_wms.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM rfid_reader_config")
    conn.commit()
    conn.close()

def update_rfid_reader_config(port=None, antennas=None, inventory_duration=None, inventory_api_retries=None, address=None, consecutive_count=None):
    conn = sqlite3.connect("rfid_wms.db")
    c = conn.cursor()
    if port:
        c.execute("UPDATE rfid_reader_config SET port = ?", (port,))
    if antennas:
        c.execute("UPDATE rfid_reader_config SET antennas = ?", (antennas,))
    if inventory_duration:
        c.execute("UPDATE rfid_reader_config SET inventory_duration = ?", (inventory_duration,))
    if inventory_api_retries:
        c.execute("UPDATE rfid_reader_config SET inventory_api_retries = ?", (inventory_api_retries,))
    if address:
        c.execute("UPDATE rfid_reader_config SET address = ?", (address,))
    if consecutive_count:
        c.execute("UPDATE rfid_reader_config SET consecutive_count = ?", (consecutive_count,))
    conn.commit()
    conn.close()

def get_rfid_reader_config():
    conn = sqlite3.connect("rfid_wms.db")
    cursor = conn.cursor()
    cursor.execute("SELECT port, antennas, inventory_duration, inventory_api_retries, address, consecutive_count FROM rfid_reader_config")
    result = cursor.fetchone()
    conn.close()
    if result:
        return {
            'port': result[0],
            'antennas': result[1],
            'inventory_duration': result[2],
            'inventory_api_retries': result[3],
            'address': result[4],
            'consecutive_count': result[5]
        }
    else:
        return None

def add_epc(epc, barcode, name, inbound_id, timestamp=None):
    conn = sqlite3.connect("rfid_wms.db")
    cursor = conn.cursor()
    if not timestamp:
        timestamp = int(round(time.time() * 1000))
    cursor.execute("INSERT INTO epcs (epc, barcode, name, inbound_id, timestamp) VALUES (?, ?, ?, ?, ?)", (epc, barcode, name, inbound_id, timestamp))
    conn.commit()
    conn.close()

def add_epcs(epc_list, barcode, name, inbound_id, timestamp=None):
    conn = sqlite3.connect("rfid_wms.db")
    cursor = conn.cursor()
    if not timestamp:
        timestamp = int(round(time.time() * 1000))
    for epc in epc_list:
        cursor.execute("INSERT INTO epcs (epc, barcode, name, inbound_id, timestamp) VALUES (?, ?, ?, ?, ?)", (epc, barcode, name, inbound_id, timestamp))
    conn.commit()
    conn.close()

def delete_epc(epc):
    conn = sqlite3.connect("rfid_wms.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM epcs WHERE epc = ?", (epc,))
    conn.commit()
    conn.close()

def update_epc(epc, barcode=None, name=None, timestamp=None):
    conn = sqlite3.connect("rfid_wms.db")
    c = conn.cursor()
    if barcode:
        c.execute("UPDATE epcs SET barcode = ? WHERE epc = ?", (barcode, epc))
    if name:
        c.execute("UPDATE epcs SET name = ? WHERE epc = ?", (name, epc))
    if timestamp:
        c.execute("UPDATE epcs SET timestamp = ? WHERE epc = ?", (timestamp, epc))
    conn.commit()
    conn.close()    

def get_epc_name(epc):
    conn = sqlite3.connect("rfid_wms.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM epcs WHERE epc = ?", (epc,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return None

def get_epc_barcode(epc):
    conn = sqlite3.connect("rfid_wms.db")
    cursor = conn.cursor()
    cursor.execute("SELECT barcode FROM epcs WHERE epc = ?", (epc,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return None

def get_epcs(inbound_id):
    conn = sqlite3.connect("rfid_wms.db")
    cursor = conn.cursor()
    cursor.execute("SELECT epc, barcode, name, timestamp FROM epcs WHERE inbound_id=?", (inbound_id,))
    results = cursor.fetchall()
    conn.close()
    return results