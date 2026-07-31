from flask import Flask, jsonify, request
import psycopg

app = Flask(__name__)
def get_connection():
    return psycopg.connect(
        host="localhost",
        dbname="learning_db",
        user="postgres",
        password="Test123!",
        port=5432,
    )


@app.get("/")
def home():
    return "Hello World!"

@app.get("/health")
def health():
    return jsonify({
        "status": "ok"
    })


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
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM products")

    products_from_db = cursor.fetchall()

    cursor.close()
    connection.close()


    return jsonify(products_from_db)


@app.get("/products/<int:product_id>")
def get_product(product_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM products WHERE id = %s",
        (product_id,)
    )

    product = cursor.fetchone()

    cursor.close()
    connection.close()

    if product is None:
        return jsonify({"message": "Product not found"}), 404

    return jsonify(product)


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


    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO products (name, category, price)
        VALUES (%s, %s, %s)
        RETURNING *
        """,
        (
            data["name"],
            data["category"],
            data["price"]
        )
    )

    new_product = cursor.fetchone()

    cursor.close()
    connection.close()

    return jsonify(new_product), 201

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


    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE products
        SET name = %s,
            category = %s,
            price = %s
        WHERE id = %s
        RETURNING *
        """,
        (
            data["name"],
            data["category"],
            data["price"],
            product_id
        )
    )

    updated_product = cursor.fetchone()

    cursor.close()
    connection.close()


    if updated_product is None:
        return jsonify({"message": "Product not found"}), 404

    return jsonify(updated_product)


@app.delete("/products/<int:product_id>")
def delete_product(product_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM products
        WHERE id = %s
        RETURNING *
        """,
        (product_id,)
    )

    deleted_product = cursor.fetchone()

    cursor.close()
    connection.close()


    if deleted_product is None:
        return jsonify({"message": "Product not found"}), 404

    return jsonify({
        "message": "Product deleted",
        "product": deleted_product
    })


if __name__ == "__main__":
    app.run()
