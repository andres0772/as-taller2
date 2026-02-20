"""
Extensiones de Flask - Instancias globales
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Instancia global de SQLAlchemy
db = SQLAlchemy()

# Instancia global de LoginManager para autenticación
login_manager = LoginManager()
