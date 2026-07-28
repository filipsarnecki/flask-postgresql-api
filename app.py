from flask import Flask, jsonify, request

app = Flask(__name__)

products = [
    {
        "id": 1,
        "name": "Mouse",
        "category": "Electronics",
        "price": 29.99,
    },
    {
        "id": 2,
        "name": "Keyboard",
        "category": "Electronics",
        "price": 79.99,
    },
    {
        "id": 3,
        "name": "Headset",
        "category": "Electronics",
        "price": 99.99,
    },
    {
        "id": 4,
        "name": "Mousepad",
        "category": "Electronics",
        "price": 19.99,
    },
    {
        "id": 5,
        "name": "Microphone",
        "category": "Electronics",
        "price": 69.99,
    },
]

users = [
    {
        "id": 1,
        "name": "Filip",
        "role": "Technical Support",
    },
    {
        "id": 2,
        "name": "Anna",
        "role": "QA Engineer",
    },
]


@app.get("/")
def home():
    return "Hello World!"


@app.get("/users")
def get_users():
    return jsonify(users)


@app.get("/users/<int:user_id>")
def get_user(user_id):
    for user in users:
        if user["id"] == user_id:
            return jsonify(user)

    return jsonify({"message": "User not found"}), 404


@app.get("/products")
def get_products():
    return jsonify(products)


@app.get("/products/<int:product_id>")
def get_product(product_id):
    for product in products:
        if product["id"] == product_id:
            return jsonify(product)

    return jsonify({"message": "Product not found"}), 404


@app.post("/products")
def post_product():
    data = request.get_json()

    if data is None:
        return jsonify({"message": "Request body must be JSON"}), 400

    required_fields = ["name", "category", "price"]

    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"Field '{field}' is required"}), 400

    if not isinstance(data["price"], (int, float)):
        return jsonify({"message": "Field 'price' must be a number"}), 400

    if data["price"] <= 0:
        return jsonify({"message": "Field 'price' must be positive"}), 400

    highest_id = 0

    for product in products:
        if product["id"] > highest_id:
            highest_id = product["id"]

    data["id"] = highest_id + 1

    products.append(data)

    return jsonify(data), 201


@app.put("/products/<int:product_id>")
def put_product(product_id):
    data = request.get_json()

    if data is None:
        return jsonify({"message": "Request body must be JSON"}), 400

    required_fields = ["name", "category", "price"]

    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"Field '{field}' is required"}), 400

    if not isinstance(data["price"], (int, float)):
        return jsonify({"message": "Field 'price' must be a number"}), 400

    if data["price"] <= 0:
        return jsonify({"message": "Field 'price' must be positive"}), 400

    for product in products:
        if product["id"] == product_id:
            product["name"] = data["name"]
            product["category"] = data["category"]
            product["price"] = data["price"]

            return jsonify(product)

    return jsonify({"message": "Product not found"}), 404


@app.delete("/products/<int:product_id>")
def delete_product(product_id):

    for product in products:
        if product["id"] == product_id:
            products.remove(product)

            return jsonify({"message": "Product deleted"})

    return jsonify({"message": "Product not found"}), 404


if __name__ == "__main__":
    app.run()
