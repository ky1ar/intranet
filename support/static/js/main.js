document.addEventListener('alpine:init', () => {
    Alpine.store('router', {
        active: window.location.pathname,
        setActive(path) {
            this.active = path;
        }
    });

    Alpine.data('data',() => ({
        test: "HOLA",
        init() {
            console.log('init')
        }
    }));

    //Alpine.data('router', data);
    /*
    window.PineconeRouter.add('/prog-template', {
        templates: ['/views/capacitaciones.html', '/views/consultas.html'],
        templateTargetId: 'app',
        preload: true,
    });*/
    
    window.PineconeRouter.settings.alwaysSendLoadingEvents = true;
});

document.addEventListener('pinecone-start', () => {
    NProgress.start();
});

document.addEventListener('pinecone-end', () => {
    //console.log(Alpine.store('router').active)
    Alpine.store('router').setActive(window.location.pathname);
    //this.active = window.location.pathname;
    NProgress.done();
});

document.addEventListener('fetch-error', (err) =>
    console.error(err)
);