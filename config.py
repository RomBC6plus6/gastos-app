import os
from dotenv import load_dotenv

# Solo cargar .env en desarrollo local
if os.path.exists('.env'):
    load_dotenv()

class Config:
    """Configuración centralizada de la aplicación"""
    
    # Base de datos
    DB_CONFIG = {
        "host": os.getenv("DB_HOST", "localhost"),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("DB_NAME", "gastos_app"),
        "port": int(os.getenv("DB_PORT", "3306"))
    }
    
    # Seguridad
    SECRET_KEY = os.getenv("SECRET_KEY", "clave-super-secreta-cambiar-en-produccion")
    
    # Categorías permitidas
    CATEGORIAS_GASTO = [
        "Alimentación",
        "Transporte",
        "Vivienda",
        "Salud",
        "Educación",
        "Entretenimiento",
        "Ropa",
        "Otros"
    ]
    
    CATEGORIAS_INGRESO = [
        "Salario",
        "Freelance",
        "Inversiones",
        "Regalos",
        "Otros"
    ]
    
    # Tipos de movimiento
    TIPOS_MOVIMIENTO = ["INGRESO", "GASTO"]
    
    # Estados
    ESTADOS_MOVIMIENTO = ["BORRADOR", "CONFIRMADO"]