function data() {
    return {
        schedule: [],
        shippingDay: [],
        drivers: [],
        vendors: [],
        districts: [],
        shippingMethod: [],
        pendingShippings: [],

        offset: 0,
        selectedOrder: null,
        scheduleRange: '',
        
        auth: {
            id: null,
            level: null,
            app_level: null,
            name: '',
            role: '',
            image: (JSON.parse(localStorage.getItem('user_data'))?.image || '/api/uploads/user_default.jpg'),
            token: null,
        },

        temp_auth: {
            document: (JSON.parse(localStorage.getItem('temp_auth'))?.document || ''),
            name: (JSON.parse(localStorage.getItem('temp_auth'))?.name || ''),
            image: (JSON.parse(localStorage.getItem('temp_auth'))?.image || '/api/uploads/user_default.jpg'),
        },

        buttons: {
            find: {
                class: '',
                text: 'Siguiente',
            },
            login: {
                class: '',
                text: 'Ingresar',
            },
            new_pin: {
                class: '',
                text: 'Continuar',
            },
            create_pin: {
                class: '',
                text: 'Crear clave',
            },
        },

        page: {
            current: 'calendar'
        },

        pages: [
            { name: 'calendar', label: 'Calendario' },
            { name: 'clients', label: 'Clientes' },
            { name: 'history', label: 'Historial' },
            { name: 'workers', label: 'Colaboradores' }
        ],

        modal: {
            shipping: false,
            completed: false,
            image: false,
            finish: false,
            transit: false,
            overlay: false,
        },

        process_shipping: {
            edit: false,
            button_text: 'Añadir',
            button_complete: 'Entregado',
            button_rejected: 'No entregado',
            button_class: '',
            driver_id: null,
            vendor_id: null,
            document: '',
            document_id: null,
            name: '',
            email: '',
            phone: '',
            order_number: '',
            method_id: null,
            method_name: '',
            address: '',
            district_id: null,
            driver_name: null,
            district_name: '',
            register_date: '',
            status_id: null,
            proof: '',
            maps: null,
        },

        socket: null,
        preview: null,
        imageFile: null,
        isProcessing: false,

        deferredPrompt: null,
        navigator: '',
        pwa: false,
        readyToInstall: false,

        firebaseConfig: {
            apiKey: "AIzaSyDzSedMzfKT5L2LklmUQsMyvPEGfZ_0fcw",
            authDomain: "krear3d-f9195.firebaseapp.com",
            projectId: "krear3d-f9195",
            storageBucket: "krear3d-f9195.firebasestorage.app",
            messagingSenderId: "291592879896",
            appId: "1:291592879896:web:674af68c5c7d1fe440a86d",
            measurementId: "G-2CCET399W9"
        },

        messaging: null,
        first_login: false,
        new_pin: false,
        onboard: localStorage.onboard === "true",//(localStorage.getItem("onboard") === "true") || false,
        open_menu: false,

        test: "Alex",

        get showOverlay() {
            return Object.values(this.modal).some(value => value);
        },

        async processShippingModal(shipping_number){
            if (shipping_number){
                await this.getShipping(shipping_number);

                if (this.process_shipping.status_id > 3){
                    this.modal.finish = true;
                } else {
                    this.modal.shipping = true;
                }
            } else {
                this.modal.shipping = true;
            }
        },
        
        installPWA() {
            if (this.deferredPrompt) {
                this.deferredPrompt.prompt();
                this.deferredPrompt.userChoice.then(choice => {
                    if (choice.outcome === 'accepted') {
                        console.log('PWA instalada');
                        window.location.reload();

                    } else {
                        console.log('Instalación cancelada');
                    }
                    this.deferredPrompt = null;
                    this.readyToInstall = false;
                });
            }
        },

        async onTheWay(){
            if (this.isProcessing) return;
            this.isProcessing = true;

            try {
                await this.updateOrderStatus(3);

                /*this.socket.emit("on_the_way", {
                    phone: this.process_shipping.phone,
                    user: this.process_shipping.name
                });*/

                //await this.updateSchedule();
                this.process_shipping.status_id = 3;
            } catch (error) {
                console.error("Error en el proceso de actualización:", error);
            } finally {
                this.isProcessing = false;
            }
        },
        
        async completeShipping() {
            if (this.isProcessing) return;
            this.isProcessing = true;

            if (!this.imageFile) {
                this.process_shipping.button_complete = 'Sube una foto';
                this.process_shipping.button_class = 'error';
                setTimeout(() => {
                    this.process_shipping.button_complete = 'Entregado';
                    this.process_shipping.button_class = '';
                }, 1500);
                this.isProcessing = false;
                return;
            }
        
            const maxWidth = 1024;
            const maxHeight = 1024;
        
            try {
                const resizedImage = await this.resizeImage(this.imageFile, maxWidth, maxHeight);
        
                const formData = new FormData();
                formData.append("image", resizedImage);
                formData.append("order_number", this.process_shipping.order_number);
        
                await this.uploadImage(formData);
                await this.updateOrderStatus(4);
        
                this.closeShipping();
        
            } catch (error) {
                console.error("Error en el proceso de entrega:", error);
            } finally {
                this.isProcessing = false;
            }
        },
        
        async rejectShipping() {
            if (this.isProcessing) return;
            this.isProcessing = true;

            if (!this.imageFile) {
                this.process_shipping.button_rejected = 'Sube una foto';
                this.process_shipping.button_class = 'error';
                setTimeout(() => {
                    this.process_shipping.button_rejected = 'No entregado';
                    this.process_shipping.button_class = '';
                }, 1500);
                this.isProcessing = false;
                return;
            } 
        
            const maxWidth = 1024;
            const maxHeight = 1024;
        
            try {
                const resizedImage = await this.resizeImage(this.imageFile, maxWidth, maxHeight);
        
                const formData = new FormData();
                formData.append("image", resizedImage);
                formData.append("order_number", this.process_shipping.order_number);
        
                await this.uploadImage(formData);
                await this.updateOrderStatus(6);
        
                this.closeShipping();
        
            } catch (error) {
                console.error("Error en el proceso de entrega:", error);
            } finally {
                this.isProcessing = false;
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
        
        async uploadImage(formData) {
            const response = await fetch('/api/photo/upload', {
                method: 'POST',
                body: formData
            });
        
            if (!response.ok) {
                throw new Error('Error al subir la imagen.');
            }
        },
        
        async deleteShipping() {
            const payload = {
                order_number: this.process_shipping.order_number,
                admin_id: this.auth.id
            };
        
            const response = await fetch('/api/order/delete', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });
        
            if (!response.ok) {
                throw new Error('Error al asignar la orden.');
            }
            //await this.updateSchedule();
            this.closeShipping();
        },

        async updateOrderStatus(status) {
            const payload = {
                order_number: this.process_shipping.order_number,
                status_id: status,
                admin_id: this.auth.id
            };
        
            const response = await fetch('/api/order/set', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });
        
            if (!response.ok) {
                throw new Error('Error al asignar la orden.');
            }
        },

        /*async updateSchedule(){
            this.socket.emit("update_schedule", {});
        },*/

        async showShipping(shipping_number){
            await this.getShipping(shipping_number);

            this.modal.transit = true;
        },

        resetModal() {
            Object.keys(this.modal).forEach(key => this.modal[key] = false);
        },

        closeShipping(){
            this.resetModal();
  
            this.preview = null;
            this.imageFile = null;
            this.selectedOrder = null;

            this.process_shipping = {
                edit: false,
                button_text: 'Añadir',
                button_complete: 'Entregado',
                button_rejected: 'No entregado',
                button_class: '',
                driver_id: this.selectFirstOption(this.drivers),
                vendor_id: null,
                document: '',
                document_id: null,
                name: '',
                email: '',
                phone: '',
                order_number: '',
                method_id: null,
                method_name: '',
                address: '',
                district_id: null,
                driver_name: null,
                district_name: '',
                register_date: '',
                status_id: null,
                proof: '',
                maps: null,
            };
        },

        showError(btnKey, errorMsg) {
            const originalText = this.buttons[btnKey].text;
            const originalClass = this.buttons[btnKey].class;

            if (originalClass == 'error') {
                return;
            }
            this.buttons[btnKey].text = errorMsg;
            this.buttons[btnKey].class = 'error';

            setTimeout(() => {
                this.buttons[btnKey].text = originalText;
                this.buttons[btnKey].class = originalClass;
            }, 2000);
        },

        clean_temp() {
            this.temp_auth = {
                document: '',
                name: '',
                role: '',
                image: '/api/uploads/user_default.jpg',
            },
            this.first_login = false;
            localStorage.removeItem('temp_auth'); 
        },

        async find() {
            const payload = { document: this.temp_auth.document }
            try {
                const response = await fetch('/api/user/find', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload),
                });
                
                const jsonData = await response.json();

                if (!response.ok) {
                    if (response.status === 400) {
                        this.showError('find', jsonData.data.message)
                    }
                    return false;
                }

                const data = jsonData.data;
                if (data.image) {
                    this.temp_auth.image = "/api/uploads/" + data.image;
                }
                this.temp_auth.name = data.name;
                if(data.first_login) {
                    this.first_login = data.first_login;
                } else {
                    localStorage.setItem('temp_auth', JSON.stringify(this.temp_auth));
                }

            } catch (e) {
                console.error('Error during login verification:', e.message);
            }
        },  

        async createPin() {
            pin = this.temp_auth.pin;
            confirm_pin = this.temp_auth.confirm_pin;

            if (pin != confirm_pin) {
                this.showError('new_pin', "Las claves son distintas");
                this.temp_auth.pin = ''
                this.temp_auth.confirm_pin = '';
                this.new_pin = false;
                return;
            }

            const payload = { document: this.temp_auth.document, pin: this.temp_auth.pin }
            try {
                const response = await fetch('/api/user/create_pin', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload),
                });
                
                const jsonData = await response.json();

                if (!response.ok) {
                    if (response.status === 400) {
                        this.showError('create_pin', jsonData.data.message)
                    }
                    return false;
                }
                localStorage.setItem('temp_auth', JSON.stringify(this.temp_auth));
                await this.login();
                this.first_login = false;
                this.new_pin = false;
            } catch (e) {
                console.error('Error during createPin:', e.message);
            }
        },  

        async login() {
            const payload = { document: this.temp_auth.document, password: this.temp_auth.pin , fcm_token: localStorage.getItem("fcm_token") }
            try {
                const response = await fetch('/api/user/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload),
                });
                
                const jsonData = await response.json();
                if (!response.ok) {
                    if (response.status === 400) {
                        this.showError('login', jsonData.data.message)
                    }
                    return false;
                }
                const userData = jsonData.data;

                if (userData.image) {
                    this.auth.image = "/api/uploads/" + userData.image;
                }
                this.auth.token = userData.token;
                this.auth.id = userData.id;
                this.auth.level = userData.level_id;
                this.auth.app_level = userData.shipping_app_level;
                this.auth.name = userData.name;
                this.auth.role = userData.department_name;

                localStorage.setItem('user_data', JSON.stringify(this.auth));
                this.temp_auth.pin = null;
                this.temp_auth.confirm_pin = null;
                this.initSocket();

                await Promise.all([
                    this.fetchData(),
                    this.recoverFCMToken()
                ]);

            } catch (e) {
                console.error('Error during login verification:', e.message);
            }
        },  

        async logout() {
            this.auth.token = null;
            this.auth.image = "/api/uploads/user_default.jpg";
            this.auth.id = null;
            this.auth.level = null;
            this.auth.app_level = null;
            this.auth.name = '';
            this.auth.role = '';
            this.offset = 0;
            this.socket.disconnect()

            localStorage.removeItem('user_data'); 
            
            const payload = { fcm_token: localStorage.getItem("fcm_token") }
            try {
                const response = await fetch('/api/user/logout', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload),
                });

                if (response.ok) {
                    console.log("Logout exitoso");
                } else {
                    console.error("Error en el logout:", await response.text());
                }
            } catch (e) {
                console.error("Error durante el logout:", e.message);
            }
        },

        async loginVerify() {
            const storedData = localStorage.getItem('user_data');
            if (storedData) {
                const userData = JSON.parse(storedData);
                this.auth.token = userData.token;
                const response = await fetch('/api/user/verify', {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${userData.token}`,
                        'Content-Type': 'application/json',
                    },
                });

                if (!response.ok) {
                    await this.logout();
                    return false;
                }   

                this.auth.id = userData.id;
                this.auth.level = userData.level;
                this.auth.app_level = userData.app_level;
                this.auth.name = userData.name;
                this.auth.role = userData.role;
                this.auth.image = userData.image;

                return true;
                
            } else {
                return false;
            }
        },

        async init() {
            try {
                await this.manageServiceWorkers();
                this.initFirebase();
                this.listenForMessages();
                this.setAgent();
                this.setupInstallPrompt();

                const loginVerify = await this.loginVerify();
                if(loginVerify) {
                    this.initSocket();

                    await Promise.all([
                        this.fetchData(),
                        this.recoverFCMToken()
                    ]);
                }
            } catch (error) {
                console.error('Error al iniciar la aplicación:', error.message);
            } 
        },

        async manageServiceWorkers() {
            if (!("serviceWorker" in navigator)) return;

            const registrations = await navigator.serviceWorker.getRegistrations();
    
            if (registrations.length > 1) {
                console.warn(`Se detectaron ${registrations.length} Service Workers, eliminando duplicados...`);
                await Promise.all(registrations.slice(1).map(sw => sw.unregister()));
                console.log("Service Workers duplicados eliminados.");
            }
    
            if (registrations.length === 0) {
                await navigator.serviceWorker.register("/firebase-messaging-sw.js");
                console.log("Service Worker registrado correctamente.");
            } else {
                console.log("Service Worker ya registrado.");
            }
        },

        async recoverFCMToken() {
            try {
                const storedToken = localStorage.getItem("fcm_token");
        
                if (!storedToken) {
                    console.warn("No hay token en localStorage");
                    return null;
                }
        
                const registration = await navigator.serviceWorker.ready;
                const newToken = await this.getFCMToken(registration);
        
                if (newToken && storedToken !== newToken) {
                    localStorage.setItem("fcm_token", newToken);
                    await this.registerFCMToken(newToken, storedToken);
                } else {
                    console.log("Token válido:", storedToken);
                }
            } catch (error) {
                console.error("Error recuperando el token FCM:", error);
            }
        },
        
        denyPermission() {
            localStorage.setItem("onboard", "true");
            this.onboard = true;
        },

        async requestPermission() {
            try {
                const storedToken = localStorage.getItem("fcm_token");
                localStorage.setItem("onboard", "true");
                this.onboard = true;
                
                if (storedToken) {
                    console.log("Token existente:", storedToken);
                    return storedToken;
                }
        
                const permission = await Notification.requestPermission();
                if (permission !== "granted") {
                    console.warn("Permiso de notificación denegado");
                    return null;
                }
        
                const registration = await navigator.serviceWorker.ready;
                const token = await this.getFCMToken(registration);
        
                if (token) {
                    localStorage.setItem("fcm_token", token);
                    await this.registerFCMToken(token);
                }
            } catch (error) {
                console.error("Error al solicitar permisos FCM:", error);
            }
        },
        
        async getFCMToken(registration) {
            try {
                const token = await this.messaging.getToken({
                    vapidKey: "BPsd2S7djGQTrd2IUttk19xkLI4t7fNyeYXZLQKmnhVlkqCWWboHNbnSMx0B-cFc_QDrUqizmVlVC5TnSrLO3Q0",
                    serviceWorkerRegistration: registration
                });
        
                if (!token) {
                    console.warn("No se pudo obtener un token FCM.");
                    return null;
                }
                return token;
            } catch (error) {
                console.error("Error obteniendo token de FCM:", error);
                return null;
            }
        },
        
        async registerFCMToken(token, oldToken=null) {
            try {

                const bodyData = {
                    token: token,
                    user_id: this.auth.id,
                    device_id: this.navigator
                };
        
                if (oldToken !== null) {
                    bodyData.old_token = oldToken;
                }

                await fetch("/api/register_token", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(bodyData)
                });

                console.log("Token FCM registrado en la API.");
            } catch (error) {
                console.error("Error registrando el token en la API:", error);
            }
        },

        listenForMessages() {
            this.messaging.onMessage(payload => {
                console.log("Mensaje recibido:", payload);
                new Notification(payload.notification.title, {
                    body: payload.notification.body,
                    icon: payload.notification.icon || "/static/images/logo1.png"
                });
            });
        },

        initFirebase() {
            if (!firebase.apps.length) {
                firebase.initializeApp(this.firebaseConfig);
                this.messaging = firebase.messaging();
                console.log("Firebase inicializado.");
            }
        },

        setupInstallPrompt() {
            window.addEventListener("beforeinstallprompt", (event) => {
                event.preventDefault();
                this.deferredPrompt = event;
                this.readyToInstall = true;
            });
        },

        setAgent() {
            const userAgent = navigator.userAgent || navigator.vendor || window.opera;
            if (/iPhone|iPad|iPod/i.test(userAgent)) {
                this.navigator = "ios";
            }else if (/Mobi|Android/i.test(userAgent)) {
                this.navigator = "android";
            } else {
                this.navigator = "pc";
            }
            
            if (window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone) {
                this.pwa = true;
            }
        },
        
        initSocket() {
            try {
                this.socket = io("/");
                console.log("Socket inicializado");
                this.socket.on("update_schedule", async () => {
                    if (this.auth.app_level == 4) {
                        await this.getShippingDay();
                    } else {
                        await Promise.all([this.getPendingShippings(), this.getSchedule()]);
                    }
                });
        
                this.socket.on("connect_error", (err) => {
                    console.error("Error en la conexión del socket:", err.message);
                });
        
            } catch (error) {
                console.error("Error inicializando WebSocket:", error);
            }
        },

        async getShippingDay() {
            try {
                const response = await fetch(`/api/shipping/day?offset=${this.offset}`).then(res => res.json());
                this.shippingDay = response.data || { orders: [] };
            } catch (error) {
                console.error('Error fetching schedule', error);
            }
        },
        
        async fetchData() {
            try {
                if (this.auth.app_level == 4) {
                    await this.getShippingDay();
                } else {
                    const [drivers, vendors, districts, shippingMethod] = await Promise.all([
                        fetch('/api/general/drivers').then(res => res.json()),
                        fetch('/api/general/vendors').then(res => res.json()),
                        fetch('/api/general/districts').then(res => res.json()),
                        fetch('/api/general/shipping_types').then(res => res.json())
                    ]);

                    this.drivers = drivers.data || [];
                    this.vendors = vendors.data || [];
                    this.districts = districts.data || [];
                    this.shippingMethod = shippingMethod.data || [];

                    this.process_shipping.driver_id = this.selectFirstOption(this.drivers);
                    await Promise.all([this.getPendingShippings(), this.getSchedule()]);
                }
            } catch (error) {
                console.error('Error fetching data', error);
            }
        },
        
        selectFirstOption(options) {
            return Array.isArray(options) && options.length > 0 ? options[0].id : null;
        },

        async getPendingShippings() {
            try {
                const response = await fetch('/api/order/pending').then(res => res.json());
                this.pendingShippings = response.data || [];
            } catch (error) {
                console.error('Error fetching schedule', error);
            }
        },

        async getShipping(order_number) {
            try {
                const response = await fetch(`/api/order/${order_number}`).then(res => res.json());
                const shipping = response.data || [];

                this.process_shipping = {
                    edit: true,
                    button_text: 'Actualizar',
                    button_complete: 'Entregado',
                    button_rejected: 'No entregado',
                    driver_id: shipping.driver_id,
                    vendor_id: shipping.vendor_id,
                    document: shipping.contacts[0].document,
                    document_id: shipping.contacts[0].document_id,
                    name: shipping.contacts[0].name,
                    email: shipping.contacts[0].email,
                    phone: shipping.contacts[0].phone,
                    order_number: shipping.order_number,
                    method_id: shipping.method_id,
                    method_name: shipping.method_name,
                    method_background: shipping.method_background,
                    method_border: shipping.method_border,
                    address: shipping.address,
                    district_id: shipping.district_id,
                    driver_name: shipping.driver_name,
                    district_name: shipping.district_name,
                    register_date: shipping.register_date_format,
                    on_the_way_date: shipping.on_the_way_date,
                    delivered_date: shipping.delivered_date,
                    not_delivered_date: shipping.not_delivered_date,
                    status_id: shipping.status_id,
                    proof: shipping.proof_photo,
                    maps: shipping.maps,
                };

            } catch (error) {
                console.error('Error fetching schedule', error);
            }
        },

        async getSchedule() {
            try {
                const scheduleRes = await fetch(`/api/order/schedule?offset=${this.offset}`).then(res => res.json());
                this.schedule = scheduleRes.data || [];
                this.scheduleRange = this.getDateRange(this.schedule)
            } catch (error) {
                console.error('Error fetching schedule', error);
            }
        },

        getDateRange(data) {
            const dates = data.map(item => new Date(item.date));
            const startDate = dates[0];
            const endDate = dates[dates.length - 1];

            const getNames = (date) => {
                const months = [
                    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
                ];
                return months[date.getMonth()];
            };

            const startMonth = getNames(startDate);
            const startYear = startDate.getFullYear();
            const endMonth = getNames(endDate);
            const endYear = endDate.getFullYear();

            if (startMonth === endMonth && startYear === endYear) {
                return `${startMonth} ${startYear}`;
            } else {
                return `${startMonth} ${startYear} - ${endMonth} ${endYear}`;
            }
        },

        async today() {
            if (this.offset == 0) {
                return;
            }
            this.offset = 0;
            if (this.auth.app_level == 4) {
                await this.getShippingDay();
            } else {
                await this.getSchedule();
            }
        },

        async next() {
            this.offset++;
            if (this.auth.app_level == 4) {
                await this.getShippingDay();
            } else {
                await this.getSchedule();
            }
        },

        async prev() {
            this.offset--;
            if (this.auth.app_level == 4) {
                await this.getShippingDay();
            } else {
                await this.getSchedule();
            }
        },

        onDragStart(shipping) {
            this.selectedOrder = shipping;
        },

        isFutureOrToday(dateString) {
            if (!dateString) return false;
            const today = new Date();
            today.setHours(0, 0, 0, 0);
        
            const dateParts = dateString.split('-');
            const targetDate = new Date(dateParts[0], dateParts[1] - 1, dateParts[2]);
        
            return targetDate >= today;
        },
        
        onDragOver(event, day=null) {
            event.preventDefault();
            if (day) {
                if (this.isFutureOrToday(day.date)) {
                    event.currentTarget.classList.add('drag-over');
                }
            }
        },
        
        onDragLeave(event) {
            event.currentTarget.classList.remove('drag-over');
        },
        
        async onDrop(day, schedule) {
            document.querySelectorAll('.order-container').forEach(container => {
                container.classList.remove('drag-over');
            });
        
            if (!this.selectedOrder) {
                console.error('No hay orden seleccionada.');
                return;
            }
        
            if (!this.isFutureOrToday(day.date)) {
                console.warn('No se puede soltar en fechas pasadas.');
                return;
            }
        
            if (this.selectedOrder.delivery_date == day.date && this.selectedOrder.schedule == schedule) {
                return;
            }
        
            const payload = {
                order_number: this.selectedOrder.order_number,
                delivery_date: day.date,
                status_id: 2,
                schedule_id: schedule,
                admin_id: this.auth.id
            };
        
            try {
                const response = await fetch('/api/order/set', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });
        
                if (!response.ok) {
                    throw new Error('Error al asignar la orden.');
                }
                
                //await this.updateSchedule();
            } catch (error) {
                console.error('Error en la asignación:', error);
            }
        },

        async onDropPending() {
            if (!this.selectedOrder) {
                console.error('No hay orden seleccionada.');
                return;
            }

            const payload = {
                order_number: this.selectedOrder.order_number,
                delivery_date: null,
                status_id: 1,
                schedule_id: null,
                admin_id: this.auth.id
            };

            try {
                const response = await fetch('/api/order/set', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) {
                    throw new Error('Error al asignar la orden.');
                }

                //await this.updateSchedule();
            } catch (error) {
                console.error('Error en la asignación:', error);
            }
        },

        async fetchUserData() {
            const document = this.process_shipping.document;
            if (!document) {
                this.process_shipping.document_id = '';
                this.process_shipping.email = '';
                this.process_shipping.name = '';
                this.process_shipping.phone = '';
                return;
            }

            try {
                const response = await fetch(`/api/user/${document}`);
                if (!response.ok) {
                    this.process_shipping.document_id = '';
                    this.process_shipping.email = '';
                    this.process_shipping.name = '';
                    this.process_shipping.phone = '';
                    return;
                }

                const data = await response.json();
                if (data.success) {
                    this.process_shipping.document_id = data.data.id;
                    this.process_shipping.email = data.data.email;
                    this.process_shipping.name = data.data.name;
                    this.process_shipping.phone = data.data.phone;
                    //this.process_shipping.disabled = true;
                } else {
                    console.warn('Respuesta de API no exitosa.');
                }
            } catch (error) {
                console.error('Error al obtener datos del usuario:', error);
            }
        },

        async processShipping() {
            const payload = {
                edit: this.process_shipping.edit,
                order_number: this.process_shipping.order_number,
                method_id: this.process_shipping.method_id,
                driver_id: this.process_shipping.driver_id,
                vendor_id: this.process_shipping.vendor_id || null,
                admin_id: this.auth.id,
                address: this.process_shipping.address,
                district_id: this.process_shipping.district_id,
                maps: this.process_shipping.maps,
                register_date: this.process_shipping.register_date,
                client_id: this.process_shipping.document_id,
                client: {
                    document: this.process_shipping.document,
                    email: this.process_shipping.email,
                    name: this.process_shipping.name,
                    phone: this.process_shipping.phone,
                },
                comments: ""
            };

            try {
                const response = await fetch('/api/order/process', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload),
                }).then(res => res.json());


                if (!response.success) {
                    this.process_shipping.button_text = response.data.message;
                    this.process_shipping.button_class = 'error';
                    setTimeout(() => {
                        this.process_shipping.button_text = 'Añadir';
                        this.process_shipping.button_class = '';
                    }, 1500);

                    return;
                }
                
                //await this.updateSchedule();
                this.closeShipping();
                
            } catch (error) {
                this.process_shipping.button_text = 'Error interno';
                this.process_shipping.button_class = 'error';
                setTimeout(() => {
                    this.process_shipping.button_text = 'Añadir';
                    this.process_shipping.button_class = '';
                }, 1500);
            }
        },
    };
}