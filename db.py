import mysql.connector

def get_db_connection():
    """
    Create and return MySQL connection
    """
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="pharmacy_db"
    )
def product_exists(name):
    """
    Check if a product exists in the database
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT id FROM product WHERE LOWER(name) = LOWER(%s)"
    cursor.execute(query, (name.strip(),))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    return result is not None

def product_exists_by_id(product_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT id FROM product WHERE id = %s"
    cursor.execute(query, (product_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result is not None


def insert_product(name, price):
    """
    Insert a new product into the database
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "INSERT INTO product (name, price, qty, created_at, updated_at) VALUES (%s, %s, %s, CURDATE(), CURDATE())"
    cursor.execute(query, (name, price, 0))
    conn.commit()
    product_id = cursor.lastrowid

    cursor.execute("SELECT * FROM product WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    cursor.close()
    conn.close()

    return product

def get_all_products():
    """
    Fetch all products from DB
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM product"
    cursor.execute(query)
    products = cursor.fetchall()
    cursor.close()
    conn.close()

    return products

def get_product_by_id(product_id):
    """
    Fetch a product by its ID
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM product WHERE id = %s"
    cursor.execute(query, (product_id,))
    product = cursor.fetchone()
    cursor.close()
    conn.close()

    return product  

def product_name_exists_by_id(name, product_id):
    """
    Check if a product name exists in the database excluding a specific product ID
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT id FROM product WHERE LOWER(name) = LOWER(%s) AND id != %s"
    cursor.execute(query, (name.strip(), product_id))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    return result is not None


def update_product(product_id, name, price):
    """
    Update product name and price, update updated_at only
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "UPDATE product SET name = %s, price = %s, updated_at = CURDATE() WHERE id = %s"
    cursor.execute(query, (name, price, product_id))
    conn.commit()

    cursor.execute("SELECT * FROM product WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    cursor.close()
    conn.close()

    return product

def delete_product(product_id):
    """
    Delete a product by its ID
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "DELETE FROM product WHERE id = %s"
        cursor.execute(query, (product_id,))
        conn.commit()
        affected_rows = cursor.rowcount
        cursor.close()
        conn.close()

        # Return True if a row was deleted, else False
        return affected_rows > 0

    except Exception as e:
        print("Error deleting product:", e)
        return False

# ----------------- BATCH RELATED FUNCTIONS -----------------
def get_batches_by_product_id(product_id):
    """
    Fetch all batches for a given product_id
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM batch WHERE product_id = %s"
    cursor.execute(query, (product_id,))
    batches = cursor.fetchall()
    cursor.close()
    conn.close()
    return batches

def insert_batch(product_id, qty, expiry_date, created_at, updated_at):
    """
    Insert a new batch for a product
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO batch (product_id, qty, expiry_date, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (product_id, qty, expiry_date, created_at, updated_at))
    conn.commit()
    batch_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return batch_id

def update_product_quantity(product_id):
    """
    Update the quantity of the product by summing all its batches
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    # Sum qty from all batches for this product
    query = "SELECT SUM(qty) as total_qty FROM batch WHERE product_id = %s"
    cursor.execute(query, (product_id,))
    result = cursor.fetchone()
    total_qty = result[0] if result[0] is not None else 0

    # Update product table
    query_update = "UPDATE product SET qty = %s, updated_at = CURDATE() WHERE id = %s"
    cursor.execute(query_update, (total_qty, product_id))
    conn.commit()
    cursor.close()
    conn.close()

def get_all_batches():
    """
    Fetch all batches from the database
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM batch"
    cursor.execute(query)
    batches = cursor.fetchall()
    cursor.close()
    conn.close()
    return batches 

def get_batch_by_id(batch_id):
    """
    Fetch a batch by its ID
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM batch WHERE batch_id = %s"
    cursor.execute(query, (batch_id,))
    batch = cursor.fetchone()
    cursor.close()
    conn.close()
    return batch 

def update_batch_qty(batch_id, new_qty):
    """
    Update the quantity of a batch
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "UPDATE batch SET qty = %s, updated_at = CURDATE() WHERE batch_id = %s"
    cursor.execute(query, (new_qty, batch_id))
    conn.commit()
    cursor.close()
    conn.close()    


def delete_batch(batch_id):
    """
    Delete a batch by its ID
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "DELETE FROM batch WHERE batch_id = %s"
        cursor.execute(query, (batch_id,))
        conn.commit()
        affected_rows = cursor.rowcount
        cursor.close()
        conn.close()

        # Return True if a row was deleted, else False
        return affected_rows > 0

    except Exception as e:
        print("Error deleting batch:", e)
        return False       


# ----------------- SALE RELATED FUNCTIONS -----------------

def get_batches_for_sale(product_id):
    """
    Fetch batches with qty > 0 for a given product_id, ordered by expiry_date ascending
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT * FROM batch
        WHERE product_id = %s AND qty > 0
        ORDER BY expiry_date ASC
    """
    cursor.execute(query, (product_id,))
    batches = cursor.fetchall()
    cursor.close()
    conn.close()
    return batches  

def insert_sale(total_amount):
    """
    Insert a new sale record
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO sales (total_amount,sale_date,created_at)
        VALUES (%s, CURDATE(), CURDATE())
    """
    cursor.execute(query, (total_amount,))
    conn.commit()
    sale_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return sale_id  


def insert_sale_item(sale_id, product_id, unit_price, quantity, subtotal):
    """
    Insert a new sale item record
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO sales_items (sale_id, product_id, unit_price, quantity, subtotal,created_at)
        VALUES (%s, %s, %s, %s, %s, CURDATE())
    """
    cursor.execute(query, (sale_id, product_id, unit_price, quantity, subtotal))
    conn.commit()
    cursor.close()
    conn.close()

def update_batch_quantity(batch_id, new_qty):
    """
    Update the quantity of a batch
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "UPDATE batch SET qty = %s, updated_at = CURDATE() WHERE batch_id = %s"
    cursor.execute(query, (new_qty, batch_id))
    conn.commit()
    cursor.close()
    conn.close()    

def update_product_quantity(product_id):
    """
    Recalculate total product quantity from batches
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    # Sum qty from all batches for this product
    query = "SELECT SUM(qty) as total_qty FROM batch WHERE product_id = %s"
    cursor.execute(query, (product_id,))
    result = cursor.fetchone()
    total_qty = result[0] if result[0] is not None else 0

    # Update product table
    query_update = "UPDATE product SET qty = %s, updated_at = CURDATE() WHERE id = %s"
    cursor.execute(query_update, (total_qty, product_id))
    conn.commit()
    cursor.close()
    conn.close( )

def get_product_price(product_id):
    """
    Fetch the price of a product by its ID
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT price FROM product WHERE id = %s"
    cursor.execute(query, (product_id,))
    product = cursor.fetchone()
    cursor.close()
    conn.close()
    return product[0] if product else None


def get_all_sales():
    """
    Fetch all sales records
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT sale_id, sale_date, total_amount, created_at
        FROM sales
        ORDER BY sale_id ASC
    """
    cursor.execute(query)
    sales = cursor.fetchall()

    cursor.close()
    conn.close()
    return sales


def get_sale_items_by_sale_id(sale_id):
    """
    Fetch all sale items for a given sale_id
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT
            sale_item_id,
            sale_id,
            product_id,
            quantity,
            unit_price,
            subtotal,
            created_at
        FROM sales_items
        WHERE sale_id = %s
        ORDER BY sale_item_id ASC
    """
    cursor.execute(query, (sale_id,))
    items = cursor.fetchall()

    cursor.close()
    conn.close()
    return items
