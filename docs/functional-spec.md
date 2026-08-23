# DupeManager — Especificación Funcional

## 1. Decisiones de Proyecto

| Aspecto | Decisión |
|---------|----------|
| **Repo** | GitHub (credenciales pendientes) |
| **Docker Hub** | Cuando haya v1.0 |
| **Licencia** | GNU GPLv3 |
| **Despliegue** | VM 100 (192.168.0.22), container Docker |
| **Puerto** | `8097` |
| **Frontend** | HTML + Tailwind CSS + Vanilla JS |
| **Auth** | Jellyfin auth (solo administradores) |
| **Acceso** | nginx-proxy-manager (config manual tras despliegue) |
| **Papelera** | Opcional, configurable vía `.env` |

---

## 2. Autenticación

### 2.1 Flujo de Login

```
┌──────────────────────────────────────┐
│           PANTALLA DE LOGIN          │
│                                      │
│   ┌──────────────────────────────┐   │
│   │  Logo DupeManager            │   │
│   │                              │   │
│   │  Usuario: [_______________]  │   │
│   │  Contraseña: [___________]   │   │
│   │                              │   │
│   │  [Entrar]                    │   │
│   │                              │   │
│   │  ¿No tienes cuenta?          │   │
│   │  Contacta al administrador   │   │
│   └──────────────────────────────┘   │
│                                      │
│   Fondo oscuro (#0f172a)             │
│   Card centrada, estilo glassmorphism│
└──────────────────────────────────────┘
```

### 2.2 Lógica de Autenticación

```
POST /api/auth/login
Body: { "username": "...", "password": "..." }

Backend:
1. Reenvía credenciales a Jellyfin:
   POST http://192.168.0.22:8096/Users/AuthenticateByName
   Headers: X-Emby-Authorization: DupeManager
   Body: { "Username": "...", "Pw": "..." }

2. Si Jellyfin responde 200:
   - Extrae token y UserId
   - Consulta perfil: GET /Users/{UserId}
   - Verifica Policy.IsAdministrator == true
   - Si NO es admin → 403 "Solo administradores pueden acceder"
   - Si ES admin → genera JWT propio con payload:
     { "sub": UserId, "name": Username, "jellyfin_token": "...", "exp": ... }
   - Devuelve { "token": "jwt...", "user": { "name": "...", "isAdmin": true } }

3. Si Jellyfin responde 401 → 401 "Credenciales incorrectas"
```

### 2.3 Protección de Rutas

```
Todas las rutas /api/* (excepto /api/auth/login) requieren:
  Header: Authorization: Bearer <jwt>

Middleware:
1. Valida JWT con JWT_SECRET
2. Si expirado → 401 "Sesión expirada, inicia sesión de nuevo"
3. Si válido → continúa
```

### 2.4 Configuración

```env
JELLYFIN_URL=http://192.168.0.22:8096
JELLYFIN_API_KEY=c0b0a3c579e54cbb9a38c8538ae76f20
JWT_SECRET=clave-secreta-random-aqui-cambiar
JWT_EXPIRY_HOURS=24
```

---

## 3. Navegación y Layout

### 3.1 Estructura de la App (SPA)

```
┌─────────────────────────────────────────────────────────┐
│  HEADER FIJO                                             │
│  ┌─────────┐  ┌─────────────────────────────────────┐   │
│  │  Logo   │  │  Dashboard | Episodios | Películas  │   │
│  │  Dupe   │  │  Ignorados | Configuración    [👤]  │   │
│  └─────────┘  └─────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  CONTENIDO PRINCIPAL (cambia según sección)              │
│                                                          │
│                                                          │
│                                                          │
│                                                          │
├─────────────────────────────────────────────────────────┤
│  TOAST BANNER (esquina inferior derecha)                 │
│  ┌──────────────────────────────────────┐                │
│  │ ⏳ Escaneando... 45%  [████████░░]  │                │
│  └──────────────────────────────────────┘                │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Secciones de la Navegación

| Sección | Ruta | Descripción |
|---------|------|-------------|
| **Dashboard** | `/#/` | Resumen y acceso rápido |
| **Episodios** | `/#/episodes` | Lista de episodios duplicados |
| **Películas** | `/#/movies` | Lista de películas duplicadas |
| **Ignorados** | `/#/ignored` | Duplicados marcados como ignorados |
| **Configuración** | `/#/settings` | Opciones del servicio |

---

## 4. Dashboard

### 4.1 Layout del Dashboard

```
┌─────────────────────────────────────────────────────────┐
│  Dashboard                                               │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │ Episodios│ │ Películas│ │ Duplic.  │ │ Ahorro   │   │
│  │  15,271  │ │    853   │ │   246    │ │  72 GB   │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Último escaneo: 23/08/2026 14:30                 │   │
│  │  [🔄 Revisar Duplicados]  [🔍 Escanear Ahora]   │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Resumen Rápido                                   │   │
│  │                                                    │   │
│  │  Episodios con duplicados:  244 grupos            │   │
│  │  Películas con duplicados:    2 grupos            │   │
│  │  Series con nombres colisionados: 4 (falsos +)    │   │
│  │                                                    │   │
│  │  Top 5 series con más duplicados:                 │   │
│  │  1. The Big Bang Theory — 24 episodios            │   │
│  │  2. La Casa del Dragón — 10 episodios             │   │
│  │  3. Fundación — 8 episodios                       │   │
│  │  4. Andor — 6 episodios                           │   │
│  │  5. Alien: Planeta Tierra — 5 episodios           │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 4.2 Tarjetas de Estadísticas

| Tarjeta | Valor | Icono | Color |
|---------|-------|-------|-------|
| Episodios totales | 15,271 | 📺 | Azul |
| Películas totales | 853 | 🎬 | Púrpura |
| Grupos duplicados | 246 | ⚠️ | Amarillo |
| Espacio recuperable | 72 GB | 💾 | Verde |

### 4.3 Botones de Acción

- **Revisar Duplicados**: Abre el modal wizard de revisión (ver sección 5)
- **Escanear Ahora**: Ejecuta un re-escaneo completo, muestra banner de progreso

---

## 5. Wizard de Revisión de Duplicados

### 5.1 Concepto

Al pulsar "Revisar Duplicados" se abre un **modal de pantalla completa** que presenta los grupos de duplicados **uno por uno**, permitiendo al usuario decidir qué hacer con cada grupo antes de pasar al siguiente.

### 5.2 Flujo del Wizard

```
┌─────────────────────────────────────────────────────────┐
│  Revisar Duplicados — Grupo 1 de 246              [X]  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━░░░░░░░░░░░░░░  12%   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  📺 The Big Bang Theory — Temporada 1, Episodio 1       │
│  "The Pilot"                                             │
│                                                          │
│  ┌─────────────────────┐  ┌─────────────────────┐       │
│  │  COPIA 1 ✅ MEJOR   │  │  COPIA 2            │       │
│  │                      │  │                      │       │
│  │  📁 Series/Big...   │  │  📁 Series/Big...   │       │
│  │  🎬 1080p HEVC      │  │  🎬 480p MPEG4      │       │
│  │  📦 2.4 GB          │  │  📦 350 MB           │       │
│  │  🎞️ x265            │  │  🎞️ XviD             │       │
│  │                      │  │                      │       │
│  │  Score: 10           │  │  Score: 2            │       │
│  │  [✅ Conservar]     │  │  [🗑️ Eliminar]      │       │
│  └─────────────────────┘  └─────────────────────┘       │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Acciones:                                        │   │
│  │                                                    │   │
│  │  [✅ Conservar la mejor, eliminar la peor]        │   │
│  │  [⏭️ Ignorar este grupo]                          │   │
│  │  [⏭️ Omitir y ver todos los grupos]               │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  [← Anterior]                    [Siguiente →]          │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 5.3 Lógica de Presentación

```
1. Se obtienen todos los grupos de duplicados (episodios + películas)
2. Se ordenan por: más espacio recuperable primero
3. Se muestra el grupo actual con TODAS sus copias
4. Se resalta cuál es la "mejor" según el score de calidad
5. El usuario elige una acción:
   a. Conservar la mejor / eliminar la peor → se marca "resuelto"
   b. Ignorar este grupo → se añade a ignorados
   c. Omitir → se deja sin resolver, se pasa al siguiente
6. Se pasa al siguiente grupo automáticamente
7. Al terminar todos → se cierra el modal y se muestra resumen
```

### 5.4 Tarjetas de Copias en el Wizard

Cada copia dentro del grupo muestra:

| Campo | Descripción |
|-------|-------------|
| **Estado** | ✅ Mejor / ⚪ Normal / 🗑️ Seleccionada para eliminar |
| **Ruta** | Ruta completa del archivo |
| **Resolución** | 1080p, 720p, 4K, etc. |
| **Codec** | HEVC, H264, MPEG4, etc. |
| **Tamaño** | Tamaño en GB/MB |
| **Score** | Puntuación según jerarquía de calidad |
| **Acción** | Botón para conservar o eliminar |

### 5.5 Acciones Disponibles

| Acción | Descripción | Efecto |
|--------|-------------|--------|
| **Conservar la mejor** | Marca la copia con mayor score | La otra(s) copia(s) van a papelera |
| **Eliminar la peor** | Elimina la copia con menor score | Va a papelera (si activada) |
| **Ignorar grupo** | Marca como "ignorado" | No se vuelve a mostrar en el wizard |
| **Omitir** | No decide ahora | El grupo permanece pendiente |

### 5.6 Operación en Segundo Plano

```
Cuando el usuario selecciona "Conservar" o "Eliminar":
1. Se muestra un spinner inline en la tarjeta
2. Se ejecuta la operación en background:
   - Si papelera activa: mover a /media/tmp/DupeManager-trash/
   - Si papelera inactiva: eliminar directamente
3. Se muestra toast "Operación completada" (3 segundos)
4. Se pasa automáticamente al siguiente grupo
5. Si hay error → toast de error en rojo, el grupo permanece
```

---

## 6. Sección de Episodios

### 6.1 Layout

```
┌─────────────────────────────────────────────────────────┐
│  Episodios Duplicados                                    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  [🔍 Buscar...]  [Filtrar por serie ▼]  [Solo pendientes]│
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  #  │ Serie              │ Ep   │ Copias │ Tamaño │   │
│  │─────┼────────────────────┼──────┼────────┼────────│   │
│  │  1  │ Big Bang Theory    │ S01E01│   2    │ 2.7 GB │   │
│  │  2  │ Big Bang Theory    │ S01E02│   2    │ 2.5 GB │   │
│  │  3  │ La Casa del Dragón │ S03E01│   2    │ 8.2 GB │   │
│  │  4  │ Fundación          │ S03E02│   3    │ 4.1 GB │   │
│  │  5  │ Andor              │ S02E01│   2    │ 3.8 GB │   │
│  │ ... │                    │      │        │        │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  Mostrando 1-25 de 244 grupos                           │
│  [← Anterior] [1][2][3]...[10] [Siguiente →]            │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 6.2 Filtros

| Filtro | Tipo | Descripción |
|--------|------|-------------|
| **Buscar** | Texto | Busca por nombre de serie o episodio |
| **Serie** | Dropdown | Filtra por serie específica |
| **Solo pendientes** | Checkbox | Oculta grupos ya resueltos/ignorados |

### 6.3 Tabla de Episodios

| Columna | Descripción |
|---------|-------------|
| **#** | Número de grupo |
| **Serie** | Nombre de la serie |
| **Ep** | Temporada y episodio (S01E01) |
| **Copias** | Número de copias detectadas |
| **Tamaño** | Tamaño total del grupo |
| **Estado** | Pendiente / Resuelto / Ignorado |

---

## 7. Sección de Películas

### 7.1 Layout

Igual que episodios pero adaptado a películas:

```
┌─────────────────────────────────────────────────────────┐
│  Películas Duplicadas                                    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  [🔍 Buscar...]  [Filtrar por año ▼]  [Solo pendientes] │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  #  │ Película            │ Año  │ Copias │ Tam. │   │
│  │─────┼─────────────────────┼──────┼────────┼──────│   │
│  │  1  │ El atlas de las     │ 2024 │   2    │ 9 GB │   │
│  │     │ nubes               │      │        │      │   │
│  │  2  │ Oppenheimer         │ 2024 │   2    │ 12GB │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 8. Sección de Ignorados

### 8.1 Concepto

Los duplicados ignorados son aquellos que el usuario ha decidido que **no son realmente duplicados** (ej: One Piece live action vs anime) o que prefiere mantener ambas versiones intencionalmente.

### 8.2 Layout

```
┌─────────────────────────────────────────────────────────┐
│  Duplicados Ignorados                                    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Estos duplicados no se mostrarán en el dashboard ni    │
│  en el wizard de revisión. Puedes restaurarlos si        │
│  cambias de opinión.                                     │
│                                                          │
│  [🔍 Buscar...]  [🔄 Restaurar seleccionados]           │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  #  │ Nombre               │ Tipo    │ Ignorado │   │
│  │─────┼──────────────────────┼─────────┼──────────│   │
│  │  1  │ ONE PIECE            │ Serie   │ 23/08/26 │   │
│  │  2  │ The Buccaneers       │ Serie   │ 23/08/26 │   │
│  │  3  │ DOC                  │ Serie   │ 23/08/26 │   │
│  │  4  │ La Casa del Dragón   │ Serie   │ 23/08/26 │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  Cada fila tiene un botón [🔄 Restaurar] individual     │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 8.3 Acciones

| Acción | Descripción |
|--------|-------------|
| **Restaurar** | Devuelve el grupo a "pendiente" para que reaparezca en el wizard |
| **Restaurar seleccionados** | Restaura múltiples grupos a la vez |

---

## 9. Sección de Configuración

### 9.1 Layout

```
┌─────────────────────────────────────────────────────────┐
│  Configuración                                           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  🗑️ Papelera de Reciclaje                         │   │
│  │                                                    │   │
│  │  [✅] Activar papelera de reciclaje               │   │
│  │                                                    │   │
│  │  Cuando se activa, los archivos eliminados se     │   │
│  │  mueven a una carpeta temporal en vez de           │   │
│  │  eliminarse permanentemente.                       │   │
│  │                                                    │   │
│  │  Tiempo antes de borrado automático:               │   │
│  │  [  30  ] [días ▼]                                 │   │
│  │                                                    │   │
│  │  [🗑️ Vaciar Papelera Ahora]                       │   │
│  │  ⚠️ Esto eliminará permanentemente todos los       │   │
│  │  archivos de la papelera.                          │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  ⏰ Escaneo Automático                             │   │
│  │                                                    │   │
│  │  [✅] Activar escaneo automático                   │   │
│  │                                                    │   │
│  │  Frecuencia:                                       │   │
│  │  [  7  ] [días ▼]                                  │   │
│  │                                                    │   │
│  │  Unidades: minutos, horas, días, semanas, meses    │   │
│  │  (mínimo: 5 minutos, máximo: 12 meses)             │   │
│  │                                                    │   │
│  │  Último escaneo automático: 23/08/2026 14:30       │   │
│  │  Próximo escaneo: 30/08/2026 14:30                │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  🔔 Notificaciones                                 │   │
│  │                                                    │   │
│  │  [✅] Notificaciones del navegador (Push)          │   │
│  │      Recibe alertas cuando se detecten nuevos      │   │
│  │      duplicados. Solo funciona con el navegador    │   │
│  │      abierto.                                      │   │
│  │                                                    │   │
│  │  [✅] Webhook                                      │   │
│  │      URL del webhook:                              │   │
│  │      [https://ntfy.sh/mi-canal_______________]    │   │
│  │                                                    │   │
│  │      Servicios compatibles: ntfy, Gotify,          │   │
│  │      Discord, Telegram, Slack, AnyDesk, etc.       │   │
│  │                                                    │   │
│  │      Formato enviado:                              │   │
│  │      { "message": "...", "title": "DupeManager" }  │   │
│  │                                                    │   │
│  │  [✅] Email                                         │   │
│  │      SMTP Host: [smtp.gmail.com_____]              │   │
│  │      Puerto:    [587___]                            │   │
│  │      Usuario:   [user@gmail.com___]                │   │
│  │      Contraseña:[••••••••••]                        │   │
│  │      Para:      [user@gmail.com___]                │   │
│  │      [✉️ Enviar email de prueba]                   │   │
│  │                                                    │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  🔧 Avanzado                                       │   │
│  │                                                    │   │
│  │  [🔄 Reconstruir Base de Datos]                    │   │
│  │  Borra la caché de escaneos y reconstruye desde    │   │
│  │  cero. Útil si los datos parecen incorrectos.     │   │
│  │                                                    │   │
│  │  [📊 Exportar Resultados]                          │   │
│  │  Descarga un CSV/Excel con todos los duplicados    │   │
│  │  detectados.                                       │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 9.2 Opciones de Configuración

| Opción | Tipo | Default | Descripción |
|--------|------|---------|-------------|
| `TRASH_ENABLED` | boolean | `true` | Activa/desactiva la papelera |
| `TRASH_RETENTION_VALUE` | integer | `30` | Valor numérico de retención |
| `TRASH_RETENTION_UNIT` | enum | `days` | Unidad: minutes, hours, days, weeks, months |
| `AUTO_SCAN_ENABLED` | boolean | `true` | Activa/desactiva escaneo automático |
| `AUTO_SCAN_VALUE` | integer | `7` | Valor numérico del intervalo |
| `AUTO_SCAN_UNIT` | enum | `days` | Unidad: minutes, hours, days, weeks, months |
| `NOTIFICATIONS_BROWSER` | boolean | `false` | Notificaciones push del navegador |
| `NOTIFICATIONS_WEBHOOK_ENABLED` | boolean | `false` | Activa webhook |
| `NOTIFICATIONS_WEBHOOK_URL` | string | `""` | URL del webhook |
| `NOTIFICATIONS_EMAIL_ENABLED` | boolean | `false` | Activa email |
| `NOTIFICATIONS_EMAIL_SMTP_HOST` | string | `""` | Servidor SMTP |
| `NOTIFICATIONS_EMAIL_SMTP_PORT` | integer | `587` | Puerto SMTP |
| `NOTIFICATIONS_EMAIL_USERNAME` | string | `""` | Usuario SMTP |
| `NOTIFICATIONS_EMAIL_PASSWORD` | string | `""` | Contraseña SMTP |
| `NOTIFICATIONS_EMAIL_TO` | string | `""` | Email destino |
| `MEDIA_PATH` | string | `/media` | Ruta base de medios dentro del container |
| `TRASH_PATH` | string | `/media/tmp/DupeManager-trash` | Ruta de la papelera |

### 9.3 Selectores de Duración

Los campos de duración (retención de papelera, intervalo de escaneo) usan un selector compuesto:

```
┌─────────┐ ┌──────────────┐
│  valor  │ │  unidad ▼    │
└─────────┘ └──────────────┘

Unidades disponibles:
  - minutos  (mín: 5)
  - horas    (mín: 1)
  - días     (mín: 1)
  - semanas  (mín: 1)
  - meses    (mín: 1, máx: 12)

Validación:
  - 5 minutos → 1440 minutos (24h)
  - 1 hora → 720 horas (30 días)
  - 1 día → 365 días
  - 1 semana → 52 semanas
  - 1 mes → 12 meses
```

### 9.4 Notificaciones — Detalle

#### Browser Push
```
Flujo:
1. Usuario activa "Notificaciones del navegador"
2. El navegador pide permiso al usuario
3. Si acepta → se almacena la suscripción push
4. Cuando se detectan duplicados nuevos:
   → Backend envía push al navegador
   → Se muestra notificación nativa del SO
   → Al hacer clic → se abre la app

Limitación: Solo funciona si el navegador está abierto
```

#### Webhook
```
Flujo:
1. Usuario activa webhook y configura URL
2. Cuando se detectan duplicados nuevos:
   → Backend hace POST a la URL configurada
   → Envía JSON:
     {
       "title": "DupeManager",
       "message": "Se detectaron 3 duplicados nuevos",
       "priority": "normal",
       "tags": ["dupemanager", "duplicates"]
     }

Servicios compatibles (sin cambios):
  - ntfy.sh          POST https://ntfy.sh/canal
  - Gotify           POST https://gotify.example.com/message
  - Discord          POST https://discord.com/api/webhooks/...
  - Telegram Bot     POST https://api.telegram.org/bot.../sendMessage
  - Slack            POST https://hooks.slack.com/services/...
```

#### Email
```
Flujo:
1. Usuario activa email y configura SMTP
2. Puede pulsar "Enviar email de prueba" para verificar
3. Cuando se detectan duplicados nuevos:
   → Backend envía email vía SMTP
   → Asunto: "DupeManager: X duplicados nuevos detectados"
   → Cuerpo: lista de duplicados encontrados

Puertos comunes:
  - 587 (TLS) - recomendado
  - 465 (SSL)
  - 25  (sin cifrar) - no recomendado
```

### 9.5 Trigger de Notificaciones

Las notificaciones se envían **únicamente** cuando:

| Evento | Notificar |
|--------|-----------|
| Escaneo automático detecta duplicados nuevos | SÍ |
| Escaneo manual ("Escanear Ahora") detecta duplicados nuevos | SÍ |
| Se completa un escaneo sin duplicados nuevos | NO |
| Se elimina un duplicado | NO |
| Se ignora un duplicado | NO |
| La papelera se vacía automáticamente | NO |

**Lógica**: Se comparan los grupos detectados con los ya conocidos en la BD. Solo se notifican los **nuevos** (que no existían en el escaneo anterior).

---

## 10. Sistema de Toast/Banners

### 10.1 Posición y Estilo

```
┌──────────────────────────────────────┐
│                               ┌──────┤
│                               │ Toast│
│                               │      │
│                               └──────┘
│                          Esquina inferior derecha
```

### 10.2 Tipos de Toast

| Tipo | Color | Icono | Duración | Ejemplo |
|------|-------|-------|----------|---------|
| **Progreso** | Azul | ⏳ | Hasta completar | "Escaneando... 45%" |
| **Éxito** | Verde | ✅ | 3 segundos | "Operación completada" |
| **Error** | Rojo | ❌ | Hasta cerrar manualmente | "Error al eliminar archivo" |
| **Info** | Gris | ℹ️ | 5 segundos | "Escaneo automático programado" |

### 10.3 Comportamiento

```
Operación iniciada (escaneo, eliminación):
  → Muestra toast de progreso con barra de progreso
  → Se queda visible mientras la operación está en curso
  → Cuando termina: se cierra el toast de progreso

Completado con éxito:
  → Se abre toast de éxito (verde, 3 segundos)
  → Se cierra automáticamente

Error:
  → Se abre toast de error (rojo)
  → NO se cierra automáticamente
  → El usuario debe pulsar [X] para cerrarlo
  → Muestra mensaje de error descriptivo
```

### 10.4 Toast de Progreso (Detalle)

```
┌──────────────────────────────────────────┐
│ ⏳ Escaneando...                          │
│ ████████████████░░░░░░░░░░░░  65%        │
│ Procesando: La Casa del Dragón S03E05    │
│ Grupo 127 de 246                          │
└──────────────────────────────────────────┘
```

---

## 11. Jerarquía de Calidad (Scoring)

### 11.1 Tabla de Scores

| Score | Resolución | Notas |
|-------|-----------|-------|
| **10** | 1080p HEVC | Máxima prioridad |
| **8** | 1080p (H264/otros) | |
| **6** | 720p | |
| **5** | 2K / 1440p | |
| **4** | 4K / 2160p | |
| **2** | SD / DVD / 3D | |
| **0** | CAM / TS / TC | |
| **-1** | No definido | Al final de prioridades |

### 11.2 Reglas

- 4K y 2K van **DESPUÉS** de 1080p/720p
- 2K tiene prioridad sobre 4K
- Cualquier formato/resolución no listado obtiene score `-1`
- El score se extrae del **filename** y de los **MediaStreams** de Jellyfin
- En empate, se prefiere el archivo de **mayor tamaño** (más bitrate = mejor calidad)

---

## 12. Detección de Duplicados

### 12.1 Algoritmo de Agrupación

#### Episodios
```
Clave de agrupación: (nombre_serie_normalizado, temporada, episodio)

Ejemplo:
  "Big Bang Theory/Season 1/Big Bang Theory s01e01.mkv"
  → ("big bang theory", 1, 1)

  "Big Bang Theory/Season 1/Big Bang Theory s01e01.avi"
  → ("big bang theory", 1, 1)

  Ambos mapean a la misma clave → DUPLICADO
```

#### Películas
```
Clave de agrupación: (nombre_normalizado, año)

Ejemplo:
  "El atlas de las nubes [MicroHD][...] (2024)"
  → ("el atlas de las nubes", 2024)

  "El atlas de las nubes [BluRay 1080p][...] (2024)"
  → ("el atlas de las nubes", 2024)

  Ambos mapean a la misma clave → DUPLICADO
```

### 12.2 Filtrado de Falsos Positivos

**Problema**: Series con nombres similares pero diferentes se agrupan incorrectamente.

**Ejemplos conocidos**:
| Nombre 1 | Nombre 2 | ¿Realmente duplicado? |
|-----------|----------|----------------------|
| ONE PIECE | One Piece | NO (anime vs live action) |
| DOC | Doc | POSIBLE (misma serie, capitalización diferente) |
| The Buccaneers: Aristócratas por amor | The Buccaneers: aristócratas por amor | SÍ (diferencia solo en mayúsculas) |
| La Casa del Dragón | La casa del dragón | SÍ (diferencia solo en mayúsculas) |

**Solución**: El usuario revisa estos casos en el wizard y los marca como "Ignorados". Los ignorados se persisten en la BD y no reaparecen.

### 12.3 Extracción de Calidad del Filename

```python
# Resolución
2160p|4k|uhd → score 4
1440p|2k → score 5
1080p → score 8 (HEVC) o score 8 (otros)
720p → score 6
480p → score 2

# Codec
hevc|h265|x265 → +2 bonus
h264|x264|avc → +0

# Fuente
bluray|bdrip|bdremux → +1 bonus
web-dl|webrip → +0
hdrip|hdtv → -1
dvdrip → -2
microhd → +0

# 3D
3d|sbs|half-ou → score 2 (forzado)
```

---

## 13. API Endpoints (Detalle)

### Auth
| Method | Endpoint | Body | Response |
|--------|----------|------|----------|
| POST | `/api/auth/login` | `{ username, password }` | `{ token, user }` |
| POST | `/api/auth/refresh` | — | `{ token }` |
| GET | `/api/auth/me` | — | `{ user }` |

### Dashboard
| Method | Endpoint | Response |
|--------|----------|----------|
| GET | `/api/dashboard` | `{ totalEpisodes, totalMovies, duplicateGroups, recoverableSize, lastScan }` |

### Scan
| Method | Endpoint | Response |
|--------|----------|----------|
| POST | `/api/scan` | `{ scanId }` (inicia en background) |
| GET | `/api/scan/status` | `{ running, progress, current, total, message }` |

### Episodes
| Method | Endpoint | Response |
|--------|----------|----------|
| GET | `/api/episodes` | `[{ groupId, seriesName, season, episode, copies[], totalSize, status }]` |
| GET | `/api/episodes/:groupId` | `{ groupId, seriesName, season, episode, copies[] }` |
| POST | `/api/episodes/:groupId/action` | `{ action: "keep"|"ignore"|"skip", keepFileId? }` |

### Movies
| Method | Endpoint | Response |
|--------|----------|----------|
| GET | `/api/movies` | `[{ groupId, name, year, copies[], totalSize, status }]` |
| GET | `/api/movies/:groupId` | `{ groupId, name, year, copies[] }` |
| POST | `/api/movies/:groupId/action` | `{ action: "keep"|"ignore"|"skip", keepFileId? }` |

### Ignored
| Method | Endpoint | Response |
|--------|----------|----------|
| GET | `/api/ignored` | `[{ groupId, name, type, ignoredAt }]` |
| POST | `/api/ignored/:groupId/restore` | `{ success }` |
| POST | `/api/ignored/restore-many` | `{ success, restored }` |

### Settings
| Method | Endpoint | Body | Response |
|--------|----------|------|----------|
| GET | `/api/settings` | — | `{ trashEnabled, trashRetentionValue, trashRetentionUnit, autoScanEnabled, autoScanValue, autoScanUnit, notifications: { browser, webhook: { enabled, url }, email: { enabled, smtpHost, ... } }, ... }` |
| PUT | `/api/settings` | `{ trashEnabled?, trashRetentionValue?, ... }` | `{ success }` |
| POST | `/api/settings/trash/empty` | — | `{ success, deleted }` |
| POST | `/api/settings/rebuild-db` | — | `{ success }` |
| POST | `/api/settings/notifications/test-email` | — | `{ success }` |
| POST | `/api/settings/notifications/test-webhook` | — | `{ success }` |

### Actions (Background)
| Method | Endpoint | Response |
|--------|----------|----------|
| GET | `/api/actions/status` | `{ running, progress, action, message }` |

---

## 14. Estructura del Proyecto (Actualizada)

```
DupeManager/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
├── LICENSE                       # GNU GPLv3
├── README.md
│
├── backend/
│   ├── main.py                   # FastAPI app + startup
│   ├── config.py                 # Settings desde .env
│   ├── database.py               # SQLite models (SQLAlchemy)
│   ├── auth.py                   # JWT + Jellyfin auth
│   │
│   ├── jellyfin/
│   │   ├── __init__.py
│   │   ├── client.py             # HTTP client para API
│   │   └── models.py             # Tipos de datos
│   │
│   ├── scanner/
│   │   ├── __init__.py
│   │   ├── detector.py           # Agrupación de duplicados
│   │   ├── normalizer.py         # Normalización de nombres
│   │   ├── quality.py            # Scoring de calidad
│   │   └── filesystem.py         # Acceso a archivos (NFS)
│   │
│   ├── actions/
│   │   ├── __init__.py
│   │   └── manager.py            # Conservar/ignorar/eliminar/trash
│   │
│   └── api/
│       ├── __init__.py
│       ├── auth.py               # POST /api/auth/login
│       ├── dashboard.py          # GET /api/dashboard
│       ├── scan.py               # POST /api/scan
│       ├── episodes.py           # GET/POST /api/episodes
│       ├── movies.py             # GET/POST /api/movies
│       ├── ignored.py            # GET/POST /api/ignored
│       └── settings.py           # GET/PUT /api/settings
│
├── frontend/
│   ├── index.html                # Shell de la SPA
│   ├── css/
│   │   └── styles.css            # Tailwind + custom styles
│   ├── js/
│   │   ├── app.js                # Router + estado global
│   │   ├── api.js                # Cliente HTTP con JWT
│   │   ├── auth.js               # Login + logout
│   │   ├── dashboard.js          # Vista dashboard
│   │   ├── episodes.js           # Lista de episodios
│   │   ├── movies.js             # Lista de películas
│   │   ├── ignored.js            # Lista de ignorados
│   │   ├── wizard.js             # Modal wizard de revisión
│   │   ├── settings.js           # Configuración
│   │   ├── toast.js              # Sistema de banners
│   │   └── components.js         # Componentes reutilizables
│   └── assets/
│       └── logo.svg
│
└── data/
    └── dupeManager.db            # SQLite (volume persistente)
```

---

## 15. Configuración de Red

### nginx-proxy-manager (Configuración manual)

| Campo | Valor |
|-------|-------|
| **Dominio** | `dupe.tudominio.com` (o IP interna) |
| **Scheme** | http |
| **Forward Host** | `192.168.0.22` |
| **Forward Port** | `8097` |
| **SSL** | Let's Encrypt (si acceso externo) |
| **WebSocket Support** | Sí |

---

## 16. Resumen de Casos de Uso

| ID | Caso de Uso | Fase |
|----|-------------|------|
| CU-LOGIN-01 | El admin se logra con credenciales de Jellyfin | 1 |
| CU-LOGIN-02 | Un usuario no-admin es rechazado | 1 |
| CU-DASH-01 | El admin ve el resumen del dashboard | 1 |
| CU-DASH-02 | El admin pulsa "Escanear ahora" | 1 |
| CU-DASH-03 | El admin pulsa "Revisar Duplicados" | 1 |
| CU-WIZ-01 | El wizard muestra el primer grupo de duplicados | 1 |
| CU-WIZ-02 | El admin conserva la mejor copia | 1 |
| CU-WIZ-03 | El admin ignora un grupo | 1 |
| CU-WIZ-04 | El wizard pasa al siguiente grupo automáticamente | 1 |
| CU-WIZ-05 | El wizard muestra progreso y completado | 1 |
| CU-EPI-01 | El admin ve la lista de episodios duplicados | 1 |
| CU-EPI-02 | El admin filtra por serie | 1 |
| CU-PEL-01 | El admin ve la lista de películas duplicadas | 1 |
| CU-IGN-01 | El admin ve los ignorados | 1 |
| CU-IGN-02 | El admin restaura un ignorado | 1 |
| CU-SET-01 | El admin configura la papelera (activar, retención) | 2 |
| CU-SET-02 | El admin vacía la papelera manualmente | 2 |
| CU-SET-03 | El admin configura el escaneo automático (intervalo con unidad) | 2 |
| CU-SET-04 | El admin activa/desactiva notificaciones del navegador | 2 |
| CU-SET-05 | El admin configura webhook (URL + prueba) | 2 |
| CU-SET-06 | El admin configura email (SMTP + prueba) | 2 |
| CU-SCAN-01 | El escaneo automático se ejecuta según intervalo configurado | 2 |
| CU-SCAN-02 | Se comparan resultados con escaneo anterior para detectar nuevos | 2 |
| CU-TRASH-01 | Los archivos eliminados van a papelera (si activada) | 2 |
| CU-TRASH-02 | La papelera se vacía automáticamente según retención | 2 |
| CU-NOTIF-01 | Se envía notificación del navegador al detectar duplicados nuevos | 2 |
| CU-NOTIF-02 | Se envía webhook al detectar duplicados nuevos | 2 |
| CU-NOTIF-03 | Se envía email al detectar duplicados nuevos | 2 |
| CU-NOTIF-04 | El admin prueba el webhook desde la configuración | 2 |
| CU-NOTIF-05 | El admin prueba el email desde la configuración | 2 |
| CU-TOAST-01 | Se muestra toast de progreso durante operaciones | 1 |
| CU-TOAST-02 | Se muestra toast de éxito al completar | 1 |
| CU-TOAST-03 | Se muestra toast de error si falla | 1 |
