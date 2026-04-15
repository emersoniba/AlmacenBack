import psycopg2
import sys

try:
    conn = psycopg2.connect(
        dbname="db.Almacen",
        user="postgres",
        password="1234",
        host="localhost",
        port="5432"
    )
    print("✅ Conexión exitosa a PostgreSQL")
    
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print(f"📦 Versión: {version[0]}")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error de conexión: {e}")
    sys.exit(1)