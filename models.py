from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    first_lastname = db.Column(db.String(200), nullable=False)
    second_lastname = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    avatar = db.Column(db.String(100), nullable=True, default="sinfoto.png")

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "avatar": self.avatar
        }

class BasicVocab(db.Model):
    __tablename__ = "basicVocab"
    id = db.Column(db.Integer, primary_key = True)
    word = db.Column(db.String(50), unique=True, nullable=False)
    meaning = db.Column(db.String(350), unique=False, nullable=False)
    example = db.Column(db.String(400), unique=False, nullable=False)
    synonyms = db.Column(db.String(200), unique=False, nullable=True)
    

class ScheduledClasses(db.Model):
    __tablename__ = "classes"
    id = db.Column(db.Integer, primary_key=True)
    #daysOfWeek = db.Column(db.)
    title = db.Column(db.String(50), unique=False, nullable=False)
    date = db.Column(db.DateTime, unique=False, nullable=False)
    hour = db.Column(db.Integer, unique=False, nullable=False)
    level = db.Column(db.Integer, unique=False, nullable=False)
    slots = db.Column(db.Integer, unique=False, nullable=False)
    #teacher = db.Column(db.String(50), unique=False, nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "date": self.date,
            "hour": self.hour,
            "level": self.level,
            "slots": self.slots,
            
        }
