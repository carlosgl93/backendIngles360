import os
from flask import Flask, jsonify, request, render_template
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from werkzeug.utils import secure_filename
from models import db, Users, ScheduledClasses
from datetime import datetime


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static")
ALLOWED_IMAGES_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app = Flask(__name__)
app.config["DEBUG"] = True
app.config["ENV"] = "development"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "db.sqlite3")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "super-secret"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAIL_SERVER"] = "stmp.gmail.com"
app.config["MAIL_PORT"] = "465"
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_DEBUG"] = True
app.config["MAIL_USERNAME"] = "cgumucio93@gmail.com"
app.config["MAIL_PASSWORD"] = "pykfpaqddpqwdxna"
app.config["MAIL_DEFAULT_SENDER"] = "cgumucio93@gmail.com"
JWTManager(app)


db.init_app(app)
mail = Mail(app)
bcrypt = Bcrypt(app)
Migrate(app, db)
CORS(app)

manager = Manager(app)
manager.add_command("db", MigrateCommand)


def allowed_images_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGES_EXTENSIONS

def send_mail(subject, sender, recipients, message):
    msg = Message(subject,
                  recipients=[recipients])

    msg.html = message

    mail.send(msg)

@app.route("/")
def root():
    return render_template("index.html")

@app.route("/api/register", methods=["POST"])
def register():
    if request.method == "POST":
        email = request.json.get("email", None)
        name = request.json.get("name", None)
        first_lastname = request.json.get("lastname1", None)
        second_lastname = request.json.get("lastname2", None)
        password = request.json.get("password", None)

        if not email or email == "":
            return jsonify({"msg": "El email es requerido"}), 400

        if not name or name == "":
            return jsonify({"msg": "Debes indicar tu nombre"}), 400

        if not first_lastname or first_lastname == "":
            return jsonify({"msg": "Debes indicar tu apellido paterno"}), 400
        
        if not second_lastname or second_lastname == "":
            return jsonify({"msg": "Debes indicar tu apellido materno"}), 400
        
        if not password or password == "":
            return jsonify({"msg": "La contrasena es requerida"}), 400
        
        user = Users.query.filter_by(email=email).first()
        if user:
            return jsonify({"msg": "El email ya existe"}), 400

        if "avatar" in request.files:
            avatar = request.files["avatar"]
            if avatar.filename != "":
                if allowed_images_file(avatar.filename):
                    filename = secure_filename(avatar.filename)
                    avatar.save(os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], "img/avatar"), filename))
                else:
                    return jsonify({"msg": "Image not allowed"})

        user = Users()
        user.email = email
        user.name = name
        user.first_lastname = first_lastname
        user.second_lastname = second_lastname
        user.password = bcrypt.generate_password_hash(password)
        
        if "avatar" in request.files:
            user.avatar = filename

        db.session.add(user)
        db.session.commit()

        html = render_template("emails/email-register.html", user=user)

        #send_mail("Registro de usuario", user.email, user.username, html)

        access_token = create_access_token(identity=user.email)
        data = {
            "access_token": access_token,
            "user": user.serialize()
        }
        return jsonify(data), 200


@app.route("/api/login", methods=["POST"])
def login():
    if request.method == "POST":
        email = request.json.get("email", None)
        password = request.json.get("password", None)

        if not email or email == "":
            return jsonify({"msg": "El email es requerido"}), 400

        if not password or password == "":
            return jsonify({"msg": "La contrasena es requerida"}), 400

        user = Users.query.filter_by(email=email).first()

        if not user:
            return jsonify({"msg": "Ese email no esta registrado con ninguna cuenta"}), 400

        if bcrypt.check_password_hash(user.password, password):
            access_token = create_access_token(identity=user.email)
            data = {
                "access_token": access_token,
                "user": user.serialize()
            }
            return jsonify(data), 200
        else:
            return jsonify({"msg": "Email o password incorrectos"}), 401

@app.route("/api/login", methods=["GET"])
def getUserInfo(email):
    user = Users.query.filter_by(email=email).first()
    return {
        "id": user.email,
        "email": user.email,
        "name": user.name,
        "lastname": user.first_lastname,
        "avatar": user.avatar
    }

@app.route("/api/contact", methods=["POST"])
def contact():
    if request.method == "POST":
        name = request.json.get("name", None)
        email = request.json.get("email", None)
        email_content = request.json.get("message", None)
        contact_email_message = render_template("emails/contact_form.html", user=userMessage)
        send_email("A lead contacted us", email, "cgumucio93@gmail.com")

@app.route("/api/events", methods=["GET"])
def getEvents():
    events = ScheduledClasses.query.all()
    events = list(map(lambda event: event.serialize(), events))
    return jsonify(events), 200
    

@app.route("/api/schedule", methods=["POST"])
def registerClass():
    if request.method == "POST":
        title = request.json.get("title", None)
        date = datetime.strptime(request.json.get("date", None), '%Y-%m-%d')
        hour = request.json.get("hour", None)
        level = request.json.get("level", None)
        slots = request.json.get("slots", None)
        teacher = request.json.get("teacher", None)
        
        if not title or title == "":
            return jsonify({"msg": "El titulo de la clase es requerido"}), 400

        if not date or date == "":
            return jsonify({"msg": "Toda clase debe registrarse con fecha"}), 400
        
        if not hour or hour == "":
            return jsonify({"msg": "Toda clase debe tener una hora especifica"}), 400
        
        if not level or level == "":
            return jsonify({"msg": "El nivel de la clase es requerido"}), 400

        if not slots or slots == "":
            return jsonify({"msg": "La debe especificar cuantos alumnos pueden atender"}), 400
        
        newClass = ScheduledClasses()
        newClass.title = title
        newClass.date = date
        newClass.hour = hour
        newClass.level = level
        newClass.slots = slots
        #newClass.teacher = teacher 

        db.session.add(newClass)
        db.session.commit()

        data = {
            "newClass": newClass.serialize()
        }
        return jsonify(data), 200

@app.route("/api/profile", methods=["GET"])
def getUserData(email):
    user = Users.query.filter_by(email=email).first()
    return {
        "name": user.name,
        "lastname1": user.first_lastname,
        "lastname2": user.second_lastname,
        "email": user.email,
        "password": user.password

    }



if __name__ == "__main__":
    manager.run()

