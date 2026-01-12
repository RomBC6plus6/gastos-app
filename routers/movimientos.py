from flask import Blueprint, request, jsonify
from datetime import datetime
from db import execute_query
from config import Config

movimientos_bp = Blueprint("movimientos", __name__)

@movimientos_bp.route("/movimientos", methods=["POST"])
def crear_movimiento():
    """Crear nuevo movimiento (ingreso o gasto)"""
    
    data = request.get_json()
    
    # Extraer y validar datos
    user_id = data.get("user_id")
    tipo = data.get("tipo", "").upper()
    monto = data.get("monto")
    categoria = data.get("categoria", "").strip()
    descripcion = data.get("descripcion", "").strip()
    fecha = data.get("fecha")
    
    # Validaciones
    if not all([user_id, tipo, monto, fecha]):
        return jsonify({"error": "Faltan campos obligatorios"}), 400
    
    if tipo not in ["INGRESO", "GASTO"]:
        return jsonify({"error": "Tipo debe ser INGRESO o GASTO"}), 400
    
    try:
        monto = float(monto)
        if monto <= 0:
            return jsonify({"error": "El monto debe ser mayor a 0"}), 400
    except ValueError:
        return jsonify({"error": "Monto inválido"}), 400
    
    try:
        query = """
        INSERT INTO movimientos
        (user_id, tipo, monto, categoria, descripcion, fecha, estado)
        VALUES (%s, %s, %s, %s, %s, %s, 'BORRADOR')
        """
        
        movimiento_id = execute_query(
            query,
            (user_id, tipo, monto, categoria, descripcion, fecha)
        )
        
        print(f"✅ Movimiento creado: {tipo} ${monto} (ID: {movimiento_id})")
        
        return jsonify({
            "mensaje": "Movimiento creado exitosamente",
            "movimiento_id": movimiento_id,
            "tipo": tipo
        }), 201
        
    except Exception as e:
        print(f"❌ Error creando movimiento: {str(e)}")
        return jsonify({"error": f"Error al crear movimiento: {str(e)}"}), 500


@movimientos_bp.route("/movimientos/<int:user_id>", methods=["GET"])
def obtener_movimientos(user_id):
    """Obtener todos los movimientos de un usuario"""
    
    # Parámetros opcionales de filtro
    tipo = request.args.get("tipo", "").upper()
    estado = request.args.get("estado", "").upper()
    
    try:
        query = "SELECT * FROM movimientos WHERE user_id = %s"
        params = [user_id]
        
        # Aplicar filtros
        if tipo and tipo in ["INGRESO", "GASTO"]:
            query += " AND tipo = %s"
            params.append(tipo)
        
        if estado and estado in ["BORRADOR", "CONFIRMADO"]:
            query += " AND estado = %s"
            params.append(estado)
        
        query += " ORDER BY fecha DESC, id DESC"
        
        movimientos = execute_query(query, tuple(params), fetch=True)
        
        print(f"📊 Obteniendo movimientos de user_id={user_id}: {len(movimientos or [])} encontrados")
        
        return jsonify({
            "movimientos": movimientos or [],
            "total": len(movimientos) if movimientos else 0
        }), 200
        
    except Exception as e:
        print(f"❌ Error obteniendo movimientos: {str(e)}")
        return jsonify({"error": f"Error al obtener movimientos: {str(e)}"}), 500


@movimientos_bp.route("/movimientos/<int:movimiento_id>/confirmar", methods=["PUT"])
def confirmar_movimiento(movimiento_id):
    """Confirmar un movimiento en estado BORRADOR"""
    
    try:
        # Verificar que existe y está en borrador
        query = "SELECT estado FROM movimientos WHERE id = %s"
        movimiento = execute_query(query, (movimiento_id,), fetch=True, fetch_one=True)
        
        if not movimiento:
            return jsonify({"error": "Movimiento no encontrado"}), 404
        
        if movimiento["estado"] != "BORRADOR":
            return jsonify({"error": "El movimiento ya está confirmado"}), 400
        
        # Actualizar estado
        query = "UPDATE movimientos SET estado = 'CONFIRMADO' WHERE id = %s"
        execute_query(query, (movimiento_id,))
        
        print(f"✅ Movimiento {movimiento_id} confirmado")
        
        return jsonify({"mensaje": "Movimiento confirmado exitosamente"}), 200
        
    except Exception as e:
        print(f"❌ Error confirmando movimiento: {str(e)}")
        return jsonify({"error": f"Error al confirmar: {str(e)}"}), 500


@movimientos_bp.route("/movimientos/<int:movimiento_id>", methods=["DELETE"])
def eliminar_movimiento(movimiento_id):
    """Eliminar un movimiento"""
    
    try:
        query = "DELETE FROM movimientos WHERE id = %s"
        execute_query(query, (movimiento_id,))
        
        print(f"🗑️ Movimiento {movimiento_id} eliminado")
        
        return jsonify({"mensaje": "Movimiento eliminado"}), 200
        
    except Exception as e:
        print(f"❌ Error eliminando movimiento: {str(e)}")
        return jsonify({"error": f"Error al eliminar: {str(e)}"}), 500


@movimientos_bp.route("/resumen/<int:user_id>", methods=["GET"])
def resumen_financiero(user_id):
    """Obtener resumen financiero del usuario"""
    
    try:
        # Total de ingresos
        query_ingresos = """
        SELECT COALESCE(SUM(monto), 0) as total
        FROM movimientos
        WHERE user_id = %s AND tipo = 'INGRESO' AND estado = 'CONFIRMADO'
        """
        ingresos = execute_query(query_ingresos, (user_id,), fetch=True, fetch_one=True)
        
        # Total de gastos
        query_gastos = """
        SELECT COALESCE(SUM(monto), 0) as total
        FROM movimientos
        WHERE user_id = %s AND tipo = 'GASTO' AND estado = 'CONFIRMADO'
        """
        gastos = execute_query(query_gastos, (user_id,), fetch=True, fetch_one=True)
        
        total_ingresos = float(ingresos["total"]) if ingresos else 0
        total_gastos = float(gastos["total"]) if gastos else 0
        balance = total_ingresos - total_gastos
        
        print(f"💰 Resumen user_id={user_id}: Ingresos=${total_ingresos}, Gastos=${total_gastos}, Balance=${balance}")
        
        return jsonify({
            "ingresos": total_ingresos,
            "gastos": total_gastos,
            "balance": balance
        }), 200
        
    except Exception as e:
        print(f"❌ Error calculando resumen: {str(e)}")
        return jsonify({"error": f"Error al calcular resumen: {str(e)}"}), 500