# Instalación con Scoop (Windows)

Puedes instalar Telelinker fácilmente usando Scoop:

1. Añade el bucket:
   ```powershell
   scoop bucket add telelinker https://github.com/nkmelndz/telelinker
   ```
2. Instala la app:
   ```powershell
   scoop install telelinker
   ```
3. Para actualizar:
   ```powershell
   scoop update telelinker
   ```
# Comandos de configuración

Antes de usar los comandos de extracción, debes configurar tu sesión de Telegram:

### Inicializar configuración
Solicita tu API ID y API HASH y guarda el archivo de configuración:
```powershell
telelinker setup
```

### Iniciar sesión en Telegram
Autentica tu cuenta y crea el archivo de sesión:
```powershell
telelinker login
```
# Uso

Telelinker es una herramienta CLI para extraer enlaces y metadatos de grupos de Telegram.

## Comandos principales

### Listar grupos
Muestra los grupos y subgrupos a los que perteneces:
```powershell
telelinker groups --format csv --out grupos.csv
```

### Fetch de enlaces
Extrae enlaces y metadatos de un grupo específico:
```powershell
telelinker fetch --group <ID_GRUPO> --limit 10 --format csv --out posts.csv
```

O desde un archivo de grupos:
```powershell
telelinker fetch --groups-file grupos.txt --format postgresql --out posts.sql
```

## Argumentos principales

| Argumento      | Descripción                                      |
|--------------- |--------------------------------------------------|
| --group        | ID o username del grupo a procesar                |
| --groups-file  | Archivo con IDs o usernames de grupos             |
| --limit        | Número máximo de enlaces a exportar               |
| --format       | Formato de exportación (`csv`, `postgresql`)      |
| --out          | Ruta del archivo de salida                        |

## Ejemplos

Exportar 20 enlaces de un grupo en CSV:
```powershell
telelinker fetch --group -1001234567890 --limit 20 --format csv
```

Exportar todos los enlaces de varios grupos en SQL:
```powershell
telelinker fetch --groups-file grupos.txt --format postgresql
```

Listar todos los grupos en JSON:
```powershell
telelinker groups --format json --out grupos.json
```

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
   python tools/list_groups.py
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
