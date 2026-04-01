from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import pyodbc
from datetime import datetime

# --- Inicialización de la API ---
app = FastAPI(
    title="Sistema de Gestión de Ventas - FastAPI",
    description="API de alto rendimiento para Ventasempresadb con análisis avanzado de datos.",
    version="2.0.0"
)

# --- Configuración de Base de Datos ---
DB_CONFIG = (
    "Driver={ODBC Driver 18 for SQL Server};"
    "Server=localhost;"
    "Database=Ventasempresadb;"
    "UID=Adminuser;"
    "PWD=Mesiasvelez0;"
    "TrustServerCertificate=yes;"
)


# --- Modelos de Datos (Pydantic) ---
# Esto asegura que los datos que salen de la API tengan el formato correcto
class ResumenVentas(BaseModel):
    total_pedidos: int
    monto_total: float
    promedio: float


class ClienteResponse(BaseModel):
    idcliente: int
    nombre: str
    ciudad: Optional[str]
    pais: Optional[str]
    fecharegistro: Optional[str]


# --- Función de Conexión ---
def get_db_connection():
    try:
        return pyodbc.connect(DB_CONFIG)
    except Exception as e:
        print(f"Error de conexión: {e}")
        return None


# --- Endpoints ---

@app.get("/", tags=["General"])
def inicio():
    """Página de bienvenida y acceso a documentación automática"""
    return {
        "mensaje": "API de Ventas Activa",
        "documentacion_interactiva": "/docs",
        "desarrollador": "Diego Calixto Mesías Vélez"
    }


@app.get("/api/clientes", response_model=Dict[str, Any], tags=["Clientes"])
def buscar_clientes(
        nombre: str = Query(..., min_length=2, description="Nombre o parte del nombre del cliente"),
        apellido: Optional[str] = Query(None, description="Apellido opcional para filtrar")
):
    """Busca clientes con filtros flexibles"""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error al conectar con SQL Server")

    try:
        cursor = conn.cursor()
        busqueda = f"%{nombre}%{apellido}%" if apellido else f"%{nombre}%"

        query = """
            SELECT idcliente, nombre, ciudad, pais, fecharegistro 
            FROM clientes 
            WHERE nombre LIKE ?
        """
        cursor.execute(query, (busqueda,))

        columns = [column[0] for column in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()

        # Formateo de fechas para JSON
        for r in results:
            if isinstance(r['fecharegistro'], datetime):
                r['fecharegistro'] = r['fecharegistro'].strftime('%Y-%m-%d')

        return {"total_encontrados": len(results), "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/reportes/ranking-vendedores", tags=["Análisis Avanzado (Window Functions)"])
def ranking_vendedores():
    """
    Reporte Pro: Clasifica vendedores usando RANK() OVER.
    Demuestra habilidades avanzadas en SQL y procesamiento de datos.
    """
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error de conexión")

    try:
        cursor = conn.cursor()

        # SQL con CTE y Window Functions
        query = """
            WITH EstadisticasVendedores AS (
                SELECT 
                    v.nombre as vendedor,
                    v.region,
                    SUM(p.total) as total_ventas,
                    COUNT(p.idpedido) as pedidos_gestionados
                FROM pedidos p
                JOIN vendedores v ON p.idvendedor = v.idvendedor
                GROUP BY v.nombre, v.region
            )
            SELECT 
                vendedor,
                region,
                total_ventas,
                pedidos_gestionados,
                RANK() OVER (ORDER BY total_ventas DESC) as ranking_global,
                RANK() OVER (PARTITION BY region ORDER BY total_ventas DESC) as ranking_por_region
            FROM EstadisticasVendedores
        """

        cursor.execute(query)
        columns = [column[0] for column in cursor.description]
        data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()

        return {
            "fecha_reporte": datetime.now().isoformat(),
            "analisis": "Ranking basado en monto total acumulado",
            "resultados": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en consulta SQL: {str(e)}")


@app.get("/api/resumen/cliente/{id_cliente}", tags=["Reportes"])
def resumen_detallado(id_cliente: int):
    """Obtiene estadísticas de compra de un cliente específico"""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error de conexión")

    try:
        cursor = conn.cursor()
        query = """
            SELECT COUNT(idpedido), SUM(total), AVG(total) 
            FROM pedidos WHERE idcliente = ?
        """
        cursor.execute(query, (id_cliente,))
        row = cursor.fetchone()
        conn.close()

        if not row[0]:  # Si no hay pedidos
            raise HTTPException(status_code=404, detail="El cliente no registra pedidos")

        return {
            "id_cliente": id_cliente,
            "resumen": {
                "cantidad_pedidos": row[0],
                "monto_total": float(row[1]),
                "ticket_promedio": round(float(row[2]), 2)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Ejecución del Servidor ---
if __name__ == "__main__":
    import uvicorn

    # Host 0.0.0.0 permite acceso desde otros dispositivos en la misma red local
    uvicorn.run(app, host="127.0.0.1", port=8000)