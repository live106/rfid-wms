import sqlite3
import time
from auto_express import Express
from config import DB_PATH, DATA_PATH

def create_table():
    conn = sqlite3.connect(DB_PATH)
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
            inventory_duration INTEGER DEFAULT 15,
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
            order_no TEXT,
            picking_no TEXT,
            FOREIGN KEY (inbound_id) REFERENCES inbounds(id)
        )
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS epcs_epc_idx ON epcs (epc)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS epcs_barcode_idx ON epcs (barcode)
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS express_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alias TEXT,
            name TEXT,
            username TEXT,
            password TEXT,
            username_field_name TEXT,
            password_field_name TEXT,
            login_url TEXT,
            logged_in_element_class TEXT,
            home_url TEXT,
            download_path TEXT
        )
    """)
    if not get_express_config(Express.SAGAWAEXP.value):
        add_express_config(Express.SAGAWAEXP.value, Express.SAGAWAEXP.value, '0476497727001', 'moal6173', 'user2', 'pass2', 'https://www.e-service.sagawa-exp.co.jp/auth/realms/sc/protocol/openid-connect/auth?response_type=code&scope=openid&client_id=sagawa-exp.co.jp&state=LfFylwnqdxU1SivhUBjX5LwPvPY&redirect_uri=https%3A%2F%2Fwww.e-service.sagawa-exp.co.jp%2Fredirect%2Fredirect_uri&nonce=3sNAU2WZclbg39LBLImJBxTV9ueiHvq_pt4svzzUcK4', 'logged-in', 'https://bmypage.kuronekoyamato.co.jp/bmypage/servlet/jp.co.kuronekoyamato.wur.hmp.servlet.user.HMPLGI0010JspServlet', str(DATA_PATH))
    if not get_express_config(Express.KURONEKOYAMATO.value):
        add_express_config(Express.KURONEKOYAMATO.value, Express.KURONEKOYAMATO.value, '080493385318', 'element06', 'CSTMR_CD', 'CSTMR_PSWD', 'https://bmypage.kuronekoyamato.co.jp/bmypage/servlet/jp.co.kuronekoyamato.wur.hmp.servlet.user.HMPLGI0010JspServlet', 'logged-in', 'https://bmypage.kuronekoyamato.co.jp/bmypage/servlet/jp.co.kuronekoyamato.wur.hmp.servlet.user.HMPLGI0010JspServlet', '')
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Type TEXT,
            JAN TEXT,
            Expiration TEXT,
            Qty INTEGER,
            ZIP TEXT,
            Address TEXT,
            Name TEXT,
            TEL TEXT,
            Comment1 TEXT,
            Comment2 TEXT,
            Comment3 TEXT,
            Comment4 TEXT,
            D_Date TEXT,
            D_Time TEXT,
            ShipperZIP TEXT,
            ShipperName TEXT,
            ShipperAddress TEXT,
            ShipperTel TEXT,
            PickingNo TEXT,
            OrNO TEXT,
            OutboundStatus TEXT DEFAULT 'waiting',
            Express TEXT,
            ExpressNo TEXT,
            ExpressTime TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shipper (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ShipperZIP TEXT,
            ShipperName TEXT,
            ShipperAddress TEXT,
            ShipperTel TEXT
        )
    """)
    check_shipper_table() 
    conn.commit()
    conn.close()

def add_inbound(barcode, name, quantity, timestamp=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if not timestamp:
        timestamp = int(round(time.time() * 1000))
    cursor.execute("INSERT INTO inbounds (barcode, name, quantity, timestamp) VALUES (?, ?, ?, ?)", (barcode, name, quantity, timestamp))
    conn.commit()
    inbound_id = cursor.lastrowid
    conn.close()
    return inbound_id

def delete_inbound(barcode):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inbounds WHERE barcode = ?", (barcode,))
    conn.commit()
    conn.close()

def update_inbound(barcode, quantity):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE inbounds SET quantity = ? WHERE barcode = ?", (quantity, barcode))
    conn.commit()
    conn.close()    

def delete_old_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = int(time.time())
    two_days_ago = now - 2 * 24 * 60 * 60
    cursor.execute("DELETE FROM inbounds WHERE timestamp < ?", (two_days_ago,))
    conn.commit()
    conn.close()

def get_inbound_name(barcode):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM inbounds WHERE barcode = ?", (barcode,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return None

def get_inbound_barcode(name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT barcode FROM inbounds WHERE name = ?", (name,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return None

def get_inbounds():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, barcode, name, quantity, timestamp FROM inbounds")
    results = cursor.fetchall()
    conn.close()
    return results

def add_product(barcode, name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (barcode, name) VALUES (?, ?)", (barcode, name))
    conn.commit()
    conn.close()

def delete_product(barcode):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE barcode = ?", (barcode,))
    conn.commit()
    conn.close()

def update_product(barcode, name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE products SET name = ? WHERE barcode = ?", (name, barcode))
    conn.commit()
    conn.close()    

def get_product_name(barcode):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM products WHERE barcode = ?", (barcode,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return None

def get_product_barcode(name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT barcode FROM products WHERE name = ?", (name,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return None

def get_products():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT barcode, name FROM products")
    results = cursor.fetchall()
    conn.close()
    return results

def add_rfid_reader_config(port=8080, antennas='1, 2', inventory_duration=30, inventory_api_retries=3, address='192.168.1.100', consecutive_count=3):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO rfid_reader_config (port, antennas, inventory_duration, inventory_api_retries, address, consecutive_count) VALUES (?, ?, ?, ?, ?, ?)", (port, antennas, inventory_duration, inventory_api_retries, address, consecutive_count))
    conn.commit()
    conn.close()

def delete_rfid_reader_config():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM rfid_reader_config")
    conn.commit()
    conn.close()

def update_rfid_reader_config(port=None, antennas=None, inventory_duration=None, inventory_api_retries=None, address=None, consecutive_count=None):
    conn = sqlite3.connect(DB_PATH)
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
    conn = sqlite3.connect(DB_PATH)
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
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if not timestamp:
        timestamp = int(round(time.time() * 1000))
    cursor.execute("INSERT INTO epcs (epc, barcode, name, inbound_id, timestamp) VALUES (?, ?, ?, ?, ?)", (epc, barcode, name, inbound_id, timestamp))
    conn.commit()
    conn.close()

def add_epcs(epc_list, barcode, name, inbound_id, timestamp=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if not timestamp:
        timestamp = int(round(time.time() * 1000))
    # convert epc_list to a list of tuples
    values = [(epc, barcode, name, inbound_id, timestamp) for epc in epc_list]
    # use executemany() to insert multiple values at once
    cursor.executemany("INSERT INTO epcs (epc, barcode, name, inbound_id, timestamp) VALUES (?, ?, ?, ?, ?)", values)
    conn.commit()
    conn.close()

def delete_epc(epc):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM epcs WHERE epc = ?", (epc,))
    conn.commit()
    conn.close()

def update_epcs(epc_list, updates):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for field, value in updates.items():
        if value is not None:
            cursor.execute(f"UPDATE epcs SET {field} = ? WHERE epc IN ({','.join('?'*len(epc_list))})", (value,) + tuple(epc_list))

    conn.commit()
    conn.close()

def get_epc_name(epc):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM epcs WHERE epc = ?", (epc,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return None

def get_epc_barcode(epc):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT barcode FROM epcs WHERE epc = ?", (epc,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return None

def get_epcs(query_dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Build the query string from the query_dict keys and values
    query_string = "SELECT epc, barcode, name, timestamp, picking_no, order_no  FROM epcs WHERE "
    query_params = []
    for key, value in query_dict.items():
        query_string += f"{key}=? AND "
        query_params.append(value)
    # Remove the last "AND " from the query string
    query_string = query_string[:-4]
    # Execute the query with the query_params
    cursor.execute(query_string, tuple(query_params))
    results = cursor.fetchall()
    conn.close()
    return results

# 查询还未出库的epc_list对应的各barcode数量
def get_valid_epc_barcode_counts(epc_list):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    epc_list = list(epc_list)
    cursor.execute("SELECT barcode, COUNT(*) as quantity FROM epcs WHERE picking_no is null and epc IN ({}) GROUP BY barcode".format(','.join('?'*len(epc_list))), epc_list)
    results = cursor.fetchall()
    conn.close()
    return {row[0]: row[1] for row in results}

def add_express_config(alias, name, username, password, username_field_name, password_field_name, login_url, logged_in_element_class, home_url, download_path):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO express_config (alias, name, username, password, username_field_name, password_field_name, login_url, logged_in_element_class, home_url, download_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (alias, name, username, password, username_field_name, password_field_name, login_url, logged_in_element_class, home_url, download_path))
    conn.commit()
    conn.close()

def delete_express_config(alias):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM express_config WHERE alias = ?", (alias,))
    conn.commit()
    conn.close()

def update_express_config(last_alias, new_alias, name, username=None, password=None, username_field_name=None, password_field_name=None, login_url=None, logged_in_element_class=None, home_url=None, download_path=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("UPDATE express_config SET alias = ?, name=?, username = ?, password = ?, username_field_name = ?, password_field_name = ?, login_url = ?, logged_in_element_class = ?, home_url = ?, download_path = ? WHERE alias = ?",
              (new_alias, name, username, password, username_field_name, password_field_name, login_url, logged_in_element_class, home_url, download_path, last_alias))

    conn.commit()
    conn.close()


def get_all_express_configs():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT alias, name, username, password, username_field_name, password_field_name, login_url, logged_in_element_class, home_url, download_path FROM express_config")
    result = cursor.fetchall()
    conn.close()
    if result:
        keys = ['alias', 'name', 'username', 'password', 'username_field_name', 'password_field_name', 'login_url', 'logged_in_element_class', 'home_url', 'download_path']
        return [dict(zip(keys, row)) for row in result]
    else:
        return None

def get_express_config(alias):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT alias, name, username, password, username_field_name, password_field_name, login_url, logged_in_element_class, home_url, download_path FROM express_config WHERE alias = ?", (alias,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {
            'alias': result[0],
            'name': result[1],
            'username': result[2],
            'password': result[3],
            'username_field_name': result[4],
            'password_field_name': result[5],
            'login_url': result[6],
            'logged_in_element_class': result[7],
            'home_url': result[8],
            'download_path': result[9],
        }
    else:
        return None

def get_express_config_by_name(name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT alias, name, username, password, username_field_name, password_field_name, login_url, logged_in_element_class, home_url, download_path FROM express_config WHERE name = ?", (name,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {
            'alias': result[0],
            'name': result[1],
            'username': result[2],
            'password': result[3],
            'username_field_name': result[4],
            'password_field_name': result[5],
            'login_url': result[6],
            'logged_in_element_class': result[7],
            'home_url': result[8],
            'download_path': result[9],
        }
    else:
        return None    

def add_order(order):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO orders (Type, JAN, Expiration, Qty, ZIP, Address, Name, TEL, Comment1, Comment2, Comment3, Comment4, D_Date, D_Time, ShipperZIP, ShipperName, ShipperAddress, ShipperTel, PickingNo, OrNO, OutboundStatus, Express, ExpressNo, ExpressTime)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
            order.get('Type', ''),
            order.get('JAN', ''),
            order.get('Expiration', ''),
            order.get('Qty', 0),
            order.get('ZIP', ''),
            order.get('Address', ''),
            order.get('Name', ''),
            order.get('TEL', ''),
            order.get('Comment1', ''),
            order.get('Comment2', ''),
            order.get('Comment3', ''),
            order.get('Comment4', ''),
            order.get('D_Date', ''),
            order.get('D_Time', ''),
            order.get('ShipperZIP', ''),
            order.get('ShipperName', ''),
            order.get('ShipperAddress', ''),
            order.get('ShipperTel', ''),
            order.get('PickingNo', ''),
            order.get('OrNO', ''),
            order.get('OutboundStatus', 'waiting'),
            order.get('Express', ''),
            order.get('ExpressNo', ''),
            order.get('ExpressTime', ''),        
    ))
    conn.commit()
    conn.close()

def add_orders(orders):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    insert_query = """
        INSERT INTO orders (Type, JAN, Expiration, Qty, ZIP, Address, Name, TEL, Comment1, Comment2, Comment3, Comment4, D_Date, D_Time, ShipperZIP, ShipperName, ShipperAddress, ShipperTel, PickingNo, OrNO, OutboundStatus, Express, ExpressNo, ExpressTime)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    insert_values = []
    for order in orders:
        insert_values.append((
            order.get('Type', ''),
            order.get('JAN', ''),
            order.get('Expiration', ''),
            order.get('Qty', 0),
            order.get('ZIP', ''),
            order.get('Address', ''),
            order.get('Name', ''),
            order.get('TEL', ''),
            order.get('Comment1', ''),
            order.get('Comment2', ''),
            order.get('Comment3', ''),
            order.get('Comment4', ''),
            order.get('D_Date', ''),
            order.get('D_Time', ''),
            order.get('ShipperZIP', ''),
            order.get('ShipperName', ''),
            order.get('ShipperAddress', ''),
            order.get('ShipperTel', ''),
            order.get('PickingNo', ''),
            order.get('OrNO', ''),
            order.get('OutboundStatus', 'waiting'),
            order.get('Express', ''),
            order.get('ExpressNo', ''),
            order.get('ExpressTime', ''),
        ))
    cursor.executemany(insert_query, insert_values)
    conn.commit()
    conn.close()    

def delete_order(order_no):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM orders WHERE OrNO = ?", (order_no,))
    conn.commit()
    conn.close()

def update_order(picking_no, updates):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for field, value in updates.items():
        if value is not None:
            cursor.execute(f"UPDATE orders SET {field} = ? WHERE PickingNo = ?", (value, picking_no))

    conn.commit()
    conn.close()

def get_orders_by_order_no(order_no):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Type, JAN, Expiration, Qty, ZIP, Address, Name, TEL, Comment1, Comment2, Comment3, Comment4, D_Date, D_Time, ShipperZIP, ShipperName, ShipperAddress, ShipperTel, PickingNo, OrNO, OutboundStatus, Express, ExpressNo, ExpressTime
        FROM orders
        WHERE OrNO = ?
    """, (order_no,))
    results = cursor.fetchall()
    conn.close()

    keys = ['Type', 'JAN', 'Expiration', 'Qty', 'ZIP', 'Address', 'Name', 'TEL', 'Comment1', 'Comment2', 'Comment3', 'Comment4', 'D_Date', 'D_Time', 'ShipperZIP', 'ShipperName', 'ShipperAddress', 'ShipperTel', 'PickingNo', 'OrNO', 'OutboundStatus', 'Express', 'ExpressNo', 'ExpressTime']
    return [dict(zip(keys, result)) for result in results]

def get_orders_by_picking_no(picking_no):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Type, JAN, Expiration, Qty, ZIP, Address, Name, TEL, Comment1, Comment2, Comment3, Comment4, D_Date, D_Time, ShipperZIP, ShipperName, ShipperAddress, ShipperTel, PickingNo, OrNO, OutboundStatus, Express, ExpressNo, ExpressTime
        FROM orders
        WHERE PickingNo = ?
    """, (picking_no,))
    results = cursor.fetchall()
    conn.close()

    keys = ['Type', 'JAN', 'Expiration', 'Qty', 'ZIP', 'Address', 'Name', 'TEL', 'Comment1', 'Comment2', 'Comment3', 'Comment4', 'D_Date', 'D_Time', 'ShipperZIP', 'ShipperName', 'ShipperAddress', 'ShipperTel', 'PickingNo', 'OrNO', 'OutboundStatus', 'Express', 'ExpressNo', 'ExpressTime']
    return [dict(zip(keys, result)) for result in results]

def get_orders_by_order_nos(order_nos):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    placeholders = ', '.join(['?'] * len(order_nos))
    query = f"SELECT Type, JAN, Expiration, Qty, ZIP, Address, Name, TEL, Comment1, Comment2, Comment3, Comment4, D_Date, D_Time, ShipperZIP, ShipperName, ShipperAddress, ShipperTel, PickingNo, OrNO, OutboundStatus, Express, ExpressNo, ExpressTime FROM orders WHERE OrNO IN ({placeholders})"
    cursor.execute(query, order_nos)
    results = cursor.fetchall()
    conn.close()

    keys = ['Type', 'JAN', 'Expiration', 'Qty', 'ZIP', 'Address', 'Name', 'TEL', 'Comment1', 'Comment2', 'Comment3', 'Comment4', 'D_Date', 'D_Time', 'ShipperZIP', 'ShipperName', 'ShipperAddress', 'ShipperTel', 'PickingNo', 'OrNO', 'OutboundStatus', 'Express', 'ExpressNo', 'ExpressTime']
    return [dict(zip(keys, result)) for result in results]

def get_orders_by_picking_nos(picking_nos):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    placeholders = ', '.join(['?'] * len(picking_nos))
    query = f"SELECT Type, JAN, Expiration, Qty, ZIP, Address, Name, TEL, Comment1, Comment2, Comment3, Comment4, D_Date, D_Time, ShipperZIP, ShipperName, ShipperAddress, ShipperTel, PickingNo, OrNO, OutboundStatus, Express, ExpressNo, ExpressTime FROM orders WHERE PickingNo IN ({placeholders})"
    cursor.execute(query, picking_nos)
    results = cursor.fetchall()
    conn.close()

    keys = ['Type', 'JAN', 'Expiration', 'Qty', 'ZIP', 'Address', 'Name', 'TEL', 'Comment1', 'Comment2', 'Comment3', 'Comment4', 'D_Date', 'D_Time', 'ShipperZIP', 'ShipperName', 'ShipperAddress', 'ShipperTel', 'PickingNo', 'OrNO', 'OutboundStatus', 'Express', 'ExpressNo', 'ExpressTime']
    return [dict(zip(keys, result)) for result in results]

def get_orders():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Type, JAN, Expiration, Qty, ZIP, Address, Name, TEL, Comment1, Comment2, Comment3, Comment4, D_Date, D_Time, ShipperZIP, ShipperName, ShipperAddress, ShipperTel, PickingNo, OrNO, OutboundStatus, Express, ExpressNo, ExpressTime
        FROM orders
    """)
    results = cursor.fetchall()
    conn.close()

    keys = ['Type', 'JAN', 'Expiration', 'Qty', 'ZIP', 'Address', 'Name', 'TEL', 'Comment1', 'Comment2', 'Comment3', 'Comment4', 'D_Date', 'D_Time', 'ShipperZIP', 'ShipperName', 'ShipperAddress', 'ShipperTel', 'PickingNo', 'OrNO', 'OutboundStatus', 'Express', 'ExpressNo', 'ExpressTime']
    return [dict(zip(keys, result)) for result in results]

def add_shipper(shipper_zip, shipper_name, shipper_address, shipper_tel):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO shipper (ShipperZIP, ShipperName, ShipperAddress, ShipperTel) VALUES (?, ?, ?, ?)", (shipper_zip, shipper_name, shipper_address, shipper_tel))
    conn.commit()
    conn.close()

def delete_shipper(shipper_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM shipper WHERE id = ?", (shipper_id,))
    conn.commit()
    conn.close()

def update_shipper(shipper_zip=None, shipper_name=None, shipper_address=None, shipper_tel=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if shipper_zip:
        c.execute("UPDATE shipper SET ShipperZIP = ?", (shipper_zip,))
    if shipper_name:
        c.execute("UPDATE shipper SET ShipperName = ?", (shipper_name,))
    if shipper_address:
        c.execute("UPDATE shipper SET ShipperAddress = ?", (shipper_address,))
    if shipper_tel:
        c.execute("UPDATE shipper SET ShipperTel = ?", (shipper_tel,))
    conn.commit()
    conn.close()

def get_shipper(shipper_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT ShipperZIP, ShipperName, ShipperAddress, ShipperTel FROM shipper WHERE id = ?", (shipper_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {
            'ShipperZIP': result[0],
            'ShipperName': result[1],
            'ShipperAddress': result[2],
            'ShipperTel': result[3]
        }
    else:
        return None
    
def get_shipper_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT ShipperZIP, ShipperName, ShipperAddress, ShipperTel FROM shipper LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    if result:
        return {
            'ShipperZIP': result[0],
            'ShipperName': result[1],
            'ShipperAddress': result[2],
            'ShipperTel': result[3]
        }
    else:
        return None

def check_shipper_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM shipper")
    result = cursor.fetchone()
    count = result[0]
    if count == 0:
        # 表为空，添加默认数据
        add_shipper('286-0113', 'ＪＧ０９－１株式会社', '千葉県成田市南三里塚７８－７プロロジスパック', '080-6009-7887')
    conn.close()

