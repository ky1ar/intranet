document.addEventListener('alpine:init', () => {
    Alpine.store('modal', {
        active: new Set(),
    
        show(modal) {
            this.active.add(modal);
        },
    
        hide(modal) {
            this.active.delete(modal);
        },
    
        hideAll() {
            this.active.clear();
        },

        isVisible(modal) {
            return this.active.has(modal);
        },

        hasActive() {
            return this.active.size > 0;
        },

        hideLast() {
            if (this.active.size > 0) {
                const lastModal = Array.from(this.active).pop();
                this.active.delete(lastModal);
            }
        }
    });
    
    Alpine.store('home', {
        team: [],

        setTeam(data) {
            console.log('Datos de team almacenados en el store');
            this.team = data;
        },

        isLoaded() {
            console.log('Verficando datos de Home...')
            if (this.team.length === 0) {
                console.log('Los datos no se encuentran en el Store');
                return false;
            } 
            console.log('Los datos se encuentran en el Store');
            return true;
        },
    });

    
    Alpine.store('sidebar', {
        active: false,
        open_menu: false,

        visible() {
            this.active = true;
        },

        off() {
            this.active = false;
            this.open_menu = false;
        },
        
        toogleMenu() { 
            this.open_menu = !this.open_menu;
        },

        hideMenu() { 
            this.open_menu = false;
        }
    });

    Alpine.data('data',() => ({
        async init() {
            console.log('Inicializando Alpine...');
        },
    }));


    Alpine.store('cache', {
        api: 'https://api.krear3d.com',
        user: {},
        active_page: window.location.pathname,
        pages: [
            { name: 'logistics', label: 'Envíos', image: 'logistics', title: 'Krear 3D - Panel de Logística' },
            { name: 'driver', label: 'Conductor', image: 'driver', title: 'Krear 3D - Conductor' },
            //{ name: '', label: '', image: 'login', title: 'Krear 3D - Intranet' },
            //{ name: 'tracking', label: 'Tracking', image: 'tracking', title: 'Krear 3D - Panel de Trackings' },
            //{ name: 'clients', label: 'Clientes', image: 'clients', title: 'Krear 3D - Clientes' },
            //{ name: 'soporte', label: 'Soporte', image: 'support', title: 'Krear 3D - Panel de Soporte' },
            //{ name: 'capacitaciones', label: 'Capacitaciones', image: 'training', title: 'Krear 3D - Panel de Capacitaciones' },
            //{ name: 'Home', label: 'Inicio', image: 'home', title: 'Krear 3D - Inicio' }
        ],

        setActivePage(path) {
            this.active_page = path;
            const name = path.replace('/', '');
            const page = this.pages.find(p => p.name === name);
            document.title = page?.title || 'Krear 3D - Intranet';
        },

        getPages() {
            const department_id = Alpine.store('cache').user.department_id;
            const level_id = Alpine.store('cache').user.level_id;

            if (level_id == 4 ) {
                return this.pages;
            } else if (department_id === 2) {
                return this.pages.filter(page =>
                    ['logistics', 'driver', 'tracking'].includes(page.name)
                );
            } else {
                return this.pages.filter(page =>
                    ['logistics', 'tracking'].includes(page.name)
                );
            }
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
            this.unsetUser()
            Alpine.store('sidebar').off();
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
    });
});


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
        Alpine.store('sidebar').visible();
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