// Detectar automáticamente la URL del backend
const API_URL = window.location.hostname === 'localhost' || 
                window.location.hostname === '127.0.0.1'
    ? "http://127.0.0.1:5000"  // Local
    : window.location.origin;   // Producción (mismo dominio)

console.log("✅ API URL configurada:", API_URL);
console.log("📍 Hostname actual:", window.location.hostname);