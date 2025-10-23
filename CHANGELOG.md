# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Archivos de configuración para proyecto open source
- Licencia MIT
- Guía de contribución (CONTRIBUTING.md)
- Código de conducta (CODE_OF_CONDUCT.md)
- Templates para issues y pull requests
- Badges en README.md
- Sección de contribución en README.md

## [1.0.0] - 2024-XX-XX

### Added
- Herramienta CLI para extraer enlaces de grupos de Telegram
- Soporte para múltiples formatos de exportación (CSV, PostgreSQL)
- Scrapers para diferentes plataformas sociales:
  - Instagram
  - LinkedIn
  - Medium
  - Dev.to
  - TikTok
  - YouTube
- Comandos principales:
  - `telelinker setup` - Configuración inicial
  - `telelinker login` - Autenticación con Telegram
  - `telelinker groups` - Listar grupos disponibles
  - `telelinker fetch` - Extraer enlaces y metadatos
- Soporte para instalación via Scoop (Windows)
- Dockerfile para contenedorización
- Utilidades para normalización de fechas y conteos

### Security
- Archivo .env.example para configuración segura
- Exclusión de credenciales en .gitignore

---

## Tipos de cambios

- `Added` para nuevas funcionalidades
- `Changed` para cambios en funcionalidades existentes
- `Deprecated` para funcionalidades que serán removidas pronto
- `Removed` para funcionalidades removidas
- `Fixed` para corrección de bugs
- `Security` para vulnerabilidades