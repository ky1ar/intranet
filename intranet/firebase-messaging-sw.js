// Importar Firebase
importScripts("https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/10.7.1/firebase-messaging-compat.js");

// Configuración de Firebase (usa la misma que en tu frontend)
firebase.initializeApp({
    apiKey: "AIzaSyDzSedMzfKT5L2LklmUQsMyvPEGfZ_0fcw",
    authDomain: "krear3d-f9195.firebaseapp.com",
    projectId: "krear3d-f9195",
    storageBucket: "krear3d-f9195.firebasestorage.app",
    messagingSenderId: "291592879896",
    appId: "1:291592879896:web:674af68c5c7d1fe440a86d",
    measurementId: "G-2CCET399W9"
});

// Inicializar Firebase Messaging
const messaging = firebase.messaging();

// Manejar notificaciones en segundo plano
messaging.onBackgroundMessage(payload => {
    console.log("Mensaje recibido en segundo plano:", payload);

    if (payload.data) {
        self.registration.showNotification(payload.data.title, {
            body: payload.data.body,
            icon: payload.data.icon || "/static/images/logo1.png"
        });
    }
    /*self.registration.showNotification(payload.notification.title, {
        body: payload.notification.body,
        icon: payload.notification.icon || "/static/images/logo1.png"
    });*/
});

self.addEventListener("activate", event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    console.log("Borrando caché antigua:", cacheName);
                    return caches.delete(cacheName);
                })
            );
        }).then(() => {
            return self.clients.claim();
        })
    );
});