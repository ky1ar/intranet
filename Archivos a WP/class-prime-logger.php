<?php
/**
 * K3D Prime - Logger
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

class K3D_Prime_Logger {

    public static function log( $message, $level = 'info' ) {
        if ( function_exists( 'wc_get_logger' ) ) {
            $logger  = wc_get_logger();
            $context = array( 'source' => 'k3d-prime' );
            
            switch ( $level ) {
                case 'error':
                    $logger->error( $message, $context );
                    break;
                case 'warning':
                    $logger->warning( $message, $context );
                    break;
                default:
                    $logger->info( $message, $context );
                    break;
            }
        } else {
            error_log( "[K3D Prime] " . $message );
        }
    }
}
