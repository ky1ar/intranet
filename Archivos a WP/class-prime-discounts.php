<?php
/**
 * K3D Prime - Motor de Descuentos
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

class K3D_Prime_Discounts {

    // Reglas de Categorías y Porcentajes
    private static $category_discounts = [
        'filamentos' => 0.10, // 10%
        'resinas'    => 0.10, // 10%
        'repuestos'  => 0.05, // 5%
        'upgrades'   => 0.05  // 5%
    ];

    // Marcas Autorizadas según el Plan
    private static $brands_lite = [ 'k3d', 'krear-3d' ];
    private static $brands_full = [
        'k3d', 'krear-3d', 'anycubic', 'bambu-lab', 
        'creality', 'elegoo', 'esun', 'panchroma', 
        'phrozen', 'polymaker', 'sunlu'
    ];

    public static function init() {
        add_action( 'woocommerce_cart_calculate_fees', [ __CLASS__, 'apply_prime_discount' ], 20, 1 );
    }

    public static function apply_prime_discount( $cart ) {
        if ( is_admin() && ! defined( 'DOING_AJAX' ) ) return;

        // 1. Validar si el usuario está logueado
        if ( ! is_user_logged_in() ) return;

        $user = wp_get_current_user();
        if ( ! $user || empty( $user->user_email ) ) return;

        // 2. Consultar a la API de la Intranet si el usuario es Prime
        $prime_data = self::get_prime_status_from_api( $user->user_email );

        if ( ! $prime_data || empty( $prime_data['is_prime'] ) || $prime_data['is_prime'] !== true ) {
            return; // No es prime
        }

        $plan = $prime_data['plan_type']; // 'lite' o 'full'
        if ( ! in_array( $plan, [ 'lite', 'full' ] ) ) return;

        // 3. Validar restricción "No Acumulable" (Si hay cupones, no aplicar Prime)
        if ( ! empty( $cart->get_applied_coupons() ) ) {
            // Ya hay cupones, el descuento Prime no es acumulable.
            return;
        }

        $total_discount = 0;
        $allowed_brands = ( $plan === 'lite' ) ? self::$brands_lite : self::$brands_full;

        // 4. Iterar sobre los productos del carrito
        foreach ( $cart->get_cart() as $cart_item_key => $cart_item ) {
            $product_id = $cart_item['product_id'];
            $product    = $cart_item['data'];

            if ( ! $product ) continue;

            $product_price = $product->get_price();
            $quantity      = $cart_item['quantity'];
            $line_total    = $product_price * $quantity;

            // Verificar Categorías
            $applicable_percentage = 0;
            $terms_cats = get_the_terms( $product_id, 'product_cat' );
            if ( $terms_cats && ! is_wp_error( $terms_cats ) ) {
                foreach ( $terms_cats as $term ) {
                    if ( isset( self::$category_discounts[ $term->slug ] ) ) {
                        $applicable_percentage = self::$category_discounts[ $term->slug ];
                        break;
                    }
                }
            }

            // Si no pertenece a las categorías con descuento, saltar.
            if ( $applicable_percentage == 0 ) continue;

            // Verificar Marca (Taxonomía: pwb-brand)
            $has_valid_brand = false;
            $terms_brands = get_the_terms( $product_id, 'pwb-brand' );
            if ( $terms_brands && ! is_wp_error( $terms_brands ) ) {
                foreach ( $terms_brands as $term ) {
                    if ( in_array( strtolower( $term->slug ), $allowed_brands ) ) {
                        $has_valid_brand = true;
                        break;
                    }
                }
            }

            // Si no tiene la marca requerida por su plan, saltar.
            if ( ! $has_valid_brand ) continue;

            // Calcular el descuento para este ítem
            $item_discount = $line_total * $applicable_percentage;
            $total_discount += $item_discount;
        }

        // 5. Aplicar la tarifa negativa (Descuento)
        if ( $total_discount > 0 ) {
            $plan_label = ucfirst( $plan );
            $cart->add_fee( "Descuento Prime {$plan_label}", -$total_discount, true );
        }
    }

    /**
     * Consulta a la Intranet para saber si el correo tiene una suscripción Prime activa.
     * Utiliza Transients para cachear la respuesta por 15 minutos y no saturar la red en cada carga de carrito.
     */
    private static function get_prime_status_from_api( $email ) {
        $transient_key = 'k3d_prime_status_' . md5( $email );
        $cached_status = get_transient( $transient_key );

        if ( false !== $cached_status ) {
            return $cached_status;
        }

        // TODO: Definir la URL real de la Intranet en wp-config.php o aquí. 
        // Por ahora usamos una variable de entorno o un fallback local.
        $api_base = defined('K3D_INTRANET_API_URL') ? K3D_INTRANET_API_URL : 'https://intranet.krear3d.com/api';
        $url = $api_base . '/prime/verify?email=' . urlencode( $email );

        $response = wp_remote_get( $url, [
            'timeout' => 5,
        ] );

        if ( is_wp_error( $response ) || wp_remote_retrieve_response_code( $response ) !== 200 ) {
            return false;
        }

        $body = wp_remote_retrieve_body( $response );
        $data = json_decode( $body, true );

        if ( is_array( $data ) ) {
            // Cacheamos la respuesta por 15 minutos (900 segundos)
            set_transient( $transient_key, $data, 15 * MINUTE_IN_SECONDS );
            return $data;
        }

        return false;
    }
}
