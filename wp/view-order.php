<?php
/**
 * View Order (My Account) — plantilla personalizada Krear 3D.
 * Override de woocommerce/myaccount/view-order.php
 */
defined( 'ABSPATH' ) || exit;

if ( empty( $order_id ) ) {
	$order_id = absint( get_query_var( 'view-order' ) );
}
$order = wc_get_order( $order_id );
if ( ! $order ) {
	echo '<p>' . esc_html__( 'Invalid order.', 'woocommerce' ) . '</p>';
	return;
}

$kd_slug  = $order->get_status();
$kd_icons = array(
	'bag'     => '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>',
	'check'   => '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="8 12 11 15 16 9"/></svg>',
	'clock'   => '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 7 12 12 15 14"/></svg>',
	'x'       => '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
	'refresh' => '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/></svg>',
	'phone'   => '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>',
	'mail'    => '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><polyline points="22,6 12,13 2,6"/></svg>',
);
$kd_smeta = array(
	'completed'  => array( 'check',   'kd-st-completed' ),
	'processing' => array( 'refresh', 'kd-st-processing' ),
	'on-hold'    => array( 'clock',   'kd-st-hold' ),
	'pending'    => array( 'clock',   'kd-st-hold' ),
	'cancelled'  => array( 'x',       'kd-st-cancelled' ),
	'failed'     => array( 'x',       'kd-st-cancelled' ),
	'refunded'   => array( 'refresh', 'kd-st-refunded' ),
);
$kd_m = isset( $kd_smeta[ $kd_slug ] ) ? $kd_smeta[ $kd_slug ] : array( 'clock', 'kd-st-hold' );
?>

<div class="kd-order-view">

	<div class="kd-ov-head">
		<div class="kd-ov-head-l">
			<span class="kd-ov-ico"><?php echo $kd_icons['bag']; ?></span>
			<div>
				<h2>Pedido #<?php echo esc_html( $order->get_order_number() ); ?></h2>
				<span class="kd-ov-date">Realizado el <?php echo esc_html( wc_format_datetime( $order->get_date_created(), 'j \d\e F \d\e Y' ) ); ?></span>
			</div>
		</div>
		<span class="kd-order-status <?php echo esc_attr( $kd_m[1] ); ?>"><?php echo $kd_icons[ $kd_m[0] ]; ?><span><?php echo esc_html( wc_get_order_status_name( $kd_slug ) ); ?></span></span>
	</div>

	<?php if ( $order->needs_payment() ) : ?>
		<a href="<?php echo esc_url( $order->get_checkout_payment_url() ); ?>" class="button kd-ov-pay">Pagar pedido</a>
	<?php endif; ?>

	<div class="kd-ov-card">
		<div class="kd-ov-card-title">Productos</div>
		<div class="kd-ov-items">
			<?php foreach ( $order->get_items() as $item_id => $item ) :
				$product = $item->get_product();
				$thumb   = $product ? $product->get_image( array( 64, 64 ) ) : '';
				$link    = ( $product && $product->is_visible() ) ? $product->get_permalink() : '';
			?>
				<div class="kd-ov-item">
					<div class="kd-ov-item-img"><?php echo $thumb; ?></div>
					<div class="kd-ov-item-info">
						<span class="kd-ov-item-name">
							<?php if ( $link ) : ?>
								<a href="<?php echo esc_url( $link ); ?>" target="_blank" rel="noopener"><?php echo esc_html( $item->get_name() ); ?></a>
							<?php else : echo esc_html( $item->get_name() ); endif; ?>
						</span>
						<span class="kd-ov-item-qty">Cantidad: <?php echo esc_html( $item->get_quantity() ); ?></span>
					</div>
					<span class="kd-ov-item-total"><?php echo wp_kses_post( $order->get_formatted_line_subtotal( $item ) ); ?></span>
				</div>
			<?php endforeach; ?>
		</div>

		<div class="kd-ov-totals">
			<?php foreach ( $order->get_order_item_totals() as $kd_key => $kd_total ) : ?>
				<div class="kd-ov-total-row <?php echo ( 'order_total' === $kd_key ) ? 'is-total' : ''; ?>">
					<span><?php echo wp_kses_post( $kd_total['label'] ); ?></span>
					<span><?php echo wp_kses_post( $kd_total['value'] ); ?></span>
				</div>
			<?php endforeach; ?>
		</div>
	</div>

	<?php $kd_note = $order->get_customer_note(); if ( $kd_note ) : ?>
		<div class="kd-ov-card">
			<div class="kd-ov-card-title">Nota del pedido</div>
			<p class="kd-ov-note"><?php echo nl2br( esc_html( $kd_note ) ); ?></p>
		</div>
	<?php endif; ?>

	<div class="kd-ov-addresses">
		<?php $kd_bill = $order->get_formatted_billing_address(); if ( $kd_bill ) : ?>
			<div class="kd-ov-card">
				<div class="kd-ov-card-title">Dirección de facturación</div>
				<address><?php echo wp_kses_post( $kd_bill ); ?></address>
				<?php if ( $order->get_billing_phone() ) : ?>
					<p class="kd-ov-contact"><?php echo $kd_icons['phone']; ?> <span><?php echo esc_html( $order->get_billing_phone() ); ?></span></p>
				<?php endif; ?>
				<?php if ( $order->get_billing_email() ) : ?>
					<p class="kd-ov-contact"><?php echo $kd_icons['mail']; ?> <span><?php echo esc_html( $order->get_billing_email() ); ?></span></p>
				<?php endif; ?>
			</div>
		<?php endif; ?>

		<?php $kd_ship = $order->get_formatted_shipping_address(); if ( $order->needs_shipping_address() && $kd_ship ) : ?>
			<div class="kd-ov-card">
				<div class="kd-ov-card-title">Dirección de envío</div>
				<address><?php echo wp_kses_post( $kd_ship ); ?></address>
			</div>
		<?php endif; ?>
	</div>

	<?php
	// Evita la tabla por defecto (ya la renderizamos arriba) pero conserva
	// contenido inyectado por plugins (ej. seguimiento de envio).
	remove_action( 'woocommerce_view_order', 'woocommerce_order_details_table', 10 );
	do_action( 'woocommerce_view_order', $order_id );
	?>
</div>
