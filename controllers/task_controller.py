"""
Controlador de Tareas - Maneja la lógica de negocio de las tareas

Este archivo contiene todas las rutas y lógica relacionada con las tareas.
Representa la capa "Controlador" en la arquitectura MVC.
"""

from datetime import datetime

from flask import flash, jsonify, redirect, render_template, request, url_for

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
        Ruta principal - Redirige a la lista de tareas

        Returns:
            Response: Redirección a la lista de tareas
        """
        return redirect(url_for("task_list"))

    @app.route("/tasks")
    def task_list():
        """
        Muestra la lista de todas las tareas

        Query Parameters:
            filter (str): Filtro para mostrar tareas ('all', 'pending', 'completed')
            sort (str): Ordenamiento ('date', 'title', 'created')

        Returns:
            str: HTML renderizado con la lista de tareas
        """

        filter_type = request.args.get("filter", "all")
        sort_by = request.args.get("sort", "created")

        # Por ahora, solo mostrar una lista vacía
        tasks = []

        if filter_type == "pending":
            tasks = Task.get_pending_tasks()
        elif filter_type == "completed":
            tasks = Task.get_completed_tasks()
        elif filter_type == "overdue":
            tasks = Task.get_overdue_tasks()
        else:
            tasks = Task.get_all_tasks()

        # ordenar segun el criterio selecionado
        if sort_by == "date":
            tasks.sort(key=lambda t: t.due_date or datetime.max)
        elif sort_by == "title":
            tasks.sort(key=lambda t: t.title.lower())
        else:
            tasks.sort(key=lambda t: t.created_at, reverse=True)

        # Datos para pasar a la plantilla
        context = {
            "tasks": tasks,
            "filter_type": filter_type,
            "sort_by": sort_by,
            "total_tasks": len(tasks),
            "pending_count": len(Task.get_pending_tasks()),
            "completed_count": len(Task.get_completed_tasks()),
        }

        return render_template("task_list.html", **context)

    @app.route("/tasks/new", methods=["GET", "POST"])
    def task_create():
        """
        Crea una nueva tarea

        GET: Muestra el formulario de creación
        POST: Procesa los datos del formulario y crea la tarea

        Returns:
            str: HTML del formulario o redirección tras crear la tarea
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

            task = Task(title, description, due_date)
            task.save()

            flash("Tarea creada con éxito", "success")
            return redirect(url_for("task_list"))

        # Mostrar formulario de creación
        return render_template("task_form.html")

    @app.route("/tasks/<int:task_id>")
    def task_detail(task_id):
        """
        Muestra los detalles de una tarea específica

        Args:
            task_id (int): ID de la tarea a mostrar

        Returns:
            str: HTML con los detalles de la tarea
        """
        pass  # TODO: implementar el método

    @app.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
    def task_edit(task_id):
        """
        Edita una tarea existente

        Args:
            task_id (int): ID de la tarea a editar

        GET: Muestra el formulario de edición con datos actuales
        POST: Procesa los cambios y actualiza la tarea

        Returns:
            str: HTML del formulario o redirección tras editar
        """
        task = Task.query.get_or_404(task_id)
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

        # Mostrar el formulario para editar la tarea
        return render_template("task_form.html", task=task)

    @app.route("/tasks/<int:task_id>/delete", methods=["POST"])
    def task_delete(task_id):
        """
        Elimina una tarea

        Args:
            task_id (int): ID de la tarea a eliminar

        Returns:
            Response: Redirección a la lista de tareas
        """
        task = Task.query.get_or_404(task_id)
        task.delete()
        flash("Tarea eliminada con éxito", "success")
        return redirect(url_for("task_list"))

    @app.route("/tasks/<int:task_id>/toggle", methods=["POST"])
    def task_toggle(task_id):
        """
        Cambia el estado de completado de una tarea

        Args:
            task_id (int): ID de la tarea a cambiar

        Returns:
            Response: Redirección a la lista de tareas
        """
        task = Task.query.get_or_404(task_id)
        if task.completed:
            task.mark_pending()
        else:
            task.mark_completed()
        flash("Estado de tarea actualizado con éxito", "success")
        return redirect(url_for("task_list"))

    # Rutas adicionales para versiones futuras

    @app.route("/api/tasks", methods=["GET"])
    def api_tasks():
        """
        API endpoint para obtener tareas en formato JSON
        (Para versiones futuras con JavaScript)

        Returns:
            json: Lista de tareas en formato JSON
        """
        # TODO: para versiones futuras
        return jsonify(
            {
                "tasks": [],
                "message": "API en desarrollo - Implementar en versiones futuras",
            }
        )

    @app.errorhandler(404)
    def not_found_error(error):
        """Maneja errores 404 - Página no encontrada"""
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Maneja errores 500 - Error interno del servidor"""
        db.session.rollback()
        return render_template("500.html"), 500
