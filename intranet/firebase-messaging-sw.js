// Importar Firebase
importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-messaging-compat.js');

const firebaseConfig = {
    apiKey: "AIzaSyDzSedMzfKT5L2LklmUQsMyvPEGfZ_0fcw",
    authDomain: "krear3d-f9195.firebaseapp.com",
    projectId: "krear3d-f9195",
    storageBucket: "krear3d-f9195.firebasestorage.app",
    messagingSenderId: "291592879896",
    appId: "1:291592879896:web:674af68c5c7d1fe440a86d",
};

firebase.initializeApp(firebaseConfig);
const messaging = firebase.messaging();

messaging.onBackgroundMessage((payload) => {
    console.log('[SW] Background message', payload);
    if (payload.notification) {
        return;
    }

    const notificationTitle = payload.data?.title || 'Krear 3D';
    const notificationOptions = {
        body: payload.data?.body || '',
        icon: '/static/images/single-logo.svg',
        data: payload.data || {},
    };

    self.registration.showNotification(notificationTitle, notificationOptions);
});

self.addEventListener('notificationclick', (event) => {
    event.notification.close();
    const url = event.notification.data?.url || '/';
    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
            const client = clientList.find(c => c.url.includes(self.location.origin));
            if (client) {
                client.focus();
                client.postMessage({ type: 'NAVIGATE', url });
                return;
            }
            return clients.openWindow(url);
        })
    );
});