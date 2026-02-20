"""
Módulo de controladores - Capa de lógica de negocio de la aplicación MVC

Este paquete contiene todos los controladores que manejan las rutas,
procesan las peticiones HTTP y coordinan entre modelos y vistas.
"""

from .task_controller import *
from .auth_controller import auth

__all__ = ["task_controller", "auth"]
