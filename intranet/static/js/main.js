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
            console.log('Inicializando Alpine...');
        },
    }));

    Alpine.store('cache', {
        api: 'https://api.krear3d.com',
        user: {},
        active_page: window.location.pathname,
        common_pages: [
            //{ name: 'Home', label: 'Inicio', image: 'home', title: 'Krear 3D - Inicio' }
            { name: 'logistics', label: 'Envíos', image: 'logistics', title: 'Krear 3D - Envíos' },
            { name: 'tracking', label: 'Tracking', image: 'tracking', title: 'Krear 3D - Trackings' },
            //{ name: 'support', label: 'Soporte', image: 'support', title: 'Krear 3D - Soporte' },
            //{ name: 'training', label: 'Capacitaciones', image: 'training', title: 'Krear 3D - Capacitaciones' },
            //{ name: 'clients', label: 'Clientes', image: 'clients', title: 'Krear 3D - Clientes' },
        ],
        restricted_pages: [
            { name: 'driver', label: 'Conductor', image: 'driver', title: 'Krear 3D - Conductor' },
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
            return this.common_pages;
        },

        setUser(data) {
            console.log('Datos de usuario almacenados en el store');
            this.user = data;
        },

        unsetUser() {
            console.log('Datos de usuario limpiados del store');
            this.user = {};
        },

        getUserData() {
            return {
                user: this.user,
            };
        },

        logout() {
            console.log('Logout');
            this.closeSocket();
            this.unsetUser();
            this.sidebarOff();
            localStorage.removeItem('user_data');
            window.PineconeRouter.context.navigate('/');
        },

        setData(key, data) {
            if (!this.hasOwnProperty(key)) {
                console.log(`La clave '${key}' no existe. Creándola automáticamente en el store.`);
                this[key] = [];
            }
            console.log(`Datos de ${key} almacenados en el store`);
            this[key] = data;
        },
    
        isLoaded(key) {
            console.log(`Verificando datos de ${key}...`);
            if (!this.hasOwnProperty(key)) {
                console.log(`La clave '${key}' no existe en el store`);
                return false;
            }
            if (!Array.isArray(this[key]) || this[key].length === 0) {
                console.log(`Los datos de '${key}' no se encuentran en el Store`);
                return false;
            }
            console.log(`Los datos de '${key}' se encuentran en el Store`);
            return true;
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