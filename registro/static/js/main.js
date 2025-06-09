document.addEventListener('alpine:init', () => {
    Alpine.data('data',() => ({
        init() {
            console.log('Inicializando Alpine...');
        },
    }));

    Alpine.store('cache', {
        api: 'https://api.krear3d.com',
    });
});

async function tokenVerify({ params }) {
    console.log('Verificando Token...');
    const token = params.token;

    NProgress.start();
    const payload = {
        token: token,
    }
    try {
        const response = await fetch(`${Alpine.store('cache').api}/support/link_token`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        
        if (!response.ok) window.PineconeRouter.context.navigate("/");

        Alpine.store('cache').token = token;
        history.replaceState(null, '', '/');

    } catch (error) {
        console.error(error)
    } finally {
        NProgress.done();
    }
}