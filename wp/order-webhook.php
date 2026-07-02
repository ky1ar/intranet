<?php
/**
 * Integración de órdenes con la Intranet (devapi.krear3d.com).
 *   1. Al procesar el checkout      -> envía la orden completa  (/wordpress/order-complete)
 *   2. En cada cambio de estado     -> notifica el nuevo estado (/wordpress/order-status)
 *   3. Endpoint REST propio         -> la intranet consulta el estado real bajo demanda
 *      (k3d/v1/order-status), usado por el botón "Actualizar estado web".
 */

if (!defined('ABSPATH')) {
    exit;
}

// Base del endpoint de la intranet.
if (!defined('K3D_API_BASE')) {
    define('K3D_API_BASE');
}
// Secreto compartido. Define K3D_WEBHOOK_SECRET en wp-config.php con el MISMO valor
// que WP_WEBHOOK_SECRET en el backend. Si queda vacío, no se envía/valida cabecera.
if (!defined('K3D_WEBHOOK_SECRET')) {
    define('K3D_WEBHOOK_SECRET');
}

/**
 * POST helper hacia la intranet. No bloquea el checkout (blocking=false).
 */
function k3d_post_to_api($path, $payload)
{
    $headers = array(
        'Content-Type' => 'application/json',
        'Accept'       => 'application/json',
    );
    if (K3D_WEBHOOK_SECRET !== '') {
        $headers['X-K3D-Secret'] = K3D_WEBHOOK_SECRET;
    }

    wp_remote_post(K3D_API_BASE . $path, array(
        'body'        => wp_json_encode($payload),
        'timeout'     => 15,
        'redirection' => 5,
        'httpversion' => '1.0',
        'blocking'    => false,
        'headers'     => $headers,
    ));
}

// ─────────────────────────────────────────────────────────────
// 1. Envío de la orden completa al terminar el checkout
// ─────────────────────────────────────────────────────────────
add_action('woocommerce_checkout_order_processed', 'k3d_send_order_to_devapi', 20, 3);

function k3d_send_order_to_devapi($order_id, $posted_data, $order)
{
    if (!$order_id) {
        return;
    }

    // 1. Recopilar la información básica de la orden
    $order_data = array(
        'order_id' => $order->get_id(),
        'order_number' => $order->get_order_number(),
        'status' => $order->get_status(),
        'total' => $order->get_total(),
        'currency' => $order->get_currency(),
        'payment_method' => $order->get_payment_method(), // ID interno (ej: 'bacs', 'culqi')
        'payment_method_title' => $order->get_payment_method_title(), // Texto legible (ej: 'Transferencia Bancaria', 'Yape')
        'date_created' => $order->get_date_created() ? $order->get_date_created()->date('Y-m-d H:i:s') : '',
        'customer_ip' => $order->get_customer_ip_address(),
    );

    // 2. Información del Cliente
    $customer_data = array(
        'first_name' => $order->get_billing_first_name(),
        'last_name' => $order->get_billing_last_name(),
        'email' => $order->get_billing_email(),
        'phone' => $order->get_billing_phone(),
        'dni_ruc' => $order->get_meta('_billing_dni') ? $order->get_meta('_billing_dni') : $order->get_meta('billing_dni'),
    );

    // 3. Dirección y Ubigeo
    $address_data = array(
        'address_1' => $order->get_billing_address_1(),
        'address_2' => $order->get_billing_address_2(),
        'departamento' => $order->get_billing_state(),
        'provincia' => $order->get_billing_city(),
        'distrito' => $order->get_billing_address_2() ? $order->get_billing_address_2() : $order->get_meta('billing_district'),
        // Capturamos las metas exactas en caso el plugin de ubigeo use otras keys
        'meta_departamento' => $order->get_meta('_billing_departamento') ?: $order->get_meta('billing_departamento'),
        'meta_provincia' => $order->get_meta('_billing_provincia') ?: $order->get_meta('billing_provincia'),
        'meta_distrito' => $order->get_meta('_billing_distrito') ?: $order->get_meta('billing_distrito'),
    );

    // 4. Información de Atención (El Vendedor Asignado)
    $vendedor_codigo = $order->get_meta('_k3d_vendedor');
    $vendedor_id = null;

    if ($vendedor_codigo && function_exists('k3d_get_vendedores_info')) {
        $vendedores_info = k3d_get_vendedores_info();
        if (isset($vendedores_info[$vendedor_codigo]['id'])) {
            $vendedor_id = $vendedores_info[$vendedor_codigo]['id'];
        }
    }

    $atencion_data = array(
        'ejecutivo_ayuda' => $order->get_meta('_k3d_ejecutivo_ayuda'), // 'si' o 'no'
        'vendedor_codigo' => $vendedor_codigo,
        'vendedor_id'     => $vendedor_id,
        'vendedor_nombre' => $order->get_meta('_k3d_vendedor_nombre'),
        'vendedor_email'  => $order->get_meta('_k3d_vendedor_email'),
    );

    // 5. Productos comprados
    $items_data = array();
    foreach ($order->get_items() as $item_id => $item) {
        $items_data[] = array(
            'product_id' => $item->get_product_id(),
            'name' => $item->get_name(),
            'quantity' => $item->get_quantity(),
            'subtotal' => $item->get_subtotal(),
            'total' => $item->get_total(),
        );
    }

    // 6. Empaquetar todo el JSON
    $payload = array(
        'order' => $order_data,
        'customer' => $customer_data,
        'address' => $address_data,
        'atencion' => $atencion_data,
        'items' => $items_data
    );

    // 7. Enviar al endpoint de la intranet
    k3d_post_to_api('/wordpress/order-complete', $payload);
}

// ─────────────────────────────────────────────────────────────
// 2. Notificar cada cambio de estado del pedido a la intranet
// ─────────────────────────────────────────────────────────────
add_action('woocommerce_order_status_changed', 'k3d_notify_status_change', 20, 4);

function k3d_notify_status_change($order_id, $old_status, $new_status, $order)
{
    if (!$order_id) {
        return;
    }
    k3d_post_to_api('/wordpress/order-status', array(
        'order_id'     => $order->get_id(),
        'order_number' => $order->get_order_number(),
        'status'       => $new_status, // slug sin prefijo 'wc-' (p.ej. 'processing')
    ));
}

// ─────────────────────────────────────────────────────────────
// 3. Endpoint REST para consultar el estado real bajo demanda
// ─────────────────────────────────────────────────────────────
add_action('rest_api_init', function () {
    register_rest_route('k3d/v1', '/order-status/(?P<id>\d+)', array(
        'methods'             => 'GET',
        'callback'            => 'k3d_rest_get_order_status',
        'permission_callback' => 'k3d_rest_check_secret',
        'args'                => array(
            'id' => array(
                'validate_callback' => function ($param) {
                    return is_numeric($param);
                },
            ),
        ),
    ));
});

function k3d_rest_check_secret(WP_REST_Request $request)
{
    // Si no hay secreto configurado, se permite (mismo criterio que el backend).
    if (K3D_WEBHOOK_SECRET === '') {
        return true;
    }
    return hash_equals(K3D_WEBHOOK_SECRET, (string) $request->get_header('X-K3D-Secret'));
}

function k3d_rest_get_order_status(WP_REST_Request $request)
{
    $order = wc_get_order((int) $request['id']);
    if (!$order) {
        return new WP_Error('not_found', 'Pedido no encontrado', array('status' => 404));
    }
    return array(
        'order_id'     => $order->get_id(),
        'order_number' => $order->get_order_number(),
        'status'       => $order->get_status(), // sin prefijo 'wc-'
    );
}
