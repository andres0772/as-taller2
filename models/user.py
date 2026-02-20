from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

    def __init__(self, username, email):
        """Constructor del modelo User"""
        self.username = username
        self.email = email

    # con esto me permite guardar contraseña encriptada
    def set_password(self, password):
        self.password = generate_password_hash(password)

    # esto es un validador para saber que la contrasela sea correcta
    def check_password(self, password):
        return check_password_hash(self.password, password)

    def save(self):
        """Guarda el usuario en la base de datos"""
        db.session.add(self)
        db.session.commit()
        return self

    def __repr__(self):
        return f"<User {self.username}>"
