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
            document: '',
            password: '',
            id: null,
            level: null,
            name: '',
            role: '',
            image: '',
            default_image: 'static/images/users/default.jpg',
            token: null,
        },

        loginButton: {
            class: '',
            text: 'Iniciar Sesión',
        },

        page: {
            current: 'calendar'
        },

        pages: [
            { name: 'calendar', label: 'Calendario' },
            { name: 'history', label: 'Historial' },
            { name: 'clients', label: 'Clientes' },
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

        async checkImage(document) {
            const url = `static/images/users/${document}.jpg`;
            const response = await fetch(url, { method: 'GET' });
            this.auth.image = response.ok ? url : this.auth.default_image;
        },

        async login() {
            const payload = { document: this.auth.document, password: this.auth.password }
            try {
                const response = await fetch('/api/user/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload),
                });
                
                const jsonData = await response.json();
                if (!response.ok) {
                    if (response.status === 400) {
                        this.loginButton.text = jsonData.data.message;
                        this.loginButton.class = 'error';
                        setTimeout(() => {
                            this.loginButton.text = 'Iniciar Sesión';
                            this.loginButton.class = '';
                        }, 1500);
                    }
                    return false;
                }
                const userData = jsonData.data;
                
                await this.checkImage(userData.document);
                this.auth.token = userData.token;
                this.auth.id = userData.id;
                this.auth.level = userData.levels;
                this.auth.name = userData.name;
                this.auth.role = userData.role;

                //console.log(this.auth)
                localStorage.setItem('user_data', JSON.stringify(this.auth));
                await this.fetchData();

            } catch (e) {
                console.error('Error during login verification:', e.message);
            }
        },  

        logout() {
            this.auth.token = null;
            this.auth.id = null;
            this.auth.level = null;
            this.auth.name = '';
            this.auth.role = '';
            this.auth.image = '';
            this.offset = 0;
            localStorage.removeItem('user_data'); 
        },

        async loginVerify() {
            const storedData = localStorage.getItem('user_data');
            if (storedData) {
                const userData = JSON.parse(storedData);
                this.auth.token = userData.token;
                this.auth.id = userData.id;
                this.auth.level = userData.level;
                this.auth.name = userData.name;
                this.auth.role = userData.role;
                this.auth.image = userData.image;

                const response = await fetch('/api/user/verify', {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${userData.token}`,
                        'Content-Type': 'application/json',
                    },
                });

                if (!response.ok) {
                    this.logout();
                    throw new Error('Sesión expirada');
                }   
                
            } else {
                throw new Error('No ha inicado sesión');
            }
        },

        async init() {
            try {
                this.initSocket();
                await this.loginVerify();
                await this.fetchData();

            } catch (error) {
                console.error('Error al iniciar la aplicación:', error.message);
            } 
        },

        initSocket() {
            try {
                this.socket = io("/");
        
                this.socket.on("update_schedule", async () => {
                    if (this.auth.level === 3 || this.auth.level === 4) {
                        await Promise.all([this.getPendingShippings(), this.getSchedule()]);
                    } else {
                        await this.getShippingDay();
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
                if (this.auth.level === 3 || this.auth.level === 4) {
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
                } else {
                    await this.getShippingDay();
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
            if (this.auth.level === 3 || this.auth.level === 4) {
                await this.getSchedule();
            } else {
                await this.getShippingDay();
            }
        },

        async next() {
            this.offset++;
            if (this.auth.level === 3 || this.auth.level === 4) {
                await this.getSchedule();
            } else {
                await this.getShippingDay();
            }
        },

        async prev() {
            this.offset--;
            if (this.auth.level === 3 || this.auth.level === 4) {
                await this.getSchedule();
            } else {
                await this.getShippingDay();
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