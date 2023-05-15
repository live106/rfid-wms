# Define a function to insert data into the table using parameterized query
def insert_data(barcode, product):
    conn, cursor = connect_db()
    cursor.execute("INSERT INTO product (barcode, product) VALUES (?, ?)", (barcode, product))
    conn.commit()
    conn.close()

# Define a function to delete data from the table using parameterized query
def delete_data(barcode):
    conn, cursor = connect_db()
    cursor.execute("DELETE FROM product WHERE barcode = ?", (barcode,))
    conn.commit()
    conn.close()

# Define a function to update data in the table using parameterized query
def update_data(barcode, product):
    conn, cursor = connect_db()
    cursor.execute("UPDATE product SET product = ? WHERE barcode = ?", (product, barcode))
    conn.commit()
    conn.close()

# Define a function to query data from the table using parameterized query
def query_data(barcode):
    conn, cursor = connect_db()
    cursor.execute("SELECT product FROM product WHERE barcode = ?", (barcode,))
    result = cursor.fetchone()
    conn.close()
    return result

# Define a function to get all the products from the table as a dictionary of barcode and product name
def get_products():
    conn, cursor = connect_db()
    cursor.execute("SELECT * FROM product")
    results = cursor.fetchall()
    conn.close()
    
     # Create an empty dictionary to store the products
     products = {}
     
     # Loop through the results and add them to the dictionary
     for barcode, product in results:
         products[barcode] = product
     
     # Return the dictionary
     return products
