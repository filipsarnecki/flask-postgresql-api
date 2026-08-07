from flask import Flask, jsonify, request
from flasgger import Swagger
import psycopg
import os
import logging
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
)

load_dotenv()

app = Flask(__name__)

template = {
    "swagger": "2.0",
    "info": {
        "title": "Products & Users API",
        "description": "REST API with PostgreSQL, JWT authentication and Swagger documentation",
        "version": "1.0.0",
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Enter the token in the following format: Bearer <TWÓJ_TOKEN_JWT>",
        }
    },
}
swagger = Swagger(app, template=template)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
jwt = JWTManager(app)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def get_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT"),
    )


def product_to_dict(product):
    return {
        "id": product[0],
        "name": product[1],
        "category": product[2],
        "price": product[3],
    }


def user_to_dict(user):
    return {
        "id": user[0],
        "username": user[1],
    }


@app.get("/")
def home():
    return "Hello World!"


@app.get("/health")
def health():
    logger.info("Health check endpoint called")
    return jsonify({"status": "ok"})


@app.post("/register")
def register():
    """
    Register a new user.
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
              example: john_doe
            password:
              type: string
              example: SecretPassword123
    responses:
      201:
        description: User registered successfully. Returns user object.
      400:
        description: Username and password are required OR registration failed / user exists.
    """
    data = request.get_json()

    if data is None or "username" not in data or "password" not in data:
        logger.warning("Register failed: missing username or password")
        return jsonify({"message": "Username and password are required"}), 400

    username = data["username"]
    password = data["password"]

    hashed_password = generate_password_hash(password)

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO users (username, password)
            VALUES (%s, %s)
            RETURNING id, username
            """,
            (username, hashed_password),
        )
        new_user = cursor.fetchone()
        connection.commit()

        logger.info(f"User registered successfully: {username} (id={new_user[0]})")
        return jsonify({"id": new_user[0], "username": new_user[1]}), 201

    except psycopg.Error as e:
        connection.rollback()
        logger.error(f"Error during registration: {e}")
        return (
            jsonify({"message": "User registration failed or user already exists"}),
            400,
        )

    finally:
        cursor.close()
        connection.close()


@app.post("/login")
def login():
    """
    Authenticate user and retrieve access token.
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
              example: john_doe
            password:
              type: string
              example: SecretPassword123
    responses:
      200:
        description: User logged in successfully. Returns JWT access_token.
      400:
        description: Missing credentials in request.
      401:
        description: Invalid username or password.
    """
    data = request.get_json()

    if data is None or "username" not in data or "password" not in data:
        logger.warning("Login failed: missing credentials in request")
        return jsonify({"message": "Username and password are required"}), 400

    username = data["username"]
    password = data["password"]

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id, password FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    cursor.close()
    connection.close()

    if user is None or not check_password_hash(user[1], password):
        logger.warning(f"Failed login attempt for user: {username}")
        return jsonify({"message": "Invalid username or password"}), 401

    access_token = create_access_token(identity=str(user[0]))
    logger.info(f"User logged in successfully: {username}")

    return jsonify({"access_token": access_token}), 200


@app.get("/users")
@jwt_required()
def get_users():
    """
    Get all registered users.
    ---
    tags:
      - Users
    security:
      - Bearer: []
    responses:
      200:
        description: List of all users.
      401:
        description: Missing or invalid JWT token.
    """
    logger.info("Fetching all users")
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id, username FROM users")

    users_from_db = cursor.fetchall()

    cursor.close()
    connection.close()

    users = []

    for user in users_from_db:
        users.append(user_to_dict(user))

    return jsonify(users)


@app.get("/users/<int:user_id>")
@jwt_required()
def get_user(user_id):
    """
    Get user details by ID.
    ---
    tags:
      - Users
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: Numeric ID of the user.
    responses:
      200:
        description: User details object.
      401:
        description: Missing or invalid JWT token.
      404:
        description: User not found.
    """
    logger.info(f"Fetching user with id={user_id}")
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id, username FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    cursor.close()
    connection.close()

    if user is None:
        logger.warning(f"User with id={user_id} not found")
        return jsonify({"message": "User not found"}), 404

    return jsonify(user_to_dict(user))


@app.get("/products")
def get_products():
    """
    Get all products.
    ---
    tags:
      - Products
    responses:
      200:
        description: List of all products.
    """
    logger.info("Fetching all products")
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM products")

    products_from_db = cursor.fetchall()

    cursor.close()
    connection.close()

    products = []

    for product in products_from_db:
        products.append(product_to_dict(product))

    return jsonify(products)


@app.get("/products/<int:product_id>")
def get_product(product_id):
    """
    Get a single product by ID.
    ---
    tags:
      - Products
    parameters:
      - in: path
        name: product_id
        type: integer
        required: true
        description: Numeric ID of the product.
    responses:
      200:
        description: Product details object.
      404:
        description: Product not found.
    """
    logger.info(f"Fetching product with id={product_id}")
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))

    product = cursor.fetchone()

    cursor.close()
    connection.close()

    if product is None:
        logger.warning(f"Product with id={product_id} not found")
        return jsonify({"message": "Product not found"}), 404

    return jsonify(product_to_dict(product))


@app.post("/products")
@jwt_required()
def post_product():
    """
    Create a new product.
    ---
    tags:
      - Products
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              example: Keyboard
            category:
              type: string
              example: Electronics
            price:
              type: number
              example: 199.99
    responses:
      201:
        description: Product created successfully. Returns the new product.
      400:
        description: Request body is not JSON, missing required fields, or invalid price.
      401:
        description: Missing or invalid JWT token.
    """
    data = request.get_json()

    if data is None:
        logger.warning("Request body is not JSON")
        return jsonify({"message": "Request body must be JSON"}), 400

    required_fields = ["name", "category", "price"]

    for field in required_fields:
        if field not in data:
            logger.warning(f"Missing required field: {field}")
            return jsonify({"message": f"Field '{field}' is required"}), 400

    if not isinstance(data["price"], (int, float)):
        logger.warning("Invalid product price format")
        return jsonify({"message": "Field 'price' must be a number"}), 400

    if data["price"] <= 0:
        logger.warning("Invalid product price")
        return jsonify({"message": "Field 'price' must be positive"}), 400

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO products (name, category, price)
        VALUES (%s, %s, %s)
        RETURNING *
        """,
        (data["name"], data["category"], data["price"]),
    )

    new_product = cursor.fetchone()

    connection.commit()

    logger.info(f"Product created with id={new_product[0]}")

    cursor.close()
    connection.close()

    return jsonify(product_to_dict(new_product)), 201


@app.put("/products/<int:product_id>")
@jwt_required()
def put_product(product_id):
    """
    Update an existing product by ID.
    ---
    tags:
      - Products
    security:
      - Bearer: []
    parameters:
      - in: path
        name: product_id
        type: integer
        required: true
        description: Numeric ID of the product to update.
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              example: Wireless Keyboard
            category:
              type: string
              example: Electronics
            price:
              type: number
              example: 249.99
    responses:
      200:
        description: Product updated successfully. Returns updated product.
      400:
        description: Request body is not JSON, missing fields, or invalid price.
      401:
        description: Missing or invalid JWT token.
      404:
        description: Product not found.
    """
    data = request.get_json()

    if data is None:
        logger.warning("Request body is not JSON")
        return jsonify({"message": "Request body must be JSON"}), 400

    required_fields = ["name", "category", "price"]

    for field in required_fields:
        if field not in data:
            logger.warning(f"Missing required field: {field}")
            return jsonify({"message": f"Field '{field}' is required"}), 400

    if not isinstance(data["price"], (int, float)):
        logger.warning("Invalid product price format")
        return jsonify({"message": "Field 'price' must be a number"}), 400

    if data["price"] <= 0:
        logger.warning("Invalid product price")
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
        (data["name"], data["category"], data["price"], product_id),
    )

    updated_product = cursor.fetchone()

    connection.commit()

    cursor.close()
    connection.close()

    if updated_product is None:
        logger.warning(f"Product with id={product_id} not found")
        return jsonify({"message": "Product not found"}), 404

    logger.info(f"Product updated with id={product_id}")

    return jsonify(product_to_dict(updated_product))


@app.delete("/products/<int:product_id>")
@jwt_required()
def delete_product(product_id):
    """
    Delete a product by ID.
    ---
    tags:
      - Products
    security:
      - Bearer: []
    parameters:
      - in: path
        name: product_id
        type: integer
        required: true
        description: Numeric ID of the product to delete.
    responses:
      200:
        description: Product deleted. Returns success message and deleted object.
      401:
        description: Missing or invalid JWT token.
      404:
        description: Product not found.
    """
    logger.info(f"Deleting product with id={product_id}")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM products
        WHERE id = %s
        RETURNING *
        """,
        (product_id,),
    )

    deleted_product = cursor.fetchone()

    connection.commit()

    cursor.close()
    connection.close()

    if deleted_product is None:
        logger.warning(f"Product with id={product_id} not found")
        return jsonify({"message": "Product not found"}), 404
    logger.info(f"Product deleted with id={product_id}")

    return jsonify(
        {"message": "Product deleted", "product": product_to_dict(deleted_product)}
    )


if __name__ == "__main__":
    app.run()
