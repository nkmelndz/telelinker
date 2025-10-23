# Contribuir a Telelinker

¡Gracias por tu interés en contribuir a Telelinker! Este documento te guiará sobre cómo participar en el desarrollo del proyecto.

## Cómo contribuir

### Reportar bugs

Si encuentras un error:

1. Verifica que no haya sido reportado anteriormente en [Issues](../../issues)
2. Crea un nuevo issue con:
   - Descripción clara del problema
   - Pasos para reproducir el error
   - Versión de Python y sistema operativo
   - Logs o capturas de pantalla si es relevante

### Sugerir mejoras

Para proponer nuevas funcionalidades:

1. Abre un issue con la etiqueta "enhancement"
2. Describe claramente la funcionalidad propuesta
3. Explica por qué sería útil para el proyecto
4. Si es posible, proporciona ejemplos de uso

### Contribuir con código

#### Configuración del entorno de desarrollo

1. Haz fork del repositorio
2. Clona tu fork:
   ```bash
   git clone https://github.com/tu-usuario/telelinker.git
   cd telelinker
   ```
3. Crea un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```
4. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

#### Proceso de desarrollo

1. Crea una rama para tu funcionalidad:
   ```bash
   git checkout -b feature/nueva-funcionalidad
   ```
2. Realiza tus cambios siguiendo las convenciones del código
3. Asegúrate de que tu código funcione correctamente
4. Commit tus cambios:
   ```bash
   git commit -m "feat: descripción clara del cambio"
   ```
5. Push a tu fork:
   ```bash
   git push origin feature/nueva-funcionalidad
   ```
6. Crea un Pull Request

#### Convenciones de código

- Usa nombres descriptivos para variables y funciones
- Mantén las funciones pequeñas y enfocadas en una tarea
- Agrega comentarios para lógica compleja
- Sigue PEP 8 para el estilo de código Python
- Usa type hints cuando sea posible

#### Convenciones de commits

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` para nuevas funcionalidades
- `fix:` para corrección de bugs
- `docs:` para cambios en documentación
- `style:` para cambios de formato
- `refactor:` para refactorización de código
- `test:` para agregar o modificar tests

### Estructura del proyecto

```
telelinker/
├── src/
│   ├── cli/          # Comandos de línea de comandos
│   ├── scrapers/     # Scrapers para diferentes plataformas
│   ├── services/     # Servicios (Telegram, etc.)
│   └── utils/        # Utilidades compartidas
├── tools/            # Scripts de desarrollo y testing
└── bucket/           # Configuración para Scoop
```

### Agregar nuevos scrapers

Para agregar soporte a una nueva plataforma:

1. Crea un archivo en `src/scrapers/` con el nombre de la plataforma
2. Implementa la función de scraping siguiendo el patrón de los scrapers existentes
3. Agrega la detección de URL en el archivo correspondiente
4. Actualiza la documentación

### Testing

Antes de enviar tu PR:

1. Prueba tu código manualmente
2. Verifica que no rompa funcionalidades existentes
3. Si es posible, agrega tests para tu nueva funcionalidad

### Documentación

- Actualiza el README.md si tu cambio afecta el uso de la herramienta
- Agrega comentarios en el código para explicar lógica compleja
- Documenta nuevos parámetros o funcionalidades

## Código de conducta

Este proyecto sigue el [Código de Conducta](CODE_OF_CONDUCT.md). Al participar, te comprometes a mantener un ambiente respetuoso y colaborativo.

## ¿Necesitas ayuda?

Si tienes preguntas sobre cómo contribuir:

- Abre un issue con la etiqueta "question"
- Revisa issues existentes para ver si tu pregunta ya fue respondida

¡Esperamos tus contribuciones!