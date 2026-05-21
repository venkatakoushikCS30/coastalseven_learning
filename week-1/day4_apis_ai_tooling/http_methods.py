from flask import Flask, jsonify, request

app = Flask(__name__)

# -----------------------------
# SAMPLE DATA (in-memory DB)
# -----------------------------
users = [
    {"id": 1, "name": "Koushik", "role": "student"},
    {"id": 2, "name": "Rahul", "role": "developer"}
]

# =========================================================
# 1. GET METHOD - Fetch all users
# =========================================================
@app.route("/users", methods=["GET"])
def get_users():
    return jsonify({
        "method": "GET",
        "data": users
    }), 200


# =========================================================
# 2. GET METHOD - Fetch single user
# =========================================================
@app.route("/users/<int:id>", methods=["GET"])
def get_user(id):

    for user in users:
        if user["id"] == id:
            return jsonify({
                "method": "GET",
                "data": user
            }), 200

    return jsonify({
        "method": "GET",
        "error": "User not found"
    }), 404


# =========================================================
# 3. POST METHOD - Create new user
# =========================================================
@app.route("/users", methods=["POST"])
def create_user():

    data = request.get_json()

    # validation
    if not data or "name" not in data:
        return jsonify({
            "method": "POST",
            "error": "Name is required"
        }), 400

    new_user = {
        "id": len(users) + 1,
        "name": data["name"],
        "role": data.get("role", "student")  # default value
    }

    users.append(new_user)

    return jsonify({
        "method": "POST",
        "message": "User created",
        "data": new_user
    }), 201


# =========================================================
# 4. PUT METHOD - Full update
# =========================================================
@app.route("/users/<int:id>", methods=["PUT"])
def update_user(id):

    data = request.get_json()

    if not data:
        return jsonify({
            "method": "PUT",
            "error": "Data required"
        }), 400

    for user in users:
        if user["id"] == id:

            # full replacement
            user["name"] = data.get("name", user["name"])
            user["role"] = data.get("role", user["role"])

            return jsonify({
                "method": "PUT",
                "message": "User updated",
                "data": user
            }), 200

    return jsonify({
        "method": "PUT",
        "error": "User not found"
    }), 404


# =========================================================
# 5. PATCH METHOD - Partial update
# =========================================================
@app.route("/users/<int:id>", methods=["PATCH"])
def patch_user(id):

    data = request.get_json()

    for user in users:
        if user["id"] == id:

            # only update provided fields
            if "name" in data:
                user["name"] = data["name"]

            if "role" in data:
                user["role"] = data["role"]

            return jsonify({
                "method": "PATCH",
                "message": "User partially updated",
                "data": user
            }), 200

    return jsonify({
        "method": "PATCH",
        "error": "User not found"
    }), 404


# =========================================================
# 6. DELETE METHOD - Remove user
# =========================================================
@app.route("/users/<int:id>", methods=["DELETE"])
def delete_user(id):

    for user in users:
        if user["id"] == id:
            users.remove(user)

            return jsonify({
                "method": "DELETE",
                "message": "User deleted"
            }), 200

    return jsonify({
        "method": "DELETE",
        "error": "User not found"
    }), 404


# =========================================================
# RUN SERVER
# =========================================================
if __name__ == "__main__":
    app.run(debug=True)