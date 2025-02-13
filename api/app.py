from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# MongoDB connection setup
client = MongoClient("mongodb://localhost:27017/")  # No username or password
db = client.Inventory  # Your database name
products_collection = db.Stock  # Your collection name

@app.route('/api/products', methods=['POST'])
def add_product():
    product_name = request.json.get('product_name')
    quantity = request.json.get('quantity')

    if not product_name or quantity is None:
        return jsonify({"error": "Product name and quantity are required!"}), 400

    # Insert the new product into the MongoDB collection
    product_id = products_collection.insert_one({
        "name": product_name,
        "quantity": quantity
    }).inserted_id

    return jsonify({"msg": "Product added successfully!", "product_id": str(product_id)}), 201

@app.route('/api/product', methods=['GET'])
def get_products():
    products = products_collection.find()
    product_list = []
    
    for product in product:
        product['_id'] = str(product['_id'])  # Convert ObjectId to string
        product_list.append(product)

    return jsonify(product_list), 200

if __name__ == '__main__':
    app.run(debug=True)
