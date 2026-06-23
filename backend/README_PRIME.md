# Documentación Técnica: Integración Krear 3D Prime

Este documento sirve como guía para el equipo de backend sobre la nueva arquitectura del módulo **Krear 3D Prime**. 
**¿Por qué se hizo esto?** Originalmente, el sistema Prime vivía 100% dentro de WordPress. Sin embargo, para tener un control más robusto, centralizado y evitar que WordPress maneje cobros y lógica pesada, la fuente de la verdad se ha migrado hacia la Intranet (Flask). Esto centraliza el control de suscripciones, estados y correos electrónicos en un sistema dedicado.

A continuación, se detallan **todos los archivos** involucrados en esta integración y su responsabilidad exacta dentro del sistema.

---

## 1. BACKEND (Intranet / Flask)
*¿Por qué se crearon? Para convertir a la Intranet en el "Cerebro" de las suscripciones, recibiendo la data de Culqi directamente y guardándola de forma segura.*

*   **`d:\K3D PROJECTS\K3D Intranet y Tienda\intranet\backend\application\db_models\prime_model.py`**
    *   **¿Por qué se creó?** Para tener un registro independiente y central de quién es Prime, sin depender de los `user_meta` de WordPress.
    *   **¿Qué hará?** Definir la estructura de la nueva tabla `prime_subscriptions` (con `email`, `plan_type`, `status` y fechas). *Nota: Requiere ejecutar migraciones para crear la tabla físicamente.*

*   **`d:\K3D PROJECTS\K3D Intranet y Tienda\intranet\backend\application\repository\prime_repository.py`**
    *   **¿Por qué se creó?** Para mantener limpio el código y aplicar el patrón "Repository" que ya usa la Intranet.
    *   **¿Qué hará?** Ejecutar las operaciones directas a la base de datos (guardar nuevos suscriptores, actualizar estados, o buscar por email).

*   **`d:\K3D PROJECTS\K3D Intranet y Tienda\intranet\backend\application\services\prime_service.py`**
    *   **¿Por qué se creó?** Para aislar la lógica compleja de negocio y que no se ensucie el controlador.
    *   **¿Qué hará?** Traducir los datos crudos que manda Culqi (como los UUIDs `pln_live_...`), decidir si es un plan *lite* o *full*, guardar la información y **disparar el envío automático de correos**.

*   **`d:\K3D PROJECTS\K3D Intranet y Tienda\intranet\backend\application\controllers\prime_controller.py`**
    *   **¿Por qué se creó?** Para interceptar las llamadas HTTP que llegan desde fuera (Culqi y WordPress).
    *   **¿Qué hará?** Extraer el JSON o los parámetros de la URL, validarlos mínimamente, pasarlos al *Service* y responder con códigos HTTP (200 OK, 400 Error).

*   **`d:\K3D PROJECTS\K3D Intranet y Tienda\intranet\backend\application\routes\prime_routes.py`**
    *   **¿Por qué se creó?** Para exponer públicamente las nuevas funciones del *Controller* bajo una ruta específica (`/api/prime/...`).
    *   **¿Qué hará?** Escuchar en `/webhook` (para Culqi), en `/verify` (para WooCommerce) y en `/list` (para el frontend de la intranet).

*   **`d:\K3D PROJECTS\K3D Intranet y Tienda\intranet\backend\application\__init__.py`**
    *   **¿Por qué se tocó?** Para decirle al núcleo de Flask que el nuevo Blueprint de rutas (creado arriba) existe y debe encenderse.

*   **`d:\K3D PROJECTS\K3D Intranet y Tienda\intranet\backend\application\templates\prime_welcome.html`** y **`prime_cancelled.html`**
    *   **¿Por qué se crearon?** Porque ahora Flask envía los correos, por lo que necesitaba sus propias plantillas HTML.
    *   **¿Qué harán?** Dar el estilo visual a los correos automáticos de bienvenida y despedida.

---

## 2. FRONTEND (Intranet / Alpine.js)
*¿Por qué se crearon? Para que el área administrativa tenga un panel de control donde pueda auditar quién tiene Prime activo sin tener que entrar a la base de datos.*

*   **`d:\K3D PROJECTS\K3D Intranet y Tienda\intranet\intranet\views\prime.html`**
    *   **¿Por qué se creó?** Para construir la interfaz de usuario.
    *   **¿Qué hará?** Mostrar una tabla dinámica que consume el endpoint `/api/prime/list`, permitiendo filtrar a los usuarios por Plan o Estado.

*   **`d:\K3D PROJECTS\K3D Intranet y Tienda\intranet\intranet\static\js\main.js`**
    *   **¿Por qué se tocó?** Para inyectar el módulo "Prime" en el diseño actual de la intranet.
    *   **¿Qué hará?** Agregar la opción de "Prime" (con su respectivo ícono) al menú lateral izquierdo.

*   **`d:\K3D PROJECTS\K3D Intranet y Tienda\intranet\intranet\index.html`**
    *   **¿Por qué se tocó?** Para agregar la nueva ruta al enrutador SPA (`PineconeRouter`).
    *   **¿Qué hará?** Asegurar que cuando el administrador haga clic en el menú Prime, cargue el archivo `prime.html` sin recargar la página.

---

## 3. WOOCOMMERCE (Tienda Krear 3D) - (REFACTORIZACIÓN NUEVA)
*¿Por qué se modificaron? WordPress ya no administra las cuentas ni recibe webhooks de Culqi. Ahora, estos archivos se comportan como simples "clientes" de la API de la Intranet.*

*   **`(MODIFICADO A NUEVO) d:\K3D PROJECTS\K3D Intranet y Tienda\Stag.Tienda Krear 3D\wp-content\themes\k3d\functions.php` (Líneas 1496-1499)**
    *   **¿Por qué se tocó?** Sigue siendo la puerta de entrada. 
    *   **¿Qué hará?** Cargar el módulo inicializador (`class-k3d-prime.php`) cuando WooCommerce arranca.

*   **`(MODIFICADO A NUEVO) d:\K3D PROJECTS\K3D Intranet y Tienda\Stag.Tienda Krear 3D\wp-content\themes\k3d\inc\k3d-prime\class-k3d-prime.php`**
    *   **¿Por qué se tocó?** Porque antes cargaba 4 archivos (descuentos, logger, usuarios y webhooks) y ahora los de webhooks y usuarios se eliminaron (al mudarse a Flask).
    *   **¿Qué hará?** Simplemente registrar e inicializar las dos clases que sobrevivieron: Descuentos y Logger.

*   **`(MODIFICADO A NUEVO) d:\K3D PROJECTS\K3D Intranet y Tienda\Stag.Tienda Krear 3D\wp-content\themes\k3d\inc\k3d-prime\class-prime-discounts.php`**
    *   **¿Por qué se tocó?** Este es el cambio fundamental. Antes, WooCommerce leía su propia base de datos (`user_meta`) para saber si alguien era Prime.
    *   **¿Qué hará ahora?** Cuando un usuario vaya al carrito, el código extraerá su correo y hará una **petición HTTP (`wp_remote_get`) a la Intranet (`/api/prime/verify`)**. Para evitar poner lento el carrito de compras, guardará la respuesta de la Intranet en la memoria caché (Transients) por 15 minutos y procederá a descontar el % correspondiente.

*   **`(MODIFICADO A NUEVO) d:\K3D PROJECTS\K3D Intranet y Tienda\Stag.Tienda Krear 3D\wp-content\themes\k3d\inc\k3d-prime\class-prime-logger.php`**
    *   **¿Por qué se dejó?** Es una utilidad valiosa para soporte técnico.
    *   **¿Qué hará?** Si falla la conexión entre WooCommerce y la Intranet, este archivo permite escribir un mensaje silencioso en una carpeta de logs (`wp-content/uploads/k3d-prime-logs/`) para que los desarrolladores puedan diagnosticar el problema sin mostrar errores al cliente.
