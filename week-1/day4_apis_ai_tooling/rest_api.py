from flask import Flask, jsonify, request

app = Flask(__name__)

students = [
    {"id": 1, "name": "Koushik"},
    {"id": 2, "name": "Rahul"}
]

# -------------------------
# GET ALL STUDENTS
# -------------------------
@app.route("/students", methods=["GET"])
def get_students():
    return jsonify(students), 200


# -------------------------
# CREATE STUDENT
# -------------------------
@app.route("/students", methods=["POST"])
def create_student():
    data = request.get_json()

    if not data or "name" not in data:
        return jsonify({"error": "name is required"}), 400

    new_student = {
        "id": len(students) + 1,
        "name": data["name"]
    }

    students.append(new_student)

    return jsonify({
        "message": "Student created",
        "data": new_student
    }), 201


# -------------------------
# UPDATE STUDENT (PUT)
# -------------------------
@app.route("/students/<int:id>", methods=["PUT"])
def update_student(id):
    data = request.get_json()

    for student in students:
        if student["id"] == id:
            if "name" not in data:
                return jsonify({"error": "name required"}), 400

            student["name"] = data["name"]

            return jsonify({
                "message": "Student updated",
                "data": student
            }), 200

    return jsonify({"error": "Student not found"}), 404


# -------------------------
# PARTIAL UPDATE (PATCH)
# -------------------------
@app.route("/students/<int:id>", methods=["PATCH"])
def patch_student(id):
    data = request.get_json()

    for student in students:
        if student["id"] == id:

            if "name" in data:
                student["name"] = data["name"]

            return jsonify({
                "message": "Student partially updated",
                "data": student
            }), 200

    return jsonify({"error": "Student not found"}), 404


# -------------------------
# DELETE STUDENT
# -------------------------
@app.route("/students/<int:id>", methods=["DELETE"])
def delete_student(id):
    for student in students:
        if student["id"] == id:
            students.remove(student)

            return jsonify({
                "message": "Student deleted"
            }), 200

    return jsonify({"error": "Student not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)