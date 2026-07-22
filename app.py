from flask import Flask, jsonify

app = Flask(__name__)

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

app.run()