from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from config import Config
import os

from routers.movimientos import movimientos_bp
from routers.auth import auth_bp

# Crear aplicación Flask
app = Flask(__name__, static_folder='frontend', static_url_path='')
app.config['SECRET_KEY'] = Config.SECRET_KEY

# Configurar CORS
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": False
    }
})

# Registrar blueprints
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(movimientos_bp, url_prefix="/api")

# Ruta principal - servir el frontend
@app.route("/")
def index():
    return send_from_directory('frontend', 'index.html')

# Servir archivos estáticos del frontend
@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory('frontend', path)

# Ruta de información de la API
@app.route("/api")
def api_info():
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
    port = int(os.environ.get("PORT", 5000))
    
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )