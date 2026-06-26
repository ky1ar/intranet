(function () {
    const ID = "pine-toast";
    let hideTimer = null;

    function ensureToast() {
        let el = document.getElementById(ID);
        if (el) return el;

        el = document.createElement("div");
        el.id = ID;
        el.className = "pine-toast frost";
        el.innerHTML = `
            <div class="spinner"></div>
            <div class="title">Cargando…</div>
            </div>
        `;
        document.body.appendChild(el);
        return el;
    }

    function setSpinner(el, visible) {
        const sp = el.querySelector(".spinner");
        if (sp) sp.style.display = visible ? "" : "none";
    }

    window.PineToast = {
        start(title = "Cargando…") {
            clearTimeout(hideTimer);
            const el = ensureToast();
            el.classList.remove("pine-flash-error", "pine-flash-success");
            setSpinner(el, true);
            el.querySelector(".title").textContent = title;
            el.classList.add("show");
        },
        done() {
            const el = document.getElementById(ID);
            if (!el) return;
            hideTimer = setTimeout(() => el.classList.remove("show"), 150);
        },
        // Mensaje transitorio (sin spinner). type: "error" | "success" | "info"
        flash(title = "", type = "info", ms = 3800) {
            clearTimeout(hideTimer);
            const el = ensureToast();
            el.classList.remove("pine-flash-error", "pine-flash-success");
            if (type === "error")   el.classList.add("pine-flash-error");
            if (type === "success") el.classList.add("pine-flash-success");
            setSpinner(el, false);
            el.querySelector(".title").textContent = title;
            el.classList.add("show");
            hideTimer = setTimeout(() => {
                el.classList.remove("show");
                // Resetea color/spinner SOLO después del fundido (transición .18s),
                // para que no parpadee blanco+spinner antes de desaparecer.
                setTimeout(() => {
                    if (el.classList.contains("show")) return; // un nuevo toast tomó el control
                    el.classList.remove("pine-flash-error", "pine-flash-success");
                    setSpinner(el, true);
                }, 220);
            }, ms);
        }
    };
})();


(function () {
  const _fetch = window.fetch;
  let active = 0;

  window.fetch = async function (input, init = {}) {
    const headers = new Headers(init.headers || {});
    const noToast = headers.get("X-No-Toast") === "1";

    if (!noToast) {
      active++;
      if (active === 1) PineToast.start("Cargando…");
    }

    try {
      return await _fetch.call(this, input, { ...init, headers });
    } finally {
      if (!noToast) {
        active = Math.max(0, active - 1);
        if (active === 0) PineToast.done();
      }
    }
  };
})();

window.addEventListener('beforeunload', () => {
    const socket = Alpine.store('cache')?.socket;
    if (socket && typeof socket.disconnect === 'function') {
        console.log("Cerrando socket antes de recargar");
        socket.disconnect();
    }
});

document.addEventListener('alpine:init', () => {
    Alpine.data('data',() => ({
        async init() {
            Alpine.store('cache').detectPlatform();
            Alpine.store('cache').watchViewport();
            Alpine.store('cache').openActivePageGroup();
            console.log('Inicializando Alpine...');

            // Alpine.store('cache').initSocket();
            // Alpine.store('cache').sidebarOn();
            // Alpine.store('cache').initPush();

            // Alpine.store('cache').verify();

            // const token = Alpine.store('cache').user.token;
            // // const storedData = localStorage.getItem('user_data');
            // if (!token) {
            //     console.log('Ventana reiniciada...');
            //     // if (storedData) {
            //     //     console.log('Obteniendo data desde el cache...');
            //     //     const userData = JSON.parse(storedData);
            //     //     Alpine.store('cache').setUser(userData);

            //     //     Alpine.store('cache').initSocket();
            //     //     Alpine.store('cache').sidebarOn();
            //     // } else {
            //         console.log('No estás logueado...');
            //         if (window.location.pathname !== '/') {
            //             window.location.href = '/';
            //         }
            //         return false;
            //     // }
            // } else {
            //     console.log('Cambiando de ruta...');
            // }
            
        },
    }));

    Alpine.store('cache', {
        api: 'https://api.krear3d.com', //https://devapi.krear3d.com
        user: {},
        active_page: window.location.pathname,
         module_ui: {
            attendance:    { image: 'attendance.svg', label: 'Asistencia',     title: 'Krear 3D - Asistencia',      category: 'General' },
            schedule:      { image: 'calendar.svg',   label: 'Agenda',         title: 'Krear 3D - Agenda',          category: 'General' },
            board:         { image: 'board.svg',      label: 'Actividades',    title: 'Krear 3D - Actividades',     category: 'General' },
            logistics:     { image: 'logistics.svg',  label: 'Envíos',         title: 'Krear 3D - Envíos',          category: 'Logística' },
            warehouse:     { image: 'warehouse.svg',  label: 'Almacén',        title: 'Krear 3D - Almacén',         category: 'Logística' },
            tracking:      { image: 'tracking.svg',   label: 'Tracking',       title: 'Krear 3D - Trackings',       category: 'Logística' },
            driver:        { image: 'driver.svg',     label: 'Conductor',      title: 'Krear 3D - Conductor',       category: 'Logística' },
            imports:       { image: 'imports.svg',    label: 'Importaciones',  title: 'Krear 3D - Importaciones',   category: 'Compras' },
            purchases:     { image: 'purchases.svg',  label: 'Compras',        title: 'Krear 3D - Compras',         category: 'Compras' },
            marketing:     { image: 'marketing.svg',  label: 'Marketing',      title: 'Krear 3D - Marketing',       category: 'Comercial' },
            conversations: { image: 'marketing.svg',  label: 'Conversaciones', title: 'Krear 3D - Conversaciones',  category: 'Comercial' },
            guest:         { image: 'fabrix.svg',     label: 'Fabrix',         title: 'Krear 3D - Fabrix',          category: 'Soporte' },
            safebuy:       { image: 'safebuy.svg',    label: 'Compra Segura',  title: 'Krear 3D - Compra Segura',   category: 'Comercial' },
            support:       { image: 'support.svg',    label: 'Taller',         title: 'Krear 3D - Soporte',         category: 'Soporte' },
            complaint:     { image: 'complaint.svg',  label: 'Reclamos',       title: 'Krear 3D - Reclamos',        category: 'Administración' },
            refunds:       { image: 'refund.svg',     label: 'Extornos',       title: 'Krear 3D - Extornos',        category: 'Administración' },
            approvals:     { image: 'approval.svg',   label: 'Aprobaciones',   title: 'Krear 3D - Aprobaciones',    category: 'Comercial' },
            orders:        { image: 'order.svg',        label: 'Pedidos',        title: 'Krear 3D - Pedidos',         category: 'Comercial' },
            admin:         { image: 'admin.svg',      label: 'Admin',          title: 'Krear 3D - Admin',           category: 'General' },
        },

        // Descripción de cada módulo para los tiles del home (por ahora aquí; luego se migra a BD).
        // Key = slug. Deja '' para no mostrar descripción.
        module_desc: {
            attendance:    'Controla asistencia, permisos y vacaciones.',
            schedule:      'Organiza y consulta eventos y reuniones.',
            board:         'Gestiona tareas y actividades programadas.',
            logistics:     'Gestiona envíos y despachos.',
            warehouse:     'Control de invantario, almacen y picking.',
            tracking:      'Rastrea envíos a nivel nacional.',
            driver:        'Gestión de conductores y vehículos.',
            imports:       'Control de importaciones y proveedores.',
            purchases:     'Gestiona solicitudes de compras internas.',
            marketing:     '',
            conversations: 'Mensajería de Fabrix y comunicaciones.',
            guest:         'Ingreso y salida de equipos mediante Fabrix.',
            safebuy:       'Gestión de compras aseguradas de Tienda.',
            support:       'Órdenes y servicios de soporte técnico.',
            complaint:     'Administra reclamos y seguimiento.',
            refunds:       'Administra solicitudes de extornos.',
            approvals:     'Revisa y aprueba solicitudes de Tienda.',
            orders:        'Gestiona pedidos realizados en Wordpress.',
            admin:         'Permisos, módulos y configuración de usuarios.',
        },

        categories: {
            'Logística':        { label: 'Logística',       icon: 'org_box.svg' },
            'Comercial':        { label: 'Comercial',       icon: 'org_trend.svg' },
            'Compras':          { label: 'Compras',         icon: 'org_cart.svg' },
            'Soporte':          { label: 'Soporte',         icon: 'org_wrench.svg' },
            'General':          { label: 'General',         icon: 'org_menu.svg' },
            'Administración':   { label: 'Administración',  icon: 'org_folder.svg' },
        },

        collapsed_categories: JSON.parse(localStorage.getItem('collapsed_categories') || '[]'),

        modals: new Set(),
        sidebar: false,
        sidebar_menu: false,
        more_menu: false,
        device_id: null,
        fcm_token: null,
        notifications_enabled: !!localStorage.getItem('push_token'),
        push_intro_seen: localStorage.getItem('push_intro_seen') === '1',
        platform: 'desktop',
        cached_keys: new Set(),
        pdf_url: null,
        pdf_title: 'Reglamento',
        sidebar_expanded: false,
        menu_grouped: window.innerWidth >= 768,
        dark_mode: localStorage.getItem('dark_mode') === '1',
        is_narrow: window.innerWidth < 768,
        _settings_modules: [],
        _settings_saving: false,
        _drag_idx: null,
        _drag_over_idx: null,
        _grouped_nodes: [],
        _g_drag: null,

        openModuleSettings() {
            const modules = this.user.modules;
            if (!modules) return;

            // clonar para editar sin afectar el store hasta guardar
            this._settings_modules = modules
                .sort((a, b) => a.sort_order - b.sort_order)
                .map((m, i) => ({
                    slug: m.slug,
                    name: m.name,
                    is_pinned: m.is_pinned,
                    is_default: m.is_default,
                    sort_order: i,
                }));

            this._buildGroupedNodes();
            this.showModal('module-settings');
        },

        setMenuGrouped(val) {
            this.menu_grouped = val;
            localStorage.setItem('menu_grouped', val ? '1' : '0');
        },
        setDarkMode(val) {
            this.dark_mode = val;
            localStorage.setItem('dark_mode', val ? '1' : '0');
            document.documentElement.classList.toggle('dark', val);
        },

        _setSettingsDefault(slug) {
            this._settings_modules.forEach(m => m.is_default = (m.slug === slug));
        },

        _dragStart(idx) {
            this._drag_idx = idx;
        },

        _dragOver(idx) {
            if (this._drag_idx === null || this._drag_idx === idx) return;
            const items = this._settings_modules;
            const dragged = items.splice(this._drag_idx, 1)[0];
            items.splice(idx, 0, dragged);
            this._drag_idx = idx;
        },

        _dragEnd() {
            this._drag_idx = null;
        },

        async saveModuleSettings() {
            this._settings_saving = true;
            const token = localStorage.getItem('user_token');

            try {
                const modules = this._settings_modules.map((m, i) => {
                    const um = this.user.modules.find(u => u.slug === m.slug);
                    return {
                        module_id: um?.module_id || 0,
                        sort_order: i,
                        is_pinned: m.is_pinned,
                        is_default: m.is_default,
                    };
                }).filter(m => m.module_id);

                await fetch(`${this.api}/modules/me/settings`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`,
                        'X-No-Toast': '1',
                    },
                    body: JSON.stringify({ modules }),
                });

                // Actualizar store local
                this._settings_modules.forEach((sm, i) => {
                    const original = this.user.modules.find(m => m.slug === sm.slug);
                    if (original) {
                        original.is_pinned = sm.is_pinned;
                        original.is_default = sm.is_default;
                        original.sort_order = i;
                    }
                });

                const defaultMod = this._settings_modules.find(m => m.is_default);
                this.user.default_page = defaultMod?.slug || this.user.default_page;
                this.hideModal('module-settings');
            } catch (e) {
                console.error('Error guardando settings:', e);
            } finally {
                this._settings_saving = false;
            }
        },

        // ---- Modo agrupado: estructura editable (grupos + páginas directas) ----
        _buildGroupedNodes() {
            const modules = this.user.modules || [];
            const catKeys = Object.keys(this.categories);

            const byCat = new Map();
            const direct = [];
            for (const m of modules) {
                const ui = this.module_ui[m.slug] || {};
                const cat = (ui.category && this.categories[ui.category]) ? ui.category : null;
                const page = { slug: m.slug, label: ui.label || m.name, image: ui.image || m.slug, sort: m.sort_order };
                if (!cat) { direct.push(page); continue; }
                if (!byCat.has(cat)) byCat.set(cat, []);
                byCat.get(cat).push(page);
            }
            for (const arr of byCat.values()) arr.sort((a, b) => a.sort - b.sort);

            const nodes = [];
            for (const p of direct) {
                nodes.push({ type: 'page', key: 'p:' + p.slug, slug: p.slug, label: p.label, image: p.image, sort: p.sort, catIndex: -1 });
            }
            for (const [cat, members] of byCat.entries()) {
                const def = this.categories[cat];
                nodes.push({
                    type: 'group',
                    key: 'g:' + cat,
                    category: cat,
                    label: def.label || cat,
                    image: def.icon,
                    sort: Math.min(...members.map(m => m.sort)),
                    catIndex: catKeys.indexOf(cat),
                    items: members.map(m => ({ slug: m.slug, label: m.label, image: m.image })),
                });
            }

            // Mismo orden que el sidebar: nav_order si existe; luego sort + def. de categorías
            const navOrder = Array.isArray(this.user.nav_order) ? this.user.nav_order : [];
            const navPos = (k) => { const i = navOrder.indexOf(k); return i < 0 ? Infinity : i; };
            nodes.sort((a, b) => {
                const pa = navPos(a.key), pb = navPos(b.key);
                if (pa !== pb) return pa - pb;
                if (a.sort !== b.sort) return a.sort - b.sort;
                return a.catIndex - b.catIndex;
            });

            this._grouped_nodes = nodes;
        },

        _gDragStart(level, gi, ii) {
            this._g_drag = { level, gi, ii };
        },
        _gDragOverTop(gi) {
            const d = this._g_drag;
            if (!d || d.level !== 'top' || d.gi === gi) return;
            const arr = this._grouped_nodes;
            arr.splice(gi, 0, arr.splice(d.gi, 1)[0]);
            d.gi = gi;
        },
        _gDragOverItem(gi, ii) {
            const d = this._g_drag;
            if (!d || d.level !== 'item' || d.gi !== gi || d.ii === ii) return;
            const items = this._grouped_nodes[gi].items;
            items.splice(ii, 0, items.splice(d.ii, 1)[0]);
            d.ii = ii;
        },
        _gDragEnd() {
            this._g_drag = null;
        },

        // Dispatcher de guardado según el modo activo
        saveSettings() {
            if (this.menu_grouped && !this.is_narrow) return this.saveGroupedOrder();
            return this.saveModuleSettings();
        },

        async saveGroupedOrder() {
            this._settings_saving = true;
            const token = localStorage.getItem('user_token');
            try {
                const nav_order = this._grouped_nodes.map(n => n.key);

                // sort_order secuencial sobre el aplanado (items de grupos + páginas directas)
                const flat = [];
                for (const n of this._grouped_nodes) {
                    if (n.type === 'group') n.items.forEach(it => flat.push(it.slug));
                    else flat.push(n.slug);
                }
                const sortMap = {};
                flat.forEach((slug, i) => { sortMap[slug] = i; });

                const modules = this.user.modules.map(m => ({
                    module_id: m.module_id,
                    sort_order: sortMap[m.slug] !== undefined ? sortMap[m.slug] : m.sort_order,
                    is_pinned: m.is_pinned,
                    is_default: m.is_default,
                })).filter(m => m.module_id);

                await fetch(`${this.api}/modules/me/settings`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`,
                        'X-No-Toast': '1',
                    },
                    body: JSON.stringify({ modules, nav_order }),
                });

                // Actualizar store local
                this.user.nav_order = nav_order;
                this.user.modules.forEach(m => {
                    if (sortMap[m.slug] !== undefined) m.sort_order = sortMap[m.slug];
                });

                PineToast.flash('Orden guardado', 'success');
                this.hideModal('module-settings');
            } catch (e) {
                console.error('Error guardando orden:', e);
                PineToast.flash('No se pudo guardar el orden', 'error');
            } finally {
                this._settings_saving = false;
            }
        },
        
        async openPdfModal(url, title = 'Reglamento') {
            this.detectPlatform();

            if (this.platform === 'desktop') {
                this.pdf_url = url;
                this.pdf_title = title;
                this.showModal('pdf-viewer');
                return;
            }

            await this.downloadPdf(url, title);
        },

        async downloadPdf(url, filename = 'reglamento.pdf') {
            const res = await fetch(url, { cache: 'no-store' });
            if (!res.ok) throw new Error('No se pudo descargar');

            const blob = await res.blob();
            const blobUrl = URL.createObjectURL(blob);

            const a = document.createElement('a');
            a.href = blobUrl;
            a.download = filename;
            a.style.display = 'none';
            document.body.appendChild(a);
            a.click();
            a.remove();

            setTimeout(() => URL.revokeObjectURL(blobUrl), 5000);
        },

        closePdfModal() {
            this.hideModal('pdf-viewer');
            this.pdf_url = null;
        },

        detectPlatform() {
            const ua = navigator.userAgent || navigator.vendor || window.opera;

            if (/android/i.test(ua)) {
                this.platform = 'android';
                return;
            }

            if (/iPad|iPhone|iPod/.test(ua) || 
                (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1)) {
                this.platform = 'ios';
                return;
            }

            this.platform = 'desktop';
        },

        watchViewport() {
            const update = () => {
                this.is_narrow = window.innerWidth < 768;
                this.menu_grouped = !this.is_narrow;
            };
            update();
            window.addEventListener('resize', update);
        },

        pushHelpMessage() {
            const base = 'Activa las notificaciones y te avisaré de tus novedades en tiempo real.<br><br>';

            if (this.platform === 'android') {
                return base + 'En <strong>Android</strong>, te recomiendo instalar la app web (añadir esta página a la pantalla de inicio) y luego activar las notificaciones.';
            }

            if (this.platform === 'ios') {
                return base + 'En <strong>iOS</strong>, primero debes guardar esta página en la pantalla de inicio (instalar la app web) y después activar las notificaciones desde allí.';
            }

            return base + 'En <strong>tu computadora</strong>, puedes activarlas directamente desde el navegador.';
        },
        
        getOrCreateDeviceId() {
            let id = localStorage.getItem('device_id');
            if (!id) {
                id = crypto.randomUUID ? crypto.randomUUID() : `dev-${Date.now()}-${Math.random()}`;
                localStorage.setItem('device_id', id);
            }
            this.device_id = id;
            return id;
        },

        async requestPushPermission() {
            if (!('Notification' in window)) {
                alert('Este navegador no soporta notificaciones push');
                return;
            }

            // Si ya está concedido, solo intentamos registrar
            if (Notification.permission === 'granted') {
                await this.initPush();
                return;
            }

            if (Notification.permission === 'denied') {
                alert('Las notificaciones están bloqueadas. Actívalas en los ajustes del navegador.');
                return;
            }

            const result = await Notification.requestPermission();

            // Marcar que ya mostramos el flujo una vez
            localStorage.setItem('push_intro_seen', '1');
            this.push_intro_seen = true;

            if (result === 'granted') {
                await this.initPush();
            } else if (result === 'denied') {
                alert('Las notificaciones están bloqueadas. Actívalas en los ajustes del navegador.');
            }
        },

        maybeShowPushModal() {
            if (!('Notification' in window)) return;
            if (!this.user?.id) return;

            const hasToken = !!localStorage.getItem('push_token');

            // Si el navegador ya tiene permiso pero aún no tenemos token,
            // intentamos registrar en segundo plano (caso compañero roto).
            if (Notification.permission === 'granted' && !hasToken) {
                this.initPush();
                return;
            }

            // Si ya tenemos token, no molestamos más
            if (hasToken) return;

            // Solo mostramos modal si es la primera vez y el permiso sigue "default"
            if (!this.push_intro_seen && Notification.permission === 'default') {
                this.showModal('push-info');
            }
        },


        async initPush() {
            console.log("Init Push...");

            try {
                if (!('serviceWorker' in navigator) || !('Notification' in window)) {
                    console.warn('Push no soportado');
                    return;
                }

                if (Notification.permission !== 'granted') {
                    console.warn('Push: permiso aún no concedido');
                    return;
                }

                this.detectPlatform();
                this.getOrCreateDeviceId();

                await navigator.serviceWorker.register('/firebase-messaging-sw.js');

                const swRegistration = await navigator.serviceWorker.ready;

                const token = await window.messaging.getToken({
                    vapidKey: 'BPsd2S7djGQTrd2IUttk19xkLI4t7fNyeYXZLQKmnhVlkqCWWboHNbnSMx0B-cFc_QDrUqizmVlVC5TnSrLO3Q0',
                    serviceWorkerRegistration: swRegistration,
                });

                if (!token) {
                    console.warn('No se pudo obtener FCM token');
                    alert('No se pudo activar las notificaciones (sin token). Intenta de nuevo más tarde.');
                    return;
                }

                this.fcm_token = token;
                console.log('FCM token:', token);

                const savedToken  = localStorage.getItem('push_token');
                const savedDevice = localStorage.getItem('push_device_id');

                if (savedToken === token && savedDevice === this.device_id) {
                    console.log('Push ya registrado para este dispositivo');
                    this.notifications_enabled = true;
                    return;
                }

                if (this.user?.id && this.user?.token) {
                    const res = await fetch(this.api + '/user/register_device', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${this.user.token}`,
                        },
                        body: JSON.stringify({
                            device_id: this.device_id,
                            fcm_token: this.fcm_token,
                            device_platform: this.platform,
                            user_agent: navigator.userAgent || null,
                        }),
                    });

                    if (res.ok) {
                        localStorage.setItem('push_token', token);
                        localStorage.setItem('push_device_id', this.device_id);
                        this.notifications_enabled = true;
                    } else {
                        console.warn('Error registrando dispositivo en backend');
                        alert('No se pudo registrar el dispositivo para notificaciones. Intenta de nuevo.');
                    }
                }

            } catch (err) {
                console.error('Error inicializando push:', err, err.code, err.message);
                alert('Ocurrió un error al activar las notificaciones. Intenta de nuevo.');
            }
        },


                        
        sidebarOn() {
            this.sidebar = true;
        },

        sidebarOff() {
            this.sidebar = false;
            this.sidebar_menu = false;
        },
        
        toogleSidebarMenu() { 
            this.sidebar_menu = !this.sidebar_menu;
        },

        toogleMoreMenu() { 
            this.more_menu = !this.more_menu;
        },

        hideMoreMenu() { 
            this.more_menu = false;
        },

        hideSidebarMenu() { 
            this.sidebar_menu = false;
        },

        showModal(modal) {
            this.modals.add(modal);
        },
    
        hideModal(modal) {
            this.modals.delete(modal);
        },
    
        hideAllModals() {
            this.modals.clear();
        },

        isVisibleModal(modal) {
            return this.modals.has(modal);
        },

        hasActiveModals() {
            return this.modals.size > 0;
        },

        hideLastModal() {
            if (this.modals.size > 0) {
                const lastModal = Array.from(this.modals).pop();
                this.modals.delete(lastModal);
            }
        },

        setActivePage(path) {
            this.active_page = path;
            const name = path.replace('/', '');
            const ui = this.module_ui[name];
            document.title = ui?.title || 'Krear 3D - Intranet';
        },

        trackScreen(path) {
            const token = localStorage.getItem('user_token');
            if (!token || !this.user?.id) return;
            if (!path || path === '/') return;
            try {
                fetch(`${this.api}/analytics/screen`, {
                    method: 'POST',
                    keepalive: true,
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`,
                        'X-No-Toast': '1',
                    },
                    body: JSON.stringify({
                        route: path,
                        device_id: this.getOrCreateDeviceId(),
                    }),
                }).catch(() => {});
            } catch (e) {}
        },

        getPages() {
            const modules = this.user.modules;

            // fallback: si no hay módulos del backend, no mostrar nada
            if (!modules || !modules.length) return [];

            return modules
                .filter(m => m.is_pinned)  // solo los pinned se muestran fijos
                .sort((a, b) => a.sort_order - b.sort_order)
                .map(m => {
                    const ui = this.module_ui[m.slug] || {};
                    return {
                        name: m.slug,
                        label: ui.label || m.name,
                        image: ui.image || m.slug,
                        title: ui.title || `Krear 3D - ${m.name}`,
                    };
                });
        },

        // Módulos no pinneados (para el menú expandible)
        getUnpinnedPages() {
            const modules = this.user.modules;
            if (!modules || !modules.length) return [];

            return modules
                .filter(m => !m.is_pinned)
                .sort((a, b) => a.sort_order - b.sort_order)
                .map(m => {
                    const ui = this.module_ui[m.slug] || {};
                    return {
                        name: m.slug,
                        label: ui.label || m.name,
                        image: ui.image || m.slug,
                        title: ui.title || `Krear 3D - ${m.name}`,
                    };
                });
        },

        // Estructura del sidebar:
        //  - Agrupado (desktop, por defecto): árbol con TODOS los menús (ignora is_pinned),
        //    páginas directas (top-level con icono) + categorías (icono + sub-páginas indentadas).
        //  - Plano (mobile rail + desktop con "Menú agrupado" apagado): lista por pin + reveal (logo).
        getSidebarItems() {
            const modules = this.user.modules;
            if (!modules || !modules.length) return [];

            const grouped = this.menu_grouped && !this.is_narrow;

            const toPage = (m) => {
                const ui = this.module_ui[m.slug] || {};
                const cat = (ui.category && this.categories[ui.category]) ? ui.category : null;
                return {
                    slug: m.slug,
                    name: m.slug,
                    label: ui.label || m.name,
                    image: ui.image || m.slug,
                    category: cat,
                    sort: m.sort_order,
                };
            };

            // ---- Modo plano: mobile (rail) o desktop con agrupado apagado ----
            // Respeta is_pinned y el reveal por logo (sidebar_expanded).
            if (!grouped) {
                const visible = (m) => m.is_pinned || this.sidebar_expanded;
                return modules
                    .filter(visible)
                    .sort((a, b) => a.sort_order - b.sort_order)
                    .map(m => {
                        const p = toPage(m);
                        return { type: 'page', key: 'p:' + p.slug, ...p };
                    });
            }

            // ---- Modo agrupado (desktop): TODOS los menús, ignora is_pinned ----
            const pages = modules.map(toPage);

            // Agrupar sub-páginas por categoría
            const byCat = new Map();
            for (const p of pages) {
                if (!p.category) continue;
                if (!byCat.has(p.category)) byCat.set(p.category, []);
                byCat.get(p.category).push(p);
            }

            // Entradas top-level: páginas directas + categorías (con >=1 página)
            const catKeys = Object.keys(this.categories);
            const entries = [];
            for (const p of pages) {
                if (!p.category) entries.push({ kind: 'page', key: 'p:' + p.slug, sort: p.sort, page: p });
            }
            for (const [cat, members] of byCat.entries()) {
                members.sort((a, b) => a.sort - b.sort);
                entries.push({
                    kind: 'cat',
                    key: 'g:' + cat,
                    sort: Math.min(...members.map(m => m.sort)),
                    catIndex: catKeys.indexOf(cat),
                    category: cat,
                    members,
                });
            }

            // Orden top-level: nav_order del usuario (si existe); luego default (sort_order + def. de categorías)
            const navOrder = Array.isArray(this.user.nav_order) ? this.user.nav_order : [];
            const navPos = (k) => {
                const i = navOrder.indexOf(k);
                return i < 0 ? Infinity : i;
            };
            entries.sort((a, b) => {
                const pa = navPos(a.key), pb = navPos(b.key);
                if (pa !== pb) return pa - pb;
                if (a.sort !== b.sort) return a.sort - b.sort;
                return (a.kind === 'cat' ? a.catIndex : -1) - (b.kind === 'cat' ? b.catIndex : -1);
            });

            const items = [];
            for (const e of entries) {
                if (e.kind === 'page') {
                    items.push({ type: 'page', key: 'p:' + e.page.slug, ...e.page });
                    continue;
                }
                const def = this.categories[e.category];
                const collapsed = this.collapsed_categories.includes(e.category);
                items.push({
                    type: 'header',
                    key: 'h:' + e.category,
                    category: e.category,
                    label: def.label || e.category,
                    image: def.icon,
                    collapsed,
                });
                if (!collapsed) {
                    e.members.forEach((m, i) => {
                        items.push({
                            type: 'subpage',
                            key: 's:' + m.slug,
                            name: m.slug,
                            label: m.label,
                            image: m.image,
                            last: i === e.members.length - 1,
                        });
                    });
                }
            }
            return items;
        },

        // Plegar/desplegar una categoría del sidebar (modo agrupado)
        toggleCategory(cat) {
            const i = this.collapsed_categories.indexOf(cat);
            if (i >= 0) this.collapsed_categories.splice(i, 1);
            else this.collapsed_categories.push(cat);
            localStorage.setItem('collapsed_categories', JSON.stringify(this.collapsed_categories));
        },

        // Al cargar/refrescar: abre el grupo de la página activa una sola vez (luego se puede cerrar manualmente)
        openActivePageGroup() {
            const activeSlug = (this.active_page || '').replace('/', '');
            const ui = this.module_ui[activeSlug];
            const cat = ui && ui.category;
            if (!cat) return;
            const i = this.collapsed_categories.indexOf(cat);
            if (i >= 0) {
                this.collapsed_categories.splice(i, 1);
                localStorage.setItem('collapsed_categories', JSON.stringify(this.collapsed_categories));
            }
        },

        // Navega al home (grilla de todas las páginas)
        goHome() {
            window.PineconeRouter.context.navigate('/home');
        },

        // Todas las páginas accesibles como tiles (icono + label) para la grilla del home.
        getAllTiles() {
            const modules = this.user.modules || [];
            return modules
                .slice()
                .sort((a, b) => a.sort_order - b.sort_order)
                .map(m => {
                    const ui = this.module_ui[m.slug] || {};
                    return { name: m.slug, label: ui.label || m.name, image: ui.image || m.slug, description: this.module_desc[m.slug] || '' };
                });
        },

        // Verificar si el usuario tiene un permiso específico
        hasPermission(moduleSlug, permissionSlug) {
            const modules = this.user.modules;
            if (!modules) return false;

            const mod = modules.find(m => m.slug === moduleSlug);
            if (!mod) return false;

            return mod.permissions[permissionSlug] === true;
        },

        // Verificar si el usuario tiene acceso a un módulo
        hasModule(moduleSlug) {
            const modules = this.user.modules;
            if (!modules) return false;

            return modules.some(m => m.slug === moduleSlug);
        },

        setUser(data) {
            console.log('Datos de usuario almacenados en el store');
            this.user = data;
            this.maybeShowPushModal();
        },

        unsetData() {
            console.log('Datos de usuario limpiados del store');
            this.user = {};
            this.team = {};
        },

        getUserData() {
            return {
                user: this.user,
            };
        },

        logout() {
            console.log('Logout...');
            this.closeSocket();
            this.clearDataCache();
            this.unsetData();
            this.sidebarOff();
            localStorage.removeItem('user_data');
            localStorage.removeItem('user_token');
            localStorage.removeItem('push_token');
            localStorage.removeItem('push_device_id');
            localStorage.removeItem('device_id');
            localStorage.removeItem('menu_grouped');
            localStorage.removeItem('sidebar_expanded');
            localStorage.removeItem('collapsed_categories');
            this.menu_grouped = !this.is_narrow;
            this.sidebar_expanded = false;
            this.collapsed_categories = [];
            window.PineconeRouter.context.navigate('/');
        },

        setData(key, value, url) {
            this[key] = { data: value, url: url || (this[key]?.url) };
            this.cached_keys.add(key);
        },

        clearDataCache() {
            this.cached_keys.forEach((key) => {
                if (this[key]) {
                    delete this[key];
                }
            });
            this.cached_keys.clear();
        },

        getData(key) {
            return this[key]?.data;
        },

        isLoaded(key) {
            const value = this[key]?.data;

            if (Array.isArray(value)) {
                return value.length > 0; // array no vacío
            }
            if (typeof value === 'object' && value !== null) {
                return Object.keys(value).length > 0; // objeto no vacío
            }
            return false;
        },

        getUrl(key) {
            return this[key]?.url;
        },

        _normalizeEndpoints(requests) {
            return requests.map(item => {
                if (typeof item === "string") {
                    const url = this.getUrl(item);
                    if (!url) {
                        console.warn(`No URL found for key: ${item}. Skipping.`);
                        return null;
                    }
                    return { key: item, url, force: false };
                }
                if (item && typeof item === "object" && item.key && item.url) {
                    return { ...item, force: !!item.force };
                }
                console.warn("Elemento inválido en fetchData/refresh:", item);
                return null;
            }).filter(Boolean);
        },

        async _fetchEndpoints(requests, ignoreCache = false) {
            if (!Array.isArray(requests)) throw new Error("fetchData debe recibir un array.");
            const endpoints = this._normalizeEndpoints(requests);

            const toFetch = endpoints.filter(ep => 
                ignoreCache || ep.force || !this.isLoaded(ep.key)
            );

            if (!toFetch.length) return;

            const token = localStorage.getItem('user_token');
            if (!token) {
                console.warn('_fetchEndpoints: sin token, abortando');
                return;
            }
            
            try {
                const responses = await Promise.all(
                    toFetch.map(ep =>
                        fetch(this.api + ep.url, {
                            headers: {
                                'Content-Type': 'application/json',
                                'Authorization': `Bearer ${token}`,
                            }
                        })
                        .then(res => res.json())
                        .then(data => ({ key: ep.key, data: data.data, url: ep.url }))
                    )
                );
                responses.forEach(({ key, data, url }) => this.setData(key, data, url));
            } catch (error) {
                console.error('Error fetching endpoints:', error);
            } 
        },

        async fetchData(requests) {
            await this._fetchEndpoints(requests, false);
        },

        async refresh(keys) {
            if (!Array.isArray(keys)) keys = [keys];
            const normalized = keys.map(item => {
                if (typeof item === "string") {
                    const url = this.getUrl(item);
                    if (!url) {
                        console.warn(`No URL found for key: ${item}. Skipping.`);
                        return null;
                    }
                    return { key: item, url };
                }
                if (item && typeof item === "object" && item.key && item.url) {
                    // Actualiza el url para el futuro
                    this.setData(item.key, this.getData(item.key), item.url);
                    return item;
                }
                console.warn("Elemento inválido en refresh:", item);
                return null;
            }).filter(Boolean);

            await this._fetchEndpoints(normalized, true);
        },

        getById(key, id) {
            return (this.getData(key) || []).find(item => item.id === id);
        },

        initSocket() {
            console.log("Init Socket...");
            if (!this.user?.id) {
                console.warn("❌ No se puede crear socket sin user.id");
                return;
            }

            if (!this.socket) {
                console.log("Creando socket para:", this.user.id);
                const socket = io(this.api + "/", {
                    query: {
                        user_id: this.user.id,
                    }
                });

                socket.on("connect_error", (err) => {
                    console.error("Error en la conexión del socket:", err.message);
                });

                socket.on("modules_updated", (data) => {
                    if (data.user_id === this.user.id) {
                        console.log("Permisos actualizados en caliente");
                        this.user.modules = data.modules;
                        this.user.default_page = data.default_page;
                    }
                });

                this.socket = socket;
            }
        },

        closeSocket() {
            if (this.socket) {
                this.socket.disconnect();
                this.socket = null;
            }
        },

        async verify() {
            console.log("Verify token...");

            const token = localStorage.getItem('user_token');
            if (!token) {
                console.log('No estás logueado...');
                await this.logout();
                return false;
            } 

            try {
                const response = await fetch(`${this.api}/user/verify`, {
                    method: 'GET',
                    headers: {'Authorization': `Bearer ${token}`},
                });

                if (!response.ok) {
                    await this.logout();
                    return false;
                }

                const result = await response.json();
                const serverVersion = result.app_version;
                const localVersion = localStorage.getItem('app_version');

                if (localVersion !== serverVersion) {
                    localStorage.setItem('app_version', serverVersion);
                    window.location.reload();
                    return;
                } 

                this.setUser(result.data);

                // ✅ Solo en F5: socket no existe aún
                if (!this.socket) {
                    this.initSocket();
                    this.sidebarOn();
                    this.initPush();
                }

                return true;

            } catch (error) {
                console.error('Error en la verificación del usuario:', error);
                await this.logout();
                return false;
            }
        },
        
        resizeImage(file, maxWidth, maxHeight) {
				return new Promise((resolve, reject) => {
					const img = new Image();
					const reader = new FileReader();
			
					reader.onload = (e) => {
						img.onload = () => {
							const canvas = document.createElement('canvas');
							const ctx = canvas.getContext('2d');
			
							let width = img.width;
							let height = img.height;
			
							if (width > height) {
								if (width > maxWidth) {
									height *= maxWidth / width;
									width = maxWidth;
								}
							} else {
								if (height > maxHeight) {
									width *= maxHeight / height;
									height = maxHeight;
								}
							}
			
							canvas.width = width;
							canvas.height = height;
							ctx.drawImage(img, 0, 0, width, height);
			
							canvas.toBlob((blob) => {
								if (blob) resolve(blob);
								else reject(new Error("Error al redimensionar la imagen"));
							}, file.type);
						};
			
						img.src = e.target.result;
					};
			
					reader.onerror = () => reject(new Error("Error al leer el archivo"));
					reader.readAsDataURL(file);
				});
			},
        
    });

    (function () {
        const isMobile = () =>
            window.matchMedia('(pointer: coarse)').matches ||
            window.matchMedia('(max-width: 768px)').matches;

        const THRESHOLD = 120;
        const CLOSE_Y = '120%';
        const SWIPE_MS = 200;
        const LEAVE_MS = 220;

        const getModalKeyFromWrap = (wrap) => {
            const id = (wrap?.id || '').trim();
            if (!id.startsWith('modal-')) return null;
            return id.replace(/^modal-/, '');
        };

        document.addEventListener('pointerdown', (e) => {
            if (!isMobile()) return;

            const grabber = e.target.closest('.modal-grabber');
            if (!grabber) return;

            const wrap = grabber.closest('.modal-wrap');
            if (!wrap) return;

            const modal = wrap.querySelector('.modal');
            if (!modal) return;

            e.preventDefault();

            const modalKey = getModalKeyFromWrap(wrap);

            const startY = e.clientY;
            let currentY = startY;

            modal.style.transition = 'none';

            const onMove = (ev) => {
            ev.preventDefault();
            currentY = ev.clientY;

            const dy = Math.max(0, currentY - startY);
            modal.style.transform = `translateY(${dy}px)`;
            };

            let closed = false;
            let fallbackTimer = null;

            const cleanup = () => {
            window.removeEventListener('pointermove', onMove);
            window.removeEventListener('pointerup', onEnd);
            window.removeEventListener('pointercancel', onEnd);
            if (fallbackTimer) clearTimeout(fallbackTimer);
            };

            const closeThisModal = () => {
            if (closed) return;
            closed = true;

            if (modalKey) Alpine.store('cache').hideModal(modalKey);
            else Alpine.store('cache').hideLastModal(); // fallback

            setTimeout(() => {
                modal.style.transition = '';
                modal.style.transform = '';
            }, LEAVE_MS);
            };

            const onEnd = () => {
            cleanup();

            const dy = Math.max(0, currentY - startY);

            if (dy <= THRESHOLD) {
                modal.style.transition = `transform ${SWIPE_MS}ms ease`;
                modal.style.transform = 'translateY(0px)';
                setTimeout(() => {
                modal.style.transition = '';
                modal.style.transform = '';
                }, SWIPE_MS + 30);
                return;
            }

            modal.style.transition = `transform ${SWIPE_MS}ms ease`;
            requestAnimationFrame(() => {
                modal.style.transform = `translateY(${CLOSE_Y})`;
            });

            const onTransitionEnd = (ev) => {
                if (ev.propertyName !== 'transform') return;
                modal.removeEventListener('transitionend', onTransitionEnd);
                closeThisModal();
            };

            modal.addEventListener('transitionend', onTransitionEnd);

            fallbackTimer = setTimeout(() => {
                modal.removeEventListener('transitionend', onTransitionEnd);
                closeThisModal();
            }, SWIPE_MS + 80);
            };

            window.addEventListener('pointermove', onMove, { passive: false });
            window.addEventListener('pointerup', onEnd, { passive: true });
            window.addEventListener('pointercancel', onEnd, { passive: true });
        }, { passive: false });
        })();



    Alpine.data('avatarCrop', () => ({
        open: false,
        zoom: 1,
        offsetX: 0,
        offsetY: 0,
        dragging: false,
        _startX: 0,
        _startY: 0,
        _file: null,

        onSelected(event) {
            const file = event.target.files[0];
            if (!file) return;
            const allowed = ['image/jpeg', 'image/png', 'image/webp'];
            if (!allowed.includes(file.type)) { alert('Solo JPG, PNG o WEBP'); return; }
            if (file.size > 6 * 1024 * 1024) { alert('La imagen supera 6 MB'); return; }
            const img = new Image();
            const url = URL.createObjectURL(file);
            img.onload = () => {
                this.zoom = 1;
                this.offsetX = 0;
                this.offsetY = 0;
                this._file = file;
                this.$refs.preview.src = url;
                this.open = true;
            };
            img.src = url;
            event.target.value = '';
        },

        onDragStart(e) {
            const client = e.touches ? e.touches[0] : e;
            this.dragging = true;
            this._startX = client.clientX - this.offsetX;
            this._startY = client.clientY - this.offsetY;
        },

        onDragMove(e) {
            if (!this.dragging) return;
            const client = e.touches ? e.touches[0] : e;
            this.offsetX = client.clientX - this._startX;
            this.offsetY = client.clientY - this._startY;
        },

        async upload() {
            if (!this._file) return;
            this.saving = true;
            try {
                const pr = this.$refs.preview;
                const size = 512, display = 220;
                const canvas = document.createElement('canvas');
                canvas.width = canvas.height = size;
                const ctx = canvas.getContext('2d');
                const scale = size / display;
                ctx.save();
                ctx.translate(size / 2, size / 2);
                ctx.scale(this.zoom * scale, this.zoom * scale);
                ctx.translate(-display / 2 + this.offsetX / this.zoom, -display / 2 + this.offsetY / this.zoom);
                ctx.drawImage(pr, 0, 0, display, display);
                ctx.restore();

                const mime = this._file.type === 'image/webp' ? 'image/webp'
                           : this._file.type === 'image/png'  ? 'image/png' : 'image/jpeg';
                const ext  = mime === 'image/webp' ? 'webp' : mime === 'image/png' ? 'png' : 'jpg';
                const blob = await new Promise(res => canvas.toBlob(res, mime, 0.92));
                const form = new FormData();
                form.append('avatar', blob, `avatar.${ext}`);
                const token = localStorage.getItem('user_token');
                const res  = await fetch(`${Alpine.store('cache').api}/user/upload_avatar`, {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${token}` },
                    body: form,
                });
                const data = await res.json();
                if (data.success) {
                    Alpine.store('cache').user.image = (data.data.message || data.data) + '?t=' + Date.now();
                    this.open = false;
                } else {
                    alert(data.data?.message || data.data || 'Error al subir imagen');
                }
            } catch {
                alert('Error al procesar la imagen');
            } finally {
                this.saving = false;
            }
        },

        saving: false,
    }));

});

function logisticsHandler({ params }) {
    const client_order_id = params.client_order_id;
    //console.log("client_order_id:", client_order_id);
    // Puedes guardarlo en Alpine store si lo usarás en la vista
    Alpine.store('cache').client_order_id = client_order_id;
    const currentPath = window.location.pathname;
    const newPath = currentPath.substring(0, currentPath.lastIndexOf('/'));
    history.replaceState(null, '', newPath);
}

// Fábrica de handlers de deeplink: guarda el id en el store y delega en la ruta base.
// La pestaña de chat de cada módulo vive dentro del modal de detalle, así que el mismo deeplink la abre.
function makeDeeplinkHandler(route, storeKey) {
    return function (context) {
        const id = context.params.id;
        if (id) Alpine.store('cache')[storeKey] = id;
        window.PineconeRouter.context.navigate(route);
        return false;
    };
}

// El service worker reenvía la URL del push cuando la app ya está abierta
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.addEventListener('message', (event) => {
        if (event.data?.type === 'NAVIGATE' && event.data.url) {
            window.PineconeRouter.context.navigate(event.data.url);
        }
    });
}

async function loginVerify(context) {
    console.log('Verificando Login...');

    const token = Alpine.store('cache').user.token 
               || localStorage.getItem('user_token');

    if (!token) {
        window.PineconeRouter.context.navigate('/');
        return false;
    }

    // ✅ Si ya hay sesión activa (socket existe = ya se inicializó)
    // renderizar inmediatamente y verificar en segundo plano
    if (Alpine.store('cache').socket) {
        Alpine.store('cache').verify(); // sin await — no bloquea
        return true;                    // render inmediato con data del store
    }

    // ✅ Solo en F5 (socket null) esperamos verify completo antes de renderizar
    const ok = await Alpine.store('cache').verify();
    if (!ok) {
        window.PineconeRouter.context.navigate('/');
        return false;
    }

    return true;
}

async function loginRedirect(context) {
    const token = Alpine.store('cache').user.token || localStorage.getItem('user_token');
    if (!token) return true; // no hay sesión, mostrar login

    const ok = await Alpine.store('cache').verify();
    if (ok) {
        const defaultPage = Alpine.store('cache').user.default_page || '/attendance';
        window.PineconeRouter.context.navigate(defaultPage);
        return false; // no renderizar login
    }

    return true; // token inválido, mostrar login
}

document.addEventListener('pinecone-start', () => {
    // Alpine.store('cache').verify();
});

document.addEventListener('pinecone-end', () => {
    const path = window.location.pathname;
    Alpine.store('cache').setActivePage(path);
    Alpine.store('cache').trackScreen(path);
    // NProgress.done();
});

// document.addEventListener('fetch-error', (err) =>
//     console.error(err)
// );