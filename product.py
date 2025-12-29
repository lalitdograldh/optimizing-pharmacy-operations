from flask import Flask, request,jsonify
from db import product_exists, insert_product,get_all_products,get_product_by_id,update_product,product_name_exists_by_id,delete_product

app = Flask(__name__)

@app.route("/product/add",methods=["POST"] )
def add_product():
    data = request.get_json()

    # ---------- Input Validation ----------

    name = data.get("name")
    price = data.get("price")

    if not name  or not name.strip():
        return jsonify({"error": "Product name cannot be blank"}), 400
    
    if price is None or price <= 0:
        return jsonify({"error": "Price must be greater than 0"}), 400
    
    # ---------- Check Existing Product ----------

    if product_exists(name):
        return jsonify({"error": "Product already exists"}), 400
    
    # ---------- Insert Product ----------
    product = insert_product(name, price)
    
    # ---------- Success Response ----------

    return jsonify({
        "id": product["id"],
        "name": product["name"],
        "qty": product["qty"],
        "price": float(product["price"]),
        "createdAt": product["created_at"].isoformat(),
        "updatedAt": product["updated_at"].isoformat()
    }), 201

# ----------------- GET List Products -----------------

@app.route("/product", methods=["GET"])
def list_products():
    products = get_all_products()

    if not products:
        return jsonify({
            "success": False,
            "message": "No products found"
        }), 404
    
    response = []
    for product in products:
        response.append({
            "id": product["id"],
            "name": product["name"],
            "qty": product["qty"],
            "price": float(product["price"]),
            "createdAt": product["created_at"].isoformat(),
            "updatedAt": product["updated_at"].isoformat()
        })
    return jsonify(response), 200

# ----------------- GET Single Product by ID -----------------

@app.route("/product/<int:product_id>", methods=["GET"])
def get_product(product_id):    
    product = get_product_by_id(product_id)

    if not product:
        return jsonify({
            "success": False,
            "message": f"Product with id {product_id} not found"
        }), 404
    
    return jsonify({
        "id": product["id"],
        "name": product["name"],
        "qty": product["qty"],
        "price": float(product["price"]),
        "createdAt": product["created_at"].isoformat(),
        "updatedAt": product["updated_at"].isoformat()
    }), 200 


# ----------------- UPDATE Product -----------------
@app.route("/product/update/<int:product_id>", methods=["PUT"])

def update_product_route(product_id):
    data = request.get_json()

        
    # ---------- Input Validation ----------
    name = data.get("name")
    price = data.get("price")

    if not name  or not name.strip():
        return jsonify({
            "error": "Product name cannot be blank"
        }), 400
    
    if price is None or price <= 0:
        return jsonify({
            "error": "Price must be greater than 0"
        }), 400

    # ---------- Check Existing Product ----------
    existing_product = get_product_by_id(product_id)
    if not existing_product:
        return jsonify({
            "error": f"Product with id {product_id} does not exist"
        }), 404

    # ---------- Duplicate Name Check ----------
    if product_name_exists_by_id(name, product_id):
        return jsonify({
            "error": "Another product with the same name already exists"
        }), 409
    
    # ---------- Update Product ----------
    updated_product = update_product(product_id, name, price)

    # ---------- Success Response ----------
    return jsonify({
        "id": updated_product["id"],
        "name": updated_product["name"],
        "qty": updated_product["qty"],
        "price": float(updated_product["price"]),
        "createdAt": updated_product["created_at"].isoformat(),
        "updatedAt": updated_product["updated_at"].isoformat()
    }), 200 

@app.route("/product/delete/<int:product_id>", methods=["DELETE"])
def delete_product_api(product_id):
    # ---------- Check Existing Product ----------
    product = get_product_by_id(product_id)
    if not product:
        return jsonify({
            "error": f"Product with id {product_id} does not exist"
        }), 404

    # ---------- Delete Product ----------
    success = delete_product(product_id)

    if not success:
        return jsonify({
            "error": "Failed to delete product"
        }), 500

    # ---------- Success Response ----------
    return jsonify({
        "message": f"Product with id {product_id} has been deleted successfully"
    }), 200 