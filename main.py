import os
import psycopg
from fastapi import FastAPI


url = os.getenv("DATABASE_URL")
app = FastAPI()

@app.get("/videojuegos", status_code=200)
def listar_videojuegos():
    try:
        with psycopg.connect(url) as connection:
            with connection.cursor() as cur:
                cur.execute("SELECT * FROM videojuegos;")
                filas = cur.fetchall()
                nombres = []
                for fila in filas:
                    nombres.append(fila[2])
                return nombres
    except Exception as e:
        print("Error:", e)
        raise