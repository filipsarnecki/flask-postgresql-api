from flask import Flask, jsonify

app = Flask(__name__)

products = [
    {
        "id": 1, 
        "name": "Mouse",
        "category": "Electronics",
        "price": 29.99
        
    },
    {

        "id": 2, 
        "name": "Keyboard",
        "category": "Electronics",
        "price": 79.99
        
    },
    {

        "id": 3, 
        "name": "Headset",
        "category": "Electronics",
        "price": 99.99
        
    },
    {
    
        "id": 4, 
        "name": "Mousepad",
        "category": "Electronics",
        "price": 19.99
        
    },
    {
            
        "id": 5, 
        "name": "Microphone",
        "category": "Electronics",
        "price": 69.99
    }
]


@app.get("/")
def home():
    return "Hello World!"

@app.get("/users")
def get_users():
    users = [
        {
            "id": 1,
            "name": "Filip",
            "role": "Technical Support"
        },
        {
            "id": 2,
            "name": "Anna",
            "role": "QA Engineer"
        }
    ]

    return jsonify(users)

@app.get("/users/<int:user_id>")
def get_user(user_id):
    users = [
        {
            "id": 1,
            "name": "Filip",
            "role": "Technical Support"
        },
        {
            "id": 2,
            "name": "Anna",
            "role": "QA Engineer"
        }
    ]

    for user in users:
        if user["id"] == user_id:
            return jsonify(user)

    return jsonify({
        "message": "User not found"
    }), 404

@app.get("/products")
def get_products():
    return jsonify(products)

@app.get("/products/<int:product_id>")
def get_product(product_id):
    for product in products:
        if product["id"] == product_id:
            return jsonify(product)

    return jsonify({
        "message": "Product not found"
    }), 404

        

if __name__ == "__main__":
    app.run()
