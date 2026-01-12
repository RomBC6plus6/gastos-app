import mysql.connector
from mysql.connector import Error
from config import Config  # Importa la clase Config

def get_connection():
    """
    Crea y retorna una conexión a MySQL
    Lanza excepción si falla
    """
    try:
        conn = mysql.connector.connect(**Config.DB_CONFIG)  # Usa Config.DB_CONFIG
        return conn
    except Error as e:
        print(f"❌ Error conectando a MySQL: {e}")
        raise

def execute_query(query, params=None, fetch=False, fetch_one=False):
    """
    Ejecuta una consulta SQL de forma segura
    
    Args:
        query: Consulta SQL
        params: Parámetros para la consulta
        fetch: Si debe retornar resultados (SELECT)
        fetch_one: Si debe retornar solo un resultado
    
    Returns:
        Resultados de la consulta o None
    """
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch:
            result = cursor.fetchone() if fetch_one else cursor.fetchall()
            return result
        else:
            conn.commit()
            return cursor.lastrowid  # Retorna ID del registro insertado
            
    except Error as e:
        if conn:
            conn.rollback()
        print(f"❌ Error en consulta: {e}")
        raise
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()