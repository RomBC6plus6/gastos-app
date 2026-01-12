from flask import Flask, jsonify
from flask_cors import CORS
from config import Config

from routers.movimientos import movimientos_bp
from routers.auth import auth_bp

# Crear aplicación Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY

# Configurar CORS
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type"]
    }
})

# Registrar blueprints
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(movimientos_bp, url_prefix="/api")

# Rutas de información
@app.route("/")
def home():
    return jsonify({
        "app": "Gastos App API",
        "version": "1.0",
        "endpoints": {
            "auth": "/api/auth/login, /api/auth/register",
            "movimientos": "/api/movimientos",
            "resumen": "/api/resumen/<user_id>"
        }
    })

@app.route("/health")
def health():
    """Endpoint para verificar que la API está funcionando"""
    return jsonify({"status": "ok", "message": "API funcionando correctamente"}), 200

# Manejo de errores global
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint no encontrado"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Error interno del servidor"}), 500

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",  # Accesible desde tu red local
        port=5000,
        debug=True
    )