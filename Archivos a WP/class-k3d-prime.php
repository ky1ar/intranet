<?php
/**
 * K3D Prime - Módulo principal de integración con Culqi
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit; // Exit if accessed directly.
}

class K3D_Prime {

    /**
     * Instancia única de la clase.
     */
    private static $instance = null;

    /**
     * Obtener instancia.
     */
    public static function get_instance() {
        if ( null === self::$instance ) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    /**
     * Constructor.
     */
    private function __construct() {
        $this->includes();
        $this->init_hooks();
    }

    /**
     * Incluir archivos necesarios.
     */
    private function includes() {
        require_once dirname( __FILE__ ) . '/class-prime-logger.php';
        require_once dirname( __FILE__ ) . '/class-prime-discounts.php';
    }

    /**
     * Inicializar hooks principales.
     */
    private function init_hooks() {
        // Init classes
        K3D_Prime_Discounts::init();
    }
}

// Inicializar módulo
K3D_Prime::get_instance();
