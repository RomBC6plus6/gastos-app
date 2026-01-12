from flask import Blueprint, request, jsonify
import bcrypt
from db import execute_query

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    """Login de usuario con contraseña hasheada"""
    
    data = request.get_json()
    
    # Validar datos recibidos
    email = data.get("email", "").strip()
    password = data.get("password", "")
    
    if not email or not password:
        return jsonify({"error": "Email y contraseña son requeridos"}), 400
    
    # Validar formato de email básico
    if "@" not in email or "." not in email:
        return jsonify({"error": "Formato de email inválido"}), 400
    
    try:
        # Buscar usuario por email
        query = "SELECT id, nombre, email, password, rol FROM users WHERE email = %s"
        user = execute_query(query, (email,), fetch=True, fetch_one=True)
        
        if not user:
            return jsonify({"error": "Credenciales incorrectas"}), 401
        
        # Verificar contraseña hasheada
        password_hash = user["password"].encode('utf-8')
        password_input = password.encode('utf-8')
        
        if not bcrypt.checkpw(password_input, password_hash):
            return jsonify({"error": "Credenciales incorrectas"}), 401
        
        # No enviar la contraseña al frontend
        user.pop("password")
        
        return jsonify({
            "mensaje": "Login exitoso",
            "user": user
        }), 200
        
    except Exception as e:
        print(f"❌ Error en login: {str(e)}")  # Debug
        return jsonify({"error": f"Error en el servidor: {str(e)}"}), 500


@auth_bp.route("/register", methods=["POST"])
def register():
    """Registrar nuevo usuario"""
    
    data = request.get_json()
    
    nombre = data.get("nombre", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")
    
    # Validaciones
    if not nombre or not email or not password:
        return jsonify({"error": "Todos los campos son requeridos"}), 400
    
    if len(password) < 6:
        return jsonify({"error": "La contraseña debe tener al menos 6 caracteres"}), 400
    
    if "@" not in email:
        return jsonify({"error": "Email inválido"}), 400
    
    try:
        # Verificar si el email ya existe
        query = "SELECT id FROM users WHERE email = %s"
        existing = execute_query(query, (email,), fetch=True, fetch_one=True)
        
        if existing:
            return jsonify({"error": "El email ya está registrado"}), 409
        
        # Hashear contraseña
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Insertar usuario
        query = """
        INSERT INTO users (nombre, email, password, rol)
        VALUES (%s, %s, %s, 'USER')
        """
        
        user_id = execute_query(query, (nombre, email, password_hash))
        
        print(f"✅ Usuario registrado: {email} (ID: {user_id})")  # Debug
        
        return jsonify({
            "mensaje": "Usuario registrado exitosamente",
            "user_id": user_id
        }), 201
        
    except Exception as e:
        print(f"❌ Error en registro: {str(e)}")  # Debug
        return jsonify({"error": f"Error al registrar: {str(e)}"}), 500