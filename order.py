from product import app
from flask import request, jsonify
from datetime import date, datetime
from db import (
    get_product_by_id,
    get_batches_for_sale,
    update_batch_quantity,
    update_product_quantity,
    insert_sale,
    insert_sale_item,
    get_product_price,
    get_all_sales,
    get_sale_items_by_sale_id
    
)

@app.route('/processOrder', methods=['POST'])
def process_order():
    try:
        data = request.get_json()
        sale_items = data.get('saleItems')
        if not sale_items or not isinstance(sale_items, list):
            return jsonify({"error": "Invalid saleItems"}), 400

        total_amount = 0
        sale_deductions = []

        # First, validate stock and calculate totals
        for item in sale_items:
            product_id = item.get("productId")
            quantity_needed = item.get("quantity")

            if not product_id or not isinstance(quantity_needed, int) or quantity_needed <= 0:
                return jsonify({"error": f"Invalid data for product {product_id}"}), 400

            product = get_product_by_id(product_id)
            if not product:
                return jsonify({"error": f"Product ID {product_id} not found"}), 404
            
            batches = get_batches_for_sale(product_id)
            stock_available = sum(batch["qty"] for batch in batches)
            if stock_available < quantity_needed:
                return jsonify({"error": f"Insufficient stock for product {product_id}"}), 400
            
            qty_to_allocate = quantity_needed

            for batch in batches:
                if batch["qty"] >= qty_to_allocate:
                    sale_deductions.append({
                        "batch_id": batch["batch_id"],
                        "product_id": product_id,
                        "deduct_qty": qty_to_allocate
                    })
                    qty_to_allocate = 0
                    break
                else:
                    sale_deductions.append({
                        "batch_id": batch["batch_id"],
                        "product_id": product_id,
                        "deduct_qty": batch["qty"]
                    })
                    qty_to_allocate -= batch["qty"]
            # Step 3: Calculate total amount
            unit_price = get_product_price(product_id)
            total_amount += unit_price * quantity_needed
        # Step 4: Insert sale
        sale_id = insert_sale(total_amount)
        # Step 5: Deduct stock from batches and create sale items
        for item in sale_items:
            product_id = item["productId"]
            quantity_needed = item["quantity"]
            unit_price = get_product_price(product_id)
            subtotal = unit_price * quantity_needed

            # Insert sale item
            insert_sale_item(sale_id, product_id, quantity_needed, unit_price, subtotal)

        # Step 6: Deduct stock from batches
        
        for deduction in sale_deductions:
            batch = get_batches_for_sale(deduction["product_id"])
            for b in batch:
                if b["batch_id"] == deduction["batch_id"]:
                    new_qty = b["qty"] - deduction["deduct_qty"]
                    update_batch_quantity(deduction["batch_id"], new_qty)
                    update_product_quantity(deduction["product_id"])
                    break

        return jsonify({
            "saleId": sale_id,
            "saleDate": date.today().strftime("%Y-%m-%d"),
            "totalAmount": round(total_amount, 2),
            "createdAt": date.today().strftime("%Y-%m-%d")
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route('/allSales', methods=['GET'])
def all_sales():
    try:
        sales = get_all_sales()

        if not sales:
            return jsonify({"message": "No sales records found"}), 200

        response = []
        for sale in sales:
            response.append({
                "saleId": sale["sale_id"],
                "saleDate": sale["sale_date"].strftime("%Y-%m-%d"),
                "totalAmount": float(sale["total_amount"]),
                "createdAt": sale["created_at"].strftime("%Y-%m-%d")
            })

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route('/sales/<int:sale_id>/items', methods=['GET'])
def get_sale_items(sale_id):
    try:
        items = get_sale_items_by_sale_id(sale_id)

        if not items:
            return jsonify({
                "message": f"No sale items found for saleId {sale_id}"
            }), 200

        response = []
        for item in items:
            response.append({
                "saleItemId": item["sale_item_id"],
                "saleId": item["sale_id"],
                "productId": item["product_id"],
                "quantity": item["quantity"],
                "unitPrice": float(item["unit_price"]),
                "subtotal": float(item["subtotal"]),
                "createdAt": item["created_at"].strftime("%Y-%m-%d")
            })

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
