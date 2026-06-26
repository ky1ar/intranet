const firebaseConfig = {
    apiKey: "AIzaSyDzSedMzfKT5L2LklmUQsMyvPEGfZ_0fcw",
    authDomain: "krear3d-f9195.firebaseapp.com",
    projectId: "krear3d-f9195",
    storageBucket: "krear3d-f9195.firebasestorage.app",
    messagingSenderId: "291592879896",
    appId: "1:291592879896:web:674af68c5c7d1fe440a86d",
};

firebase.initializeApp(firebaseConfig);
window.messaging = firebase.messaging();

window.messaging.onMessage((payload) => {
    console.log('[FCM] Mensaje en foreground:', payload);

    const title = payload.notification?.title || 'Krear 3D';
    const options = {
        body: payload.notification?.body || '',
        icon: '/static/images/logo-512a.png',
        data: payload.data || {},
    };

    if (Notification.permission === 'granted') {
        const notification = new Notification(title, options);
        notification.onclick = (e) => {
            e.preventDefault();
            window.focus();
            const url = payload.data?.url;
            if (url && window.PineconeRouter) window.PineconeRouter.context.navigate(url);
            notification.close();
        };
    }
});
