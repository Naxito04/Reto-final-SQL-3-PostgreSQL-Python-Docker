# Reto final SQL 3 — PostgreSQL + Python + Docker

## Objetivo

Vas a construir un pequeño proyecto desde cero en **dos fases**. Primero pondrás en marcha una base de datos PostgreSQL con Docker Compose y trabajarás con ella desde la extensión de PostgreSQL de VS Code. Después crearás una aplicación en Python que consulte esa misma base de datos desde otro contenedor.

Al terminar, cuando ejecutes tu aplicación, deberán aparecer en la terminal los datos que tú has insertado.

**Modalidad:** individual. **Entrega:** enlace a tu repositorio de GitHub.

# Fase 1 — PostgreSQL con Docker Compose

En esta primera fase ejecutaremos PostgreSQL.

## Paso 1. Crea la carpeta del proyecto

Crea una carpeta llamada `mi_proyecto` y ábrela en VS Code:

```bash
mkdir mi_proyecto
cd mi_proyecto
code .
```

Si `code .` no funciona, abre la carpeta manualmente desde VS Code.

## Paso 2. Crea el archivo `.env`

En la raíz del proyecto, crea un archivo llamado `.env` con estas variables:

```dotenv
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=pruebadb
DATABASE_URL=postgresql://postgres:postgres@db:5432/pruebadb
```

- `POSTGRES_USER`: usuario de PostgreSQL.
- `POSTGRES_PASSWORD`: contraseña de PostgreSQL. La contraseña del ejemplo es **solo para uso local en clase**.
- `POSTGRES_DB`: base de datos que se creará al inicializar PostgreSQL.
- `DATABASE_URL`: dirección que utilizará **Python más adelante**, desde otro contenedor. Todavía no la necesitamos.

**Importante:** `.env` contiene credenciales y **no debe subirse a GitHub**. Crea también un archivo `.gitignore`:

```gitignore
.env
__pycache__/
```

Para que otra persona sepa cómo configurar el proyecto, crea un archivo `.env.example` con los mismos nombres de variables y **valores de ejemplo**, sin secretos reales:

```dotenv
POSTGRES_USER=postgres
POSTGRES_PASSWORD=cambia_esta_contrasena
POSTGRES_DB=pruebadb
DATABASE_URL=postgresql://postgres:cambia_esta_contrasena@db:5432/pruebadb
```

> Cuando se copie `.env.example` a `.env`, el usuario, contraseña y nombre de base de datos de `DATABASE_URL` deben coincidir con el resto de variables.

## Paso 3. Crea `docker-compose.yml` (solo PostgreSQL)

Crea este archivo en la raíz:

```yaml
services:
  db:
    image: postgres:17-alpine
    env_file: .env
    ports:
      - "5433:5432"
    volumes:
      - postgresDB:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgresDB:
```

¿Qué significa cada parte?

- `services`: contenedores que forman el proyecto.
- `db`: nombre del servicio de PostgreSQL.
- `image`: imagen existente de PostgreSQL; **no necesitas construirla ni crear un Dockerfile**.
- `env_file`: pasa las variables de `.env` al contenedor.
- `ports`: conecta el puerto **5433 de tu ordenador** con el **5432 de PostgreSQL dentro del contenedor**. Si ya utilizas el 5433, elige otro puerto libre y utilízalo también al conectarte desde VS Code.
- `volumes`: conserva los datos aunque se elimine y vuelva a crear el contenedor.
- `restart`: política de reinicio del servicio.

## Paso 4. Arranca la base de datos

Ejecuta desde la carpeta del proyecto:

```bash
docker compose up -d db
```

El comando `-d` inicia PostgreSQL en segundo plano. Comprueba que está arrancado:

```bash
docker compose ps
```

Si no funciona, revisa los mensajes con:

```bash
docker compose logs db
```

> La primera vez puede tardar un poco en inicializarse. Espera a que PostgreSQL esté listo antes de conectar VS Code.

## Paso 5. Conéctate desde VS Code

Utiliza la extensión PostgreSQL que ya tienes instalada:

1. Abre la extensión **PostgreSQL**.
2. Selecciona **Add Connection** y después **Connection String**.
3. Introduce:

   ```text
   postgresql://postgres@127.0.0.1:5433/pruebadb
   ```

4. Cuando te pida la contraseña, introduce la que has escrito en tu `.env` (en el ejemplo, `postgres`).
5. Guarda la conexión y conéctate.

**¿Por qué `127.0.0.1:5433` y no `db:5432`?** VS Code está en tu ordenador y entra por el puerto publicado `5433`. Más adelante Python se ejecutará **dentro de Docker**, y podrá localizar PostgreSQL utilizando el nombre del servicio `db` y el puerto interno `5432`.

## Paso 6. Crea tu tabla desde la extensión

Elige una temática que te guste: videojuegos, libros, películas, mascotas, viajes, etc. Abre una consulta SQL en la extensión sobre la base de datos `pruebadb`.

Tu tabla debe incluir **como mínimo**:

- Una clave primaria (`PRIMARY KEY`).
- Un campo de texto obligatorio (`NOT NULL`).
- Dos campos adicionales con tipos de datos adecuados.


Ejecuta tu propia sentencia `CREATE TABLE`. Después inserta **al menos 3 registros** con `INSERT INTO`:

Comprueba los datos con un `SELECT`:

```sql
SELECT * FROM tablaquehascreado;
```

# Fase 2 — Añadir Python

Ahora sí: vamos a crear la aplicación. Como el servicio `app` se construirá a partir de nuestro propio código, primero crearemos **el Dockerfile y los archivos de Python** y **después modificaremos Docker Compose**.

## Paso 7. Crea `requirements.txt`

Este archivo indica qué librerías necesita la aplicación:

```text
psycopg[binary]==3.1.18
```

`psycopg` permite a Python conectarse a PostgreSQL.

## Paso 8. Crea el `Dockerfile`

En la raíz del proyecto crea un archivo llamado exactamente `Dockerfile` (**sin extensión**):

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

- `FROM`: parte de una imagen que ya tiene Python.
- `WORKDIR`: elige la carpeta de trabajo dentro del contenedor.
- `COPY requirements.txt .`: copia la lista de dependencias.
- `RUN pip install`: instala `psycopg` durante la construcción de la imagen.
- `COPY . .`: copia el código del proyecto.
- `CMD`: indica qué ejecutar al arrancar el contenedor.

Crea además un archivo `.dockerignore` para evitar copiar secretos al construir la imagen:

```text
.env
.git
__pycache__/
```

## Paso 9. Crea `main.py`

Tu programa debe conectarse a la base de datos utilizando `DATABASE_URL`, realizar un `SELECT` sobre **tu tabla** y mostrar los registros por pantalla.

Este código te servirá de punto de partida. **Sustituye `videojuegos` por el nombre real de tu tabla**:

```python
import os
import psycopg

url = os.getenv("DATABASE_URL")

try:
    with psycopg.connect(url) as connection:
        with connection.cursor() as cur:
            cur.execute("SELECT * FROM tablaquehascreado;")
            filas = cur.fetchall()

            for fila in filas:
                print(fila)
except Exception as e:
    print("Error:", e)
    raise
```

¿Qué hace?

1. `os.getenv` lee la dirección de conexión desde las variables de entorno.
2. `psycopg.connect` conecta Python con PostgreSQL.
3. `cursor()` permite enviar consultas SQL.
4. `execute` ejecuta el `SELECT`.
5. `fetchall` recoge todas las filas de la consulta.
6. `for` imprime cada fila.

No escribas la contraseña directamente en `main.py`: utiliza siempre la variable de entorno.

## Paso 10. Modifica `docker-compose.yml` para añadir `app`

**Ahora que ya existen `Dockerfile`, `requirements.txt` y `main.py`**, puedes añadir el servicio `app`. Tu archivo completo quedará así:

```yaml
services:
  db:
    image: postgres:17-alpine
    env_file: .env
    ports:
      - "5433:5432"
    volumes:
      - postgresDB:/var/lib/postgresql/data
    restart: unless-stopped

  app:
    build: .
    env_file: .env
    depends_on:
      - db

volumes:
  postgresDB:
```

Fíjate en las novedades:

- `app` es el nuevo servicio que ejecutará Python.
- `build: .` le dice a Docker Compose que construya la imagen utilizando el **Dockerfile de esta misma carpeta**. Por eso lo hemos creado antes.
- `env_file` hace que Python reciba `DATABASE_URL`.
- `depends_on` establece el orden de arranque: `db` antes que `app`. **No garantiza por sí solo** que la base de datos ya esté lista para aceptar conexiones, así que comprueba que PostgreSQL esté funcionando antes de ejecutar Python.

## Paso 11. Ejecuta tu aplicación

Si PostgreSQL no está arrancado, inícialo primero:

```bash
docker compose up -d db
```

Después ejecuta:

```bash
docker compose up --build app
```

- `--build`: construye (o reconstruye) la imagen de Python a partir de tu Dockerfile. Es útil cuando has cambiado el código o las dependencias.
- `app`: ejecuta el servicio Python.

**Resultado esperado:** en los mensajes del contenedor `app` deberían aparecer los registros que insertaste desde la extensión PostgreSQL de VS Code. Por ejemplo:

```text
app-1  | (1, 'The Legend of Zelda', 'Switch', 2017)
```

Tu salida deberá mostrar **tus propios registros**. Si has insertado tres, deben poder recuperarse los tres.

---

# Extra opcional — Inserta datos desde Python

Si has terminado el reto principal, amplíalo:

1. Antes del `SELECT`, ejecuta un `INSERT` desde `main.py`.
2. Utiliza parámetros `%s`, pasando los valores por separado (no concatenes textos para crear el SQL).
3. Confirma la operación con `connection.commit()`; también puedes utilizar correctamente el contexto de conexión mostrado en el ejemplo, que confirma la transacción al salir sin errores.
4. Ejecuta de nuevo la aplicación y comprueba que ahora aparece también el registro nuevo.

Ejemplo de la sintaxis parametrizada (adáptala a tu tabla):

```python
cur.execute(
    "INSERT INTO videojuegos (titulo, plataforma, anio) VALUES (%s, %s, %s)",
    ("Minecraft", "PC", 2011)
)
```

---

Estructura esperada:

```text
mi_proyecto/
├── README.md
├── docker-compose.yml
├── Dockerfile
├── .dockerignore
├── .gitignore
├── .env.example
├── requirements.txt
├── main.py
└── consultas.sql
```

**El archivo `.env` debe existir en tu equipo, pero NO debe aparecer en GitHub.**


## Lista de comprobación antes de terminar

- [ ] He creado la carpeta del proyecto y sus archivos.
- [ ] He levantado PostgreSQL con Docker Compose.
- [ ] Me he conectado desde la extensión PostgreSQL de VS Code.
- [ ] He creado una tabla con una clave primaria, un campo obligatorio y otros dos campos.
- [ ] He insertado al menos tres registros.
- [ ] He guardado mi `CREATE TABLE` y mis `INSERT` en `consultas.sql`.
- [ ] He creado `requirements.txt`, `Dockerfile` y `main.py`.
- [ ] He añadido el servicio `app` a Docker Compose **después** de crear el Dockerfile.
- [ ] `docker compose up --build app` muestra mis registros.

## Si algo falla

| Problema | Qué revisar |
|---|---|
| `connection refused` | Comprueba que `db` esté iniciado y PostgreSQL haya terminado de arrancar. |
| `relation "..." does not exist` | Comprueba que el nombre de la tabla sea correcto y que la creaste en `pruebadb`. |
| No aparecen los cambios de Python | Reconstruye con `docker compose up --build app`. |
| VS Code no conecta | Comprueba el puerto del ordenador (`5433` en este ejemplo), el usuario, la contraseña y la base de datos. |
| Python no conecta dentro de Docker | Comprueba `DATABASE_URL`: debe usar `db:5432`, no `localhost:5433`. |
| Modifiqué `.env` y la contraseña no cambia | El volumen de PostgreSQL conserva la base ya inicializada. Cambiar `POSTGRES_PASSWORD` en `.env` no cambia automáticamente la contraseña de una base existente. No borres el volumen si necesitas conservar tus datos. |

**¡Reto conseguido y repaso completado enhorabuena!**
