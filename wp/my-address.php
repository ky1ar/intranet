<?php
/**
 * Addresses (My Account) — plantilla personalizada Krear 3D.
 * Override de woocommerce/myaccount/my-address.php
 */
defined( 'ABSPATH' ) || exit;

$customer_id   = get_current_user_id();
$show_shipping = ! wc_ship_to_billing_address_only() && wc_shipping_enabled();

$kd_icons = array(
	'doc'    => '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>',
	'truck'  => '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="3" width="15" height="13"/><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/></svg>',
	'user'   => '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/></svg>',
	'company'=> '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 21V5a1 1 0 0 1 1-1h9a1 1 0 0 1 1 1v16"/><path d="M15 9h4a1 1 0 0 1 1 1v11"/><line x1="3" y1="21" x2="21" y2="21"/><line x1="8" y1="8" x2="8.01" y2="8"/><line x1="8" y1="12" x2="8.01" y2="12"/><line x1="8" y1="16" x2="8.01" y2="16"/></svg>',
	'pin'    => '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13S3 17 3 10a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>',
	'city'   => '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"/><line x1="8" y1="2" x2="8" y2="18"/><line x1="16" y1="6" x2="16" y2="22"/></svg>',
	'phone'  => '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>',
	'shield' => '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>',
	'edit'   => '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.12 2.12 0 0 1 3 3L12 15l-4 1 1-4z"/></svg>',
);

$kd_cards = array(
	'billing' => array(
		'l1' => 'Dirección', 'l2' => 'de facturación',
		'header_icon' => 'doc',
		'badge'       => 'Dirección predeterminada para facturación',
		'badge_class' => 'kd-addr-badge--billing',
	),
);
if ( $show_shipping ) {
	$kd_cards['shipping'] = array(
		'l1' => 'Dirección', 'l2' => 'de envío',
		'header_icon' => 'truck',
		'badge'       => 'Dirección predeterminada para envío',
		'badge_class' => 'kd-addr-badge--shipping',
	);
}
?>

<p class="kd-addr-intro"><?php esc_html_e( 'The following addresses will be used on the checkout page by default.', 'woocommerce' ); ?></p>

<div class="woocommerce-Addresses kd-addr-grid">
	<?php foreach ( $kd_cards as $type => $cfg ) :
		$first    = get_user_meta( $customer_id, $type . '_first_name', true );
		$last     = get_user_meta( $customer_id, $type . '_last_name', true );
		$company  = get_user_meta( $customer_id, $type . '_company', true );
		$addr1    = get_user_meta( $customer_id, $type . '_address_1', true );
		$addr2    = get_user_meta( $customer_id, $type . '_address_2', true );
		$city     = get_user_meta( $customer_id, $type . '_city', true );
		$state    = get_user_meta( $customer_id, $type . '_state', true );
		$postcode = get_user_meta( $customer_id, $type . '_postcode', true );
		$phone    = get_user_meta( $customer_id, $type . '_phone', true );

		$name     = trim( $first . ' ' . $last );
		$address  = trim( $addr1 . ( $addr2 ? ' ' . $addr2 : '' ) );
		$loc      = trim( $city . ( $state ? ', ' . $state : '' ) . ( $postcode ? ' ' . $postcode : '' ), ', ' );
		$has_any  = $name || $company || $address || $loc || $phone;

		$edit_url = wc_get_endpoint_url( 'edit-address', $type, wc_get_page_permalink( 'myaccount' ) );
	?>
		<div class="kd-addr-card">
			<header class="kd-addr-head">
				<div class="kd-addr-head-title">
					<span class="kd-addr-head-ico"><?php echo $kd_icons[ $cfg['header_icon'] ]; ?></span>
					<h3><?php echo esc_html( $cfg['l1'] ); ?><br><?php echo esc_html( $cfg['l2'] ); ?></h3>
				</div>
				<a href="<?php echo esc_url( $edit_url ); ?>" class="kd-addr-edit"><?php echo $kd_icons['edit']; ?> <span><?php esc_html_e( 'Edit', 'woocommerce' ); ?></span></a>
			</header>

			<?php if ( $has_any ) :
				$rows = array( array( 'user', 'Nombre', $name ?: '—' ) );
				if ( $company ) $rows[] = array( 'company', 'Empresa', $company );
				if ( $address ) $rows[] = array( 'pin', 'Dirección', $address );
				if ( $loc )     $rows[] = array( 'city', 'Ciudad', $loc );
				if ( $phone )   $rows[] = array( 'phone', 'Teléfono', $phone );
			?>
				<div class="kd-addr-rows">
					<?php foreach ( $rows as $r ) : ?>
						<div class="kd-addr-row">
							<span class="kd-addr-row-ico"><?php echo $kd_icons[ $r[0] ]; ?></span>
							<div class="kd-addr-row-data">
								<span class="kd-addr-row-lbl"><?php echo esc_html( $r[1] ); ?></span>
								<span class="kd-addr-row-val"><?php echo esc_html( $r[2] ); ?></span>
							</div>
						</div>
					<?php endforeach; ?>
				</div>
				<div class="kd-addr-badge <?php echo esc_attr( $cfg['badge_class'] ); ?>">
					<?php echo $kd_icons['shield']; ?>
					<span><?php echo esc_html( $cfg['badge'] ); ?></span>
				</div>
			<?php else : ?>
				<div class="kd-addr-empty">
					<p><?php esc_html_e( 'You have not set up this type of address yet.', 'woocommerce' ); ?></p>
					<a href="<?php echo esc_url( $edit_url ); ?>" class="kd-addr-empty-btn">Agregar dirección</a>
				</div>
			<?php endif; ?>
		</div>
	<?php endforeach; ?>
</div>
