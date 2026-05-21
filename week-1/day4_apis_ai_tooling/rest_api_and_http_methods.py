from flask import Flask, jsonify, request

app = Flask(__name__)

students = [
    {"id": 1, "name": "Bunny"},
    {"id": 2, "name": "Rahul"}
]

# ---------------------------
# GET ALL STUDENTS
# ---------------------------
@app.route("/students", methods=["GET"])
def get_students():
    return jsonify({
        "data": students,
        "message": "Students fetched successfully"
    }), 200   # OK


# ---------------------------
# GET SINGLE STUDENT
# ---------------------------
@app.route("/students/<int:id>", methods=["GET"])
def get_student(id):

    for student in students:
        if student["id"] == id:
            return jsonify({
                "data": student,
                "message": "Student found"
            }), 200   # OK

    return jsonify({
        "error": "Student not found"
    }), 404   # NOT FOUND


# ---------------------------
# CREATE STUDENT (POST)
# ---------------------------
@app.route("/students", methods=["POST"])
def add_student():

    data = request.get_json()

    if not data or "name" not in data:
        return jsonify({
            "error": "Name is required"
        }), 400   # BAD REQUEST

    new_student = {
        "id": len(students) + 1,
        "name": data["name"]
    }

    students.append(new_student)

    return jsonify({
        "message": "Student created successfully",
        "data": new_student
    }), 201   # CREATED


# ---------------------------
# UPDATE STUDENT (PUT)
# ---------------------------
@app.route("/students/<int:id>", methods=["PUT"])
def update_student(id):

    data = request.get_json()

    if not data or "name" not in data:
        return jsonify({
            "error": "Name is required"
        }), 400   # BAD REQUEST

    for student in students:
        if student["id"] == id:
            student["name"] = data["name"]

            return jsonify({
                "message": "Student updated successfully",
                "data": student
            }), 200   # OK

    return jsonify({
        "error": "Student not found"
    }), 404   # NOT FOUND


# ---------------------------
# PARTIAL UPDATE (PATCH)
# ---------------------------
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
            }), 200   # OK

    return jsonify({
        "error": "Student not found"
    }), 404   # NOT FOUND


# ---------------------------
# DELETE STUDENT
# ---------------------------
@app.route("/students/<int:id>", methods=["DELETE"])
def delete_student(id):

    for student in students:
        if student["id"] == id:
            students.remove(student)

            return jsonify({
                "message": "Student deleted successfully"
            }), 200   # OK

    return jsonify({
        "error": "Student not found"
    }), 404   # NOT FOUND


if __name__ == "__main__":
    app.run(debug=True)