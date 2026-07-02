<?php
/**
 * Envío de órdenes a Endpoint Externo (Webhook)
 * Se ejecuta justo cuando se procesa la orden en el checkout.
 */

if (!defined('ABSPATH')) {
    exit;
}

// Usamos woocommerce_checkout_order_processed que se dispara al terminar el proceso de checkout
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

    // 7. Enviar la petición HTTP POST al Endpoint
    // Ruta indicada por el equipo de backend
    $endpoint_url = 'https://devapi.krear3d.com/wordpress/order-complete';

    $args = array(
        'body' => wp_json_encode($payload),
        'timeout' => 15,
        'redirection' => 5,
        'httpversion' => '1.0',
        'blocking' => false, // Para que el checkout no se quede congelado esperando respuesta
        'headers' => array(
            'Content-Type' => 'application/json',
            'Accept' => 'application/json',
        ),
    );

    wp_remote_post($endpoint_url, $args);
}
