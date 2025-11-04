# Auditoría del Frontend (HTML/CSS/JS + Alpine) y guía de migración a React + Vite

Este documento detalla la estructura y el contenido del frontend actual, identificando componentes y patrones reutilizables en HTML/JS/Alpine, y propone un mapa de migración a React + Vite con enfoque en reutilización de componentes.

## Módulos Frontend
- `intranet/intranet`: SPA para usuarios internos con múltiples páginas (board, logistics, tracking, support, etc.).
- `intranet/registro`: SPA pública para registro guiado de órdenes (wizard de pasos) y verificación por token.

---

## Estructura: `intranet/intranet`

- `index.html`
  - Carga librerías: `pinecone-router`, `alpinejs`, `nprogress`, `signature_pad`, `socket.io`, `chart.js`, `zxing-browser`.
  - Hoja de estilos global: `/static/css/new.css`.
  - Inicializa Alpine y el store vía `x-data="data"`.
  - Router (Pinecone) con templates precargados:
    - Rutas: `/` (login), `/home`, `/guest`, `/training`, `/board`, `/support`, `/tracking`, `/logistics`, `/driver`, `/clients`, `/machines`, `/marketing`, `notfound`.
  - Layout principal:
    - `<div id="sidebar">` visible si `$store.cache.user.id`.
    - Menú lateral con páginas según perfil: `$store.cache.getPages()`.
    - Menú de usuario (avatar, nombre, teléfono, departamento) y acción `logout`.
    - Área de contenido: `<div id="content" :class="{'sidebar': $store.cache.sidebar}"></div>`.
  - Componentes/Patrones:
    - Sidebar de navegación (reutilizable en todas las vistas internas).
    - Menú de usuario con desplegable (`$store.cache.sidebar_menu`).
    - Sistema de modales global manejado por `$store.cache.modals`.

- `static/js/main.js`
  - Alpine `data('data')`: componente raíz del layout.
  - `Alpine.store('cache')`: store global con:
    - `api`: base de API.
    - `user`, `active_page`, páginas `common_pages` y `restricted_pages`.
    - Gestión de sidebar y menú (`sidebarOn/Off`, `toogleSidebarMenu`).
    - Gestión de modales (`showModal`, `hideModal`, `hideAllModals`, `isVisibleModal`, `hasActiveModals`).
    - Helpers de datos: `setData/getData/isLoaded/getUrl`, `_normalizeEndpoints`, `_fetchEndpoints`, `fetchData`, `refresh`.
    - Navegación y título dinámico: `setActivePage`.
    - Sesión: `setUser`, `unsetData`, `logout` (limpia cache y navega `/`).
  - Hooks de router/eventos:
    - `loginVerify(context)`: verificación de auth y navegación.
    - Eventos `pinecone-start/pinecone-end` para NProgress.
  - Componente repetido: `data` (existe también en `intranet/registro`).

- `static/css/new.css`
  - Estilos globales y utilitarios (contenedores, `glass`, `hover-opacity`, layout, inputs, botones, menús, tarjetas, modales, etc.).

- `views/`
  - `base.html`
    - Componente Alpine: `x-data="data"`.
    - Patrón básico de inicialización; sin contenido funcional (plantilla base).

  - `login.html`
    - Componente: `login_data`.
    - Flujo OTP + creación de PIN con pasos controlados por `step`.
    - Entradas (`x-model`): `temp_auth.document`, `temp_auth.phone`, `temp_auth.otp`, `temp_auth.pin`, `temp_auth.confirm_pin` (6 campos aprox.).
    - Endpoints: `/user/send_otp`, `/user/validate_otp`, `/user/find`, `/user/login`, `/user/create_pin`.

  - `home.html`
    - Componente: `home_data`.
    - Vista inicial/dashboard (usa `Alpine.data('home_data')`).

  - `board.html`
    - Componente: `board_data`.
    - Kanban de actividades (issues): crear, ver, actualizar, borrar, cambiar estado.
    - Modales: `view`, `add` (2 modales principales).
    - Entradas: `x-model` en `title`, `description` (4 aprox.).
    - Endpoints: `/board/dashboard/{department_id}`, `/user/team/{user_id}`, `/board/issue`, `/board/issue/update`, `/board/issue/delete`, `/board/issue/status`, `/board/issue/id/{issue_id}`.

  - `logistics.html`
    - Componente: `logistics_data`.
    - Flujo de envíos: pendientes, procesar, terminar, ver imagen, historial, estadísticas, búsqueda.
    - Modales: `process`, `finish`, `image`, `history`, `statistics`, `search` (~6).
    - Entradas: orden, método, fechas, datos de cliente, dirección, distrito, asignado, conductor (~14 `x-model`).
    - Endpoints: múltiples `/logistic/*` y paneles `logistics_dashboard`, `logistics_pendings`.

  - `driver.html`
    - Componente: `logistics_data` (reutiliza lógica de logística para conductor).
    - Modales: `status_change`, `image` (2).
    - Endpoints: `/logistic/shipping_order_id/{id}`, `/logistic/set`, `/logistic/upload_proof`.

  - `tracking.html`
    - Componente: `tracking_data`.
    - Gestión de tracking con varios modales: `add`, `read`, `view`, `history`, `statistics`, `search` (~6).
    - Entradas `x-model`: `order_number`, `agency`, `document`, `name`, `phone`, `email`, `code1`, `code2`, `code3`, `find_order_number` (≈11).
    - Endpoints: `/client/order_number/{}`, `/client/data/{}`, `/tracking/*`, QR y sockets.

  - `support.html`
    - Componente: `support_data`.
    - Módulo más complejo: añade órdenes, fotos, historial, links, estadísticas, búsqueda, estado (≈9 modales).
    - Entradas `x-model`: pago, método, técnico, origen, y formulario completo de registro `process_service` (≈16 campos).
    - Endpoints: paneles `support_dashboard`, `support_ready`, y múltiples `/support/*`.

  - `clients.html`
    - Componente: `clients_data`.
    - Listado de clientes con carga inicial desde `/client/all`.

  - `machines.html`
    - Componente: `data`.
    - Gestión/visualización de máquinas (similar a `clients/marketing` en estructura de store y fetch).

  - `marketing.html`
    - Componente: `clients_data` (nombre reutilizado).
    - Ejemplo de llamadas: `/dev/confirm_flow/list`.

  - `training.html`
    - Componente: `training_data`.
    - Calendario de capacitaciones vía `/training/calendar`.

  - `guest.html`
    - Componente: `guest_data`.
    - Flujo guiado de servicio (steps): `select_type`, `start`, `confirm_name`, `phone`, `machine`, `problem`, `accessories`, `review`, `terms`, `signature`, `finish_success`.
    - Entradas: documento, teléfono, máquina, notas, accesorios, otros (≈6+).

- `static/images/` y `static/images/icons/`
  - Íconos y recursos visuales (numerosos SVG/PNG) para menú, estados, tracking, soporte, etc.

- `static/js/zxing-browser.min.js`
  - Librería para lectura de códigos (QR/barcode) usada en tracking/soporte.

- `firebase-messaging-sw.js`
  - Service Worker (notificaciones push) listo pero comentado en `index.html`.

---

## Estructura: `intranet/registro`

- `index.html`
  - Carga librerías: `html2canvas`, `jspdf`, `pinecone-router`, `alpinejs`, `nprogress`, `signature_pad`.
  - Estilos: `/static/css/new.css`.
  - Router:
    - `/:token` con `x-handler="tokenVerify"` para validar token y luego redirigir a `/`.
    - `/` carga `views/home.html`.
  - Layout simple: `<div id="content"></div>`.

- `static/js/main.js`
  - Componente Alpine raíz: `data`.
  - `Alpine.store('cache')`: solo define `api` (más sencillo que intranet).
  - `tokenVerify({ params })`: llama `/support/link_token`, guarda `token` en store y reemplaza URL.

- `views/home.html`
  - Componente: `default_data`.
  - Página base de bienvenida.

- `views/guest.html` (extenso, ~1100 líneas)
  - Componente: `guest_data`.
  - Wizard de registro de servicio con pasos: `start`, `confirm_name`, `phone`, `machine`, `problem`, `accessories`, `origin`, `protect`, `review`, `terms`, `signature`, `success`.
  - Entradas: documento, nombre, teléfono, máquina, notas, accesorios, otros (≈10+ campos a lo largo del flujo).
  - Integraciones: `signature_pad` (firma), generación de PDF/imagen (`html2canvas`, `jspdf`).

- `static/css/new.css`
  - Hoja de estilos compartida con intranet (reutilizable).

- `static/images/`
  - Íconos mínimos (`back.svg`, `home.svg`) y logos.

---

## Inventario de componentes y repeticiones

- Componente Alpine raíz `data`
  - Aparición: `intranet/intranet/static/js/main.js` y `intranet/registro/static/js/main.js` (2 veces).

- Store global `Alpine.store('cache')`
  - Aparición: en ambos módulos (2 veces), con distinta complejidad.
  - Responsabilidades: sesión de usuario, páginas visibles, modales, fetch/refresh de endpoints, socket, navegación.

- Sidebar de navegación
  - Aparición: `intranet/intranet/index.html` (se renderiza en todas las rutas internas).

- Menú de usuario (avatar + dropdown)
  - Aparición: `intranet/intranet/index.html`.

- Sistema de Modales global (`$store.cache.modals`)
  - Aparición por vista (estimado por `isVisibleModal`):
    - `support.html`: ~9 modales (`status`, `view`, `photos`, `image`, `add`, `history`, `search`, `links`, `statistics`).
    - `tracking.html`: ~6 modales (`add`, `read`, `view`, `history`, `statistics`, `search`).
    - `logistics.html`: ~6 modales (`process`, `finish`, `image`, `history`, `statistics`, `search`).
    - `board.html`: ~2 modales (`view`, `add`).
    - `driver.html`: ~2 modales (`status_change`, `image`).
    - `guest.html` (intranet): usa wizard por pasos, no modales del store.

- Formularios con `x-model` (cantidad aproximada de campos por vista)
  - `login.html`: ~6.
  - `tracking.html`: ~11.
  - `support.html`: ~16.
  - `logistics.html`: ~14.
  - `board.html`: ~4.
  - `guest.html` (intranet): ~6+ según paso.
  - `guest.html` (registro): ~10+ a lo largo del wizard.

- Integraciones externas repetidas
  - `socket.io`: soporte, tracking, logística y tablero (vía store y vistas).
  - `signature_pad`: soporte (firmas), registro (firma del cliente).
  - `chart.js`: estadísticas (soporte/tracking/logística).
  - `zxing-browser`: lectura de QR (tracking, soporte).
  - `html2canvas` + `jspdf`: módulo registro (capturas y PDF).

---

## Recomendaciones de migración a React + Vite

- Bootstrapping
  - Crear proyecto Vite React: `npm create vite@latest intranet-react -- --template react`.
  - Estructura propuesta:
    - `src/pages/`: `Login`, `Home`, `Board`, `Support`, `Tracking`, `Logistics`, `Driver`, `Clients`, `Machines`, `Marketing`, `Training`, `Guest`.
    - `src/components/`: `Sidebar`, `UserMenu`, `ModalManager`, `FormControls` (inputs, selects, textareas), `Card`, `List`, `Table`, `SignaturePad`, `QRReader`.
    - `src/stores/`: `cache.ts` (Zustand o Context + Reducer) replicando API del store Alpine.
    - `src/hooks/`: `useApi`, `useSocket`, `useModals`, `useAuth`.
    - `src/lib/`: `fetchClient`, `endpoints`, `router.tsx`.
    - `public/`: mover `manifest.json`, imágenes y `firebase-messaging-sw.js`.

- Router
  - Mapear rutas Pinecone a `react-router-dom` (`<Routes><Route path="..." element={<Page/>} /></Routes>`).
  - Soportar preload/lazy con `React.lazy` y `Suspense`.

- Store `cache`
  - Replicar campos y métodos:
    - `user`, `activePage`, `commonPages`, `restrictedPages`.
    - Modales: Set/List + helpers (`showModal`, `hideModal`, `hideAllModals`, `isVisibleModal`, `hasActiveModals`).
    - Fetch/refresh: normalizar endpoints, cache local por `key`.
    - Navegación y título dinámico.
  - Opciones: Zustand (simple y performante) o Context + Reducer.

- Componentización y reutilización
  - `Sidebar` + `UserMenu`: componentes compartidos en todas las páginas internas.
  - `ModalManager`: un contenedor global que muestra/oculta modales por `key` (props con render props o contexto).
  - `FormControls`: inputs/textarea/select con binding controlado (`value`/`onChange`) y máscaras (teléfono, documento).
  - `SignaturePad` y `QRReader`: componentes aislados con librerías existentes.
  - `Statistics`/`Charts`: wrapper de `chart.js` con props de datasets.

- Páginas
  - `BoardPage`: estados locales por issue, modales `view/add`.
  - `LogisticsPage`: wizard de proceso/envío, modales múltiples y revisiones.
  - `DriverPage`: vista simplificada para conductor.
  - `TrackingPage`: formularios de búsqueda y modales para lectura/visualización/historial/estadísticas.
  - `SupportPage`: la más grande, separar en subcomponentes (panel, add form, viewer, history, links, stats, search).
  - `GuestPage` (intranet y registro): implementar wizards con estado por paso y validaciones.

- Estilos
  - Reutilizar `new.css` inicial, y progresivamente migrar a CSS Modules/Tailwind si se desea.

- Integraciones
  - `socket.io-client`: inicialización en store y hooks.
  - `signature_pad`, `chart.js`, `zxing-browser`, `html2canvas`, `jspdf`: instalar vía npm y crear wrappers React.

- Consideraciones
  - Mantener semántica de `Alpine.store('cache')` para reducir fricción.
  - Migrar `x-model` a `useState`/controlled components y encapsular máscaras/validaciones.
  - Sustituir `x-show` por condiciones render (`{cond && <Comp/>}`) y transiciones con CSS o `framer-motion` si se requiere.
  - Centralizar llamadas a API y manejo de `NProgress` en `useApi`.

---

## Tabla rápida de mapeo (archivo → componente React sugerido)

- `index.html` → `App.tsx` + `Sidebar`, `UserMenu`, `Content`.
- `static/js/main.js` → `src/stores/cache.ts` + `src/hooks/*` + `router.tsx`.
- `views/login.html` → `pages/Login.tsx`.
- `views/home.html` → `pages/Home.tsx`.
- `views/board.html` → `pages/Board.tsx` + `IssueModal`, `AddIssueModal`.
- `views/logistics.html` → `pages/Logistics.tsx` + `ProcessModal`, `FinishModal`, `ImageModal`, `HistoryModal`, `StatisticsModal`, `SearchModal`.
- `views/driver.html` → `pages/Driver.tsx` + `StatusChangeModal`, `ImageModal`.
- `views/tracking.html` → `pages/Tracking.tsx` + `AddModal`, `ReadModal`, `ViewModal`, `HistoryModal`, `StatisticsModal`, `SearchModal`.
- `views/support.html` → `pages/Support.tsx` + `StatusModal`, `ViewModal`, `PhotosModal`, `ImageModal`, `AddModal`, `HistoryModal`, `SearchModal`, `LinksModal`, `StatisticsModal`.
- `views/clients.html` → `pages/Clients.tsx`.
- `views/machines.html` → `pages/Machines.tsx`.
- `views/marketing.html` → `pages/Marketing.tsx`.
- `views/training.html` → `pages/Training.tsx`.
- `views/guest.html` (intranet) → `pages/Guest.tsx` (wizard por pasos).
- `registro/views/home.html` → `pages/RegistroHome.tsx`.
- `registro/views/guest.html` → `pages/RegistroGuest.tsx` (wizard por pasos + firma + PDF).
- `firebase-messaging-sw.js` → `public/firebase-messaging-sw.js`.
- `static/css/new.css` → `public/new.css` o `src/styles/new.css` según preferencia.

---

## Notas finales
- El frontend está fuertemente basado en Alpine.js con un store global `cache` que centraliza datos, sesión, endpoints, sockets y modales.
- La migración debe preservar el store y los nombres/llaves de modales para minimizar cambios en lógica.
- Las vistas más grandes y con mayor número de entradas/modales son `support.html`, `tracking.html` y `logistics.html`; priorizar su componentización en React.
- `registro` es autónomo y más simple; puede migrarse primero para validar la arquitectura React + Vite.

---

## Componentes por archivo (inventario específico)

Esta sección lista, por archivo HTML, los componentes UI y patrones usados, con conteos aproximados: `modal` (basado en `$store.cache.isVisibleModal('...')`), `button`, `input`, `select`, `textarea`, `form`, `x-model` (bindings), y el nombre del componente Alpine (`x-data`). Los conteos se basan en coincidencias del código actual.

### intranet/intranet/index.html
- Alpine root: `x-data="data"`.
- Componentes: `Sidebar` (navegación), `UserMenu` (dropdown), `ModalManager` global (clases y helper `$store.cache.modals`).
- Buttons: acciones de menú (logout) y navegación por `<a>`; botones explícitos mínimos.
- Forms: no.
- Modales: no directos; las vistas cargadas gestionan modales.

### intranet/intranet/views/login.html
- x-data: `login_data`.
- forms: 6 (`find`, `sendOTP`, `validateOTP`, `step=3`, `register`, `login`).
- buttons: 6 visibles en formularios (find, add_phone, validate_otp, continuar, register, login).
- inputs: 6 (document, phone, otp, pin, confirm_pin, pin).
- textareas: 0.
- selects: 0.
- x-model: 6 (document, phone, otp, pin, confirm_pin, pin).
- modales: 0 (`isVisibleModal` no presente).

### intranet/intranet/views/home.html
- x-data: `home_data`.
- forms: 0.
- buttons: 0.
- inputs: 0.
- selects: 0.
- textareas: 0.
- x-model: 0.
- modales: 0.

### intranet/intranet/views/guest.html
- x-data: `guest_data`.
- forms: 0 (usa layout por pasos, no `<form>`).
- buttons: ~14 (navegación de pasos, validar, limpiar, crear nueva orden).
- inputs: 6 (document, phone, machine, checkbox accesorios, otros accesorios, file optional vía label; algunos inputs múltiples por paso).
- selects: 0.
- textareas: 2 (status_notes, problem notes).
- x-model: 7 (status_notes, service_order.document, service_order.phone, service_order.machine, service_order.notes, accessories, other_accessories).
- modales: 0 (usa contenedores `.content` por paso; sin `isVisibleModal`).

### intranet/intranet/views/board.html
- x-data: `board_data`.
- forms: 0.
- buttons: 3 (delete, update, add).
- inputs: 0.
- selects: 0.
- textareas: 4 (view_issue.title, view_issue.description, add_issue.title, add_issue.description).
- x-model: 4 (coinciden con las textareas anteriores).
- modales: 2 (`view`, `add`).

### intranet/intranet/views/logistics.html
- x-data: `logistics_data`.
- forms: 1 principal (`processShipping` dentro de modal `process` manejado por eventos; structurado por inputs/selects).
- buttons: 3 (delete, process/update, process/update condicionales).
- inputs: 11 (order_number, date register_date_format, client_document, client_id hidden, client_name, client_phone, address, reference, maps, find_order_number y otro input adicional de filtro).
- selects: 4 (method_id, district_id, assigned_id, driver_id).
- textareas: 0.
- x-model: ~13 (todos los anteriores + find_order_number).
- modales: 6 (`process`, `finish`, `image`, `history`, `statistics`, `search`).

### intranet/intranet/views/driver.html
- x-data: `logistics_data`.
- forms: 0.
- buttons: 2 (reject, complete).
- inputs: 1 (file input para subir foto de prueba).
- selects: 0.
- textareas: 0.
- x-model: 0 explícito en fragmentos vistos.
- modales: 2 (`status_change`, `image`).

### intranet/intranet/views/tracking.html
- x-data: `tracking_data`.
- forms: 1 (`registerTrackings` con múltiples campos y submit).
- buttons: 1 (submit add).
- inputs: 9 (order_number, document, name, phone, email, code1, code2 como input además de select, code3, find_order_number).
- selects: 2 (agency, code2 select).
- textareas: 0.
- x-model: ~11 (campos anteriores incluyendo select bindings).
- modales: 6 (`add`, `read`, `view`, `history`, `statistics`, `search`).

### intranet/intranet/views/support.html
- x-data: `support_data`.
- forms: múltiples secciones dentro de modales (no `<form>` genérico, pero estructura de edición y creación en `add/status`).
- buttons: 4+ (updateStatus, toggle show_document, newOrder, newLink y acciones varias dentro de modales).
- inputs: ~10 (checkbox sendWhatsapp, date register_date, client_document, client_name, client_phone, client_email, machine, más inputs en filtros `find_order_number` y otros campos de pago `service_order.*`).
- selects: 5 (service_order.method_id, technician_id, origin_id; process_service.method_id, origin_id).
- textareas: 3 (status_notes en dos secciones y process_service.status_notes).
- x-model: ~16 (service_order.pay_amount y todos los anteriores; incluye `find_order_number`).
- modales: 9 (`status`, `view`, `photos`, `image`, `add`, `history`, `search`, `links`, `statistics`).

### intranet/intranet/views/clients.html
- x-data: `clients_data`.
- forms: 0.
- buttons: 0.
- inputs: 0.
- selects: 0.
- textareas: 0.
- x-model: 0.
- modales: 0.

### intranet/intranet/views/machines.html
- x-data: `data`.
- forms: 0.
- buttons: 0.
- inputs: 0.
- selects: 0.
- textareas: 0.
- x-model: 0.
- modales: 0.

### intranet/intranet/views/marketing.html
- x-data: `clients_data`.
- forms: 0.
- buttons: 0.
- inputs: 0.
- selects: 0.
- textareas: 0.
- x-model: 0 (fragmento principal muestra fetchs y no inputs).
- modales: 0.

### intranet/intranet/views/training.html
- x-data: `training_data`.
- forms: 0.
- buttons: 0.
- inputs: 0.
- selects: 0.
- textareas: 0.
- x-model: 0.
- modales: 0.

### intranet/registro/index.html
- Alpine root: `x-data="data"`.
- forms: 0.
- buttons: navegación por router; sin botones explícitos fuera de vistas.
- inputs: 0.
- selects: 0.
- textareas: 0.
- x-model: 0.
- modales: 0.

### intranet/registro/views/home.html
- x-data: `default_data`.
- forms: 0.
- buttons: 0.
- inputs: 0.
- selects: 0.
- textareas: 0.
- x-model: 0.
- modales: 0.

### intranet/registro/views/guest.html
- x-data: `guest_data`.
- forms: 0 (wizard por pasos con botones).
- buttons: ~14 (validaciones de paso y navegación: document, name, phone, machine, accessories, origin, protect, continuar, limpiar, nueva orden, descargar PDF, etc.).
- inputs: 6 (document, name, phone, machine, checkbox accesorios, otros accesorios).
- selects: 0.
- textareas: 1 (notes).
- x-model: 7 (service_order.document, service_order.name, service_order.phone, service_order.machine, service_order.notes, accessories, other_accessories).
- modales: 0 (no usa `isVisibleModal`).

---

## Observaciones prácticas para migración de componentes
- `ModalManager`: centralizar en React un gestor de modales con llaves equivalentes y portar vistas que actualmente usan `isVisibleModal('key')`.
- `FormControls`: crear `Input`, `Select`, `Textarea`, `Checkbox` controlados y reutilizarlos en `support`, `logistics`, `tracking`, `login` y ambos `guest`.
- `Wizard`: encapsular flujo por pasos de `guest` (intranet y registro) en un componente `Wizard` con navegación, validaciones y mascarillas.
- `Sidebar`/`UserMenu`: extraer como componentes globales y compartir entre páginas internas.
- `Charts`, `SignaturePad`, `QRReader`: crear wrappers React y usarlos donde aparecen repetidos.