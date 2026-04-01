Este proyecto es una API REST de alto rendimiento diseñada para la consulta y análisis de una base de datos de ventas (`Ventasempresadb`). Originalmente concebido en Flask, el sistema fue migrado a **FastAPI** para aprovechar el procesamiento asíncrono y la validación de datos en tiempo real.
Tecnologías Utilizadas
Backend: Python 3.x, FastAPI.
Servidor ASGI: Uvicorn.
Base de Datos: Microsoft SQL Server.
Conectividad: PyODBC.
Validación de Datos: Pydantic Models.

Características Principales
Documentación Automática: Generación instantánea de endpoints mediante Swagger UI (`/docs`) y ReDoc (`/redoc`).
Análisis Avanzado: Endpoint de reportes que utiliza **Window Functions (CTE & RANK)** para clasificar el desempeño de vendedores globalmente y por región.
Robustez: Validación estricta de tipos de datos mediante modelos de Pydantic.
Arquitectura Limpia: Separación clara entre la lógica de conexión, modelos de datos y controladores de rutas.

Instalación y Uso

1. Clonar el repositorio:
   ```bash
   git clone [https://github.com/tu-usuario/nombre-del-repo.git](https://github.com/tu-usuario/nombre-del-repo.git)
   
2. Instalar dependencias:
pip install fastapi uvicorn pyodbc pydantic
3.Configurar la cadena de conexión en main.py (DB_CONFIG).
4. Ejecutar el servidor:
python main.py
5. Acceder a la documentación interactiva en http://127.0.0.1:8000/docs.
