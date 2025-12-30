from product import app
from flask import request, jsonify
from datetime import date, datetime
from db import (
    get_db_connection,
    get_product_by_id,
    product_exists_by_id,
    get_batches_by_product_id,
    insert_batch,
    update_product_quantity,
    get_all_batches,
    get_batch_by_id,
    update_batch_qty,
    delete_batch
)

@app.route("/product/batch/add/<int:product_id>", methods=["POST"])
def add_batch(product_id):
    try:
        # Check if product exists
        if not product_exists_by_id(product_id):
            return jsonify({"error": "Product not found"}), 404

        data = request.get_json()
        qty = data.get("qty")
        expiry_date_str = data.get("expiryDate")

        # Validate quantity
        if not isinstance(qty, int) or qty <= 0:
            return jsonify({"error": "Quantity must be a positive integer"}), 400

        # Validate expiry date
        try:
            expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
            if expiry_date <= date.today():
                return jsonify({"error": "Expiry date must be a future date"}), 400
        except Exception:
            return jsonify({"error": "Invalid expiry date format. Use YYYY-MM-DD"}), 400

        # Check if batch with same expiry date already exists
        existing_batches = get_batches_by_product_id(product_id)
        for batch in existing_batches:
            if batch['expiry_date'] == expiry_date:
                return jsonify({"error": "Batch with this expiry date already exists"}), 400

        # Insert batch into database
        created_at = updated_at = date.today()
        batch_id = insert_batch(product_id, qty, expiry_date, created_at, updated_at)

        # Update product quantity by summing all batches
        update_product_quantity(product_id)

        # Respond with added batch details
        response = {
            "batchId": batch_id,
            "productId": product_id,
            "qty": qty,
            "expiryDate": str(expiry_date),
            "createdAt": str(created_at),
            "updatedAt": str(updated_at)
        }
        return jsonify(response), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/product/batch", methods=["GET"])
def get_all_product_batches():
    try:
        batches = get_all_batches()


        if not batches:
            return jsonify({"message": "No batches found"}), 404
        
        response = []
        for batch in batches:
            response.append({
                "batchId": batch['batch_id'],
                "productId": batch['product_id'],
                "qty": batch['qty'],
                "expiryDate": str(batch['expiry_date']),
                "createdAt": str(batch['created_at']),
                "updatedAt": str(batch['updated_at'])
            })
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/product/batchById/<int:batch_id>", methods=["GET"])
def get_batch_details(batch_id): 
    try:
        batch = get_batch_by_id(batch_id)
        if not batch:
            return jsonify({"error": "Batch not found"}), 404

        response = {
            "batchId": batch['batch_id'],
            "productId": batch['product_id'],
            "qty": batch['qty'],
            "expiryDate": str(batch['expiry_date']),
            "createdAt": str(batch['created_at']),
            "updatedAt": str(batch['updated_at'])
        }
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/product/batch/update/<int:batch_id>", methods=["PUT"])
def update_batch(batch_id): 
    try:
        # Step 1: Check batch existence
        batch = get_batch_by_id(batch_id)
        if not batch:
            return jsonify({"error": "Batch with given ID does not exist"}), 400
        
        product_id = batch['product_id']
        old_qty = batch['qty']
        expiry_date = batch['expiry_date']

        today = date.today()
        
        # Step 2: Check expiry
        if expiry_date <= today:
            # Delete expired batch
            delete_batch(batch_id)

            # Update product quantity after deletion
            update_product_quantity(product_id)

            return jsonify({"message": "Batch expired. Batch deleted and product quantity updated"}), 400
        
        # Step 3: Get new quantity from request
        data = request.get_json()
        new_qty = data.get("qty")

        if not isinstance(new_qty, int) or new_qty < 0:
            return jsonify({"error": "Quantity must be greater than 0"}), 400
        
        # Step 4: Update batch quantity (add to existing)
        updated_qty = old_qty + new_qty
        update_batch_qty(batch_id, updated_qty)

        # Step 5: Update product quantity
        update_product_quantity(product_id)

        # Step 6: Build response

        response = {
            "batchId": batch_id,
            "productId": product_id,
            "qty": updated_qty,
            "expiryDate": str(expiry_date),
            "createdAt": str(batch['created_at']),
            "updatedAt": str(date.today())
        }

        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500  
    

@app.route("/product/batch/delete/<int:batch_id>", methods=["DELETE"])
def delete_batch_route(batch_id):
    try:
        # Step 1: Check batch existence
        batch = get_batch_by_id(batch_id)
        if not batch:
            return jsonify({"error": "Batch with given ID does not exist"}), 400
        
        product_id = batch['product_id']

        # Step 2: Delete batch
        delete_success = delete_batch(batch_id)
        if not delete_success:
            return jsonify({"error": "Failed to delete batch"}), 500

        # Step 3: Update product quantity
        update_product_quantity(product_id)

        return jsonify({"message": "Batch deleted and product quantity updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route("/product/stock/<int:product_id>", methods=["GET"])
def get_product_stock(product_id):
    try:
        # Check if product exists
        product = get_product_by_id(product_id)
        if not product:
            return jsonify({"error": "Product not found"}), 404

        batches = get_batches_by_product_id(product_id)

        total_qty = 0
        batch_list = []
        for batch in batches:
            batch_list.append({
                "batchId": batch['batch_id'],
                "quantity": batch['qty'],
                "expiryDate": str(batch['expiry_date'])
            })
            total_qty += batch['qty']

        alert_message = "Enough stock" if total_qty >= 10 else "Add stock"
        response = {
            "productName": product["name"],
            "productId": product["id"],
            "batches": batch_list,
            "totalQuantity": total_qty,
            "alertMessage": alert_message
        }

        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500  
    