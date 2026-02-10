from flask import Flask, request, jsonify
import pyodbc
from datetime import datetime

app = Flask(__name__)
# Solución para ver tildes correctamente en el navegador
app.config['JSON_AS_ASCII'] = False

# Configuración centralizada
DB_CONFIG = (
    "Driver={ODBC Driver 18 for SQL Server};"
    "Server=localhost;"
    "Database=Ventasempresadb;"
    "UID=Adminuser;"
    "PWD=Mesiasvelez0;"
    "TrustServerCertificate=yes;"
)

def get_db_connection():
    """Establece una nueva conexión a SQL Server"""
    try:
        return pyodbc.connect(DB_CONFIG)
    except Exception as e:
        print(f"Error al conectar: {e}")
        return None

def serialize_dates(data):
    """Convierte objetos datetime a string para JSON"""
    for row in data:
        for key, value in row.items():
            if isinstance(value, datetime):
                row[key] = value.strftime('%Y-%m-%d')
    return data
@app.route('/')
def home():
    """Página de inicio con documentación"""
    return jsonify({
        "mensaje": "API de Consulta - Ventasempresadb",
        "endpoints_disponibles": {
            "/api/clientes": "Buscar información de clientes",
            "/api/vendedores": "Buscar información de vendedores",
            "/api/pedidos/cliente": "Obtener pedidos de un cliente",
            "/api/pedidos/vendedor": "Obtener pedidos de un vendedor",
            "/api/resumen/cliente": "Resumen completo de un cliente",
            "/api/resumen/vendedor": "Resumen completo de un vendedor"
        },
        "ejemplo_uso": {
            "GET": "/api/clientes?nombre=María&apellido=González",
            "GET": "/api/vendedores?nombre=Roberto&apellido=Sánchez",
            "GET": "/api/resumen/cliente?nombre=María&apellido=González"
        }
    })
@app.route('/api/clientes', methods=['GET'])
def buscar_cliente():
    """
    Busca información básica de un cliente
    Parámetros: nombre, apellido (opcional)
    """
    nombre = request.args.get('nombre', '').strip()
    apellido = request.args.get('apellido', '').strip()
    if not nombre:
        return jsonify({"error": "Debe proporcionar al menos el nombre"}), 400
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500
    try:
        cursor = conn.cursor()
        # Construir búsqueda flexible
        if apellido:
            nombre_completo = f"%{nombre}%{apellido}%"
        else:
            nombre_completo = f"%{nombre}%"
        query = """
            SELECT idcliente, nombre, ciudad, pais, fecharegistro
            FROM clientes
            WHERE nombre LIKE ?
        """
        cursor.execute(query, (nombre_completo,))
        columns = [column[0] for column in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        if not results:
            return jsonify({"mensaje": "No se encontraron clientes"}), 404
        return jsonify({
            "total_resultados": len(results),
            "clientes": serialize_dates(results)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/api/vendedores', methods=['GET'])
def buscar_vendedor():
    """
    Busca información básica de un vendedor
    Parámetros: nombre, apellido (opcional)
    """
    nombre = request.args.get('nombre', '').strip()
    apellido = request.args.get('apellido', '').strip()
    if not nombre:
        return jsonify({"error": "Debe proporcionar al menos el nombre"}), 400
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500
    try:
        cursor = conn.cursor()
        if apellido:
            nombre_completo = f"%{nombre}%{apellido}%"
        else:
            nombre_completo = f"%{nombre}%"
        query = """
            SELECT idvendedor, nombre, region, comision
            FROM vendedores
            WHERE nombre LIKE ?
        """
        cursor.execute(query, (nombre_completo,))
        columns = [column[0] for column in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        if not results:
            return jsonify({"mensaje": "No se encontraron vendedores"}), 404

        return jsonify({
            "total_resultados": len(results),
            "vendedores": results
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/api/pedidos/cliente', methods=['GET'])
def pedidos_cliente():
    """
    Obtiene todos los pedidos de un cliente
    Parámetros: nombre, apellido (opcional)
    """
    nombre = request.args.get('nombre', '').strip()
    apellido = request.args.get('apellido', '').strip()
    if not nombre:
        return jsonify({"error": "Debe proporcionar al menos el nombre"}), 400
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500
    try:
        cursor = conn.cursor()
        if apellido:
            nombre_completo = f"%{nombre}%{apellido}%"
        else:
            nombre_completo = f"%{nombre}%"
        query = """
            SELECT 
                c.nombre as cliente,
                p.idpedido,
                pr.nombreproducto,
                pr.categoria,
                p.cantidad,
                p.total,
                p.fechaorden,
                v.nombre as vendedor
            FROM pedidos p
            JOIN clientes c ON p.idcliente = c.idcliente
            JOIN productos pr ON p.idproducto = pr.idproducto
            JOIN vendedores v ON p.idvendedor = v.idvendedor
            WHERE c.nombre LIKE ?
            ORDER BY p.fechaorden DESC
        """
        cursor.execute(query, (nombre_completo,))
        columns = [column[0] for column in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        if not results:
            return jsonify({"mensaje": "No se encontraron pedidos para este cliente"}), 404
        return jsonify({
            "total_pedidos": len(results),
            "pedidos": serialize_dates(results)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/api/pedidos/vendedor', methods=['GET'])
def pedidos_vendedor():
    """
    Obtiene todos los pedidos gestionados por un vendedor
    Parámetros: nombre, apellido (opcional)
    """
    nombre = request.args.get('nombre', '').strip()
    apellido = request.args.get('apellido', '').strip()
    if not nombre:
        return jsonify({"error": "Debe proporcionar al menos el nombre"}), 400
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500
    try:
        cursor = conn.cursor()
        if apellido:
            nombre_completo = f"%{nombre}%{apellido}%"
        else:
            nombre_completo = f"%{nombre}%"
        query = """
            SELECT 
                v.nombre as vendedor,
                p.idpedido,
                c.nombre as cliente,
                pr.nombreproducto,
                p.cantidad,
                p.total,
                p.fechaorden
            FROM pedidos p
            JOIN vendedores v ON p.idvendedor = v.idvendedor
            JOIN clientes c ON p.idcliente = c.idcliente
            JOIN productos pr ON p.idproducto = pr.idproducto
            WHERE v.nombre LIKE ?
            ORDER BY p.fechaorden DESC
        """
        cursor.execute(query, (nombre_completo,))
        columns = [column[0] for column in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        if not results:
            return jsonify({"mensaje": "No se encontraron pedidos para este vendedor"}), 404
        return jsonify({
            "total_pedidos": len(results),
            "pedidos": serialize_dates(results)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/api/resumen/cliente', methods=['GET'])
def resumen_cliente():
    """
    Obtiene un resumen completo de un cliente:
    - Información personal
    - Total de pedidos
    - Monto total gastado
    - Productos más comprados
    """
    nombre = request.args.get('nombre', '').strip()
    apellido = request.args.get('apellido', '').strip()
    if not nombre:
        return jsonify({"error": "Debe proporcionar al menos el nombre"}), 400
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500
    try:
        cursor = conn.cursor()

        if apellido:
            nombre_completo = f"%{nombre}%{apellido}%"
        else:
            nombre_completo = f"%{nombre}%"
        # Información básica del cliente
        query_info = """
            SELECT idcliente, nombre, ciudad, pais, fecharegistro
            FROM clientes
            WHERE nombre LIKE ?
        """
        cursor.execute(query_info, (nombre_completo,))
        info_cliente = cursor.fetchone()

        if not info_cliente:
            conn.close()
            return jsonify({"mensaje": "Cliente no encontrado"}), 404

        idcliente = info_cliente[0]
        # Resumen de compras
        query_resumen = """
            SELECT 
                COUNT(p.idpedido) as total_pedidos,
                SUM(p.total) as monto_total_gastado,
                AVG(p.total) as promedio_por_pedido
            FROM pedidos p
            WHERE p.idcliente = ?
        """
        cursor.execute(query_resumen, (idcliente,))
        resumen = cursor.fetchone()
        # Productos más comprados
        query_productos = """
            SELECT TOP 5
                pr.nombreproducto,
                SUM(p.cantidad) as cantidad_total,
                SUM(p.total) as gasto_total
            FROM pedidos p
            JOIN productos pr ON p.idproducto = pr.idproducto
            WHERE p.idcliente = ?
            GROUP BY pr.nombreproducto
            ORDER BY cantidad_total DESC
        """
        cursor.execute(query_productos, (idcliente,))
        columns_prod = [column[0] for column in cursor.description]
        productos = [dict(zip(columns_prod, row)) for row in cursor.fetchall()]
        conn.close()
        return jsonify({
            "informacion_cliente": {
                "nombre": info_cliente[1],
                "ciudad": info_cliente[2],
                "pais": info_cliente[3],
                "fecha_registro": info_cliente[4].strftime('%Y-%m-%d')
            },
            "estadisticas": {
                "total_pedidos": resumen[0] if resumen[0] else 0,
                "monto_total_gastado": float(resumen[1]) if resumen[1] else 0.0,
                "promedio_por_pedido": float(resumen[2]) if resumen[2] else 0.0
            },
            "productos_mas_comprados": productos
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/api/resumen/vendedor', methods=['GET'])
def resumen_vendedor():
    """
    Obtiene un resumen completo de un vendedor:
    - Información personal
    - Total de ventas
    - Comisiones ganadas
    - Productos más vendidos
    """
    nombre = request.args.get('nombre', '').strip()
    apellido = request.args.get('apellido', '').strip()
    if not nombre:
        return jsonify({"error": "Debe proporcionar al menos el nombre"}), 400
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500
    try:
        cursor = conn.cursor()
        if apellido:
            nombre_completo = f"%{nombre}%{apellido}%"
        else:
            nombre_completo = f"%{nombre}%"
        # Información básica del vendedor
        query_info = """
            SELECT idvendedor, nombre, region, comision
            FROM vendedores
            WHERE nombre LIKE ?
        """
        cursor.execute(query_info, (nombre_completo,))
        info_vendedor = cursor.fetchone()
        if not info_vendedor:
            conn.close()
            return jsonify({"mensaje": "Vendedor no encontrado"}), 404
        idvendedor = info_vendedor[0]
        comision_pct = float(info_vendedor[3])
        # Resumen de ventas
        query_resumen = """
            SELECT 
                COUNT(p.idpedido) as total_ventas,
                SUM(p.total) as monto_total_vendido,
                AVG(p.total) as promedio_por_venta
            FROM pedidos p
            WHERE p.idvendedor = ?
        """
        cursor.execute(query_resumen, (idvendedor,))
        resumen = cursor.fetchone()

        monto_total = float(resumen[1]) if resumen[1] else 0.0
        comision_ganada = (monto_total * comision_pct) / 100

        # Productos más vendidos
        query_productos = """
            SELECT TOP 5
                pr.nombreproducto,
                SUM(p.cantidad) as cantidad_vendida,
                SUM(p.total) as total_vendido
            FROM pedidos p
            JOIN productos pr ON p.idproducto = pr.idproducto
            WHERE p.idvendedor = ?
            GROUP BY pr.nombreproducto
            ORDER BY cantidad_vendida DESC
        """
        cursor.execute(query_productos, (idvendedor,))
        columns_prod = [column[0] for column in cursor.description]
        productos = [dict(zip(columns_prod, row)) for row in cursor.fetchall()]
        conn.close()
        return jsonify({
            "informacion_vendedor": {
                "nombre": info_vendedor[1],
                "region": info_vendedor[2],
                "porcentaje_comision": comision_pct
            },
            "estadisticas": {
                "total_ventas": resumen[0] if resumen[0] else 0,
                "monto_total_vendido": monto_total,
                "promedio_por_venta": float(resumen[2]) if resumen[2] else 0.0,
                "comision_ganada": round(comision_ganada, 2)
            },
            "productos_mas_vendidos": productos
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
if __name__ == '__main__':
    print(" API iniciada en http://127.0.0.1:5000")
    print(" Documentación disponible en http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)