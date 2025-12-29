from product import app
from flask import request, jsonify
from datetime import date, datetime
from db import (
    get_db_connection,
    product_exists_by_id,
    get_batches_by_product_id,
    insert_batch,
    update_product_quantity
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
