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
                console.log('Cambiando de routa...');
            }
            
        },
    }));

    Alpine.store('cache', {
        api: 'https://api.krear3d.com',
        user: {},
        active_page: window.location.pathname,
        common_pages: [
            //{ name: 'Home', label: 'Inicio', image: 'home', title: 'Krear 3D - Inicio' }
            { name: 'board', label: 'Actividades', image: 'board', title: 'Krear 3D - Actividades' },
            { name: 'logistics', label: 'Envíos', image: 'logistics', title: 'Krear 3D - Envíos' },
            { name: 'tracking', label: 'Tracking', image: 'tracking', title: 'Krear 3D - Trackings' },
            { name: 'support', label: 'Soporte', image: 'support', title: 'Krear 3D - Soporte' },
            //{ name: 'training', label: 'Capacitaciones', image: 'training', title: 'Krear 3D - Capacitaciones' },
            //{ name: 'clients', label: 'Clientes', image: 'clients', title: 'Krear 3D - Clientes' },
        ],
        restricted_pages: [
            { name: 'driver', label: 'Conductor', image: 'driver', title: 'Krear 3D - Conductor' },
            { name: 'marketing', label: 'Marketing', image: 'marketing', title: 'Krear 3D - Marketing' },
            { name: 'guest', label: 'Fabrix', image: 'fabrix', title: 'Krear 3D - Fabrix' },
        ],

        fabrix_pages: [
            { name: 'guest', label: 'Fabrix', image: 'fabrix', title: 'Krear 3D - Fabrix' },
        ],
        modals: new Set(),
        sidebar: false,
        sidebar_menu: false,
        
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
                return this.fabrix_pages;
            }

            if (level_id === 4) {
                return [...this.common_pages, ...this.restricted_pages];
            }

            if (department_id === 2) {
                const allowedRestricted = ['driver'];
                const filteredRestricted = this.restricted_pages.filter(page =>
                    allowedRestricted.includes(page.name)
                );
                return [...this.common_pages, ...filteredRestricted];
            }

            if (department_id === 4) {
                const allowedRestricted = ['marketing'];
                const filteredRestricted = this.restricted_pages.filter(page =>
                    allowedRestricted.includes(page.name)
                );
                return [...this.common_pages, ...filteredRestricted];
            }

            if (user_id === 19) {
                const allowedRestricted = ['guest'];
                const filteredRestricted = this.restricted_pages.filter(page =>
                    allowedRestricted.includes(page.name)
                );
                return [...this.common_pages, ...filteredRestricted];
            }
            return this.common_pages;
        },

        setUser(data) {
            console.log('Datos de usuario almacenados en el store');
            this.user = data;
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
            this.unsetData();
            this.sidebarOff();
            localStorage.removeItem('user_data');
            window.PineconeRouter.context.navigate('/');
        },

        setData(key, value, url) {
            this[key] = { data: value, url: url || (this[key]?.url) };
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
                        fetch(this.api + ep.url)
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

    NProgress.start();

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
        
        if (context.route == '/') {
            console.log('Sesión iniciada. Redirigiendo a default...');
            window.PineconeRouter.context.navigate(Alpine.store('cache').user.default_page);
        }
        return true;

    } catch (error) {
        console.error('Error en la verificación del usuario:', error);

        await Alpine.store('cache').logout();
        return false;

    } finally {
        NProgress.done();
    }
}

document.addEventListener('pinecone-start', () => {
    NProgress.start();
});

document.addEventListener('pinecone-end', () => {
    Alpine.store('cache').setActivePage(window.location.pathname);
    NProgress.done();
});

document.addEventListener('fetch-error', (err) =>
    console.error(err)
);