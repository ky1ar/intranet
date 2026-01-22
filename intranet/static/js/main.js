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

    window.PineToast = {
        start(title = "Cargando…") {
            clearTimeout(hideTimer);
            const el = ensureToast();
            el.querySelector(".title").textContent = title;
            el.classList.add("show");
        },
        done() {
            const el = document.getElementById(ID);
            if (!el) return;
            hideTimer = setTimeout(() => el.classList.remove("show"), 150);
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
        init() {
            Alpine.store('cache').detectPlatform();

            console.log('Inicializando Alpine...');

            const token = Alpine.store('cache').user.token;
            const storedData = localStorage.getItem('user_data');
            if (!token) {
                console.log('Ventana reiniciada...');
                if (storedData) {
                    console.log('Obteniendo data desde el cache...');
                    const userData = JSON.parse(storedData);
                    Alpine.store('cache').setUser(userData);
                    Alpine.store('cache').initSocket();
                    Alpine.store('cache').sidebarOn();
                } else {
                    console.log('No estás logueado...');
                    if (window.location.pathname !== '/') {
                        window.location.href = '/';
                    }
                    return false;
                }
            } else {
                console.log('Cambiando de ruta...');
            }
            
        },
    }));

    Alpine.store('cache', {
        api: 'https://devapi.krear3d.com', //https://devapi.krear3d.com
        user: {},
        active_page: window.location.pathname,
        common_pages: [
            { name: 'attendance', label: 'Asistencia', image: 'attendance', title: 'Krear 3D - Asistencia' },
            { name: 'schedule', label: 'Agenda', image: 'calendar2', title: 'Krear 3D - Agenda' },
            { name: 'board', label: 'Actividades', image: 'board', title: 'Krear 3D - Actividades' },
            { name: 'logistics', label: 'Envíos', image: 'logistics', title: 'Krear 3D - Envíos' },
            { name: 'tracking', label: 'Tracking', image: 'tracking', title: 'Krear 3D - Trackings' },
            { name: 'support', label: 'Soporte', image: 'support', title: 'Krear 3D - Soporte' },
            { name: 'purchases', label: 'Compras', image: 'purchases', title: 'Krear 3D - Compras' },
            //{ name: 'training', label: 'Capacitaciones', image: 'training', title: 'Krear 3D - Capacitaciones' },
            //{ name: 'clients', label: 'Clientes', image: 'clients', title: 'Krear 3D - Clientes' },
        ],
        restricted_pages: [
            { name: 'driver', label: 'Conductor', image: 'driver', title: 'Krear 3D - Conductor' },
            //{ name: 'marketing', label: 'Marketing', image: 'marketing', title: 'Krear 3D - Marketing' },
            { name: 'guest', label: 'Fabrix', image: 'fabrix', title: 'Krear 3D - Fabrix' },
        ],

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
            const pages = [...this.common_pages, ...this.restricted_pages];
            const page = pages.find(p => p.name === name);
            document.title = page?.title || 'Krear 3D - Intranet';
        },

        getPages() {
            const department_id = this.user.department_id;
            const level_id = this.user.level_id;
            const user_id = this.user.id;

            if (user_id === 21) {
                return this.getRestricted(['guest']);
            }

            if (level_id === 4) {
                return [...this.common_pages, ...this.restricted_pages];
            }

            if (department_id === 2) {
                return [...this.common_pages, ...this.getRestricted(['driver'])];
            }

            if (department_id === 4) {
                return [...this.common_pages, ...this.getRestricted(['marketing'])];
            }

            if (user_id === 19 || user_id === 12) {
                return [...this.common_pages, ...this.getRestricted(['guest'])];
            }

            return this.common_pages;
        },

        getRestricted(allowedNames) {
            return this.restricted_pages.filter(page =>
                allowedNames.includes(page.name)
            );
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
            localStorage.removeItem('push_token');
            localStorage.removeItem('push_device_id');
            localStorage.removeItem('device_id');
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
            try {
                const responses = await Promise.all(
                    toFetch.map(ep =>
                        fetch(this.api + ep.url, {
                            headers: {
                                'Content-Type': 'application/json',
                                'Authorization': `Bearer ${this.user.token}`,
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
            try {
                const response = await fetch(this.api + '/user/verify', {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${this.user.token}`,
                    },
                });

                if (!response.ok) {
                    console.error('Error en la verificación del usuario', response.statusText);
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

async function loginVerify(context) {
    console.log('Verificando Login...');
    let token = Alpine.store('cache').user.token;
    const storedData = localStorage.getItem('user_data');
    if (!token) {
        if (storedData) {
            console.log('Verificando desde localStorage');
            const userData = JSON.parse(storedData);
            token = userData.token;
        } else {
            console.log('No estás logueado');
            if (context.route !== "/") {
                window.PineconeRouter.context.navigate("/");
            }
            return false;
        }
    } else {
        console.log('Verificando desde el router');
    }

    try {
        const response = await fetch(Alpine.store('cache').api + '/user/verify', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            console.error('Error en la verificación del usuario', response.statusText);
            await Alpine.store('cache').logout();
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

        console.log('Usuario logeado');
        
        if (storedData && !Alpine.store('cache').user.token) {
            const userData = JSON.parse(storedData);
            Alpine.store('cache').setUser(userData);
        }

        Alpine.store('cache').initSocket();
        Alpine.store('cache').sidebarOn();
        Alpine.store('cache').initPush();
        
        if (context.route == '/') {
            console.log('Sesión iniciada. Redirigiendo a default...');
            window.PineconeRouter.context.navigate(Alpine.store('cache').user.default_page);
        }
        return true;

    } catch (error) {
        console.error('Error en la verificación del usuario:', error);

        await Alpine.store('cache').logout();
        return false;

    }
}

// document.addEventListener('pinecone-start', () => {
//     NProgress.start();
// });

document.addEventListener('pinecone-end', () => {
    Alpine.store('cache').setActivePage(window.location.pathname);
    // NProgress.done();
});

// document.addEventListener('fetch-error', (err) =>
//     console.error(err)
// );