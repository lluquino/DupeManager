# DupeManager — Fases de Desarrollo

## Visión General

El proyecto se divide en **3 fases principales** con **12 hitos**. Cada hito produce un entregable funcional que se puede probar de forma independiente.

```
Fase 0: Fundación         ──── Setup proyecto + infraestructura base
Fase 1: Core              ──── Lo mínimo para que la app funcione
  ├── Hito 1.1: Backend Base      (API + Auth + BD)
  ├── Hito 1.2: Scanner           (Detección de duplicados)
  ├── Hito 1.3: Frontend Base     (Login + Layout + Router)
  ├── Hito 1.4: Dashboard         (Estadísticas + acciones)
  ├── Hito 1.5: Wizard            (Revisión de duplicados)
  └── Hito 1.6: Listas            (Episodios + Películas + Ignorados)
Fase 2: Gestión           ──── Funcionalidades de administración
  ├── Hito 2.1: Acciones          (Conservar/eliminar archivos)
  ├── Hito 2.2: Papelera          (Trash + auto-limpieza)
  ├── Hito 2.3: Configuración     (Settings UI completa)
  └── Hito 2.4: Notificaciones    (Browser push + Webhook + Email)
Fase 3: Producción        ──── Preparado para desplegar
  ├── Hito 3.1: Docker            (Dockerfile + Compose)
  └── Hito 3.2: Deploy            (Despliegue en VM 100 + nginx)
```

---

## Fase 0: Fundación

### Hito 0.1: Inicialización del Proyecto
**Objetivo**: Estructura base del repo, dependencias, configuración.

**Tareas**:
| # | Tarea | Archivos | Dependencias |
|---|-------|----------|--------------|
| 0.1.1 | Inicializar repo Git + LICENSE GPLv3 | `.gitignore`, `LICENSE` | — |
| 0.1.2 | Crear estructura de directorios | Todos los directorios | — |
| 0.1.3 | Configurar `requirements.txt` | `requirements.txt` | — |
| 0.1.4 | Crear `.env.example` con todas las variables | `.env.example` | — |
| 0.1.5 | Crear `config.py` para leer `.env` | `backend/config.py` | 0.1.4 |
| 0.1.6 | Crear `Dockerfile` base (solo Python) | `Dockerfile` | 0.1.3 |
| 0.1.7 | Crear `docker-compose.yml` base | `docker-compose.yml` | 0.1.6 |

**Entregable**: Repo con estructura lista, `docker-compose up` ejecuta un servidor FastAPI vacío.

**Dependencias externas**: Ninguna (solo Python + Docker local).

---

## Fase 1: Core (MVP)

### Hito 1.1: Backend Base
**Objetivo**: API funcional con auth, BD, y conexión a Jellyfin.

**Tareas**:
| # | Tarea | Archivos | Dependencias |
|---|-------|----------|--------------|
| 1.1.1 | Crear models de SQLAlchemy (episodios, películas, ignorados, settings, scan_log) | `backend/database.py` | 0.1.5 |
| 1.1.2 | Crear cliente HTTP para Jellyfin API | `backend/jellyfin/client.py` | 0.1.5 |
| 1.1.3 | Crear módulo de autenticación (JWT + Jellyfin auth) | `backend/auth.py` | 1.1.1, 1.1.2 |
| 1.1.4 | Crear endpoint POST /api/auth/login | `backend/api/auth.py` | 1.1.3 |
| 1.1.5 | Crear endpoint GET /api/dashboard | `backend/api/dashboard.py` | 1.1.1, 1.1.2 |
| 1.1.6 | Crear main.py con FastAPI app + middleware | `backend/main.py` | Todas anteriores |
| 1.1.7 | Probar conexión a Jellyfin desde container | Test manual | 1.1.2 |

**Entregable**: `curl http://localhost:8097/api/dashboard` devuelve datos reales de Jellyfin.

**Criterio de aceptación**:
- Login funcional contra Jellyfin real
- Solo admins pueden acceder
- Dashboard devuelve totales correctos

---

### Hito 1.2: Scanner
**Objetivo**: Motor de detección de duplicados.

**Tareas**:
| # | Tarea | Archivos | Dependencias |
|---|-------|----------|--------------|
| 1.2.1 | Crear normalizador de nombres | `backend/scanner/normalizer.py` | — |
| 1.2.2 | Crear extractor de calidad del filename | `backend/scanner/quality.py` | — |
| 1.2.3 | Crear detector de duplicados (agrupación) | `backend/scanner/detector.py` | 1.2.1, 1.2.2 |
| 1.2.4 | Crear módulo de acceso a filesystem (tamaños) | `backend/scanner/filesystem.py` | 0.1.5 |
| 1.2.5 | Crear endpoint POST /api/scan + GET /api/scan/status | `backend/api/scan.py` | 1.2.3, 1.2.4 |
| 1.2.6 | Crear sistema de colas para escaneo en background | `backend/queue.py` | — |
| 1.2.7 | Probar escaneo completo con datos reales | Test manual | Todas anteriores |

**Entregable**: `curl -X POST http://localhost:8097/api/scan` ejecuta escaneo completo y almacena resultados.

**Criterio de aceptación**:
- Detecta duplicados correctamente (244+ grupos episodios, 2+ películas)
- Scores de calidad correctos según jerarquía
- Escaneo funciona en background sin bloquear la API
- Progreso visible vía /api/scan/status

---

### Hito 1.3: Frontend Base
**Objetivo**: App con login, layout, y navegación funcional.

**Tareas**:
| # | Tarea | Archivos | Dependencias |
|---|-------|----------|--------------|
| 1.3.1 | Crear index.html con Tailwind CDN + estructura base | `frontend/index.html` | — |
| 1.3.2 | Crear sistema de router hash (#/) | `frontend/js/app.js` | 1.3.1 |
| 1.3.3 | Crear cliente HTTP con JWT | `frontend/js/api.js` | 1.3.1 |
| 1.3.4 | Crear pantalla de login | `frontend/js/auth.js` | 1.3.2, 1.3.3 |
| 1.3.5 | Crear layout con header + navegación | `frontend/js/components.js` | 1.3.2 |
| 1.3.6 | Crear sistema de toast/banners | `frontend/js/toast.js` | 1.3.1 |
| 1.3.7 | Crear estilos custom | `frontend/css/styles.css` | 1.3.1 |
| 1.3.8 | Crear assets (logo SVG) | `frontend/assets/logo.svg` | — |

**Entregable**: Login funcional, navegar entre secciones vacías, toasts funcionan.

**Criterio de aceptación**:
- Login muestra errores correctamente
- JWT se almacena en localStorage
- Navegación funciona con hash routes
- Toast de éxito/error se muestra y se cierra

---

### Hito 1.4: Dashboard
**Objetivo**: Dashboard con datos reales y acciones.

**Tareas**:
| # | Tarea | Archivos | Dependencias |
|---|-------|----------|--------------|
| 1.4.1 | Crear vista dashboard con tarjetas de stats | `frontend/js/dashboard.js` | 1.3.5 |
| 1.4.2 | Conectar dashboard con API /api/dashboard | `frontend/js/dashboard.js` | 1.3.3, 1.1.5 |
| 1.4.3 | Agregar botón "Escanear Ahora" con toast de progreso | `frontend/js/dashboard.js` | 1.3.6, 1.2.5 |
| 1.4.4 | Agregar botón "Revisar Duplicados" (placeholder) | `frontend/js/dashboard.js` | 1.3.5 |
| 1.4.5 | Mostrar top 5 series con más duplicados | `frontend/js/dashboard.js` | 1.1.5 |

**Entregable**: Dashboard muestra datos reales, escaneo funciona desde la UI.

**Criterio de aceptación**:
- Tarjetas muestran totales correctos
- "Escanear Ahora" ejecuta escaneo con toast de progreso
- Top 5 se muestra correctamente

---

### Hito 1.5: Wizard
**Objetivo**: Modal de revisión de duplicados funcional.

**Tareas**:
| # | Tarea | Archivos | Dependencias |
|---|-------|----------|--------------|
| 1.5.1 | Crear modal base de pantalla completa | `frontend/js/wizard.js` | 1.3.5 |
| 1.5.2 | Crear tarjetas de copias con info de calidad | `frontend/js/wizard.js` | 1.5.1 |
| 1.5.3 | Implementar navegación entre grupos (anterior/siguiente) | `frontend/js/wizard.js` | 1.5.2 |
| 1.5.4 | Implementar acción "Conservar la mejor" | `frontend/js/wizard.js` | 1.5.3 |
| 1.5.5 | Implementar acción "Ignorar grupo" | `frontend/js/wizard.js` | 1.5.3 |
| 1.5.6 | Implementar acción "Omitir" | `frontend/js/wizard.js` | 1.5.3 |
| 1.5.7 | Conectar wizard con API de escaneo | `frontend/js/wizard.js` | 1.3.3, 1.2.5 |
| 1.5.8 | Mostrar progreso (barra + contador) | `frontend/js/wizard.js` | 1.5.3 |
| 1.5.9 | Mostrar resumen al completar todos los grupos | `frontend/js/wizard.js` | 1.5.8 |

**Entregable**: Wizard completamente funcional con todas las acciones.

**Criterio de aceptación**:
- Muestra grupos correctamente con toda la info
- Score y "mejor" resaltados
- Acciones funcionan (por ahora marcan en BD, sin mover archivos)
- Progreso se muestra correctamente
- Se puede cerrar y reabrir

---

### Hito 1.6: Listas
**Objetivo**: Tablas de episodios, películas e ignorados.

**Tareas**:
| # | Tarea | Archivos | Dependencias |
|---|-------|----------|--------------|
| 1.6.1 | Crear vista de episodios con tabla | `frontend/js/episodes.js` | 1.3.5 |
| 1.6.2 | Agregar filtros (buscar, serie, pendientes) | `frontend/js/episodes.js` | 1.6.1 |
| 1.6.3 | Agregar paginación | `frontend/js/episodes.js` | 1.6.2 |
| 1.6.4 | Crear vista de películas (similar a episodios) | `frontend/js/movies.js` | 1.3.5 |
| 1.6.5 | Crear vista de ignorados | `frontend/js/ignored.js` | 1.3.5 |
| 1.6.6 | Agregar acción "Restaurar" en ignorados | `frontend/js/ignored.js` | 1.6.5 |
| 1.6.7 | Conectar todas las vistas con sus endpoints | Todos | 1.3.3 |

**Entregable**: Las 3 listas funcionan con filtros y paginación.

**Criterio de aceptación**:
- Episodios muestra todos los grupos duplicados
- Filtros funcionan correctamente
- Películas muestra duplicados de películas
- Ignorados muestra los marcados y permite restaurar

---

### Fin de Fase 1 — MVP Funcional

**En este punto la app es usable**:
- Login funcional
- Dashboard con datos reales
- Wizard de revisión funcional
- Listas con filtros
- Escaneo manual funciona

**NO hace todavía**:
- Mover/eliminar archivos reales
- Papelera
- Notificaciones
- Escaneo automático
- Configuración UI

---

## Fase 2: Gestión

### Hito 2.1: Acciones
**Objetivo**: Que las acciones del wizard realmente funcionen.

**Tareas**:
| # | Tarea | Archivos | Dependencias |
|---|-------|----------|--------------|
| 2.1.1 | Crear manager de acciones (conservar/eliminar) | `backend/actions/manager.py` | 1.1.1, 1.2.4 |
| 2.1.2 | Implementar movimiento a papelera (si activada) | `backend/actions/manager.py` | 2.1.1 |
| 2.1.3 | Implementar eliminación directa (si papelera desactivada) | `backend/actions/manager.py` | 2.1.1 |
| 2.1.4 | Crear endpoint POST /api/episodes/:id/action | `backend/api/episodes.py` | 2.1.1 |
| 2.1.5 | Crear endpoint POST /api/movies/:id/action | `backend/api/movies.py` | 2.1.1 |
| 2.1.6 | Crear endpoint POST /api/ignored/:id/restore | `backend/api/ignored.py` | 2.1.1 |
| 2.1.7 | Crear endpoint POST /api/ignored/restore-many | `backend/api/ignored.py` | 2.1.1 |
| 2.1.8 | Conectar wizard con endpoints de acción reales | `frontend/js/wizard.js` | 2.1.4-7, 1.5 |
| 2.1.9 | Crear endpoint GET /api/actions/status | `backend/api/actions.py` | 2.1.1 |
| 2.1.10 | Probar flujo completo: wizard → eliminar → archivo movido | Test manual | Todas anteriores |

**Entregable**: Wizard ejecuta acciones reales sobre archivos.

**Criterio de aceptación**:
- "Conservar la mejor" mueve la peor a papelera (o la elimina)
- "Ignorar" marca el grupo como ignorado en BD
- Archivos se mueven/eliminan correctamente en el NFS
- Errores se muestran en toast
- Progreso de la operación visible

---

### Hito 2.2: Papelera
**Objetivo**: Sistema de papelera con auto-limpieza.

**Tareas**:
| # | Tarea | Archivos | Dependencias |
|---|-------|----------|--------------|
| 2.2.1 | Crear servicio de papelera (mover a trash) | `backend/actions/trash.py` | 2.1.1 |
| 2.2.2 | Crear servicio de auto-limpieza (cron interno) | `backend/actions/cleanup.py` | 2.2.1 |
| 2.2.3 | Crear endpoint POST /api/settings/trash/empty | `backend/api/settings.py` | 2.2.1 |
| 2.2.4 | Integrar cleanup en el startup de FastAPI | `backend/main.py` | 2.2.2 |
| 2.2.5 | Probar auto-limpieza con tiempo acelerado | Test manual | 2.2.2 |

**Entregable**: Papelera funciona con auto-limpieza.

**Criterio de aceptación**:
- Archivos van a `/media/tmp/DupeManager-trash/`
- Auto-limpieza respeta el tiempo de retención configurado
- "Vaciar papelera" elimina todo
- Estructura de carpetas en trash mantiene organización

---

### Hito 2.3: Configuración
**Objetivo**: UI completa de configuración.

**Tareas**:
| # | Tarea | Archivos | Dependencias |
|---|-------|----------|--------------|
| 2.3.1 | Crear vista de configuración | `frontend/js/settings.js` | 1.3.5 |
| 2.3.2 | Sección papelera (toggle, retención, vaciar) | `frontend/js/settings.js` | 2.2.1 |
| 2.3.3 | Sección escaneo automático (toggle, intervalo) | `frontend/js/settings.js` | — |
| 2.3.4 | Crear componente selector de duración (valor + unidad) | `frontend/js/components.js` | 1.3.5 |
| 2.3.5 | Sección avanzado (reconstruir BD, exportar) | `frontend/js/settings.js` | — |
| 2.3.6 | Crear endpoint GET/PUT /api/settings | `backend/api/settings.py` | 1.1.1 |
| 2.3.7 | Crear endpoint POST /api/settings/rebuild-db | `backend/api/settings.py` | 1.1.1 |
| 2.3.8 | Crear endpoint POST /api/settings/export | `backend/api/settings.py` | 1.1.1 |
| 2.3.9 | Conectar UI con endpoints | `frontend/js/settings.js` | 2.3.6-8 |

**Entregable**: Configuración completamente funcional.

**Criterio de aceptación**:
- Todos los toggle guardan correctamente
- Selector de duración funciona con todas las unidades
- "Vaciar papelera" funciona con confirmación
- "Reconstruir BD" funciona
- "Exportar" descarga CSV/Excel

---

### Hito 2.4: Notificaciones
**Objetivo**: Sistema de notificaciones completo.

**Tareas**:
| # | Tarea | Archivos | Dependencias |
|---|-------|----------|--------------|
| 2.4.1 | Crear servicio de notificaciones base | `backend/notifications/__init__.py` | — |
| 2.4.2 | Implementar browser push (Web Push API) | `backend/notifications/push.py` | 2.4.1 |
| 2.4.3 | Implementar webhook (HTTP POST) | `backend/notifications/webhook.py` | 2.4.1 |
| 2.4.4 | Implementar email (SMTP) | `backend/notifications/email.py` | 2.4.1 |
| 2.4.5 | Crear endpoint POST /api/notifications/subscribe (push) | `backend/api/notifications.py` | 2.4.2 |
| 2.4.6 | Crear endpoint POST /api/notifications/test-webhook | `backend/api/notifications.py` | 2.4.3 |
| 2.4.7 | Crear endpoint POST /api/notifications/test-email | `backend/api/notifications.py` | 2.4.4 |
| 2.4.8 | Integrar notificaciones en el scanner (comparar con anterior) | `backend/scanner/detector.py` | 2.4.1, 1.2.3 |
| 2.4.9 | Agregar sección notificaciones en UI de settings | `frontend/js/settings.js` | 2.4.6-7 |
| 2.4.10 | Crear service worker para push notifications | `frontend/sw.js` | 2.4.2 |
| 2.4.11 | Probar flujo completo: escaneo → nuevos → notificación | Test manual | Todas anteriores |

**Entregable**: Las 3 notificaciones funcionan.

**Criterio de aceptación**:
- Browser push: al suscribirse, recibe notificación cuando hay duplicados nuevos
- Webhook: al configurar URL, recibe POST con JSON correcto
- Email: al configurar SMTP, recibe email con formato correcto
- Solo notifica duplicados NUEVOS (no los ya conocidos)
- Pruebas de webhook/email funcionan desde settings

---

### Fin de Fase 2 — App Completa

**En este punto la app tiene todas las funcionalidades**:
- Login + Auth
- Dashboard con stats
- Wizard de revisión
- Listas con filtros
- Acciones reales sobre archivos
- Papelera con auto-limpieza
- Configuración completa
- Notificaciones (push, webhook, email)

---

## Fase 3: Producción

### Hito 3.1: Docker
**Objetivo**: Imagen Docker lista para producción.

**Tareas**:
| # | Tarea | Archivos | Dependencias |
|---|-------|----------|--------------|
| 3.1.1 | Optimizar Dockerfile (multi-stage build) | `Dockerfile` | Todas Fase 2 |
| 3.1.2 | Configurar volumes para persistencia | `docker-compose.yml` | 3.1.1 |
| 3.1.3 | Configurar health checks | `Dockerfile`, `docker-compose.yml` | 3.1.1 |
| 3.1.4 | Configurar variables de entorno por defecto | `docker-compose.yml` | 0.1.4 |
| 3.1.5 | Probar `docker-compose up` limpio | Test manual | Todas anteriores |

**Entregable**: `docker-compose up -d` levanta la app completa.

**Criterio de aceptación**:
- Container arranca sin errores
- Persiste datos en volumes
- Health check responde
- Se conecta a Jellyfin correctamente

---

### Hito 3.2: Deploy
**Objetivo**: Despliegue en VM 100 + nginx.

**Tareas**:
| # | Tarea | Archivos | Dependencias |
|---|-------|----------|--------------|
| 3.2.1 | Copiar proyecto a VM 100 | — | 3.1 |
| 3.2.2 | Ejecutar docker-compose en VM 100 | — | 3.2.1 |
| 3.2.3 | Verificar conexión a Jellyfin | — | 3.2.2 |
| 3.2.4 | Verificar acceso al NFS (/mnt/stream) | — | 3.2.2 |
| 3.2.5 | Documentar config nginx-proxy-manager | `docs/nginx-config.md` | 3.2.2 |
| 3.2.6 | Probar desde navegador vía IP | Test manual | 3.2.2 |
| 3.2.7 | Crear README.md con instrucciones | `README.md` | 3.2.5 |
| 3.2.8 | Push a GitHub | — | Todas anteriores |

**Entregable**: App desplegada y accesible vía http://192.168.0.22:8097

**Criterio de aceptación**:
- Login funcional desde navegador
- Dashboard muestra datos reales
- Wizard funciona
- Acciones funcionan sobre archivos del NFS
- Accesible vía nginx (cuando se configure)

---

### Fin de Fase 3 — v1.0 Lista

**La app está lista para uso diario y para subir a Docker Hub**.

---

## Diagrama de Dependencias

```
Fase 0
  0.1.1 → 0.1.2 → 0.1.3 → 0.1.4 → 0.1.5 → 0.1.6 → 0.1.7

Fase 1
  0.1.5 ──→ 1.1.1 ──→ 1.1.3 ──→ 1.1.4 ──→ 1.1.6
  0.1.5 ──→ 1.1.2 ──→ 1.1.7
  1.1.1, 1.1.2 ──→ 1.1.5

  1.2.1 ──→ 1.2.3 ──→ 1.2.5
  1.2.2 ──→ 1.2.3
  0.1.5 ──→ 1.2.4
  1.2.3, 1.2.4 ──→ 1.2.7

  1.3.1 ──→ 1.3.2, 1.3.3, 1.3.6, 1.3.7, 1.3.8
  1.3.2 ──→ 1.3.4, 1.3.5

  1.3.5 ──→ 1.4.1
  1.3.3, 1.1.5 ──→ 1.4.2
  1.3.6, 1.2.5 ──→ 1.4.3

  1.3.5 ──→ 1.5.1 → 1.5.2 → 1.5.3 → 1.5.4, 1.5.5, 1.5.6
  1.3.3, 1.2.5 ──→ 1.5.7

  1.3.5 ──→ 1.6.1 → 1.6.2 → 1.6.3
  1.3.5 ──→ 1.6.4, 1.6.5

Fase 2
  1.1.1, 1.2.4 ──→ 2.1.1 → 2.1.2, 2.1.3
  2.1.1 ──→ 2.1.4, 2.1.5, 2.1.6, 2.1.7

  2.1.1 ──→ 2.2.1 → 2.2.2 → 2.2.4
  2.2.1 ──→ 2.2.3

  1.3.5 ──→ 2.3.1
  2.3.6 ──→ 2.3.9

  2.4.1 → 2.4.2, 2.4.3, 2.4.4
  2.4.2 ──→ 2.4.5, 2.4.10
  2.4.3 ──→ 2.4.6
  2.4.4 ──→ 2.4.7
  2.4.1, 1.2.3 ──→ 2.4.8

Fase 3
  Todas Fase 2 ──→ 3.1.1 → 3.1.2, 3.1.3, 3.1.4
  3.1 ──→ 3.2.1 → 3.2.2 → 3.2.3, 3.2.4, 3.2.6
```

---

## Estimación de Tiempo por Hito

| Hito | Descripción | Tareas | Estimación |
|------|-------------|--------|------------|
| 0.1 | Inicialización | 7 | ~30 min |
| 1.1 | Backend Base | 7 | ~2-3 horas |
| 1.2 | Scanner | 7 | ~3-4 horas |
| 1.3 | Frontend Base | 8 | ~2-3 horas |
| 1.4 | Dashboard | 5 | ~1-2 horas |
| 1.5 | Wizard | 9 | ~3-4 horas |
| 1.6 | Listas | 7 | ~2-3 horas |
| 2.1 | Acciones | 10 | ~3-4 horas |
| 2.2 | Papelera | 5 | ~1-2 horas |
| 2.3 | Configuración | 9 | ~2-3 horas |
| 2.4 | Notificaciones | 11 | ~3-4 horas |
| 3.1 | Docker | 5 | ~1 hora |
| 3.2 | Deploy | 8 | ~1-2 horas |
| **Total** | | **~100** | **~25-35 horas** |

---

## Orden de Desarrollo Recomendado

```
1.  0.1  Fundación
2.  1.1  Backend Base
3.  1.2  Scanner
4.  1.3  Frontend Base
5.  1.4  Dashboard
6.  1.5  Wizard
7.  1.6  Listas
        ↳ Entrega MVP al usuario para feedback
8.  2.1  Acciones
9.  2.2  Papelera
10. 2.3  Configuración
11. 2.4  Notificaciones
12. 3.1  Docker
13. 3.2  Deploy
        ↳ v1.0 lista para GitHub + Docker Hub
```

---

## Criterios de Aceptación por Fase

### Fase 1 (MVP)
- [ ] Login funcional contra Jellyfin real
- [ ] Dashboard muestra totales correctos
- [ ] Escaneo detecta duplicados correctamente
- [ ] Wizard muestra grupos con info completa
- [ ] Listas muestran datos con filtros
- [ ] Toast funcionan (progreso, éxito, error)

### Fase 2 (Gestión)
- [ ] Wizard ejecuta acciones reales (mover/eliminar archivos)
- [ ] Papelera funciona con auto-limpieza
- [ ] Configuración guarda y aplica cambios
- [ ] Notificaciones llegan (al menos 1 método)

### Fase 3 (Producción)
- [ ] Docker-compose levanta la app
- [ ] Accesible desde navegador en LAN
- [ ] Conecta a Jellyfin y NFS correctamente
- [ ] README con instrucciones claras
- [ ] Repo en GitHub
