"""
Controlador de Autenticación - Maneja registro, login y logout
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from models.user import User
from extensions import db

# Crear un Blueprint para las rutas de autenticación
# Un Blueprint es como un "mini app" que agrupa rutas relacionadas
auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["GET", "POST"])
def register():
    """
    Registro de nuevos usuarios

    GET: Muestra el formulario de registro
    POST: Procesa el registro y crea el usuario
    """
    if request.method == "POST":
        # Obtener datos del formulario
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # Validaciones
        if not username or username.strip() == "":
            flash("El nombre de usuario es obligatorio", "error")
            return render_template("register.html")

        if not email or email.strip() == "":
            flash("El email es obligatorio", "error")
            return render_template("register.html")

        if not password:
            flash("La contraseña es obligatoria", "error")
            return render_template("register.html")

        if password != confirm_password:
            flash("Las contraseñas no coinciden", "error")
            return render_template("register.html")

        # Verificar si el usuario ya existe
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            flash("El usuario o email ya está registrado", "error")
            return render_template("register.html")

        # Crear nuevo usuario
        new_user = User(username=username, email=email)
        new_user.set_password(password)  # Encriptar contraseña
        new_user.save()

        flash("¡Registro exitoso! Ahora podés iniciar sesión.", "success")
        return redirect(url_for("auth.login"))

    # GET: Mostrar formulario de registro
    return render_template("register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    """
    Inicio de sesión

    GET: Muestra el formulario de login
    POST: Verifica credenciales y crea la sesión
    """
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Validaciones básicas
        if not username or not password:
            flash("Completá todos los campos", "error")
            return render_template("login.html")

        # Buscar usuario por username
        user = User.query.filter_by(username=username).first()

        # Verificar si existe y la contraseña es correcta
        if user and user.check_password(password):
            # Crear sesión del usuario
            login_user(user)
            flash(f"¡Bienvenido, {user.username}!", "success")
            return redirect(url_for("task_list"))
        else:
            flash("Usuario o contraseña incorrectos", "error")
            return render_template("login.html")

    # GET: Mostrar formulario de login
    return render_template("login.html")


@auth.route("/logout")
@login_required
def logout():
    """
    Cierra la sesión del usuario
    """
    logout_user()
    flash("Sesión cerrada correctamente", "success")
    return redirect(url_for("auth.login"))
