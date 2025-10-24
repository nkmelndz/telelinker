# Telelinker

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](CONTRIBUTING.md)

**Telelinker** es una herramienta de línea de comandos que extrae y analiza enlaces compartidos en grupos de Telegram. Detecta automáticamente el tipo de contenido (Instagram, LinkedIn, YouTube, TikTok, etc.), obtiene metadatos relevantes y exporta toda la información en diferentes formatos para análisis posterior.

## 🚀 ¿Qué hace Telelinker?

Telelinker te permite:

- **📱 Extraer enlaces** de grupos de Telegram de forma automatizada
- **🔍 Detectar plataformas** automáticamente (Instagram, LinkedIn, YouTube, TikTok, Medium, Dev.to)
- **📊 Obtener metadatos** como títulos, descripciones, fechas, contadores de interacción
- **💾 Exportar datos** en múltiples formatos (CSV, PostgreSQL)
- **⚡ Procesar múltiples grupos** de forma eficiente

### Casos de uso típicos:

- **Análisis de contenido**: Estudiar qué tipo de enlaces se comparten más en comunidades
- **Investigación social**: Analizar tendencias y patrones de compartición
- **Gestión de comunidades**: Monitorear el contenido compartido en grupos
- **Data mining**: Recopilar datos para análisis de redes sociales

## 📦 Instalación

### Opción 1: Scoop (Windows - Recomendado)

```powershell
# Añadir el bucket
scoop bucket add telelinker https://github.com/nkmelndz/telelinker

# Instalar
scoop install telelinker

# Actualizar
scoop update telelinker
```

### Opción 2: Desde el código fuente

```bash
# Clonar el repositorio
git clone https://github.com/nkmelndz/telelinker.git
cd telelinker

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### Opción 3: Docker

```bash
# Construir la imagen
docker build -t telelinker .

# Ejecutar
docker run --rm -it -u "$(id -u):$(id -g)" -v "$(pwd)":/app telelinker

```

## ⚙️ Configuración inicial

Antes de usar Telelinker, necesitas configurar tu acceso a la API de Telegram:

### 1. Obtener credenciales de Telegram

1. Ve a https://my.telegram.org
2. Inicia sesión con tu número de teléfono
3. Haz clic en "API development tools"
4. Completa el formulario para crear una aplicación
5. Guarda tu **API ID** y **API HASH**

### 2. Configurar Telelinker

```powershell
# Configurar credenciales
telelinker setup

# Iniciar sesión en Telegram
telelinker login
```

## 🎯 Cómo usar Telelinker

### Comandos básicos

#### 1. Listar tus grupos disponibles

```powershell
# Ver grupos en consola
telelinker groups

# Exportar a CSV
telelinker groups --format csv --out mis_grupos.csv

# Exportar a JSON
telelinker groups --format json --out mis_grupos.json
```

#### 2. Extraer enlaces de un grupo específico

```powershell
# Extraer últimos 50 enlaces
telelinker fetch --group -1001234567890 --limit 50 --format csv --out enlaces.csv

# Usar username del grupo
telelinker fetch --group @mi_grupo --limit 100 --format csv --out datos.csv
```

#### 3. Procesar múltiples grupos

```powershell
# Crear archivo con IDs de grupos (uno por línea)
echo "-1001234567890" > grupos.txt
echo "@otro_grupo" >> grupos.txt

# Procesar todos los grupos
telelinker fetch --groups-file grupos.txt --format postgresql --out datos.sql
```

### Parámetros disponibles

| Parámetro | Descripción | Ejemplo |
|-----------|-------------|---------|
| `--group` | ID o username del grupo | `-1001234567890` o `@migrupo` |
| `--groups-file` | Archivo con lista de grupos | `grupos.txt` |
| `--limit` | Máximo número de enlaces | `100` |
| `--format` | Formato de salida | `csv`, `postgresql` |
| `--out` | Archivo de salida | `datos.csv` |

### Ejemplos prácticos

```powershell
# Análisis rápido de un grupo
telelinker fetch --group @tecnologia --limit 20 --format csv

# Exportar datos para base de datos
telelinker fetch --group -1001234567890 --format postgresql --out insertar_datos.sql

# Procesar múltiples grupos con límite
telelinker fetch --groups-file comunidades.txt --limit 500 --format csv --out analisis_completo.csv
```

## 🛠️ Plataformas soportadas

Telelinker detecta y extrae metadatos de:

- **📸 Instagram**: Posts, reels, stories
- **💼 LinkedIn**: Posts, artículos
- **🎥 YouTube**: Videos, shorts
- **🎵 TikTok**: Videos
- **📝 Medium**: Artículos
- **👨‍💻 Dev.to**: Posts técnicos

## 📋 Requisitos del sistema

- **Python 3.11+**
- **Conexión a internet** (para acceder a APIs)
- **Cuenta de Telegram** con acceso a los grupos que quieres analizar
- **Credenciales de API de Telegram** (API ID y API HASH)

### Dependencias opcionales:
- **Docker** (para ejecución en contenedor)
- **PostgreSQL** (si usas formato de exportación SQL)

## 🤝 Contribuir al proyecto

¡Telelinker es un proyecto open source y las contribuciones son muy bienvenidas!

### ¿Cómo puedes ayudar?

- 🐛 **Reportar bugs** - Encuentra errores y ayúdanos a mejorar
- 💡 **Sugerir funcionalidades** - Propón nuevas características
- 🔧 **Agregar plataformas** - Implementa soporte para nuevas redes sociales
- 📝 **Mejorar documentación** - Ayuda a otros usuarios
- ✨ **Optimizar código** - Mejora el rendimiento y la calidad

### Primeros pasos para contribuir

1. **Lee la guía**: Consulta [CONTRIBUTING.md](CONTRIBUTING.md) para instrucciones detalladas
2. **Revisa el código de conducta**: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
3. **Explora issues**: Busca [issues abiertos](../../issues) para empezar
4. **Haz fork del repo**: Crea tu propia copia para trabajar
5. **Envía un PR**: Comparte tus mejoras con la comunidad

### Desarrollo local

```bash
# Fork y clona el repositorio
git clone https://github.com/tu-usuario/telelinker.git
cd telelinker

# Configura el entorno
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Crea una rama para tu feature
git checkout -b feature/mi-nueva-funcionalidad

# ¡Empieza a programar! 🚀
```

## 📄 Licencia

Este proyecto está licenciado bajo la **Licencia MIT**. Esto significa que puedes:

- ✅ Usar el código comercialmente
- ✅ Modificar el código
- ✅ Distribuir el código
- ✅ Usar el código privadamente

Ver [LICENSE](LICENSE) para más detalles.

## 🆘 Soporte y ayuda

¿Necesitas ayuda? Aquí tienes varias opciones:

- 📋 **Issues**: [Reportar bugs o solicitar features](../../issues)
- 💬 **Discusiones**: [Preguntas generales y ayuda](../../discussions)
- 📖 **Documentación**: [Guía completa de contribución](CONTRIBUTING.md)

## ⚠️ Consideraciones importantes

- **Privacidad**: Solo puedes extraer enlaces de grupos donde eres miembro
- **Rate limiting**: Respeta los límites de la API de Telegram
- **Términos de servicio**: Asegúrate de cumplir con los ToS de las plataformas
- **Datos sensibles**: Nunca compartas tu API HASH públicamente

---

**¿Te gusta Telelinker?** ⭐ ¡Dale una estrella al repositorio y compártelo con otros desarrolladores!
