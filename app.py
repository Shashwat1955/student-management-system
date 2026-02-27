from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity
)

from werkzeug.security import generate_password_hash, check_password_hash

from flasgger import Swagger


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['JWT_SECRET_KEY'] = 'super-secret-key'

db = SQLAlchemy(app)
jwt = JWTManager(app)

Swagger(app)


# USER MODEL
class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), unique=True)

    password = db.Column(db.String(200))


# STUDENT MODEL
class Student(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))

    age = db.Column(db.Integer)

    course = db.Column(db.String(100))


with app.app_context():
    db.create_all()


# FRONTEND ROUTES

@app.route("/")
def home():
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# REGISTER API

@app.route("/register", methods=["POST"])
def register():

    data = request.json

    hashed = generate_password_hash(data["password"])

    user = User(
        username=data["username"],
        password=hashed
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered"})


# LOGIN API

@app.route("/login", methods=["POST"])
def login():

    data = request.json

    user = User.query.filter_by(
        username=data["username"]
    ).first()

    if user and check_password_hash(user.password, data["password"]):

        token = create_access_token(identity=user.username)

        return jsonify({"access_token": token})

    return jsonify({"message": "Invalid credentials"})


# ADD STUDENT

@app.route("/students", methods=["POST"])
@jwt_required()
def add_student():

    data = request.json

    student = Student(
        name=data["name"],
        age=data["age"],
        course=data["course"]
    )

    db.session.add(student)
    db.session.commit()

    return jsonify({"message": "Student added"})


# GET STUDENTS

@app.route("/students", methods=["GET"])
@jwt_required()
def get_students():

    students = Student.query.all()

    output = []

    for s in students:

        output.append({

            "id": s.id,
            "name": s.name,
            "age": s.age,
            "course": s.course

        })

    return jsonify(output)


# RUN

if __name__ == "__main__":
    app.run(debug=True)