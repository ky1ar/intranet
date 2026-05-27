document.addEventListener('alpine:init', () => {
    Alpine.data('data',() => ({
        init() {
            console.log('Inicializando Alpine...');
        },
    }));

    Alpine.store('cache', {
        api: 'https://devapi.krear3d.com', //https://api.krear3d.com
    });
});

async function refundTokenVerify({ params }) {
    console.log('Verificando token de extorno...');
    const token = params.token;

    NProgress.start();
    try {
        const response = await fetch(`${Alpine.store('cache').api}/refund/link_verify`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token }),
        });

        if (!response.ok) {
            window.PineconeRouter.context.navigate("/");
            return;
        }

        Alpine.store('cache').refund_token = token;
    } catch (error) {
        console.error(error);
        window.PineconeRouter.context.navigate("/");
    } finally {
        NProgress.done();
    }
}

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