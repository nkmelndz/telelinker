# ...existing code...
import psycopg2
from psycopg2 import pool

class DB:
    def __init__(self, cfg):
        self.pool = pool.SimpleConnectionPool(1, 10,
            host=cfg.DB_HOST,
            dbname=cfg.DB_NAME,
            user=cfg.DB_USER,
            password=cfg.DB_PASSWORD
        )

    def insert_enlace(self, datos):
        conn = self.pool.getconn()
        try:
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO enlaces (url, plataforma, tipo_contenido, autor_contenido, fecha_publicacion, likes, comentarios, compartidos, visitas)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                datos.get('url'),
                datos.get('plataforma'),
                datos.get('tipo_contenido'),
                datos.get('autor_contenido'),
                datos.get('fecha_publicacion'),
                datos.get('likes'),
                datos.get('comentarios'),
                datos.get('compartidos'),
                datos.get('visitas')
            ))
            conn.commit()
        finally:
            self.pool.putconn(conn)
# ...existing code...