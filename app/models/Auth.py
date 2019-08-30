from main import db
from werkzeug.security import generate_password_hash, check_password_hash
from models.Clients import ClientsModel


class AuthModel(db.Model):
    __tablename__ = 'system_users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String())

    # create a pseudo column
    clients = db.relationship(ClientsModel, backref='system_user')

    # insert into db
    def insert_records(self):
        db.session.add(self)
        db.session.commit()

    # fetch user by username
    @classmethod
    def fetch_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    # fetch system_user by id
    @classmethod
    def fetch_by_id(cls, id):
        return cls.query.filter_by(id=id).first().id

    @staticmethod
    def generate_hash(password):
        return generate_password_hash(password)

    @classmethod
    def check_username(cls, username):
        record = cls.query.filter_by(username=username).first()
        if record:
            return True
        else:
            return False

    @classmethod
    def check_email(cls, email):
        record = cls.query.filter_by(email=email).first()
        if record:
            return True
        else:
            return False

    @classmethod
    def check_password(cls, username, password):
        record = cls.query.filter_by(username=username).first()

        if record and check_password_hash(record.password, password):
            return True
        else:
            return False