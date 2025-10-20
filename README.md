# telegram-links-app

Extrae enlaces compartidos en grupos de Telegram, detecta la red social, obtiene metadatos y los guarda en PostgreSQL.

## Requisitos
- Python 3.11+
- Docker (opcional, recomendado para producción)
- Acceso a la API de Telegram (api_id, api_hash)
- Base de datos PostgreSQL


## Cómo obtener tu API ID y API HASH de Telegram

Para usar la API de Telegram necesitas dos credenciales:

- **API ID**
- **API HASH**

Sigue estos pasos para obtenerlos:

1. Ve a https://my.telegram.org y accede con tu número de teléfono de Telegram.
2. Haz clic en "API development tools".
3. Llena el formulario (nombre de la app, URL, etc.).
4. Al enviar, verás tu **API ID** y **API HASH**. Guárdalos y colócalos en tu archivo `.env`.

> **Nota:** Nunca compartas tu API HASH ni lo subas a repositorios públicos.

## Uso con Docker
1. Construye la imagen:
   ```powershell
   docker build -t telegram-links-app .
   ```
2. Ejecuta el contenedor pasando tu `.env`:
   ```powershell
   docker run -it --env-file .env telegram-links-app
   ```


## ¿Cómo saber el ID de tu grupo de Telegram?

Para obtener el ID de los grupos a los que perteneces, puedes usar el script incluido:

1. Edita el archivo `extras/list_groups.py` y coloca tu API ID, API HASH y SESSION_NAME (igual que en tu `.env`).
2. Ejecuta el script:
   ```powershell
   python extras/list_groups.py
   ```
3. El script mostrará una lista con el nombre y el ID de cada grupo. Copia el ID que te interese y pégalo en la variable `GROUP_USERNAME` de tu `.env`.

> Puedes usar tanto el ID numérico como el username público del grupo (si tiene uno).

Ver `.env.example` para la lista completa de variables requeridas.

## Estructura de la base de datos
Ver `apuntes.txt` para el esquema SQL sugerido.

## Notas
- El archivo `.env` está en `.gitignore` y no debe subirse al repositorio.
- Si usas Docker, asegúrate de que tu base de datos sea accesible desde el contenedor.
- Si usas Selenium/Chromium, la imagen Docker ya incluye los binarios necesarios.
