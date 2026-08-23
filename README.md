# DupeManager

Gestor de duplicados de Jellyfin — Encuentra y gestiona archivos duplicados en tu servidor de medios.

## Features

- 🔍 Detección automática de episodios y películas duplicadas
- 📊 Dashboard con estadísticas de espacio recuperable
- 🧙 Wizard de revisión grupo por grupo
- 📋 Listas con filtros de episodios, películas e ignorados
- 🗑️ Papelera de reciclaje configurable
- 🔔 Notificaciones (browser push, webhook, email)
- ⏰ Escaneo automático configurable
- 🔒 Autenticación vía Jellyfin (solo administradores)

## Quick Start

```bash
# Clonar el repo
git clone https://github.com/lluquino/DupeManager.git
cd DupeManager

# Configurar
cp .env.example .env
# Editar .env con tus datos de Jellyfin

# Ejecutar
docker-compose up -d
```

La app estará disponible en `http://localhost:8097`

## Configuration

Edit the `.env` file:

```env
JELLYFIN_URL=http://192.168.0.22:8096
JELLYFIN_API_KEY=your-api-key
JWT_SECRET=your-random-secret
```

## Tech Stack

- **Backend**: Python + FastAPI
- **Frontend**: HTML + Tailwind CSS + Vanilla JS
- **Database**: SQLite (async)
- **Container**: Docker

## License

GNU GPLv3 — See [LICENSE](LICENSE) for details.
