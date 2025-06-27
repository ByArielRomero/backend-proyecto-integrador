import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

print(f"Conectando a MySQL en puerto {os.getenv('MYSQL_PORT', '3306')}...")

try:
    conn = mysql.connector.connect(
       
        user="root",
        password=os.getenv("MYSQL_ROOT_PASSWORD"),
        port=3306
    )
    print("Conexión exitosa a MySQL")
    
    cursor = conn.cursor()
    database_name = os.getenv("MYSQL_DATABASE", "huellas_db")
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
    print(f"Base de datos '{database_name}' creada/verificada")

    cursor.execute(f"USE {database_name}")
    print(f"Usando base de datos '{database_name}'")

    tables = [
        ("Marca", """
        CREATE TABLE IF NOT EXISTS Marca (
            id_marca INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(50) UNIQUE
        )
        """),
        ("Modelo", """
        CREATE TABLE IF NOT EXISTS Modelo (
            id_modelo INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) UNIQUE
        )
        """),
        ("Categoria", """
        CREATE TABLE IF NOT EXISTS Categoria (
            id_categoria INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(50) UNIQUE
        )
        """),
        ("Colores", """
        CREATE TABLE IF NOT EXISTS Colores (
            id_color INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(50) UNIQUE
        )
        """),
        ("Cuadrante", """
        CREATE TABLE IF NOT EXISTS Cuadrante (
            id_cuadrante INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(50)
        )
        """),
        ("FormaGeometrica", """
        CREATE TABLE IF NOT EXISTS FormaGeometrica (
            id_forma INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(50)
        )
        """),
        ("Usuarios", """
        CREATE TABLE IF NOT EXISTS Usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            password_hash VARCHAR(128) NOT NULL,
            role VARCHAR(20) NOT NULL
        )
        """),
        ("Calzado", """
        CREATE TABLE IF NOT EXISTS Calzado (
            id_calzado INT AUTO_INCREMENT PRIMARY KEY,
            talle VARCHAR(10),
            ancho DECIMAL(5,2),
            alto DECIMAL(5,2),
            tipo_registro ENUM('indubitada_proveedor', 'indubitada_comisaria', 'dubitada'),
            id_marca INT,
            id_modelo INT,
            id_categoria INT,
            FOREIGN KEY (id_marca) REFERENCES Marca(id_marca),
            FOREIGN KEY (id_modelo) REFERENCES Modelo(id_modelo),
            FOREIGN KEY (id_categoria) REFERENCES Categoria(id_categoria)
        )
        """),
        ("calzado_color", """
        CREATE TABLE IF NOT EXISTS calzado_color (
            id_calzado INT,
            id_color INT,
            PRIMARY KEY (id_calzado, id_color),
            FOREIGN KEY (id_calzado) REFERENCES Calzado(id_calzado) ON DELETE CASCADE,
            FOREIGN KEY (id_color) REFERENCES Colores(id_color) ON DELETE CASCADE
        )
        """),
        ("Suela", """
        CREATE TABLE IF NOT EXISTS Suela (
            id_suela INT AUTO_INCREMENT PRIMARY KEY,
            id_calzado INT,
            descripcion_general TEXT,
            FOREIGN KEY (id_calzado) REFERENCES Calzado(id_calzado)
        )
        """),
        ("DetalleSuela", """
        CREATE TABLE IF NOT EXISTS DetalleSuela (
            id_detalle INT AUTO_INCREMENT PRIMARY KEY,
            id_suela INT,
            id_cuadrante INT,
            id_forma INT,
            detalle_adicional TEXT,
            FOREIGN KEY (id_suela) REFERENCES Suela(id_suela),
            FOREIGN KEY (id_cuadrante) REFERENCES Cuadrante(id_cuadrante),
            FOREIGN KEY (id_forma) REFERENCES FormaGeometrica(id_forma)
        )
        """),
          ("Imputados", """
        CREATE TABLE IF NOT EXISTS Imputado (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(50) NOT NULL,
            dni INT NOT NULL,
            direccion VARCHAR(100) NOT NULL,
            comisaria VARCHAR(100) NOT NULL,
            jurisdiccion VARCHAR(100) NOT NULL
        )
        """)
    ]

    for table_name, create_sql in tables:
        cursor.execute(create_sql)
        print(f"Tabla '{table_name}' creada/verificada")

    conn.commit()
    print("Todas las tablas creadas correctamente.")
    
except Exception as e:
    print(f"Error: {e}")
    raise
finally:
    if 'conn' in locals() and conn.is_connected():
        cursor.close()
        conn.close()
        print("Conexión cerrada.")
