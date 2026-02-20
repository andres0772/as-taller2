"""
Controlador de Tareas - Maneja la lógica de negocio de las tareas

Este archivo contiene todas las rutas y lógica relacionada con las tareas.
Representa la capa "Controlador" en la arquitectura MVC.
"""

from datetime import datetime

from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_login import login_required, current_user

from extensions import db
from models.task import Task


def register_routes(app):
    """
    Registra todas las rutas del controlador de tareas en la aplicación Flask

    Args:
        app (Flask): Instancia de la aplicación Flask
    """

    @app.route("/")
    def index():
        """
        Ruta principal - Redirige a login o a la lista de tareas
        """
        if current_user.is_authenticated:
            return redirect(url_for("task_list"))
        return redirect(url_for("auth.login"))

    @app.route("/tasks")
    @login_required
    def task_list():
        """
        Muestra la lista de tareas DEL USUARIO ACTUAL
        """
        filter_type = request.args.get("filter", "all")
        sort_by = request.args.get("sort", "created")

        # Obtener SOLO las tareas del usuario actual
        tasks = Task.query.filter_by(user_id=current_user.id)

        # Aplicar filtro
        if filter_type == "pending":
            tasks = tasks.filter_by(completed=False)
        elif filter_type == "completed":
            tasks = tasks.filter_by(completed=True)
        elif filter_type == "overdue":
            tasks = tasks.filter(
                Task.due_date.is_not(None),
                Task.due_date < datetime.now(),
                Task.completed == False,
            )

        tasks = tasks.all()

        # Ordenar
        if sort_by == "date":
            tasks.sort(key=lambda t: t.due_date or datetime.max)
        elif sort_by == "title":
            tasks.sort(key=lambda t: t.title.lower())
        else:
            tasks.sort(key=lambda t: t.created_at, reverse=True)

        # Contar tareas del usuario
        user_tasks = Task.query.filter_by(user_id=current_user.id)
        total = user_tasks.count()
        pending = user_tasks.filter_by(completed=False).count()
        completed = user_tasks.filter_by(completed=True).count()

        context = {
            "tasks": tasks,
            "filter_type": filter_type,
            "sort_by": sort_by,
            "total_tasks": total,
            "pending_count": pending,
            "completed_count": completed,
        }

        return render_template("task_list.html", **context)

    @app.route("/tasks/new", methods=["GET", "POST"])
    @login_required
    def task_create():
        """
        Crea una nueva tarea para el usuario actual
        """
        if request.method == "POST":
            title = request.form.get("title")
            if not title or title.strip() == "":
                flash("El título no puede estar vacío", "error")
                return render_template("task_form.html")

            description = request.form.get("description")
            due_date_str = request.form.get("due_date")
            due_date = None
            if due_date_str:
                due_date = datetime.strptime(due_date_str, "%Y-%m-%dT%H:%M")
            if due_date and due_date < datetime.now():
                flash(
                    "La fecha de vencimiento no puede ser anterior a la fecha actual",
                    "error",
                )
                return render_template("task_form.html")

            # Crear tarea asociada al usuario actual
            task = Task(title, description, due_date)
            task.user_id = current_user.id
            task.save()

            flash("Tarea creada con éxito", "success")
            return redirect(url_for("task_list"))

        return render_template("task_form.html")

    @app.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
    @login_required
    def task_edit(task_id):
        """
        Edita una tarea existente (solo si pertenece al usuario actual)
        """
        # Solo puede editar SUS propias tareas
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()

        if request.method == "POST":
            task.title = request.form.get("title")
            if not task.title or task.title.strip() == "":
                flash("El título no puede estar vacío", "error")
                return render_template("task_form.html", task=task)

            task.description = request.form.get("description")
            due_date_str = request.form.get("due_date")
            due_date = None
            if due_date_str:
                due_date = datetime.strptime(due_date_str, "%Y-%m-%dT%H:%M")
            task.due_date = due_date
            if task.due_date and task.due_date < datetime.now():
                flash(
                    "La fecha de vencimiento no puede ser anterior a la fecha actual",
                    "error",
                )
                return render_template("task_form.html", task=task)
            task.completed = "completed" in request.form
            task.save()

            flash("Tarea editada con éxito", "success")
            return redirect(url_for("task_list"))

        return render_template("task_form.html", task=task)

    @app.route("/tasks/<int:task_id>/delete", methods=["POST"])
    @login_required
    def task_delete(task_id):
        """
        Elimina una tarea (solo si pertenece al usuario actual)
        """
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
        task.delete()
        flash("Tarea eliminada con éxito", "success")
        return redirect(url_for("task_list"))

    @app.route("/tasks/<int:task_id>/toggle", methods=["POST"])
    @login_required
    def task_toggle(task_id):
        """
        Cambia el estado de completado (solo si pertenece al usuario actual)
        """
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
        if task.completed:
            task.mark_pending()
        else:
            task.mark_completed()
        flash("Estado de tarea actualizado con éxito", "success")
        return redirect(url_for("task_list"))

    @app.errorhandler(404)
    def not_found_error(error):
        """Maneja errores 404 - Página no encontrada"""
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Maneja errores 500 - Error interno del servidor"""
        db.session.rollback()
        return render_template("500.html"), 500
